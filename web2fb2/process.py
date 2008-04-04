#coding=utf-8
import logging
import logging.handlers
import traceback

import md5
import random

import urlparse
import urllib2
import sys
import socket
import shutil
import time
import os
import StringIO
import cStringIO
import zipfile

import chardet
from BeautifulSoup import BeautifulSoup
import h2fb
import img_download

EBOOKZ_PATH = "ebookz" #путь к папке, гду будут хранится ebookи =)
TEMP_PATH = "temp" #папка для временных файлов
CLEAN_TIME = 900 #время, через которое будут удалятся старые ебуки
LOGZ_PATH = 'logz' #папка где будут логи лежать

#http://python.com.ua/ru/news/2006/04/20/zaschita-ot-duraka-v-programmah-na-yazyike-python/
#http://python.com.ua/ru/news/2006/04/07/rabota-s-fajlami/

log = logging.getLogger('web2fb2.process')

class web_params(object):
	def __init__(self):
		self.url = ''
		self.is_img = ''
		self.descr = None
		self.is_zip = True
		
class ebook_stat_(object):
	def __init__(self):
		self.file_size = 0
		self.work_time = 0.0
		self.url = ''
		self.path_with_file = ''
		self.file_name = '' 
		self.img = False
		self.descr = None

def clean_up():
	'''
	удаляем мусор, старые файлы
	'''
	#удаляем старые папки с книжками
	for dir in os.listdir(EBOOKZ_PATH):
		if time.time() - os.path.getmtime(os.path.join(EBOOKZ_PATH, dir)) > CLEAN_TIME:
			log.debug('Clearning up %s' % os.path.join(EBOOKZ_PATH, dir))
			shutil.rmtree(os.path.join(EBOOKZ_PATH, dir))
			
	#удаляем временные файлы
	for dir in os.listdir(TEMP_PATH):
		if time.time() - os.path.getmtime(os.path.join(TEMP_PATH, dir)) > CLEAN_TIME:
			log.debug('Clearning up %s' % os.path.join(TEMP_PATH, dir))
			shutil.rmtree(os.path.join(TEMP_PATH, dir))
			
class process:
	def do_web(self, params):
		
		#настраиваем логгер, чтоб логи сыпались в еще одно место (отдельный файл)
		log_file_name = urlparse.urlparse(params.url)[1][:48] + '_' + md5.new(params.url).hexdigest()[:10] + '.log'
		
		handler = logging.handlers.RotatingFileHandler(os.path.join(LOGZ_PATH, log_file_name), maxBytes = 50000, backupCount = 1)
		handler.setFormatter(logging.Formatter('%(asctime)s %(name)-24s %(levelname)-8s %(message)s'))			
		log.addHandler(handler)
		log.setLevel(logging.DEBUG)
		
		#начало работы
		log.info('************************************')
		log.info(str(params.url))
		
		#перехватываем все ошибки в лог
		try:
			rez = self.web(params)
		except:
			log.error('\n------------------------------------------------\n' + traceback.format_exc() + '------------------------------------------------\n')
			return (0, 'Internal error')
		else:
			return rez


	def web(self, params):
		
		start_time = time.time() #засекаем время
		
		#проверяем урл
		log.debug('Checking url')
		if not params.url:
			log.warning('Bad url')
			return (0, bad_url)
		
		ebook_stat = ebook_stat_()
		ebook_stat.url = params.url
		
		#генерируем имя для папок и файлов
		#имя временной папки генерится на основе урла и того - с картинкаи он или без
		#это нужно для кеширования
		source_folder_name = md5.new(params.url + str(params.is_img)).hexdigest()[:10]
		
		log.debug('Generated source folder name: %s' % (source_folder_name))
		
		source_folder = os.path.join(TEMP_PATH, source_folder_name)

		source_file_name = '__ebook.html'
		
		try:
			log.debug('Try to set  new time for %s' % os.path.join(source_folder))
			os.utime(os.path.join(source_folder), None) #пытаемся перевести время модификации папки, чтоб ее не удалили при подчистке
		except OSError, er:
			log.debug('Cant set new time')
			if er.errno != 2:
				raise er
		
		#НАДО ВМЕСТО ЭТОЙ ЗАДЕРЖКИ ПОДУМАТЬ О ЛОКАХ
		#делаем небольшую задержку, чтоб папку успели удалить при подчистке
		#на случай, если при подчистке после опеределения времени папки, не успели ее удалить
		time.sleep(0.2)
		
		#пытаемся создать временную папку. если она уже есть - значит файл уже есть и скачивать не надо.
		try:
			log.debug('Create temp folder: %s' % (source_folder))
			os.mkdir(source_folder) #создаем временную папку
		except OSError, er:
			if er.errno != 17:
				raise er
			else:
				log.info('Folder exist')
		else:
			#попытка скачать html
			log.info('Url downloading')
			log.debug('Start url downloading')
			try:
				data, real_url = self.download_html(params.url)
			except (urllib2.HTTPError, urllib2.URLError, IOError, ValueError), er:
				log.warning('Download error %s' % (er))
				return (0, er)
			log.debug('End of url downloading')
			log.info('Real download url is: %s ' % (real_url))
		
			#чистка html, получение списка картинок
			log.debug('Start processing html')
			data, imgs_list = process_html().do(data, source_folder, params.url, params.is_img)
			log.debug('End of processing html')
		
			#записываем html в файл
			log.debug('Writing source file: %s' % os.path.join(source_folder, source_file_name))
			file(os.path.join(source_folder, source_file_name), 'w').write(data)
		
			if params.is_img:
				#качаем картинки
				log.debug('Start image downloading')
				imgs_down = img_download.download(imgs_list, source_folder, log)
				log.debug('End of image downloading')
		
		#готовим параметры для преобразования html2fb2
		log.debug('Reading source file: %s' % os.path.join(source_folder, source_file_name))
		data = file(os.path.join(source_folder, source_file_name)).read()
		
		h2fb_params = h2fb.default_params.copy()
		h2fb_params['data'] = data
		h2fb_params['verbose'] = 1
		h2fb_params['encoding-from'] = 'UTF-8'
		h2fb_params['encoding-to'] = 'UTF-8'
		h2fb_params['convert-images'] = 1
		#params['file-name'] = os.path.join(source_folder, file_name)
		if params.is_img:
			h2fb_params['skip-images'] = 0

		if params.descr:
			log.info('Set descr')
			h2fb_params['descr'] = params.descr
				
		h2fb_params['informer'] = lambda msg: log.debug('h2fb ' + msg.strip()) #делаем вывод сообщений от h2fb2 в лог
		
		#собственно преобразование
		log.debug('Start h2fb process')
		mp = h2fb.MyHTMLParser()
		out_data = mp.process(h2fb_params)
		ebook_stat.descr = mp.get_descr()
		log.debug('End of h2fb process')
		
		#генерим имя файла и папки для готовой книги
		#имя папки с результатом - случайное
		ebookz_folder_name = md5.new(str(random.random())).hexdigest()[:10]
		log.debug('Generated ebookz folder name: %s' % (ebookz_folder_name))
		
		result_folder = os.path.join(EBOOKZ_PATH, ebookz_folder_name)
		
		ebook_stat.path = result_folder
		
		#генерируем имя для получившегося файла
		tmp_name = self.gen_name('_'.join(( ebook_stat.descr.author_first, ebook_stat.descr.title )))
		if tmp_name:
			file_name = tmp_name + '.fb2'
		else:
			file_name = urlparse.urlparse(params.url)[1][:48] + '.fb2'
		log.debug('Generated file name: %s' % (file_name))
		
		#создаем папку для готовой книги
		os.mkdir(result_folder)
		
		#zip файл
		if params.is_zip:
			f = cStringIO.StringIO()
			zp = zipfile.ZipFile(f, 'w')
			
			zip_info = zipfile.ZipInfo(file_name)
			zip_info.date_time = time.localtime(time.time())[:6]
			zip_info.compress_type = zipfile.ZIP_DEFLATED
			
			zp.writestr(zip_info, out_data)
			zp.close()
			
			out_data = f.getvalue()
			f.close()
			file_name += '.zip'
		
		ebook_stat.file_name  = file_name
		
		#записываем книгу
		log.debug('Writing ebook: %s into: %s (ebook len: %s)' % (file_name, result_folder, len(out_data)))
		file(os.path.join(result_folder, file_name), 'wb').write(out_data)
		
		ebook_stat.file_size = os.path.getsize(os.path.join(result_folder, file_name))    # размер файла в байтах
		ebook_stat.work_time = time.time() - start_time, #размер книги в килобайтах
		ebook_stat.img = params.is_img

		return (1, ebook_stat)
	
	def download_html(self, url):
		'''
		скачка html страницы
		возвращает html страничку и real URL of the page fetched. This is useful because it may have followed a redirect.
		'''
		socket.setdefaulttimeout(20)
		
		opener = urllib2.build_opener()
		request = urllib2.Request(url, None, {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.8.1.8) Gecko/20071008 Firefox/2.0.0.8"})
		handle = opener.open(request)
		text = handle.read()
		realurl = handle.geturl()
		handle.close()
		return text, realurl
	
	def gen_name(self, name):
		'''
		функция пробразования имени файла.
		если в имени есть русские быквы - переводит их в транслит.
		если в имени есть быквы других алфавитов, кроме русских и аглийских - возвращает None
		вырезает все ненужные символы, уменьшает имя до 64 символов
		'''
		
		good_alphanum = u'abcdefghijklmnopqrstuvwxyz1234567890' #хорошие символы, которые надо оставить
		good_not_convert = u'' #хорошие символы, которые не явл. быквами или цифрами, но которые тоже надо оставить
		convert_2_space = u' _' #сиволы, которые надо конверитировать в пробельные
			
		space_char = '_' #символ пробела
		
		trans = {
			u'а':u'a',
			u'б':u'b',
			u'в':u'v',
			u'г':u'g',
			u'д':u'd',
			u'е':u'e',
			u'ё':u'e',
			u'ж':u'zh',
			u'з':u'z',
			u'и':u'i',
			u'й':u'i',
			u'к':u'k',
			u'л':u'l',
			u'м':u'm',
			u'н':u'n',
			u'о':u'o',
			u'р':u'r',
			u'п':u'p',
			u'с':u's',
			u'т':u't',
			u'у':u'u',
			u'ф':u'f',
			u'х':u'h',
			u'ц':u'ts',
			u'ч':u'ch',
			u'ш':u'sh',
			u'щ':u'sch',
			u'ь':u'\'',
			u'ы':u'y',
			u'ъ':u'\'',
			u'э':u'e',
			u'ю':u'yu',
			u'я':u'ya'
		}
			
		name = name.lower()
			
		tmp_name = u''
		for c in name:
			if ord(c) > 128: #если выходит за пределы латиницы
				if c in trans.keys(): #и при этом русские
					new_c = trans.get(c, u'') #транслитерация
				else:
					return None
			else:
				new_c = c
			tmp_name += new_c
			
			
		#фильтруем символы
		new_name = u''
		alphanum_flag = False #флаг, что в имени попалась буква или цифра
		
		for c in tmp_name:
			if c in good_alphanum:
				alphanum_flag = True
				new_name += c
					
			elif c in good_not_convert:
				new_name += c
					
			elif c in convert_2_space:
				if new_name:
					if new_name[-1] != space_char: #не ставим повторяющиеся пробелы
						new_name += space_char
					
		new_name = new_name.strip('-' + space_char)
			
		if not alphanum_flag: #
			return None
		
		if not new_name:
			return None
			
		return str(new_name[:64]) #обрезаем имя по 64-ый символ.

class process_html:

	def do(self, data, source_folder, url, is_img):
		'''
		рабочая функция - вынести в отделный модуль.
		на входе - строка html, на выходе строка fb2
		'''
		sys.setrecursionlimit(40000)
		
		log.debug('Start recoding')
		data = self.recoding(data)
		log.debug('End of recoding')
		
		if is_img:
			log.debug('Start process images')
			data, img_list = self.process_images(data, source_folder, url)
			log.debug('End of process images')
		else:
			img_list = None
		
		return data, img_list
	
	def recoding(self, data):
		'''
		конвертируем в UTF-8
		'''
		
		tmp = chardet.detect(data) #определяем кодировку
		
		log.info('Detected encoding: %s' % (tmp))
		
		new_data = data.decode(tmp['encoding']).encode('UTF-8') #перекодируем в UTF8
		return  new_data

	def process_images(self, data, source_folder, url):
		'''
		обработка картинок в html:
		замена путей картинок на пути в файловой системе, составление списка картинок для скачки
		Входные переменные:
			data - HTML
			source_floder - папка, где будут картинки
			url - адрес страницы, откуда скачивался html
		возвращает  HTML с замененными путями и список картинок
		'''
		
		imgs_list = {}
		
		soup = BeautifulSoup(data)
		img_tags = soup.findAll(name = 'img')
		
		log.info('Find %s images' % (len(img_tags)))
		
		for img_tag in img_tags:
			if img_tag['src']:
				#делаем абсолютный урл
				new_url = urlparse.urljoin(url, img_tag['src'])
				
				#генерим имя картинки
				img_name = md5.new(str(random.random())).hexdigest()[:10]
				
				#заносим в словарь урл и имя файла
				imgs_list[new_url] = img_name
				
				# меняем ссылку на путь + имя файла
				img_tag['src'] = source_folder + '/' + img_name
				
		log.info('%s images to download' % (len(imgs_list)))
		
		new_data = str(soup)
		
		return new_data, imgs_list
	

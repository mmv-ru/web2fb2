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

import chardet
from BeautifulSoup import BeautifulSoup
import h2fb
import img_download

EBOOKZ_PATH = "ebookz" #путь к папке, гду будут хранится ebookи =)
TEMP_PATH = "temp" #папка для временных файлов
CLEAN_TIME = 600 #время, через которое будут удалятся старые ебуки
LOGZ_PATH = 'logz' #папка где будут логи лежать

#http://python.com.ua/ru/news/2006/04/20/zaschita-ot-duraka-v-programmah-na-yazyike-python/
#http://python.com.ua/ru/news/2006/04/07/rabota-s-fajlami/

log = logging.getLogger('web2fb2.process')

def clean_up():
	'''
	удаляем мусор, старые файлы
	'''
	for dir in os.listdir(EBOOKZ_PATH):
		if time.time() - os.path.getmtime(os.path.join(EBOOKZ_PATH, dir)) > CLEAN_TIME:
			log.debug('Clearning up %s' % os.path.join(EBOOKZ_PATH, dir))
			shutil.rmtree(os.path.join(EBOOKZ_PATH, dir))
					
	for dir in os.listdir(TEMP_PATH):
		if time.time() - os.path.getmtime(os.path.join(TEMP_PATH, dir)) > CLEAN_TIME:
			log.debug('Clearning up %s' % os.path.join(TEMP_PATH, dir))
			shutil.rmtree(os.path.join(TEMP_PATH, dir))
			
class process:
	def do_web(self, url):
		#настраиваем логгер, чтоб логи сыпались в еще одно место (отдельный файл)
		log_file_name = urlparse.urlparse(url)[1][:48] + '_' + md5.new(url).hexdigest()[:10] + '.log'
		
		handler = logging.handlers.RotatingFileHandler(os.path.join(LOGZ_PATH, log_file_name), maxBytes = 50000, backupCount = 1)
		handler.setFormatter(logging.Formatter('%(asctime)s %(name)-24s %(levelname)-8s %(message)s'))			
		log.addHandler(handler)
		log.setLevel(logging.DEBUG)
		
		#начало работы
		log.info('************************************')
		log.info(str(url))
		
		#перехватываем все ошибки в лог
		try:
			rez = self.web(url)
		except:
			log.error('\n------------------------------------------------\n' + traceback.format_exc() + '------------------------------------------------\n')
			return (0, 'Internal error')
		else:
			return rez


	def web(self, url):
		
		#проверяем урл
		log.debug('Checking url')
		if not url:
			log.warning('Bad url')
			return (0, bad_url)
		
		log.info('Url downloading')
		
		#попытка скачать html
		log.debug('Start url downloading')
		try:
			data, real_url = self.download_html(url)
		except (urllib2.HTTPError, urllib2.URLError, IOError, ValueError), er:
			log.warning('Download error %s' % (er))
			return (0, er)
		log.debug('End of url downloading')
		log.info('Real download url is: %s ' % (real_url))
		
		#генерируем имя для временной папки
		folder_name = md5.new(url + str(random.random())).hexdigest()[:10]
		log.debug('Generated folder name: %s' % (folder_name))
		
		source_folder = os.path.join(TEMP_PATH, folder_name)
		
		result_folder = os.path.join(EBOOKZ_PATH, folder_name)
		
		#генерируем имя для получившегося файла
		file_name = urlparse.urlparse(url)[1][:48] + '.fb2'
		log.debug('Generated file name: %s' % (file_name))
		
		#создаем временную папку
		log.debug('Create temp folder: %s' % (source_folder))
		os.mkdir(source_folder)
		
		#чистка html, получение списка картинок
		log.debug('Start processing html')
		data, imgs_list = process_html().do(data, source_folder, url)
		log.debug('End of processing html')
		
		#качаем картинки
		log.debug('Start image downloading')
		img_download.download(imgs_list, source_folder, log)
		log.debug('End of image downloading')
		
		#создаем папку для готовой книги
		log.debug('Create folder for storing ebook: %s' % (result_folder))
		os.mkdir(result_folder)

		
		#готовим параметры для преобразования html2fb2
		params = h2fb.default_params.copy()
		params['data'] = data
		params['verbose'] = 1
		params['encoding-from'] = 'UTF-8'
		params['encoding-to'] = 'UTF-8'
		params['convert-images'] = 1
		params['skip-images'] = 0
		params['informer'] = lambda msg: log.debug('h2fb ' + msg.strip()) #делаем вывод сообщений от h2fb2 в лог
		
		#собственно преобразование
		log.debug('Start h2fb process')
		out_data = h2fb.MyHTMLParser().process(params)
		log.debug('End of h2fb process')
		
		#записываем книгу
		log.debug('Writing ebook: %s into: %s (ebook len: %s)' % (file_name, result_folder, len(out_data)))
		file(os.path.join(result_folder, file_name), 'w').write(out_data)
		
		#удаляем временную папку
		log.debug('Removing temp folder: %s' % (source_folder))
		shutil.rmtree(source_folder)

		return (1, os.path.join(result_folder, file_name), file_name)
	
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
	

class process_html:

	def do(self, data, source_folder, url):
		'''
		рабочая функция - вынести в отделный модуль.
		на входе - строка html, на выходе строка fb2
		'''
		sys.setrecursionlimit(40000)
		
		log.debug('Start recoding')
		data = self.recoding(data)
		log.debug('End of recoding')
		
		log.debug('Start process images')
		data, img_list = self.process_images(data, source_folder, url)
		log.debug('End of process images')
		
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
	
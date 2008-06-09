#coding=utf-8
import traceback


import md5
import random
import sys
import shutil
import time
import os
import pickle
import StringIO
import cStringIO
import zipfile
import time
import urlparse

import h2fb
import yah2fb
import fb_utils

import lock
import log

import progress
import webprocess
import htmlprocess


EBOOKZ_PATH = "ebookz" #путь к папке, гду будут хранится ebookи =)
RAW_PATH = "raw" #путь к папке, где лежат скачанные html и картинки
TEMP_PATH = "raw_temp" #папка для временных файлов
CLEAN_TIME = 600 #время, через которое будут удалятся старые ебуки

#http://python.com.ua/ru/news/2006/04/20/zaschita-ot-duraka-v-programmah-na-yazyike-python/
#http://python.com.ua/ru/news/2006/04/07/rabota-s-fajlami/


class web_params(object):
	def __init__(self):
		self.url = ''
		self.is_img = ''
		self.is_zip = True
		self.descr = None
		self.yah2fb = False
		
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
	def clean_folder(folder, clean_time):
		for dir in os.listdir(folder):
			if time.time() - os.path.getmtime(os.path.join(folder, dir)) > clean_time:
				log.debug('Clearning up %s' % os.path.join(folder, dir))
				shutil.rmtree(os.path.join(folder, dir))
	
	#удаляем старые папки с книжками
	l = lock.lock_('book')
	clean_folder(EBOOKZ_PATH, CLEAN_TIME)
	l.unlock()	
	
	#удаляем временные файлы
	l = lock.lock_('temp')
	clean_folder(TEMP_PATH, CLEAN_TIME)
	l.unlock()
			
	#удаляем скаченные файлы
	l = lock.lock_('raw')
	clean_folder(RAW_PATH, CLEAN_TIME)
	l.unlock()
			
def do(params, ajax = False):

	log.debug('start process')
	#создаем хешь из всего - для однозначной идентификации файла
	folder_name = md5.new(str(pickle.dumps(params))).hexdigest()
	log.debug('Generate name: %s'% folder_name)
	
	ebook_folder = os.path.join(EBOOKZ_PATH, folder_name)
	
	progres = progress.progress(os.path.join(ebook_folder, '.progress'))
	
	l = lock.lock_('book')
	if not try_create_folder(ebook_folder): #такая книга уже создается или уже есть
		l.unlock()
		
		if ajax:
			log.debug('time to load progress')
			progres.load()
			log.debug('progeress loaded!')
			
			return progres
		
		log.info('ebook %s folder exist, waitnig for done' % ebook_folder)
		while 1: #ждем, пока книга создаcтся
			progres.load()
			if progres.done or progres.error:
				break
			time.sleep(1)
		log.debug('wating complete!')
		return progres #возваращаем результат

	else:
		progres.save()
		l.unlock()
		
		if ajax:
			sys.stdout.flush()
			if os.fork():
				progres.load()
				return progres
			else:
				fw = open('/dev/null','w')
				os.dup2(fw.fileno(),1)
				os.dup2(fw.fileno(),2)
		
		try:
			raw_name = md5.new(str(pickle.dumps([params.url, params.is_img]))).hexdigest()
			raw_folder = os.path.join(RAW_PATH, raw_name)
			raw_path = os.path.join(raw_folder, 'html.html')
			
			l = lock.lock_('raw')
			if check_folder(raw_folder):		
				l.unlock()
				
			else:
				l.unlock()
			
				temp_name = md5.new(str(random.random())).hexdigest()[:10]
				temp_folder = os.path.join(TEMP_PATH, temp_name)
				temp_path = os.path.join(temp_folder, 'html.html')
			
				l = lock.lock_('temp')
				os.mkdir(temp_folder)
				l.unlock()
			
				data = webprocess.do(params.url, params.is_img, temp_folder, progres)
				file(temp_path, 'w').write(data.encode('UTF-8'))
			
				l = lock.lock_("temp")
				l1 = lock.lock_("raw")
				log.debug('lock2')
				try_move_folder(temp_folder, raw_folder)
				l1.unlock()
				l.unlock()
			
			params.descr.url = params.url
			
			#data = file(raw_path).read().decode('UTF-8')
			ebook_tmp_path = os.path.join(ebook_folder, '.ebook.fb2')
			
			log.debug('start html process')
			progres.level = 3
			progres.save()
			log.debug('start html process2')
			descr = htmlprocess.do(raw_path, params.descr, ebook_tmp_path, progres, params.yah2fb, params.is_img)
			log.debug('End of html process')
			
			ebook_name = gen_name('_'.join((descr.author_last, descr.author_first, descr.title )))
			if ebook_name:
				ebook_path = os.path.join(ebook_folder, ebook_name + '.fb2')
			else:
				ebook_path = os.path.join(ebook_folder, urlparse.urlparse(params.url)[1][:48] + '.fb2')

			os.rename(ebook_tmp_path, ebook_path)
			
			if params.is_zip:
				log.debug("Start file zipping")
				ebook_path = zip_file(ebook_path, ebook_folder)
				log.debug("End of file zipping")
				
			ebook_stat = ebook_stat_()
			ebook_stat.url = params.url
			ebook_stat.path = ebook_folder
			ebook_stat.descr = descr
			ebook_stat.file_name = os.path.split(ebook_path)[1]
			ebook_stat.work_time  = 0
			ebook_stat.file_size = os.path.getsize(ebook_path) 
			ebook_stat.img =  params.is_img
			
			progres.done = ebook_stat
		except Exception, er:
			progres.error = er
			log.error('\n------------------------------------------------\n' + traceback.format_exc() + '------------------------------------------------\n')
			
		progres.save()
		return progres

	
def try_create_folder(folder)	:

	try:
		log.debug('Try to set  new time for %s' % folder)
		os.utime(folder, None) #пытаемся перевести время модификации папки, чтоб ее не удалили при подчистке
	except OSError, er:
		log.debug('Cant set new time')
		if er.errno != 2:
			raise er
	
	#пытаемся создать временную папку. если она уже есть значит кто-то уже делает работу %.
	try:
		log.debug('Create folder: %s' % (folder))
		os.mkdir(folder) #создаем временную папку
	except OSError, er:
		if er.errno != 17:
			raise er
		else:
			log.info('Folder exist')
			return False
			
	else:
		return True
		
def check_folder(folder):
	log.debug('Check folder %s' % folder)
	try:
		log.debug('Try to set  new time for %s' % folder)
		os.utime(folder, None) #пытаемся перевести время модификации папки, чтоб ее не удалили при подчистке
	except OSError, er:
		log.debug('Cant set new time')
		if er.errno != 2:
			raise er
		return False
	else:
		return True
	
def try_move_folder(source_folder, dest_folder):
	log.debug('try to move folder %s to %s' % (source_folder, dest_folder))
	if not os.path.exists(dest_folder):
		shutil.move(source_folder, dest_folder)
		log.debug('Move success')
	else:
		shutil.rmtree(source_folder)
		log.debug('Dest folder exist, delete source folder')
		
def zip_file(source_path, rez_folder):
	file_name = os.path.split(source_path)[1]
	zip_path = os.path.join(rez_folder, file_name + ".zip")
	
	zp = zipfile.ZipFile(zip_path, 'w')
	zip_info = zipfile.ZipInfo(file_name)
	
	zip_info.date_time = time.localtime(time.time())[:6]
	zip_info.compress_type = zipfile.ZIP_DEFLATED
	
	zp.writestr(zip_info, file(source_path, 'rb').read())
	zp.close()
	
	return zip_path

def gen_name(name):
	'''
	функция пробразования имени файла.
	если в имени есть русские буквы - переводит их в транслит.
	если в имени есть быквы других алфавитов, кроме русских и аглийских - возвращает None
	вырезает все ненужные символы, уменьшает имя до 64 символов
	'''
	
	inglish_chars = u'§©«»—' + u''.join([chr(x) for x in xrange(127)]) #английские символы
	
	#русские символы
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
				u'я':u'ya',
				u'à':u'ya'
			}
	
	
	good_alphanum = u'abcdefghijklmnopqrstuvwxyz1234567890' #хорошие символы, которые надо оставить
	good_not_convert = u'' #хорошие символы, которые не явл. быквами или цифрами, но которые тоже надо оставить
	convert_2_space = u' _-' #сиволы, которые надо конверитировать в пробельные
		
	space_char = '_' #символ пробела

	name = name.lower()
		
	tmp_name = u''
	for c in name:
		if c not in inglish_chars: #если выходит за пределы латиницы
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



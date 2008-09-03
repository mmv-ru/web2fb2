#coding=utf-8

# главный модуль обработки

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

import lock
import log

import progress
import webprocess
import htmlprocess

import sess_wrap

EBOOKZ_PATH = "ebookz" #путь к папке, гду будут хранится ebookи =)
RAW_PATH = "raw" #путь к папке, где лежат скачанные html и картинки
TEMP_PATH = "raw_temp" #папка для временных файлов
CLEAN_TIME = 600 #время, через которое будут удалятся старые ебуки

class web_params(object):
	"""
	класс, контейнер параметров, передаваемых в обратку из веб-интерфейса
	"""
	def __init__(self):
		self.urls = []
		self.is_img = ''
		self.is_zip = True
		self.is_tab = False
		self.descr = None
		self.yah2fb = False
		
class ebook_stat_(object):
	"""
	модуль контейнер для параметров книги, возвращаемых из обработки в веб-интерйфейс
	"""
	def __init__(self):
		self.file_size = 0
		self.work_time = 0.0
		self.urls = []
		self.path_with_file = ''
		self.file_name = '' 
		self.img = False
		self.tab = False
		self.yah2fb = False
		self.descr = None
		self.valid = None
		
class SessRet(Exception):
	'''
	объект, исключение, возвращаемый если работа не началась и надо вернуть очередь
	'''
	def __init__(self, value):
		self.value = value
		
class ProgError(Exception):
	'''
	объект - исключение при обработке
	
	'''
	def __init__(self, value = 'Progress Error'):
		self.value = value
	def __str__(self):
		return repr(self.value)
		
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
			
def do(params, sess, ajax = False):

	"""
	рабочая функция процесса. принимает объект класса web_params, возвращает объект класса progress.progress
	"""

	log.debug('start process')
	#создаем хешь из всего - для однозначной идентификации файла. имя папки однозначно отображает параметры создания книги
	folder_name = md5.new(str(pickle.dumps(params))).hexdigest()
	
	log.debug('Generate name: %s'% folder_name)
	
	ebook_folder = os.path.join(EBOOKZ_PATH, folder_name) #путь к папке с будующей книгой
	
	progres = progress.progress(os.path.join(ebook_folder, '.progress'))  #создаем объект прогресса ( ифнормация о ходе обработки книги)
	
	l = lock.lock_('book') #делаем блокировку на папку с книгами
	#надо не в коем случае не забыть ее снять
	if not try_create_folder(ebook_folder): #такая книга уже создается или уже есть
		l.unlock() #снимаем блокировку
		
		log.debug('loading progress')
		progres.load() #загружаем данные прогресса из файла
		
		if ajax: #если у нас ajax версия
			#считываем прогресс и отправляем в вебинтерфейс
			log.debug('time to load progress')
			progres.load() #считываем прогересс и от
			log.debug('progeress loaded!')
			
			#если книга создается уж слишком долго как-то - возвращаем ошибку
			if ((time.time()  - progres.time) > 600) and not (progres.error or progres.done):
				raise ProgError, 'Script error'
			
			return progres
		
		#если не ajax
		#тупо ждем в цикле, пока книга не сделается
		log.info('ebook %s folder exist, waitnig for done' % ebook_folder)
		while 1: #ждем, пока книга создаcтся
			progres.load()
			
			#если книга создается уж слишком долго как-то - возвращаем ошибку
			if ((time.time()  - progres.time) > 600) and not (progres.error or progres.done):
				raise ProgError, 'Script error'
			
			if progres.done or progres.error:
				break
		log.debug('wating complete!')
		return progres #возвращаем результат
	
	else: # если папки с книгой нету (т.е. такой книги не создается и не создавалось, будем ее создавать
		
		log.debug('start session')
		
		sl = lock.lock_('sess')
		s = sess_wrap.session_start(sess) #делаем запрос на старт сессий
		sl.unlock()
		
		#проверяем, можем работать, или нет
		if s != True:
			shutil.rmtree(ebook_folder) #удаляем ранее созданную папку для ебуки
			l.unlock() #снимаем блокировку
			
			raise SessRet, s #возвращаем ошибку
		
		log.info('Yes! new session')
		
		progres.save() #сохраняем новый погресс
		l.unlock() #снимаем блокировку
		
		if ajax:
			#создаем отдельный поток для процесса создания книги
			#грязынй хак с потоками ввода-вывода
			sys.stdout.flush()
			if os.fork(): #поток, из которого возвращаемся
				progres.load()
				return progres
			else:
				#грязынй хак с потоками ввода-вывода
				#отсытковываем процесс от потоков ввода вывода, чтоб апач не ждал окончания работы, а отдал страницу целиком
				fw = open('/dev/null','w')
				os.dup2(fw.fileno(),1)
				os.dup2(fw.fileno(),2)
		
		#собственно сам процесс
		try:
			raw_paths = []
			for url in params.urls:
				#создаем имя для папки, в которую скачивается страница и картинки. имя папки однозначно отображает параметры страницы
				raw_name = md5.new(str(pickle.dumps([url, params.is_img]))).hexdigest()
				raw_folder = os.path.join(RAW_PATH, raw_name)
				raw_paths.append(os.path.join(raw_folder, 'html.html'))
			
				#если такая папка уже есть - нафиг работать, пользуемся готовым
				l = lock.lock_('raw')
				if check_folder(raw_folder):
					l.unlock()
				
				else:
					l.unlock()
				
					# если халявы нет, придется все делать с нуля
					#созаем рандомное имя для папки
					temp_name = md5.new(str(random.random())).hexdigest()[:10]
					temp_folder = os.path.join(TEMP_PATH, temp_name)
					temp_path = os.path.join(temp_folder, 'html.html')
			
					l = lock.lock_('temp')
					os.mkdir(temp_folder)
					l.unlock()
			
					#запускаем скачку страницы и разные предобработки
					data = webprocess.do(url, params.is_img, temp_folder, progres)
					file(temp_path, 'w').write(data.encode('UTF-8'))
			
					# пытаемся перенести временную папку в папку в которую все скачивается
					l = lock.lock_("temp")
					l1 = lock.lock_("raw")
					log.debug('lock2')
					try_move_folder(temp_folder, raw_folder)
					l1.unlock()
					l.unlock()
			
			params.descr.urls = params.urls
			
			#data = file(raw_path).read().decode('UTF-8')
			ebook_tmp_path = os.path.join(ebook_folder, '.ebook.fb2') #временное имя книги, вместе с папкой
			
			#сохраняем прогресс
			progres.level = 3
			progres.save()
			log.debug('start html process')
			descr, valid = htmlprocess.do(raw_paths, params.descr, ebook_tmp_path, progres, params.yah2fb, params.is_img, params.is_tab) #процесс перевода html в книгу
			log.debug('End of html process')
			
			#создаем имя
			auths_str = '_'.join([ auth['last'] + '_' + auth['first'] for auth in descr.authors])
			
			log.debug('book_auth_str %s' % auths_str.encode('UTF8'))
			log.debug('book_title %s' % descr.title.encode('UTF8')) 
			ebook_name = gen_name('_'.join((auths_str, descr.title )))
			if ebook_name:
				ebook_path = os.path.join(ebook_folder, ebook_name + '.fb2')
			else:
				ebook_path = os.path.join(ebook_folder, urlparse.urlparse(params.urls[0])[1][:64] + '.fb2')

			#переименовываем книгу из временного имени в новое
			os.rename(ebook_tmp_path, ebook_path)
			
			#зипуем книгу
			if params.is_zip:
				log.debug("Start file zipping")
				ebook_path = zip_file(ebook_path, ebook_folder)
				log.debug("End of file zipping")
				
			#создаем и заполняем объект реузльтатов.
			ebook_stat = ebook_stat_()
			ebook_stat.urls = params.urls
			ebook_stat.path = ebook_folder
			ebook_stat.descr = descr
			ebook_stat.file_name = os.path.split(ebook_path)[1]
			ebook_stat.work_time  = 0
			ebook_stat.file_size = os.path.getsize(ebook_path) 
			ebook_stat.img =  params.is_img
			ebook_stat.tab =  params.is_tab
			ebook_stat.yah2fb = params.yah2fb
			ebook_stat.valid = valid
			
			progres.done = ebook_stat # сохраняем в прогрессе
		except Exception, er: # если в процессе всей этой деятельности произошла ошибка, возвращаем ошибку
			progres.error = er
			log.error('\n------------------------------------------------\n' + traceback.format_exc() + '------------------------------------------------\n')
		
		#завершаем сессию
		log.debug('end session')
		sl = lock.lock_('sess')
		sess_wrap.session_end(sess)
		sl.unlock()
		
		progres.save() 
		return progres #возвращаем прогресс

	
def try_create_folder(folder)	:
	'''
	пытается создать папку folder
	если такая есть - возвращает False, иначе True
	'''

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
	'''
	проверяет наличие папки folder, при этом переводит время создания папки на текущее
	'''
	
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
	'''
	пытается перенести папку source_folder в dest_folder
	'''

	log.debug('try to move folder %s to %s' % (source_folder, dest_folder))
	if not os.path.exists(dest_folder):
		shutil.move(source_folder, dest_folder)
		log.debug('Move success')
	else:
		shutil.rmtree(source_folder)
		log.debug('Dest folder exist, delete source folder')
		
def zip_file(source_path, rez_folder):
	'''
	упаковывает файл source_path в папку rez_dolder, к имени файла добавляет zip и возвращает новое имя файла вместе с путем
	'''
	
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



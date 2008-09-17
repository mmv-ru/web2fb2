#coding=utf-8
import time
from xml.sax.saxutils import escape as xmlescaper #функция, экранируюущая невалидные для xml символы
import md5


#на текущий момент BeautifulSoup плохо обрабатывает &nbsp;
import BeautifulSoup as BS
#отключаем в BeautifulSoup - недопускание вложенности одинаковых тегов
#(она закрывает тег, перед открытием такого-же)
BS.BeautifulSoup.NESTABLE_TAGS['strong'] = []
BS.BeautifulSoup.NESTABLE_TAGS['b'] = []
BS.BeautifulSoup.NESTABLE_TAGS['i'] = []
BS.BeautifulSoup.NESTABLE_TAGS['em'] = []
BS.BeautifulSoup.NESTABLE_TAGS['var'] = []
BS.BeautifulSoup.NESTABLE_TAGS['cite'] = []
BS.BeautifulSoup.NESTABLE_TAGS['p'] = []
BS.BeautifulSoup.NESTABLE_TAGS['pre'] = []


import codecs
import re
import urllib
import os.path
import base64
import os
import shutil
from PIL import Image
import cStringIO

import fb_utils

class params_(object):
	'''
	параметры, передаваемые в парсер
	'''
	def __init__(self):
		self.file_out = None #имя выходного файла (можно с путями)
		self.source_files = [] #имена выходных файлов (можно с путями)
		self.descr = None #объкт дескрипшена (см. fb_utils) для формирования заголовка fb2
		self.skip_images = None #не обрабатывать картинки
		self.skip_tables = None #не обрабатывать картинки

class binary(object):
	'''
	служебный объект, для работы со стораджем fb2 (там где картинки хранятся
	'''
	
	def __init__(self):
		self.f = os.tmpfile()
		self.ids = []

	def get(self):
		self.f.seek(0)
		return self.f

	def add(self, type, id, data):
		if id not in self.ids: #если такого объекта еще нет в сторадже, сохраняем его туда
			self.f.write('<binary content-type="%s" id="%s">' % (type, id))
			self.f.write(base64.encodestring(data))
			self.f.write('</binary>\n')
			self.ids.append(id)

def get_image( src):
	'''
	src - путь к файлу с картинкой.
	возвращает {'type':'png' или 'jpg', 'data':данные}, None - в случае неудачи.
	понимает gif, jpeg, png. gif - перекодирует в png
	'''
	try:
		im = Image.open(src)
	except IOError:
		return None

	if im.format == 'GIF':
		f = cStringIO.StringIO()
		im.save(f, "PNG")
		return {'data':f.getvalue(), 'type':'png'}

	elif im.format == 'PNG':
		try:
			data = open(src, 'rb').read()
		except IOError:
			return None
		else:
			return {'data':data, 'type':'png'}

	elif im.format == 'JPEG':
		try:
			data = open(src, 'rb').read()
		except IOError:
			return None
		else:
			return {'data':data, 'type':'jpg'}

	return None

def fix_nbsp_bug(s):
	"""
	заменяет то, что получается в процессе конвертации из &nbsp; на пробел
	"""
	return s.replace(u' ', u' ')
	

class fb2_(object):
	'''
	собственно - здесь формируется костяк fb2
	'''
	def __init__(self, f_name):
		'''
		f_name - имя выходного файла
		'''

		self.f_out = file(f_name, 'wb')

		self.soup = BS.BeautifulStoneSoup(selfClosingTags=['image'])
		body = BS.Tag(self.soup, 'body')
		self.soup.append(body) #делаем склет для fb2 (вставляем тег боди, чтоб к нему все приклеивать)

		self.binary = binary() #подключаем бинарные данные
		
		self.description = ''

	def get_rez(self):
		'''
		собираем все вместе и записываем в файл.
		'''

	
		head = """<?xml version="1.0" encoding="UTF-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:xlink="http://www.w3.org/1999/xlink">
"""
		foot = """\n</FictionBook>"""

		self.f_out.write(head) #служебные теги
		self.f_out.write(self.description.encode('UTF-8')) #подключаем дискрипшн
		self.f_out.write( self.soup.renderContents(encoding='UTF-8', prettyPrint = False) ) # рендерим в XML soup -структуру
		shutil.copyfileobj(self.binary.get(), self.f_out) #добавляем в файл секцию binary
		self.f_out.write(foot) #служебные теги

	def make_description(self, descr):
		'''
		формирование секции description для fb2
		она формируется в текстовом виде, что улучшить читабельность исходника
		'''
		
		#fill title-info
		self.description += '<description>\n'
		self.description += '<title-info>\n'
		self.description += '<genre>%s</genre>\n' % descr.genre
		for author_d in descr.authors:
			authors = '<author>'
			authors  += '<first-name>%s</first-name>' % xmlescaper(author_d['first'])
			authors  += '<middle-name>%s</middle-name>' % xmlescaper(author_d['middle'])
			authors  += '<last-name>%s</last-name>' % xmlescaper(author_d['last'])
			authors += '</author>\n'
		
		self.description += authors
		self.description += '<book-title>%s</book-title>\n' % xmlescaper(descr.title)
		self.description += '<annotation></annotation>\n'
		self.description += '<lang>%s</lang>\n' % xmlescaper(descr.lang)
		self.description += '</title-info>\n'
		
		#fill document-info
		self.description += '<document-info>\n'
		self.description += '<author><nickname></nickname></author>\n'
		if descr.program_info:
			self.description += '<program-used>%s</program-used>\n' % descr.program_info
		self.description += '<date value="%s">%s</date>\n' % (time.strftime('%Y-%m-%d'), time.strftime('%Y-%m-%d'))
		
		if descr.urls:
			self.description += '<src-url>%s</src-url>\n' % ' '.join(descr.urls)
		self.description += '<id>%s</id>\n' % descr.id
		self.description += '<version>%s</version>\n' % descr.version
		self.description += '</document-info>\n'
		self.description += '</description>\n'

class html2fb2(object):
	'''
	парсер html
	'''
	def __init__(self, fb2, in_file, skip_images = False, skip_tables = False):
		self.in_file = in_file 
		self.skip_images = skip_images
		self.skip_tables = skip_tables
		self.fb2 = fb2
		self.fb2s = fb2.soup # soup структура fb2
		

		#читаем файлс html-кой
		data = codecs.open(self.in_file, 'r', 'utf-8').read()

		self.soup = BS.BeautifulSoup(data, selfClosingTags=[], convertEntities="html") #парсим html в soup структуру
		

	def detect_descr(self):
		'''
		пытаемся вытащить title
		'''
		
		try:
			#ищем его в <head><title>
			title = fix_nbsp_bug( u''.join( self.soup.html.title.findAll(text = True) ) ) #try take title from <title>
			
		except AttributeError:
			
			try:
				#пробуем взять его из первого попавшегося h1, h2, ...
				title = fix_nbsp_bug( ''.join(self.soup.html.body.find(name = re.compile(r'h\d')).findAll(text = True)) )#try to found h tags for title
				
			except AttributeError:
				title = ''
		return title

	
	def process(self):
		
		soup = self.fb2s
		
		#создаем секцию
		section = BS.Tag(soup, 'section')
		
		#пытаемся подобрать для секции загловок
		try:
			title_text = fix_nbsp_bug( ''.join(self.soup.html.title.findAll(text = True)) ).strip() #try take title from <title>
		except AttributeError:
			pass
		else:
			if title_text:
				#если получилось, пишем заголовок в секцию
				title = BS.Tag(soup, 'title')
				p = BS.Tag(soup, 'p')
				p.append( BS.NavigableString( xmlescaper(title_text) ) )
				title.append(p)
				section.append(title)
		
		
		
		#если есть текст тег body - начинаем обработку с него
		body_data = self.soup.body
		if body_data:
			rez = self.proc_tag(body_data)
		#если нет, то скорее всего это не html-ка, а текстовый файл, и начинаем обоаботку с самого начала
		else:
			rez = self.proc_tag(self.soup)
		
		
		#если надо, оборачиваем полученый результат в тег p и присоединяем к секции, во время оборачивания, стрипаем теги br
		for r in self.break_tags('p', rez, ('strong', 'emphasis', 'code'), image_outline = False, image_inline = True, string = True, bad_tags = ['br']):
			section.append(r)
			
		#присоединяем секцию к fb2
		self.fb2s.body.append(section)
	
	def break_tags(self, this_tag, rez, good_tags, image_outline = False, image_inline = True, string = True, bad_tags = ['br']):
		'''
		оборачивает массив rez тегом this_tag
		возвращает массив.
		Если в массиве rez объекты из good_tags или image_outline, image_inline, string (если они включены), то они обораиваются.
		если нет, то таг this_tag прерывается, в массив результата добавляется объект, который нельзя обернуть, а потом продолжаетсмя оборачивание
		если тег, на котором прерывается, находится в bad_tags - на нем прерывание происходит, но он не добавляется в возвращаемый массив
		'''
		soup = self.fb2s
		
		coll = [] #возвращаемый массив
		this = BS.Tag(soup, this_tag)
		for r in rez:
			
			if string and isinstance(r, BS.NavigableString):
				this.append(r)
				
			elif isinstance(r, BS.Tag) and (r.name in good_tags):
				this.append(r)
			elif image_outline and ( isinstance(r, BS.Tag) and  (r.name == 'image') and not r.inline):
				this.append(r)
			elif image_inline and ( isinstance(r, BS.Tag) and  (r.name == 'image') and r.inline):
				this.append(r)
			else:
				if this.contents:
					coll.append(this)
					this = BS.Tag(soup, this_tag) 
				if r.name not in bad_tags:
					coll.append(r)
		if this.contents:
			coll.append(this)
			
		return coll
	
	
	def check_tags(self, rez, good_tags, string = False):
		'''
		проверяет, какие soup теги содержаться в массиве rez
		возвращает True - если в нем содержаться только теги из набора good_tags или строки (если они разрешены в  string)
		'''
		for r in rez:
			if isinstance(r, BS.NavigableString):
				if (not string) and str(r).strip():
					return False
			
			elif isinstance(r, BS.Tag) and (r.name not in good_tags):
				return False
			
		return True

	
	def proc_tab_tags(self, tag):
		'''
		обработка тегов таблиц
		'''
		soup = self.fb2s
		coll = [] #возвращаемый массив
		
		if tag.name == 'table':
			rez = self.proc_tag(tag)
			#если внутри содержится что-то кроме tr, th, td - вынимаем контент из th, td и добавляем к результату
			#из tr - вынимать ничего не надо - он не ничего не содержит (см. код обработки tr)
			#вместо самих же тегов: на всякий случай ставим пробелы (чтоб не скливались буковки
			if not self.check_tags(rez, ('td', 'th', 'tr'), string = False):
				for r in rez:
					if isinstance(r, BS.Tag):
						if r.name == 'tr':
							coll.append(BS.NavigableString(' '))
						elif r.name in ('td', 'th'):
							coll.append(BS.NavigableString(' '))
							for sub_r in r.contents:
								coll.append(sub_r)
						else:
							coll.append(r)
					
					else:
						coll.append(r)
			else:
				#пробегаем по массиву, если встречается tr - создаем этот тег
				#если встречаем td или th - добавляем им в созданный tr (если таковой существует)
				table = BS.Tag(soup, 'table')
				tr = None
				for r in rez:
					if isinstance(r, BS.Tag):
						if r.name == 'tr':
							if tr:
								table.append(tr)
							tr = r
						elif r.name in ('th', 'td'):
							if tr:
								tr.append(r)
				if tr:
					table.append(tr)
				if table.contents:
					coll.append(table)
				
		elif tag.name == 'tr':
			rez = self.proc_tag(tag)
			#если внутри встретилось что-то кроме тегов td, th -  добавляем это что-то к результату 
			if rez:
				if not self.check_tags(rez, ('td', 'th'), string = False):
					coll += rez

				else: #иначе, добавляем tr, td к результату
					tr = BS.Tag(soup, 'tr')
					coll.append(tr)
					coll += rez
			#надо заметить, что tr, td, th - располагаются не вложенно, а линейно в массиве.
			# это будет учтено при обработке table
				
		elif (not self.skip_tables) and (tag.name in ('td','th')):
			#обрабатываем внутренности таблицы
			rez = self.proc_tag(tag)
			#проверям, что внутренние теги - те которые допустимы.
			if not self.check_tags(rez, ('strong', 'emphasis', 'code', 'image'), string = True):
				coll += rez #если внутри все слишком сложно - нафиг такую внутри.
				
			else:
				if tag.name == 'td':
					this = BS.Tag(soup, 'td')
				else:
					this = BS.Tag(soup, 'th')
				
				#обрабатываем спаны
				rowspan  = tag.get('rowspan', None)
				colspan  = tag.get('colspan', None)
				
				if rowspan != None:
					this['rowspan'] = rowspan
				if colspan != None:
					this['colspan'] = colspan
					
				for r in rez:
					this.append(r)
				
				coll.append(this)
				
		return coll
		
	
	def proc_tag(self, parent_tag):
		'''
		рекурсивная обработка тегов
		возвращает массив тегов
		
		'''
		soup = self.fb2s
		coll = [] #возвращаемый массив
		
		for tag in parent_tag.contents: # перебираем дочерние таги
			
			if tag.__class__ == BS.NavigableString: #если строка (не коммент, не cdata а именно строка)
				
				s = fix_nbsp_bug(unicode(tag))#фикс бага с &nbsp;
				text = BS.NavigableString(xmlescaper(s)) #создаем строку и эскейпим ее
				coll.append(text)

			elif isinstance(tag, BS.Tag): #если тег
			
				if tag.name in ('script', 'form', 'style'): #теги, обработка внутри которых не производится
					pass
				
				elif tag.name in ('b', 'strong'): #жирный
					rez = self.proc_tag(tag)
					coll += self.break_tags('strong', rez, ('strong', 'emphasis', 'code'), image_outline = False, image_inline = True, string = True)

				elif tag.name == 'pre': #преформатированный текст
					rez = self.proc_tag(tag)
					coll += self.break_tags('code', rez, ('strong', 'emphasis', 'code'), image_outline = False, image_inline = True, string = True)
				
				elif tag.name == 'p': #параграф
					rez = self.proc_tag(tag)
					#оборачиваем те теги, который можно обернуть, при этом стрипаем теги br
					coll += self.break_tags('p', rez, ('strong', 'emphasis', 'code'), image_outline = False, image_inline = True, string = True, bad_tags = ['br'])
				
				elif tag.name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'): #если заголовки - оформляем их жирным выделяем в отдельный параграф
					rez = self.proc_tag(tag)
					coll += self.break_tags('subtitle', rez, ('strong', 'emphasis', 'code'),image_outline = False, image_inline = True, string = True)
					
				elif tag.name == 'br':
					# если br - приходится временно ввести дополнительный тег br (потом его надо обязательно удалить)
					# он не входит не в список разрешенных тегов и поэтому будет выталкиваться, пока его не удалят
					# удаление происходит на уровне тега p
					rez = self.proc_tag(tag)
					br = BS.Tag(soup, 'br')
					coll.append(br)

				#если обрабатываем таблицы, теги ее обработки собраны в отдельной функции
				#теги таблиц, собраны в отдельной функции
				elif (not self.skip_tables) and (tag.name in ('table', 'tr', 'td', 'th')):
					coll += self.proc_tab_tags(tag)
					
				#если таблицы не обрабатываем - на всякий случай ставим пробелы, чтоб буковки не склеивались
				elif (self.skip_tables) and (tag.name in ('table', 'tr', 'td', 'th')):
					coll.append(BS.NavigableString(' '))
					coll += self.proc_tag(tag)
					coll.append(BS.NavigableString(' '))
					
				elif tag.name == 'img':
					#обрабатываем картинки
					if not self.skip_images:
						src = tag.get('src', None)
						#если у картинки есть выравнивание, значит она не inline
						
						inline = not ( tag.get('align', '').lower() in ('left', 'right') )
						if src:
							img_path = os.path.join( os.path.dirname(self.in_file), urllib.unquote(src) )
							img = get_image( img_path )
							if img:
								id =  'i' + md5.new(img_path).hexdigest()[:10] #даем картинке новое, заведомо валидное имя
								self.fb2.binary.add('image/%s' % img['type'], id, img['data']) #добавляем в сторадж
								tag = BS.Tag(soup, 'image', [('xlink:href', "#%s"%id)] )
								tag.inline = inline #добавляем к тегу свойство inline

								coll.append(tag)
				else: 
					coll += self.proc_tag(tag)

		return coll

def htmls2fb2(params):
	'''
	собственно запускаемая функция
	обрабатывает все html файлы переданные в params в fb2 файл
	
	'''

	fb2 = fb2_(params.file_out) #создаем fb2 файл

	descr = params.descr
	
	titles = []
	
	for in_file in params.source_files:
		#обрабатываем отдельно каждый html файл
		h2f = html2fb2(fb2, in_file, params.skip_images, params.skip_tables)
		h2f.process()
			
		if descr.selfdetect: #если нужно самим определить дискрипшн - пытаемся определить title
			titles.append( h2f.detect_descr() )
			
	if descr.selfdetect: 
		#склеиваем титлы в один
		descr.title = ' ||| '.join( [ t.strip() for t in titles if t.strip() ] )
		descr.authors = [descr.def_author]

	fb2.make_description(descr) #формируем дискрипшн у fb2

	fb2.get_rez() # завершем формирование fb2
	
	return descr

if __name__ == '__main__':
	

	params = params_()
	params.skip_images = False
	params.skip_tables = False
	#params.source_files = ['html/test.html', 'html/mail.htm']
	#params.source_files = [ 'html/html.html']
	#params.source_files = [ 'html/mail.htm']
	params.source_files = [ 'html/test.html']
	params.file_out = 'out.fb2'
	params.descr = fb_utils.description()
	#params.descr.authors = [{'first': u'петер', 'middle': u'Михайлович', 'last': u'Размазня'}, {'first': 'Галина', 'middle':'Николаевна', 'last':'Борщь'}]
	#params.descr.selfdetect = False

	
	htmls2fb2(params)

#coding=utf-8
import time
from xml.sax.saxutils import escape as xmlescaper #функция, экранируюущая невалидные для xml символы
import md5
import re


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

#this code used for get control chars
#import unicodedata
#all_chars = [unichr(i) for i in xrange(0x10000)]
#all_chars = [unichr(i) for i in xrange(0x110000)]
#control_chars = u''.join(c for c in all_chars if (unicodedata.category(c) == 'Cc' ) and c not in (unichr(13), unichr(10), unichr(9))) #unichr(13), unichr(10), unichr(9) is \n, \r, \t
#control_chars_int = [ord(cc) for cc in control_chars]
BAD_CHARS = ''.join([unichr(c) for c in [0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159]])
BAD_CHARS_replace = re.compile('[%s]' % re.escape(BAD_CHARS))


def bad_chars_proc(s):
	#use for all string, what adding to fb2
	
	#s.replace(u' ', u' ') - for fix beatefualsoup bag: заменяет то, что получается в процессе конвертации из &nbsp; на пробел
	return BAD_CHARS_replace.sub('', s.replace(u' ', u' '))


class params_(object):
	'''
	параметры, передаваемые в парсер
	'''
	def __init__(self):
		self.file_out = None #имя выходного файла (можно с путями)
		self.source_files = [] #имена выходных файлов (можно с путями)
		self.descr = None #объкт дескрипшена (см. fb_utils) для формирования заголовка fb2
		self.skip_images = None #не обрабатывать картинки
		self.skip_tables = None #не обрабатывать таблицы
		self.skip_pre = None #не обрабатывать таблицы

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
			self.description += '<src-url>%s</src-url>\n' % ' '.join([ xmlescaper(bad_chars_proc(unicode(x))) for x in descr.urls ])
		self.description += '<id>%s</id>\n' % descr.id
		self.description += '<version>%s</version>\n' % descr.version
		self.description += '</document-info>\n'
		self.description += '</description>\n'

class html2fb2(object):
	'''
	парсер html
	'''
	def __init__(self, fb2, in_file, skip_images = False, skip_tables = False, skip_pre = True):
		self.in_file = in_file 
		self.skip_images = skip_images
		self.skip_tables = skip_tables
		self.skip_pre = skip_pre
		self.fb2 = fb2
		self.fb2s = fb2.soup # soup структура fb2
		

		#читаем файлс html-кой
		data = codecs.open(self.in_file, 'r', 'utf-8').read()

		self.soup = BS.BeautifulSoup(data, selfClosingTags=[], convertEntities="html") #парсим html в soup структуру
		
		#регулярка для разделение строки на переносы
		self.split_lines = re.compile(r"\r\n|\r|\n", re.MULTILINE)
		

	def detect_descr(self):
		'''
		пытаемся вытащить title
		'''
		
		try:
			#ищем его в <head><title>
			title = bad_chars_proc( u''.join( self.soup.html.title.findAll(text = True) ) ) #try take title from <title>
			
		except AttributeError:
			
			try:
				#пробуем взять его из первого попавшегося h1, h2, ...
				title = bad_chars_proc( ''.join(self.soup.html.body.find(name = re.compile(r'h\d')).findAll(text = True)) )#try to found h tags for title
				
			except AttributeError:
				title = ''
		return title

	
	def process(self):
		
		soup = self.fb2s
		
		#создаем секцию
		big_section = BS.Tag(soup, 'section')
		
		#пытаемся подобрать для секции загловок
		try:
			title_text = bad_chars_proc( ''.join(self.soup.html.title.findAll(text = True)) ).strip() #try take title from <title>
		except AttributeError:
			pass
		else:
			if title_text:
				#если получилось, пишем заголовок в секцию
				title = BS.Tag(soup, 'title')
				p = BS.Tag(soup, 'p')
				p.append( BS.NavigableString( xmlescaper(title_text) ) )
				title.append(p)
				big_section.append(title)
		
		
		#если есть текст тег body - начинаем обработку с него
		body_data = self.soup.body
		if body_data:
			rez = self.proc_tag(body_data)
		#если нет, то скорее всего это не html-ка, а текстовый файл, и начинаем обоаботку с самого начала
		else:
			rez = self.proc_tag(self.soup)
		
		
		#если надо, оборачиваем полученый результат в тег p и присоединяем к секции, во время оборачивания, стрипаем теги br
		#оборачиваем необренутые в p теги, стрипаем br
		p_rez =  self.break_tags('p', rez, ('strong', 'emphasis', 'code'), image_outline = False, image_inline = True, string = True, bad_tags = ['br'])
		#оборачиваем необренутые в section теги, стрипаем sect
		sects = self.break_tags('section', p_rez, ('strong', 'emphasis', 'code', 'p', 'table', 'title'), image_outline = True, image_inline = True, string = True, bad_tags = ['sect'])
		
		for sec in sects:
			big_section.append(sec)
		
		#присоединяем секцию к fb2
		self.fb2s.body.append(big_section)
	
	def break_tags(self, this_tag, rez, good_tags, image_outline = False, image_inline = True, string = True, bad_tags = []):
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

	
	def proc_tab_tags(self, tag, in_pre = False):
		'''
		обработка тегов таблиц
		'''
		soup = self.fb2s
		coll = [] #возвращаемый массив
		
		if tag.name == 'table':
			rez = self.proc_tag(tag, in_pre)
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
			rez = self.proc_tag(tag, in_pre)
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
			rez = self.proc_tag(tag, in_pre)
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
		
	
	def proc_tag(self, parent_tag, in_pre = False):
		'''
		рекурсивная обработка тегов
		возвращает массив тегов
		in_pre - если нужна специальная обработка строк, в pre
		
		'''
		soup = self.fb2s
		
		coll = [] #возвращаемый массив
		
		for tag in parent_tag.contents: #бежим по дочерним тегам
		
			if tag.__class__ == BS.NavigableString: #если строка (не коммент, не cdata а именно строка)
				
				s = bad_chars_proc(unicode(tag))#обработка левых символов
				if in_pre: #если включена обработка переносов, ставим всесто каждого переноса br
					s_l = self.split_lines.split(s)
					for c in s_l[:-1]:
						text = BS.NavigableString(xmlescaper(c)) #создаем строку и эскейпим ее
						coll.append(text)
						br = BS.Tag(soup, 'br')
						coll.append(br)
					c = s_l[-1]
					text = BS.NavigableString(xmlescaper(c))
					coll.append(text)
				else:	
					text = BS.NavigableString(xmlescaper(s)) #создаем строку и эскейпим ее
					coll.append(text)

			elif isinstance(tag, BS.Tag): #если тег
			
				if tag.name in ('script', 'form', 'style'): #теги, обработка внутри которых не производится
					pass
				
				elif tag.name in ('b', 'strong'): #жирный
					rez = self.proc_tag(tag, in_pre)
					coll += self.break_tags('strong', rez, ('strong', 'emphasis', 'code'), image_outline = False, image_inline = True, string = True)
				
				elif tag.name in ('i', 'cite', 'em', 'var'): #жирный
					rez = self.proc_tag(tag, in_pre)
					coll += self.break_tags('emphasis', rez, ('strong', 'emphasis', 'code'), image_outline = False, image_inline = True, string = True)

				elif tag.name == 'pre': #преформатированный текст
					if self.skip_pre: #если не обрабатываем pre, включаем спец-обработчик переносов строки для всех дочерних тегов
						rez = self.proc_tag(tag, in_pre = True)
						coll += rez
					else:
						rez = self.proc_tag(tag, in_pre)
						coll += self.break_tags('code', rez, ('strong', 'emphasis', 'code'), image_outline = False, image_inline = True, string = True)
				
				elif tag.name == 'p': #параграф
					rez = self.proc_tag(tag, in_pre)
					#оборачиваем те теги, который можно обернуть, при этом стрипаем теги br
					coll += self.break_tags('p', rez, ('strong', 'emphasis', 'code'), image_outline = False, image_inline = True, string = True, bad_tags = ['br'])
				
				elif tag.name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'): #если заголовки - оформляем их жирным выделяем в отдельный параграф
					#ставим воспомагетальный тег - начало секции. Потом на обработке секции его надо обработать  и удалить
					sect = BS.Tag(soup, 'sect')
					coll.append(sect)
					
					#обрабатываем то, что внутри title
					rez_title = self.proc_tag(tag, in_pre)
					#добавляем p
					p_title = self.break_tags('p', rez_title, ('strong', 'emphasis', 'code'), image_outline = False, image_inline = True, string = True, bad_tags = ['br'])
					#добавляем title
					title_tags = self.break_tags('title', p_title, ('strong', 'emphasis', 'code', 'p'),image_outline = False, image_inline = True, string = True)
					
					#проверям, не была-ли title рассечена чем-нибудь (например таблица выдавилась или не inline картинка)
					#в таком случае тоже надо добавить новую секцию
					#и добавляем все в возвращаемый массив
					if title_tags:
						coll.append(title_tags[0])
						for title_tag in title_tags[1:]:
							#если еще где-то, кроме как в первом элементе встретился title, значит он был где-то рассечен
							if isinstance(title_tag, BS.Tag) and (title_tag.name == 'title'):
								sect = BS.Tag(soup, 'sect') #добавдяем секцию
								coll.append(sect)
								coll.append(title_tag)
							else:
								coll.append(title_tag)
					
				elif tag.name == 'br':
					# если br - приходится временно ввести дополнительный тег br (потом его надо обязательно удалить)
					# он не входит не в список разрешенных тегов и поэтому будет выталкиваться, пока его не удалят
					# удаление происходит на уровне тега p
					rez = self.proc_tag(tag, in_pre)
					br = BS.Tag(soup, 'br')
					coll.append(br)

				#если обрабатываем таблицы, теги ее обработки собраны в отдельной функции
				#теги таблиц, собраны в отдельной функции
				elif (not self.skip_tables) and (tag.name in ('table', 'tr', 'td', 'th')):
					coll += self.proc_tab_tags(tag, in_pre)
					
				#если таблицы не обрабатываем - на всякий случай ставим пробелы, чтоб буковки не склеивались
				elif (self.skip_tables) and (tag.name in ('table', 'tr', 'td', 'th')):
					coll.append(BS.NavigableString(' '))
					coll += self.proc_tag(tag, in_pre)
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
					coll += self.proc_tag(tag, in_pre)

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
		h2f = html2fb2(fb2, in_file, params.skip_images, params.skip_tables, params.skip_pre)
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
	params.source_files = [ 'html/nosov.html']
	#params.source_files = [ 'html/test.html']
	params.file_out = 'out.fb2'
	params.descr = fb_utils.description()
	#params.descr.authors = [{'first': u'петер', 'middle': u'Михайлович', 'last': u'Размазня'}, {'first': 'Галина', 'middle':'Николаевна', 'last':'Борщь'}]
	#params.descr.selfdetect = False

	htmls2fb2(params)

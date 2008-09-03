#coding=utf-8
import time
import xml.sax.saxutils
import md5
import log

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


#import htmldata
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
		if id not in self.ids:
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
		имя выходного файла
		'''

		self.f_out = file(f_name, 'wb')

		self.soup = BS.BeautifulStoneSoup()

		self.binary = binary() #подключаем бинарные данные
		
		self.description = ''

	def get_soup(self):
		return self.soup()

	def get_rez(self):

		head = """<?xml version="1.0" encoding="UTF-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:xlink="http://www.w3.org/1999/xlink">
"""
		foot = """\n</FictionBook>"""

		self.f_out.write(head)
		self.f_out.write(self.description.encode('UTF-8'))
		self.f_out.write( self.soup.renderContents(encoding='UTF-8', prettyPrint = False) )
		shutil.copyfileobj(self.binary.get(), self.f_out)
		self.f_out.write(foot)

		#f_p = open('v.fb2', 'wb')
		#f_p.write(head)
		#f_p.write(self.description.encode('UTF-8'))
		#f_p.write( self.soup.renderContents(encoding='UTF-8', prettyPrint = True) )
		#shutil.copyfileobj(self.binary.get(), f_p)
		#f_p.write(foot)
		#f_p.close()


	def make_description(self, descr):
		'''
		формирование секции description для fb2
		'''
		
		#fill title-info
		self.description += '<description>\n'
		self.description += '<title-info>\n'
		self.description += '<genre>%s</genre>\n' % descr.genre
		for author_d in descr.authors:
			authors = '<author>'
			authors  += '<first-name>%s</first-name>' % author_d['first']
			authors  += '<middle-name>%s</middle-name>' % author_d['middle']
			authors  += '<last-name>%s</last-name>' % author_d['last']
			authors += '</author>\n'
		
		self.description += authors
		self.description += '<book-title>%s</book-title>\n' % descr.title
		self.description += '<annotation></annotation>\n'
		self.description += '<lang>%s</lang>\n' % descr.lang
		self.description += '</title-info>\n'
		
		#fill document-info
		self.description += '<document-info>\n'
		self.description += '<author><nickname></nickname></author>\n'
		if descr.program_info:
			self.description += '<program-used>%s</program-used>\n' % descr.program_info
		self.description += '<date value="%s">%s</date>\n' % (time.strftime('%Y-%m-%d'), time.strftime('%Y-%m-%d'))
		
		#rez += '<date value="%s">%s</date>\n' % (time.strftime('%Y-%m-%d'), time.strftime('%Y-%m-%d'))
		
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
		self.fb2s = fb2.soup
		

		#читаем файл
		data = codecs.open(self.in_file, 'r', 'utf-8').read()

		self.soup = BS.BeautifulSoup(data, selfClosingTags=[], convertEntities="html")

	def detect_descr(self):
		#descr = fb_utils.description()
		try:
			title = ''.join(self.soup.html.title.findAll(text = True)) #try take title from <title>
		except Exception, NoneType:
			
			
			try:
				title = ''.join(self.soup.html.body.find(name = re.compile(r'h\d')).findAll(text = True)) #try to found h tags for title
				
			except Exception, NoneType:
				title = ''
		return title

	def process(self):
		self.proc_body(self.soup.body)

	
	def proc_body(self, data):
		soup = self.fb2s

		
		rez = self.proc_tag(data)
		
		section_coll = []
		for r in self.break_tags('p', rez, ('strong', 'emphasis', 'code'), image_outline = False, image_inline = True, string = True):
			section_coll.append(r)
		
		body = BS.Tag(self.fb2s, 'body')
		for r in self.break_tags('section', section_coll, ('p', 'title', 'table', 'br'), image_outline = True, image_inline = True, string = False):
			body.append(r)
			
		for br in body.findAll(name ='br'):
			br.extract()

		self.fb2s.append(body)


	def break_tags(self, this_tag, rez, good_tags, image_outline = False, image_inline = True, string = True, sort = None):
		soup = self.fb2s
		
		coll = []
		head_coll = []
		
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
				if this:
					if this.name == sort:
						head_coll.append(this)
					else:
						coll.append(this)
						
					this = BS.Tag(soup, this_tag) 
				
				if r.name == sort:
					head_coll.append(r)
				else:
					coll.append(r)
		if this:
			if this.name == sort:
				head_coll.append(this)
			else:
				coll.append(this)
			
		return head_coll + coll
	
	def check_tags(self, rez, good_tags, string = False):
		for r in rez:
			if isinstance(r, BS.NavigableString):
				if (not string) and str(r).strip():
					return False
			
			elif isinstance(r, BS.Tag) and (r.name not in good_tags):
				return False
			
		return True

	def proc_tag(self, parent_tag):
		soup = self.fb2s
		coll = []
		for tag in parent_tag.contents:
			if tag.__class__ == BS.NavigableString: #если строка - добавляем в текст
				s = str(tag)
				text = BS.NavigableString(xml.sax.saxutils.escape(s))
				coll.append(text)

			elif isinstance(tag, BS.Tag):
			
				if tag.name in ('script', 'form', 'style'): #пропускаемые теги
					pass
				
				elif tag.name in ('b', 'strong'):
					rez = self.proc_tag(tag)
					coll += self.break_tags('strong', rez, ('strong', 'emphasis', 'code'), image_outline = False, image_inline = True, string = True)

				elif tag.name == 'pre':
					rez = self.proc_tag(tag)
					coll += self.break_tags('code', rez, ('strong', 'emphasis', 'code'), image_outline = False, image_inline = True, string = True)
				
				elif tag.name == 'p':
					rez = self.proc_tag(tag)
					coll += self.break_tags('p', rez, ('strong', 'emphasis', 'code'), image_outline = False, image_inline = True, string = True)
				
				elif tag.name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
					rez = self.proc_tag(tag)
					strong = self.break_tags('strong', rez, ('strong', 'emphasis', 'code'),image_outline = False, image_inline = True, string = True)
					coll += self.break_tags('p', strong, ('strong', 'emphasis', 'code'), image_outline = False, image_inline = True, string = True)
					
				elif tag.name == 'br':
					rez = self.proc_tag(tag)
					br = BS.Tag(soup, 'br')
					coll.append(br)

				elif (not self.skip_tables) and (tag.name == 'table'):
					#обрабатываем внутренности таблицы
					rez = self.proc_tag(tag)
					if not self.check_tags(rez, ('td', 'th', 'tr'), string = False):
						for r in rez:
							if isinstance(r, BS.Tag):
								if r.name == 'tr':
									pass
								elif r.name in ('td', 'th'):
									for sub_r in r.contents:
										coll.append(sub_r)
								else:
									coll.append(r)
							
							else:
								coll.append(r)
					else:
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
									else:
										table.append(r)
						if tr:
							table.append(tr)
						coll.append(table)
						
				elif (not self.skip_tables) and (tag.name == 'tr'):
					rez = self.proc_tag(tag)
					if not self.check_tags(rez, ('td', 'th'), string = False):
						coll += rez #если внутри все слишком сложно - нафиг такую внутри.
						
					else:
						tr = BS.Tag(soup, 'tr')
						coll.append(tr)
						coll += rez
						
				
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
						
						rowspan  = tag.get('rowspan', None)
						colspan  = tag.get('colspan', None)
						
						if rowspan != None:
							this['rowspan'] = rowspan
						if colspan != None:
							this['colspan'] = colspan
							
						for r in rez:
							this.append(r)
						
						coll.append(this)
				
				
				elif tag.name == 'img':
					#обрабатываем картинки
					if not self.skip_images:
						src = tag.get('src', None)
						#если у картинки есть выравнивание, значит она не inline
						inline = not ( tag.get('align', None) in ('left', 'right') )
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
	rez = {}
	fb2 = fb2_(params.file_out)

	descr = params.descr
	
	titles = []
	
	for in_file in params.source_files:
		h2f = html2fb2(fb2, in_file, params.skip_images, params.skip_tables)
		
		h2f.process()
			
		if descr.selfdetect:
			titles.append( h2f.detect_descr() )
			
	if descr.selfdetect:
		descr.title = ' ||| '.join( [ t.strip() for t in titles if t.strip() ] )
		descr.authors = [descr.def_author]
	
	log.debug(str(params.descr.authors))
	log.debug(str(len(params.descr.title)))
	fb2.make_description(descr)

	fb2.get_rez()
	
	return descr

if __name__ == '__main__':

	params = params_()
	params.skip_images = False
	params.skip_tables = True
	params.source_files = ['html/test.html', 'html/mail.htm']
	#params.source_files = [ 'html/mail.htm']
	#params.source_files = [ 'html/test.html']
	params.file_out = 'out.fb2'
	params.descr = fb_utils.description()
	#params.descr.authors = [{'first': u'петер', 'middle': u'Михайлович', 'last': u'Размазня'}, {'first': 'Галина', 'middle':'Николаевна', 'last':'Борщь'}]
	#params.descr.selfdetect = False

	htmls2fb2(params)

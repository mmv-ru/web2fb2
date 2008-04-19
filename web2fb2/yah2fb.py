#coding=utf-8
import time

from BeautifulSoup import BeautifulSoup, NavigableString, Tag
#import htmldata
import re
import urllib
import os.path
import base64
from PIL import Image
import cStringIO

import fb_utils

class binary(object):
	def __init__(self):
		self.f = cStringIO.StringIO()
		self.ids = []
		
	def get(self):
		return self.f.getvalue()
	
	def add(self, type, id, data):
		if id not in self.ids:
			self.f.write('<binary content-type="%s" id="%s">' % (type, id))
			self.f.write(base64.encodestring(data))
			self.f.write('</binary>\n')
			self.ids.append(id)
		

class fb2(object):
	def __init__(self):
		self.FB_TAGS = ['section', 'title', 'p']
		self.cr_tags = ['p']
		
		self.body = ''
		self.description = ''
		self.binary = binary()
		
		self.tags_stack = []
	
	def get_rez(self):
		data = '<?xml version="1.0" encoding="UTF-8"?>\n'
		data += '<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:xlink="http://www.w3.org/1999/xlink">\n'
		data += '<description>\n'
		data += self.description
		data += '</description>\n'
		data += '<body>\n'
		data += self.body
		data += '</body>\n'
		
		data = data.encode('utf8')
		
		data += self.binary.get()
		
		data += '</FictionBook>'.encode('utf8')
		
		return data#.encode('utf8')
	
	def make_description(self, descr):
		
		#fill title-info
		self.description += '<title-info>\n'
		self.description += '<genre>%s</genre>\n' % descr.genre
		self.description += '<author>'
		self.description += '<first-name>%s</first-name>' % descr.author_first
		self.description += '<middle-name>%s</middle-name>' % descr.author_middle
		self.description += '<last-name>%s</last-name>' % descr.author_last
		self.description += '</author>\n'
		self.description += '<book-title>%s</book-title>\n' % descr.title
		self.description += '<annotation></annotation>\n'
		self.description += '<lang>%s</lang>\n' % descr.lang
		self.description += '</title-info>\n'
		
		#fill document-info
		self.description += '<document-info>\n'
		self.description += '<author><nickname></nickname></author>\n'
		if descr.program_info != None:
			self.description += '<program-used>%s</program-used>\n' % descr.program_used
		self.description += '<date value="%s">%s</date>\n' % (time.strftime('%Y-%m-%d'), time.strftime('%d %B %Y'))
		#rez += '<date value="%s">%s</date>\n' % (time.strftime('%Y-%m-%d'), time.strftime('%Y-%m-%d'))
		
		if descr.src_url != None:
			self.description += '<src-url>%s</src-url>\n' % descr.url
		self.description += '<id>%s</id>\n' % descr.id
		self.description += '<version>1.0</version>\n'
		self.description += '</document-info>\n'
		
	def start_tag(self, tag):
		if tag in self.FB_TAGS:
			self.body += '<%s>\n' % tag
			self.tags_stack.append(tag)
		else:
			raise ValueError, 'Bad tag'
		
	def end_tag(self, tag):
		if tag == self.tags_stack[-1]:
			self.body += '</%s>\n' % tag
			self.tags_stack.pop()
		else:
			raise ValueError, 'Closing non opened tag'
	
	def add_text(self, text):
		self.body += text + '\n'
	
	def add_tag(self, tag, content):
		self.start_tag(tag)
		self.add_text(content)
		self.close_tag(tag)
		
	def add_img(self, src):
		id = os.path.basename(src)
		
		img = self.get_image(src)
		
		if img:
			self.binary.add('image/%s' % img['type'], id, img['data'])
			self.body += '<image xlink:href="#%s"/>\n' % id
			
	def get_image(self, src):
		
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


class html2fb2(object):
	def __init__(self):
		pass
		
	def process(self, params):
		rez = {}
		
		self.params = params
		self.fb2 = fb2()
		
		self.soup = BeautifulSoup(params['data'])
		
		#
		#fill description
		#
		descr = params['descr']
		#title
		if descr.title == descr.SELFDETECT:
			try:
				descr.title = ''.join(self.soup.html.title.findAll(text = True)) #try take title from <title>
			except Exception, NoneType:
				try:
					descr.title = ''.join(self.soup.html.body.find(name = re.compile(r'h\d')).findAll(text = True)) #try to found h tags for title
				except Exception, NoneType:
					descr.title = ''

		#author
		if descr.author_first == descr.SELFDETECT:
			descr.author_first = ''
			
		if descr.author_middle == descr.SELFDETECT:
			descr.author_middle = ''
			
		if descr.author_last == descr.SELFDETECT:
			descr.author_last = ''
		
		self.fb2.make_description(descr)
		#
		#end of fill description
		#
		
		
		self.proc_body(self.soup.body)
		
		rez['data'] = self.fb2.get_rez()
		rez['descr'] = descr
		
		return rez
		
	
	def proc_text(self, text):
		'''
		обрабока текста (убираем переводы строк, лишние пробелы)
		'''
		text = text.replace('\n', ' ').replace('\n', ' ')
		text = ' '.join([c for c in text.split(' ') if c])
		return text		
	
	def proc_body(self, body):
		self.fb2.start_tag('section')
		
		self.proc_tag(body)
		
		self.fb2.end_tag('section')

		
	def proc_tag(self, parent_tag):

		tags = parent_tag.childGenerator()
		
		while 1:
			try:
			
				tag = tags.next()
				
				
				if tag.__class__ == NavigableString: #если строка - добавляем в текст
					text = self.proc_text(tag)
					if text:
						self.fb2.start_tag('p')
						self.fb2.add_text(text)
						self.fb2.end_tag('p')
						
				
						
				elif tag.__class__ == Tag: #если теги
					#пропускаемые теги
					if tag.name in ['script', 'form', 'style']: #пропускаемые теги
						pass
					
					#специально обарабатываемые теги
					elif tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']: #заголовок
						self.fb2.end_tag('section')
						self.fb2.start_tag('section')
						self.fb2.start_tag('title')
						self.proc_tag(tag)
						self.fb2.end_tag('title')
						
					elif tag.name == 'img':
						if not self.params['skip-images']:
							src = tag['src']
							if src:
								self.fb2.add_img(urllib.unquote(src))
					
					else:
						self.proc_tag(tag)
				
				
			except StopIteration:
				break

if __name__ == '__main__':
	
	params = {}
	params['data'] = file('test.html').read()
	#params['data'] = file('mail.htm').read()
	params['descr'] = fb_utils.description()
	params['skip-images'] = True

	detector = html2fb2()
	result = detector.process(params)
	
	file('out.fb2', 'w').write(result['data'])
	#print result['data']
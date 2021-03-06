#coding=utf-8

# скачивание html, исправление, поиск картинок, скачка картинок
#
#

import urllib2
import urllib
import urlparse
import socket
import md5
import random
import os

import chardet

import html5lib
import html5lib.treewalkers
import html5lib.serializer

from BeautifulSoup import BeautifulSoup
BeautifulSoup.NESTABLE_TAGS['strong'] = []
BeautifulSoup.NESTABLE_TAGS['b'] = []
BeautifulSoup.NESTABLE_TAGS['i'] = []
BeautifulSoup.NESTABLE_TAGS['em'] = []
BeautifulSoup.NESTABLE_TAGS['var'] = []
BeautifulSoup.NESTABLE_TAGS['cite'] = []
BeautifulSoup.NESTABLE_TAGS['p'] = []
BeautifulSoup.NESTABLE_TAGS['pre'] = []


import log

class WebError(Exception):
	'''
	объект - исключение
	
	'''

	def __init__(self, value = 'Web Error'):
		self.value = value
	def __str__(self):
		return repr(self.value)


def url_fix(s, charset='utf-8'):
	"""Sometimes you get an URL by a user that just isn't a real
	URL because it contains unsafe characters like ' ' and so on.  This
	function can fix some of the problems in a similar way browsers
	handle data entered by the user:

	>>> url_fix(u'http://de.wikipedia.org/wiki/Elf (Begriffsklärung)')
	'http://de.wikipedia.org/wiki/Elf%20%28Begriffskl%C3%A4rung%29'

	:param charset: The target charset for the URL if the url was
					given as unicode string.
	"""
	if isinstance(s, unicode):
		s = s.encode(charset, 'ignore')
	scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
	path = urllib.quote(path, '/%')
	qs = urllib.quote_plus(qs, ':&=')
	return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))
	
	

def do(url, is_img, rez_folder, progres):

	"""главная рабочая функция"""
	
	try:
		data, real_url = download_html(url)
	except (urllib2.HTTPError, urllib2.URLError, IOError, ValueError), er:
		log.warning('Download error %s' % (er))
		raise WebError, "Bad url"
	
	progres.level = 1
	progres.save()
	
	data = decoding(data)
	data = correct(data)
	
	if is_img:
		data, img_list = process_images(data, rez_folder, url)
		
		progres.level = 2
		progres.save()
		
		img_download(img_list, rez_folder)
	
	return data

def correct(data):

	"""корректировка кривого html"""
	
	log.debug('start html correct')
	#p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("BeautifulSoup"))
	#soup = p.parse(data)
	
	#out_data = unicode(soup)
	
	document = html5lib.HTMLParser().parse(data)
	tokens = html5lib.treewalkers.getTreeWalker('simpleTree')(document)
	out_data = ''.join(html5lib.serializer.HTMLSerializer(omit_optional_tags = False, quote_attr_values = True).serialize(tokens))
	
	log.debug('end of html correct')
	return out_data
	
def decoding(data):
	'''
	определяем кодировку файла и декодируем в юникод
	'''
		
	tmp = chardet.detect(data) #определяем кодировку
		
	log.info('Detected encoding: %s' % (tmp))
		
	new_data = data.decode(tmp['encoding'])
	return  new_data
	
def process_images(data, source_folder, url):
	'''
	обработка картинок в html:
	замена путей картинок на пути в файловой системе, составление списка картинок для скачки
	Входные переменные:
		data - HTML
		source_floder - папка, где будут картинки
		url - адрес страницы, откуда скачивался html
	возвращает  HTML с замененными путями и список картинок
	'''
	
	log.debug('start img process')
	soup = BeautifulSoup(data)
		
	#вычисляем базовый урл
	try:
		base_url = soup.html.head.base['href']
	except (KeyError, TypeError, AttributeError), er:
		base_url = url
		
	log.debug('Base url = %s' % base_url)
	
	imgs_list = {}
	img_tags = soup.findAll(name = 'img')
		
	log.info('Find %s images' % (len(img_tags)))
	
	for img_tag in img_tags:
		if img_tag.get('src', None):
			#делаем абсолютный урл
			new_url = urlparse.urljoin(base_url, img_tag['src'])
			
			if new_url in imgs_list:
				img_name = imgs_list[new_url]
			else:
				#генерим имя картинки
				img_name = "img" + md5.new(str(random.random())).hexdigest()[:10]
				#img_name = md5.new(str(random.random())).hexdigest()[:10]
				#заносим в словарь урл и имя файла
				imgs_list[new_url] = img_name
				
			# меняем ссылку на путь + имя файла
			img_tag['src'] = img_name

				
	log.info('%s images to download' % (len(imgs_list)))
	
	new_data = str(soup).decode('utf8') #после beatefulsoap приходится декодировать 
	log.debug('end of img process')
	
	return new_data, imgs_list
	
def download_html(url):
	'''
	скачка html страницы
	возвращает html страничку и real URL of the page fetched. This is useful because it may have followed a redirect.
	'''
	log.debug('start url downloading')
	socket.setdefaulttimeout(20)
		
	opener = urllib2.build_opener()
	request = urllib2.Request( url_fix(url), None, {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.8.1.8) Gecko/20071008 Firefox/2.0.0.8"})
	handle = opener.open(request)
	text = handle.read()
	realurl = handle.geturl()
	handle.close()
	
	log.debug('end of url downloading: %s' % (realurl))
	return text, realurl
	
def img_download(files_list, folder):
	'''
	входные параметры:
		files_list - словарь {url: file_name}....}
		folder - папка для сохранения
	возвращает:
		словарь {url: реузльтат}....}
			где результат: 0 - если не получилось, 1- если получилось
	'''
	log.debug('%s images for download' % len(files_list))
	rez = {}
	
	socket.setdefaulttimeout(20)
	opener = urllib2.build_opener()

	for url, file_name in files_list.items():
		log.debug('Download image: %s into: %s' % (url, file_name))
		try:
			request = urllib2.Request( url_fix(url), None, {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.8.1.8) Gecko/20071008 Firefox/2.0.0.8"})
			handle = opener.open(request)
			data = handle.read()
			handle.close()
		except (urllib2.HTTPError, urllib2.URLError, IOError, ValueError), er:
			log.warning('Downloading image: %s error: %s' % (url, er))
			rez[url] = 0
		else:
			file(os.path.join(folder, file_name), 'wb').write(data)
			rez[url] = 1

	log.info('Downloaded %s images from %s' % (len(rez), len(files_list))) 
	return rez

if __name__ == '__main__':
	file('tmp/temp.htm', 'w').write(do('http://revolver.ru', True, 'tmp').encode('UTF-8'))
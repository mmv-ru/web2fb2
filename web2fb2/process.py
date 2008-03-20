#coding=utf-8
import logging
log = logging.getLogger('web2fb2.process')

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

#http://python.com.ua/ru/news/2006/04/20/zaschita-ot-duraka-v-programmah-na-yazyike-python/
#http://python.com.ua/ru/news/2006/04/07/rabota-s-fajlami/
	
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
	def web(self, url):
		
		#проверяем урл
		log.debug('url: %s Checking url' % url)
		if not url:
			log.warning('url: %s Bad url' % url)
			return (0, bad_url)
		
		log.info('url: %s Url downloading' % url)
		
		log.debug('url: %s Start url downloading' % url)
		try:
			data, real_url = self.download_html(url)
		except (urllib2.HTTPError, urllib2.URLError, IOError, ValueError), er:
			log.warning('url: %s Download error %s' % (url, er))
			return (0, er)
		log.debug('url: %s End of url downloading' % url)
		log.info('url: %s Real download url is: %s ' % (url, real_url))
		
		#генерируем имя для временной папки
		folder_name = md5.new(url + str(random.random())).hexdigest()[:10]
		log.debug('url: %s Generated folder name: %s' % (url, folder_name))
		
		source_folder = os.path.join(TEMP_PATH, folder_name)
		
		result_folder = os.path.join(EBOOKZ_PATH, folder_name)
		
		#генерируем имя для получившегося файла
		file_name = urlparse.urlparse(url)[1][:48] + '.fb2'
		log.debug('url: %s Generated file name: %s' % (url, file_name))
		
		#создаем временную папку
		log.debug('url: %s Create temp folder: %s' % (url, source_folder))
		os.mkdir(source_folder)
		
		#чистка html, получение списка картинок
		log.debug('url %s Start processing html' % url)
		data, imgs_list = process_html().do(data, source_folder, url)
		log.debug('url %s End of processing html' % url)
		
		#качаем картинки
		log.debug('url %s Start image downloading' % url)
		img_download.download(imgs_list, source_folder)
		log.debug('url %s End of image downloading'% url)
		
		#создаем папку для готовой книги
		log.debug('url: %s Create folder for storing ebook: %s' % (url, result_folder))
		os.mkdir(result_folder)

		
		#готовим параметры для преобразования html2fb2
		params = h2fb.default_params.copy()
		params['data'] = data
		params['verbose'] = 1
		params['encoding-from'] = 'UTF-8'
		params['encoding-to'] = 'UTF-8'
		params['convert-images'] = 1
		params['skip-images'] = 0
		params['informer'] = lambda msg: log.debug(('h2fb Url: %s ' % url) + msg.strip())
		
		#собственно преобразование
		log.debug('url %s Start h2fb process' % url)
		out_data = h2fb.MyHTMLParser().process(params)
		log.debug('url %s End of h2fb process' % url)
		
		#записываем книгу
		log.debug('url %s Writing ebook: %s into: %s (ebook len: %s)' % (url, file_name, result_folder, len(out_data)))
		file(os.path.join(result_folder, file_name), 'w').write(out_data)
		
		#удаляем временную папку
		log.debug('url: %s Removing temp folder: %s' % (url, source_folder))
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
		self.url = url
		
		sys.setrecursionlimit(40000)
		
		log.debug('url: %s Start recoding' % self.url)
		data = self.recoding(data)
		log.debug('url: %s End of recoding' % self.url)
		
		log.debug('url: %s Start process images' % self.url)
		data, img_list = self.process_images(data, source_folder, url)
		log.debug('url: %s End of process images' %self.url)
		
		return data, img_list
	
	def recoding(self, data):
		'''
		конвертируем в UTF-8
		'''
		
		tmp = chardet.detect(data) #определяем кодировку
		
		log.info('url: %s Detected encoding: %s' % (self.url, tmp))
		
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
		
		log.info('url: %s Find %s images' % (self.url, len(img_tags)))
		
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
				
		log.info('url: %s  %s images to download' % (self.url, len(imgs_list)))
		
		new_data = str(soup)
		
		return new_data, imgs_list
	
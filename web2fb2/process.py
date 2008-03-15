#coding=utf-8

import md5
import random
import h2fb
import chardet
import urlparse
from BeautifulSoup import BeautifulSoup

class process:

	def do(self, data, source_folder, url):
		'''
		рабочая функция - вынести в отделный модуль.
		на входе - строка html, на выходе строка fb2
		'''
		data = self.recoding(data)
		data, img_list = self.process_images(data, source_folder, url)
		
		return data, img_list
	
	def recoding(self, data):
		'''
		конвертируем в UTF-8
		'''
		
		tmp = chardet.detect(data) #определяем кодировку
		return  data.decode(tmp['encoding']).encode('UTF-8') #перекодируем в UTF8

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
				
		new_data = str(soup)
		
		return new_data, imgs_list
	
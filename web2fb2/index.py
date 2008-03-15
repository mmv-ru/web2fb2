#!/usr/bin/python2.4
#coding=utf-8

import cgi, cgitb
import urllib2
import urlparse
import os
import md5
import random
import urlparse
import time
import shutil
import socket

cgitb.enable()

import process
import h2fb
import img_download

EBOOKZ_PATH = "ebookz" #путь к папке, гду будут хранится ebookи =)
TEMP_PATH = "temp" #папка для временных файлов
EBOOKZ_WEB_PATH = "ebookz" #URL - где будут хранится ebookи
CLEAN_TIME = 60 #время, через которое будут удалятся старые ебуки

def draw_header():
	'''
	вывод html хедера
	'''
	return """
<html>
<title>web2fb2</title>
<body>

</br></br></br></br></br></br></br>
<div align="center">
<h1>web2fb2</h1>
	"""

def draw_footer():
	'''
	вывод html футера ;)
	'''
	return """
</div>
</body>
</html>
	"""

def draw_error(er):
	'''
	вывод ошибки
	'''
	return "<font color = 'red'>ERROR: " + str(er).replace("<", "").replace(">", "") + "</font>"


def draw_form():
	'''
	вывод html формы
	'''
	return """
<form action="" method="get">
<strong>Enter url:</strong>
<input name="url" type="text" size="50" maxlength="50" value="http://" />
<input name="" type="submit" />
</form>
"""

def work(data, source_folder, url):
	'''
	рабочая функция - вынести в отделный модуль.
	на входе - строка html, на выходе строка fb2
	'''

	pro = process.process()
	data, imgs_list = pro.do(data, source_folder, url) #обработка html
	
	img_download.download(imgs_list, source_folder)

	#готовим параметры для преобразования html2fb2
	params = h2fb.default_params.copy()
	params['data'] = data
	params['verbose'] = 1
	params['encoding-from'] = 'UTF-8'
	params['encoding-to'] = 'UTF-8'
	params['convert-images'] = 1
	params['skip-images'] = 0

	#собственно преобразование
	out_data = h2fb.MyHTMLParser().process(params)

	return out_data

def clean_up():
	'''
	удаляем мусор, старые файлы
	'''

	dir_lists = os.listdir(EBOOKZ_PATH + '')
	for dir in dir_lists:
		f_info = os.stat(EBOOKZ_PATH + '/' + dir)
		if time.time() - f_info.st_mtime > CLEAN_TIME:
			shutil.rmtree(EBOOKZ_PATH + '/' + dir )
				
	dir_lists = os.listdir(TEMP_PATH + '')
	for dir in dir_lists:
		f_info = os.stat(TEMP_PATH + '/' + dir)
		if time.time() - f_info.st_mtime > CLEAN_TIME:
			shutil.rmtree(TEMP_PATH + '/' + dir )
	
	

def download_html(url):
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

def main():
	clean_up() #уборка территорий
	
	print "Content-Type: text/html; charset=UTF-8\n"
	print draw_header()

	#пытаемся получить url
	form = cgi.FieldStorage()
	url = form.getvalue('url')

	if not url:
		print draw_form()
	else:
		#генерируем имя для временной папки
		folder_name = md5.new(url + str(random.random())).hexdigest()[:10]
		
		#генерируем имя для получившегося файла
		ebook_name = urlparse.urlparse(url)[1][:48]
		
		file_name = ebook_name + '.fb2' 
		
		#создаем временную папку
		os.mkdir(TEMP_PATH + "/" + folder_name)
		
		try:
			data, real_url = download_html(url) #скачиваем страничку
		except (urllib2.HTTPError, urllib2.URLError, IOError, ValueError), er:
			print draw_error(er)
			print draw_form()
		else:
			try:
				out_data = work(data, TEMP_PATH + '/' + folder_name, real_url)  #процесс преобразования
			except Exception, er:
				print draw_error(er)
				print draw_form()
			else:
				#создаем папку
				os.mkdir(EBOOKZ_PATH + '/' + folder_name)
				
				#записываем книгу
				file(EBOOKZ_PATH + '/' + folder_name + '/' + file_name, 'w').write(out_data)
				
				#выводим линк на скачку
				print "<b>Download link:</b> <a href = '" + EBOOKZ_WEB_PATH + '/' + folder_name + '/' + file_name + "'>" + file_name + "</a>"

		#удаляем временную папку
		shutil.rmtree(TEMP_PATH + "/" + folder_name)

	print draw_footer()

if __name__=='__main__':
	main()


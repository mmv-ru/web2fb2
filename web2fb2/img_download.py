#!/usr/bin/python
#coding=utf-8

import urllib2
import socket
'''
модуль скачки файлов (картинок)
'''

def download(files_list, folder):
	'''
	входные параметры:
		files_list - словарь {url: file_name}....}
		folder - папка для сохранения
	возвращает:
		словарь {url: реузльтат}....}
			где результат: 0 - если не получилось, 1- если получилось
	'''
	rez = {}
	
	socket.setdefaulttimeout(20)
	opener = urllib2.build_opener()

	for url, file_name in files_list.items():
		try:
			request = urllib2.Request(url, None, {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.8.1.8) Gecko/20071008 Firefox/2.0.0.8"})
			handle = opener.open(request)
			data = handle.read()
			handle.close()
		except (urllib2.HTTPError, urllib2.URLError, IOError, ValueError), er:
			rez[url] = 0
		else:
			try:
				file(folder + '/' + file_name, 'wb').write(data)
			except:
				rez[url] = 0
			else:
				rez[url] = 1

	return rez

if __name__ == '__main__':
	files_list = {
		r'http://oboi.kards.ru/images/wallpapehghgr/773/77274_prev_98.jpg': r'77274_prev_98.jpg',
		r'http://img12.nnm.ru/imagez/gallery/1/8/4/5/d/1845d9bac3a1ab31ca0cde793e08e691_full.jpg': r'1845d9bac3a1ab31ca0cde793e08e691_full.jpg',
		r'http://img11.nnm.ru/imagez/gallery/a/a/0/d/4/aa0d405073e5fc42f3cfac37a4c79fc1.jpg':r'aa0d405073e5fc42f3cfac37a4c79fc1.jpg'
	}
	folder  = 'f:\\tmp\\'
	print download(files_list, folder)

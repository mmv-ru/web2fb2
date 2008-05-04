#coding=utf-8
'''
модуль, для работы с сессиями (как-бы сессиями)
'''

import random
import md5
import os
import time

class session:
	def __init__(self):
		self.SEESION_DIR = 'sess' #путь к сессиям
		self.MAX_SESSIONS = 32 #максимальное количество сессий
		self.CLEAN_TIME = 600 #время через которое сессии будут удалятся
		
		self.clean_up() #подчищаем старые сессии
		 
		self.cur_session_name = md5.new(str(random.random())).hexdigest()[:10] #уникальное имя сессии
		
	def start(self):
		'''
		создаем сессию, если предел сессий возвращаем False
		'''
	
		file(os.path.join(self.SEESION_DIR, self.cur_session_name), 'w').write('') #создаем на диске файл
		
		names = os.listdir(self.SEESION_DIR) #считаем кол-во файлов (сессий)
		if len(names) > self.MAX_SESSIONS: #если слишком много
			self._delete_file(os.path.join(self.SEESION_DIR, self.cur_session_name)) #удаляем файл
			return False

		return True

	def _delete_file(self, path):
		'''
		удаление файла
		'''
		try:
			os.remove(path) #пытаемся удаить файл
		except OSError, er: 
			if er.errno != 2: #если такого файла нет - значит его удалила другая копия скрипта
				raise er #если другая какая-то ошибка - это весьма странно

	def end(self):
		'''
		закрываем сессию
		'''
		self._delete_file(os.path.join(self.SEESION_DIR, self.cur_session_name))
				
	def clean_up(self):
		'''
		подчищаем старые сессии - которые не закрылись (например скрипт вдруг упал)
		'''
		for files in os.listdir(self.SEESION_DIR): 
			if time.time() - os.path.getmtime(os.path.join(self.SEESION_DIR, files)) > self.CLEAN_TIME: #если файл слишком старый
				self._delete_file(os.path.join(self.SEESION_DIR, files)) #трем его нафиг
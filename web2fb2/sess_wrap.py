#!/usr/bin/python2.4
#coding=utf-8

#модуль обертка для работы с сессиями
#может или напрямую импортировать модуль сессий
#или вызвать его как отдельную программу

import prior #модуль определения приоритета
import time

WRAP = True #если True - работа с сессиями происходит через вызов их модуля как программы


if WRAP:

	import subprocess
	import pickle

	def call_sess(func):
		'''
		выполнение скрипта который работает с сессияим, с переданными ему командами и обработка результата выполнения
		'''
		a = subprocess.Popen('./sessions.py', shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		
		#вызываем скрипт сессий
		#передаем ему команду на выполнение через stdin
		rez =  a.communicate(func)
		
		if rez[1]: #если что-то есть в stderr
			raise Exception, rez[1]
		else:
			r = pickle.loads(rez[0]) #переводим в объекты питона, то что пришло с stdout вызванного скрипта
			if isinstance(r, Exception): #если полученный объект - исключение - генерим его
				raise r
			else:
				return r
	

	def session_start(sess):
		'''
		начинаем сессию
		'''
		return call_sess("sess('%s').start(%s)" % (sess, prior.detect_prior()))

	def session_end(sess):
		'''
		конец сессии
		'''
		return call_sess("sess('%s').end()" % (sess))
			
else:
	import sessions
	
	def session_start(sess):
		'''
		начинаем сессию
		'''
		return sessions.sess(sess).start(prior.detect_prior())
		
	def session_end(sess):
		'''
		конец сессии
		'''
		return sessions.sess(sess).end()
	
if __name__ == '__main__':
	
	print time.time()
	print session_start('0')
	print time.time()
	print session_end('0')

# -*- coding: UTF8 -*-
#
# модуль для ведения логов
#

import time
levels = {'debug': 10, 'info': 20, 'warning':30, 'error': 40, 'critical':50} #уровни критичности

def setlogfunction(f):
	'''
	установка новой фукнции для вывода лога
	'''
	global log_function
	log_function = f
	
def setlevel(l):
	'''
	устанавливаем уровень
	'''
	global levels
	global level
	if l in levels:
		level = levels[l]
	else:
		raise ValueError, 'Bad level'
		
def write(msg, l):
	'''
	добаляем к сообщения тайм-штамп и вызываем функция вывода лога
	'''
	global  log_function
	log_function('%s %s: %s' % (time.strftime('%m.%d %H:%M:%S'), l, msg), l)
	
def debug(msg):
	

	global level
	global write
	if level <= 10:
		write(msg, 'debug')

def info(msg):
	global level
	global write

	if level <= 20:
		write(msg, 'info')

def warning(msg):
	global level
	global write
	if level <= 30:
		write(msg, 'warning')
	
def error(msg):
	global level
	global write
	if level <= 40:
		write(msg, 'error')

def critical(msg):
	global level
	global write
	if level <= 50:
		write(msg, 'critical')

def log2file(msg, l):
	#не забывать про кодировку!
	file('log.log', 'a').write(msg.encode('UTF-8') + '\n')

def log2console(msg, l):
	'''
	функция вывода по умолчанию
	'''
	#не забывать про кодировку!
	print msg
		
#log_function = log2console
log_function = log2file
level = levels['debug']

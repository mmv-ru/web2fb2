#!/usr/bin/python2.4
#coding=utf-8

import cgi, cgitb
cgitb.enable()
import traceback

import logging
import logging.handlers
from string import Template
import os

import web.template
render = web.template.render('templates/')


#настраиваем главный логгер
handler = logging.handlers.RotatingFileHandler('web2fb2.log', maxBytes = 1000000, backupCount = 1)
handler.setFormatter(logging.Formatter('%(asctime)s %(name)-24s %(levelname)-8s %(message)s'))
log = logging.root
log.addHandler(handler)
log.setLevel(logging.DEBUG)

import process
import sessions
import fb_utils

def main():
	log.info('************************************')
	log.info('Start web')
	
	print "Content-Type: text/html; charset=UTF-8\n"

	log.debug('Cleaning up')
	try:
		process.clean_up() #уборка территорий
	except:
		log.error('\n------------------------------------------------\n' + traceback.format_exc() + '------------------------------------------------\n')

	#пытаемся получить получить переменные из формы
	form = cgi.FieldStorage()
	url = form.getvalue('url')
	img = form.getvalue('img')
	yah2fb = form.getvalue('yah2fb')
	
	set_descr = form.getvalue('set_descr') #флаг, что надо передается описание
	
	log.debug('Try to get url: %s' % url)

	if not url:
		print render.simple_base(render.simple_form())
	else:
		log.info('We get url: %s' % url)
	
		sess = sessions.session()
		log.debug('start session')
		if not sess.start(): #начинаем сессию
			#если не удачно - выводим try again и ссылку на запрашиваемый урл
			log.info('cant start session')
			print render.base(render.simple_try(os.environ['REQUEST_URI']))
		else:
			log.info('Yes! new session')
			
			params = process.web_params()
			params.url = url
			params.yah2fb = yah2fb
			
			log.info('Set descr for url %s' % url)
			#заполняем описани
			
			descr = fb_utils.description()
			
			if set_descr:
				descr.author_first = form.getvalue('author_first', '').decode('UTF-8')
				descr.author_middle = form.getvalue('author_middle', '').decode('UTF-8')
				descr.author_last = form.getvalue('author_last', '').decode('UTF-8')
				descr.title = form.getvalue('title', '').decode('UTF-8')
				descr.genre = form.getvalue('genre', '').decode('UTF-8')
				descr.lang = form.getvalue('lang', '').decode('UTF-8')

			else:
				descr.author_first = descr.SELFDETECT
				descr.author_middle = descr.SELFDETECT
				descr.author_last = descr.SELFDETECT
				descr.title = descr.SELFDETECT
				descr.genre = descr.SELFDETECT
				descr.lang = descr.SELFDETECT
				
			descr.url = url
				
			params.descr = descr
			
			#работаем с картинками или без
			if img:
				params.is_img = True # с картинками
				log.info('With images. for url: %s' % url)
			else:
				params.is_img = False # без картинок
				log.info('Without images. for url: %s' % url)

			#запускаем сам процесс, перехватываем все неперехваченые ошибки в лог
			log.debug('url: %s Start process' % url)
			try:
				rez = process.process().do_web(params)
			except:
				log.error('\n------------------------------------------------\n' + traceback.format_exc() + '------------------------------------------------\n')
				print render.base( render.simple_error('Internal error') )
		
			else:
				log.debug('url: %s Stop process' % url)
				if rez[0] == 0:
					log.warning('url: %s Process return error' % (rez, ))
					print render.simple_base(
						render.simple_error('Internal error' + rez[1]) + render.simple_form()
					)
				elif rez[0] == 1:
					stat = rez[1]
					#log.info('url: %s Stat: %s' % (url, stat))
					log.info('url: %s Draw result: %s' % (url, stat.path_with_file))
					result_html = render.simple_result(
						stat.url,
						'%.1f' % stat.work_time,
						stat.img,
						stat.path + '/' + stat.file_name,
						stat.file_name,
						stat.file_size//1024
					)
					descr_html = render.simple_descr(
						stat.descr.title,
						stat.descr.author_first,
						stat.descr.author_middle,
						stat.descr.author_last,
						fb_utils.genres().get_genres_descrs(),
						stat.descr.genre,
						stat.descr.lang,
						stat.img,
						stat.url
					)
					print render.simple_base(result_html + descr_html)
			
			log.debug('end session')
			sess.end() #завершаем сессию
	log.info('End web')

if __name__=='__main__':
	main()
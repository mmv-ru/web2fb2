#!/usr/bin/python2.4
#coding=utf-8

import cgi, cgitb
cgitb.enable()
import traceback

import log
from string import Template
import os

import web.template
render = web.template.render('templates/')


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
	
	set_descr = form.getvalue('set_descr') #флаг, что надо передается описание
	
	log.debug('Try to get url: %s' % url)

	if not url:
		print render.simple_base(render.simple_form())
	else:
		log.info('We get url: %s' % url)
		
		
		params = process.web_params()
		params.url = form.getvalue('url', '')
		
		if form.getvalue('img', False):
			params.is_img = True
		
		if form.getvalue('yah2fb', False):
			params.yah2fb = True
		
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
			
		descr.url = params.url
			
		params.descr = descr
		
		#запускаем сам процесс, перехватываем все неперехваченые ошибки в лог
		log.debug('url: %s Start process' % url)
		try:
			progres = process.do(params)
		except Exception, er:
			if 'Try error' in str(er):
				print render.simple_base( render.simple_try(os.environ['REQUEST_URI']) )
				log.debug('Try later')
				
			else:
				log.error('\n------------------------------------------------\n' + traceback.format_exc() + '------------------------------------------------\n')
				print render.simple_base( render.simple_error(str(er)) )
	
		else:
			log.debug('url: %s Stop process' % url)
			
			if progres.error:
				print render.simple_base( render.simple_error(str(progres.error)) )
			elif progres.done:
				stat = progres.done
			
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
			
	log.info('End web')

if __name__=='__main__':
	main()
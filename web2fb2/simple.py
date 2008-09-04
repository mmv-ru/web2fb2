#!/usr/bin/python
#coding=utf-8

import cgi, cgitb
cgitb.enable()
import traceback

import Cookie

import log
from string import Template
import os

import web.template
render = web.template.render('templates/')
import webutils

import process
import fb_utils
import prior
import urlparse


def main():
	log.info('************************************')
	log.info('Start web')
	
	global sid
	sid = webutils.sid_work()
	
	log.debug('Cleaning up')
	try:
		process.clean_up() #уборка территорий
	except:
		log.error('\n------------------------------------------------\n' + traceback.format_exc() + '------------------------------------------------\n')


	
	#пытаемся получить получить переменные из формы
	form = cgi.FieldStorage()
	
	urls = []
	
	for url in form.getlist('url'):
		if urlparse.urlparse(url)[1]:
			urls.append(url)
	
	if not urls:
		webutils.print_page( render.simple_base(render.simple_form()) )
		
	else:
		log.info('We get urls: %s' % urls)
		
		
		params = process.web_params()
		
		params.urls = urls
		
		if form.getvalue('img', False):
			params.is_img = True
		
		if form.getvalue('tab', False):
			params.is_tab = True
		
		if form.getvalue('old_h2fb2', False):
			params.old_h2fb2 = True
		
		log.info('Set descr for urls %s' % urls)
		#заполняем описани
		
		descr = fb_utils.description()
		
		set_descr = form.getvalue('set_descr') #флаг, что надо передается описание
		
		if set_descr:
			descr.selfdetect = False
			
			author_first_0 = form.getvalue('author_first_0', '').decode('UTF-8')
			author_middle_0 = form.getvalue('author_middle_0', '').decode('UTF-8')
			author_last_0 = form.getvalue('author_last_0', '').decode('UTF-8')
			
			if author_first_0 or author_middle_0 or author_last_0:
				descr.authors.append(
					{
						'first': author_first_0,
						'middle': author_middle_0,
						'last': author_last_0
					}
				)
			
			author_first_1 = form.getvalue('author_first_1', '').decode('UTF-8')
			author_middle_1 = form.getvalue('author_middle_1', '').decode('UTF-8')
			author_last_1 = form.getvalue('author_last_1', '').decode('UTF-8')
			
			if author_first_1 or author_middle_1 or author_last_1:
				descr.authors.append(
					{
						'first': author_first_1,
						'middle': author_middle_1,
						'last': author_last_1
					}
				)
			
			author_first_2 = form.getvalue('author_first_2', '').decode('UTF-8')
			author_middle_2 = form.getvalue('author_middle_2', '').decode('UTF-8')
			author_last_2 = form.getvalue('author_last_2', '').decode('UTF-8')
			
			if author_first_2 or author_middle_2 or author_last_2:
				descr.authors.append(
					{
						'first': author_first_2,
						'middle': author_middle_2,
						'last': author_last_2
					}
				)
			
			if not descr.authors:
				descr.authors.append(descr.def_author)
			
			
			descr.title = form.getvalue('title', '').decode('UTF-8')
			descr.genre = form.getvalue('genre', '').decode('UTF-8')
			descr.lang = form.getvalue('lang', '').decode('UTF-8')

		else:
			descr.selfdetect = True
			
		descr.urls = params.urls
			
		params.descr = descr
		
		#запускаем сам процесс, перехватываем все неперехваченые ошибки в лог
		log.debug('urls: %s Start process' % urls)
		try:
			progres = process.do(params, sid)
		except process.SessRet, er:
			webutils.print_page( render.simple_base( render.simple_try(os.environ['REQUEST_URI'], er.value['place'], prior.priors.get( er.value['prior'], 'unknown') ), refresh = True ))
			
			log.debug('Try later')
		except Exception, er:
				log.error('\n------------------------------------------------\n' + traceback.format_exc() + '------------------------------------------------\n')
				webutils.print_page( render.simple_base( render.simple_error(str(er)) ) )
	
		else:
			log.debug('urls: %s Stop process' % urls)
			
			if progres.error:
				webutils.print_page( render.simple_base( render.simple_error(str(progres.error)) ) )
			elif progres.done:
				stat = progres.done
			
				result_html = render.simple_result(
					stat.urls,
					'%.1f' % stat.work_time,
					stat.img,
					stat.path + '/' + stat.file_name,
					stat.file_name,
					stat.file_size//1024,
					stat.valid['is_valid'],
					stat.valid['msg']
				)
				descr_html = render.simple_descr(
					stat.descr.title,
					stat.descr.authors,
					len(stat.descr.authors),
					fb_utils.genres().get_genres_descrs(),
					stat.descr.genre,
					stat.descr.lang,
					stat.img,
					stat.urls,
					[i for i in xrange(len(stat.urls))],
					stat.tab,
					stat.old_h2fb2
				)
				webutils.print_page( render.simple_base(result_html + descr_html) )
			
	log.info('End web')

if __name__=='__main__':
	main()

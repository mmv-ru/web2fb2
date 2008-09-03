#!/usr/bin/python
#coding=utf-8

import cgi, cgitb
cgitb.enable()
import traceback

import urlparse

import fb_utils
import process

import json
import web.template
render = web.template.render('templates/')

import webutils
import prior

import log

def main():
	log.info('************************************')
	log.info('Start widget')
	
	global sid
	sid = webutils.sid_work()
	
	form = cgi.FieldStorage()
	
	if form.getvalue('ajax'):
		ajax()
	else:
		base()

def base():

	webutils.print_page(
		render.widget_base(
			render.widget_form('http://', True, False, False),
			render.widget_descr(
				'',
				'',
				'',
				'',
				fb_utils.genres().get_genres_descrs(),
				fb_utils.genres().get_default(),
				''
			)
		)
	)
	
def ajax():


	log.info('************************************')
	log.info('Start ajax')
	
	log.debug('Cleaning up')
	try:
		process.clean_up() #уборка территорий
	except:
		log.error('\n------------------------------------------------\n' + traceback.format_exc() + '------------------------------------------------\n')

	
	params = process.web_params()
	
	form = cgi.FieldStorage()
	
	urls = []
	for url in form.getlist('url'):
		if urlparse.urlparse(url)[1]:
			urls.append(url)
			
	if not urls:
		webutils.print_page( json.write({'error': render.widget_error('Bad url')}) )
	else:
		log.info('We get urls: %s' % urls)
	
		params.urls = urls
		
		if form.getvalue('img') == 'true':
			params.is_img = True
		
		
		if form.getvalue('tab') == 'true':
			params.is_tab = True
		
			
		if form.getvalue('yah2fb') == 'true':
			params.yah2fb = True
		
		descr = fb_utils.description()
		descr.urls = params.urls
		
		if form.getvalue('autodetect') == 'true':
			descr.selfdetect = True
		else:
			descr.selfdetect = False
			
			descr.authors.append(
				{
					'first': form.getvalue('author_first', '').decode('UTF-8'),
					'middle': form.getvalue('author_middle', '').decode('UTF-8'),
					'last': form.getvalue('author_last', '').decode('UTF-8')
				}
			)
			
			descr.title = form.getvalue('title', '').decode('UTF-8')
			descr.genre = form.getvalue('genre', '').decode('UTF-8')
			descr.lang = form.getvalue('lang', '').decode('UTF-8')
		
		params.descr = descr
			
		try:
			progres = process.do(params, sid, True)
			
		except process.SessRet, er:	
			webutils.print_page( json.write({'tryagain': render.widget_try( er.value['place'], prior.priors.get( er.value['prior'], 'unknown') )}) )
			log.debug('Try later')
			
		except Exception, er:
				webutils.print_page( json.write({'error': render.widget_error(str(er))}) )
				log.error('\n------------------------------------------------\n' + traceback.format_exc() + '------------------------------------------------\n')

		else:
			log.debug(str(progres))
			
			if progres.error:
				webutils.print_page( json.write({'error': render.widget_error(str(progres.error))}) )
				log.debug('progres return error: %s' % progres.error)

			elif progres.done:
				
				stat = progres.done
				
				webutils.print_page(
					json.write(
						{
							'result':render.widget_result(
								stat.urls,
								'%.1f' % stat.work_time,
								stat.img,
								stat.path + '/' + stat.file_name,
								stat.file_name,
								stat.file_size//1024,
								stat.valid['is_valid'],
								stat.valid['msg']
							),
							'descr':{
								'title':stat.descr.title.encode('UTF-8'),
								'author_first':stat.descr.authors[0]['first'].encode('UTF-8'),
								'author_middle':stat.descr.authors[0]['middle'].encode('UTF-8'),
								'author_last':stat.descr.authors[0]['last'].encode('UTF-8'),
								'genre':stat.descr.genre.encode('UTF8'),
								'lang':stat.descr.lang.encode('UTF8')
							}
						}
					)
				)
			else:
				
				webutils.print_page(
					json.write({'progres': render.widget_progres(
						progres.msgs,
						progres.level,
						[x for x in xrange(len(progres.msgs))],
						progres.level + 1,
						len(progres.msgs)
					)})
				)

if __name__=='__main__':
	main()
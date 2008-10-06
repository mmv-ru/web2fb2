#!/usr/bin/python
#coding=utf-8

import cgi, cgitb
cgitb.enable()
import traceback
import re

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
	log.info('Start ajax')
	
	global sid
	sid = webutils.sid_work()
	
	form = cgi.FieldStorage()
	
	if form.getvalue('ajax'):
		ajax()
	else:
		base()

def base():
	
	form = cgi.FieldStorage()
	
	url = form.getvalue('url', '')
	
	if form.getvalue('doit', ''): doit = True
	else: doit = False
	
	if not form.getvalue('img', False): img = True;
	else: img = False
	
	webutils.print_page(
		render.ajax_base(
			render.ajax_form(url, img, False, doit, False),
			render.ajax_descr(
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
		webutils.print_page( json.write({'error': render.ajax_error('Bad url')}) )
	else:
		log.info('We get urls: %s' % urls)
	
		params.urls = urls
		
		if form.getvalue('img', ''):
			params.is_img = True
		
		if form.getvalue('tab', ''):
			params.is_tab = True
			
		if form.getvalue('pre', ''):
			params.is_pre = True
			
		if form.getvalue('old_h2fb2', ''):
			params.old_h2fb2 = True
			
		
		descr = fb_utils.description()
		descr.urls = params.urls
		
		if form.getvalue('autodetect', ''):
			descr.selfdetect = True
			log.debug('selfdetect yes')
		else:
			descr.selfdetect = False
			log.debug('selfdetect no')
			descr.title = form.getvalue('title', '').decode('UTF-8')
			descr.genre = form.getvalue('genre', '').decode('UTF-8')
			descr.lang = form.getvalue('lang', '').decode('UTF-8')
			
			ids = set()
			for key in form.keys():
				try:
					id = int(re.findall(r"author_\S+\|(\d+)", key)[0])
				except (IndexError, ValueError):
					pass
				else:
					ids.add(id)
					
			for id in ids:
				first = form.getvalue('author_first|%s' % id, '').decode('UTF-8')
				middle = form.getvalue('author_middle|%s' % id, '').decode('UTF-8')
				last = form.getvalue('author_last|%s' % id, '').decode('UTF-8')
			
				if first or middle or last:
					descr.authors.append(
						{
							'first': first,
							'middle': middle,
							'last': last
						}
					)
			if not descr.authors:
				descr.authors.append(descr.def_author)

			descr.genre = form.getvalue('genre', '').decode('UTF-8')
			descr.lang = form.getvalue('lang', '').decode('UTF-8')
			
			log.debug('descrs %s' % descr.authors)
			
		params.descr = descr
		#log.debug(str(params.descr.genre))
			
		try:
			progres = process.do(params, sid, True)
		except process.SessRet, er:
				webutils.print_page( json.write({'tryagain': render.ajax_try( er.value['place'], prior.priors.get( er.value['prior'], 'unknown') )}))
				log.debug('Try later')
		except Exception, er:
				webutils.print_page( json.write({'error': render.ajax_error(str(er))}) )
				log.error('\n------------------------------------------------\n' + traceback.format_exc() + '------------------------------------------------\n')

		else:
			log.debug(str(progres))
			
			if progres.error:
				webutils.print_page( json.write({'error': render.ajax_error(str(progres.error))}) )
				log.debug('progres return error: %s' % progres.error)

			elif progres.done:
				
				stat = progres.done
				
				webutils.print_page(
					json.write(
						{
							'result':render.ajax_result(
								stat.urls,
								'%.1f' % stat.work_time,
								stat.img,
								stat.path + '/' + stat.file_name,
								stat.file_name,
								stat.file_size//1024,
								stat.valid['is_valid'],
								stat.valid['msg'],
								stat.preview_file
							),
							'descr':{
								'title':stat.descr.title.encode('UTF-8'),
								'authors': [ 
									{ 
										'first': author['first'].encode('UTF-8'), 
										'middle': author['middle'].encode('UTF-8'), 
										'last': author['last'].encode('UTF-8') 
									} 
									for author in stat.descr.authors 
								],
								'genre':stat.descr.genre.encode('UTF8'),
								'lang':stat.descr.lang.encode('UTF8')
							}
						}
					)
				)
			else:
				webutils.print_page(
					json.write({'progres': render.ajax_progres(
						progres.msgs,
						progres.level,
						[x for x in xrange(len(progres.msgs))]
					)})
				)

if __name__=='__main__':
	main()
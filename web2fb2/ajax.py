#!/usr/bin/python2.4
#coding=utf-8

import cgi, cgitb
cgitb.enable()
import traceback

import fb_utils
import process

import json
import web.template
render = web.template.render('templates/')

import log

def main():
	print "Content-Type: text/html; charset=UTF-8\n"
	
	form = cgi.FieldStorage()
	
	if form.getvalue('ajax'):
		ajax()
	else:
		base()

def base():
	print render.ajax_base(
		render.ajax_form(),
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
	
	params.url =  form.getvalue('url', '')
	
	if form.getvalue('img') == 'true':
		params.is_img = True
		
	if form.getvalue('yah2fb') == 'true':
		params.yah2fb = True
	
	descr = fb_utils.description()
	descr.url = params.url
	
	if form.getvalue('autodetect') == 'true':
		descr.author_first = descr.SELFDETECT
		descr.author_middle = descr.SELFDETECT
		descr.author_last = descr.SELFDETECT
		descr.title = descr.SELFDETECT
		descr.genre = descr.SELFDETECT
		descr.lang = descr.SELFDETECT
	else:
		descr.title = form.getvalue('title', '').decode('UTF-8')
		descr.author_first = form.getvalue('author_first', '').decode('UTF-8')
		descr.author_middle = form.getvalue('author_middle', '').decode('UTF-8')
		descr.author_last = form.getvalue('author_last', '').decode('UTF-8')
		descr.genre = form.getvalue('genre', '').decode('UTF-8')
		descr.lang = form.getvalue('lang', '').decode('UTF-8')
	
	params.descr = descr
	#log.debug(str(params.descr.genre))
		
	try:
		progres = process.do(params, True)
	except Exception, er:
		print json.write({'error': render.ajax_error(str(er))})
	else:
		log.debug(str(progres))
		
		if progres.error:
			print json.write({'error': render.ajax_error(str(progres.error))})
		elif progres.done:
			
			stat = progres.done
			
			print json.write(
				{
					'result':render.ajax_result(
						stat.url,
						'%.1f' % stat.work_time,
						stat.img,
						stat.path + '/' + stat.file_name,
						stat.file_name,
						stat.file_size//1024
					),
					'descr':{
						'title':stat.descr.title.encode('UTF-8'),
						'author_first':stat.descr.author_first.encode('UTF-8'),
						'author_middle':stat.descr.author_middle.encode('UTF-8'),
						'author_last':stat.descr.author_last.encode('UTF-8'),
						'genre':stat.descr.genre.encode('UTF8'),
						'lang':stat.descr.lang.encode('UTF8')
					}
				}
			)
		else:
			
			print json.write({'progres': render.ajax_progres(
				progres.msgs,
				progres.level,
				[x for x in xrange(len(progres.msgs))]
			)})

if __name__=='__main__':
	main()
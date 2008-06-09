#coding=utf-8
import time
import random
import os

import ngram
from BeautifulSoup import BeautifulSoup

import yah2fb
import h2fb

import log

def do(source_file, descr, rez_file, progres, is_yah2fb = False, is_img = True):
	
	data = file(source_file).read().decode('UTF-8')
	
	log.debug("prs y %s i %s" % (is_yah2fb, is_img) )
	descr.id = 'web2fb2_%s_%08i' % (time.strftime('%Y%m%d%H%M'),  random.randint(0, 9999999999))
	descr.program_used = 'http://web2fb2.net/'
	
	if descr.lang == descr.SELFDETECT:
			#детектор языка
			log.debug('Detecting language')
			descr.lang = detect_lang(data)
			log.info('Detected language: %s' % descr.lang)
			
	if not is_yah2fb:
		params = h2fb.default_params.copy()
		params['data'] = data.encode('utf8')
		params['verbose'] = 1
		params['encoding-from'] = 'UTF-8'
		params['encoding-to'] = 'UTF-8'
		if is_img:
			params['skip-images'] = 0
		else:
			params['skip-images'] = 1
		params['descr'] = descr
		params['informer'] = lambda msg: log.debug('h2fb ' + msg.strip()) #делаем вывод сообщений от h2fb2 в лог
		params['file_out'] = file(rez_file, 'w')
		params['source_file_path'] = os.path.split(source_file)[0]
		
		log.debug('Start h2fb process')
		mp = h2fb.MyHTMLParser()
		out_data = mp.process(params)
		descr = mp.get_descr()
		params['file_out'].close()
		log.debug('End of h2fb process')
		
		return descr
	
	else:
		params = yah2fb.params_()
		params.data = data
		if is_img:
			params.skip_images = False
		else:
			params.skip_images = True
		params.descr = descr
		params.file_out = file(rez_file, 'w')
		params.source_file_path = os.path.split(source_file)[0]
		
		log.debug('Start yah2fb process')
		
		rez = yah2fb.html2fb2().process(params)
		out_data = rez['data']
		descr = rez['descr']
		params.file_out.close()
		
		log.debug('End of yah2fb process')
		
		return descr

def detect_lang(data):
	soup = BeautifulSoup(data)
	text = ''.join(soup.findAll(text = True))
		
	l = ngram.NGram('lm')
	return l.classify(text.encode('utf8')).split('.')[0]
	
if __name__ == '__main__':
	import fb_utils
	do(
		file("tmp/temp.htm").read().decode('UTF-8'),
		descr = fb_utils.description(),
		rez_file = file('tmp/temp.fb2', 'w'),
		is_yah2fb = False,
		is_img = False
	)


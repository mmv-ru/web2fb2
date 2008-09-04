#coding=utf-8
import time
import random
import os

import codecs

import ngram
from BeautifulSoup import BeautifulSoup

BeautifulSoup.NESTABLE_TAGS['strong'] = []
BeautifulSoup.NESTABLE_TAGS['b'] = []
BeautifulSoup.NESTABLE_TAGS['i'] = []
BeautifulSoup.NESTABLE_TAGS['em'] = []
BeautifulSoup.NESTABLE_TAGS['var'] = []
BeautifulSoup.NESTABLE_TAGS['cite'] = []
BeautifulSoup.NESTABLE_TAGS['p'] = []
BeautifulSoup.NESTABLE_TAGS['pre'] = []


from lxml import etree

import html5lib
from html5lib import treebuilders

import yah2fb
import h2fb

import log

SCHEMA_DIR = 'schemas'
SCHEMA_MAIN = 'FictionBook2.21.xsd'


def do(source_files, descr, rez_file, progres, is_old_h2fb2 = False, is_img = True, is_tab = False):

	"""
	преобразрвание html в fb2, c определением языка и поддержкой нескольких движков
	source_file - html файл
	descr - объект типа fb_utils.description
	rez_file - куда писать результат
	is_yah2fb - какой движок использовать
	is_img - с картинками или без
	
	"""
	
	

	log.debug("prs y %s i %s" % (is_old_h2fb2, is_img) )
	descr.id = 'web2fb2_%s_%08i' % (time.strftime('%Y%m%d%H%M'),  random.randint(0, 9999999999))
	descr.program_used = 'http://web2fb2.net/'
	
	if descr.selfdetect:
			#детектор языка
			log.debug('Detecting language')
			data = codecs.open(source_files[0], 'r', 'utf-8').read()
			descr.lang = detect_lang(data)
			log.info('Detected language: %s' % descr.lang)
			
	if is_old_h2fb2:
		params = h2fb.default_params.copy()
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
		params['source_file_path'] = source_files
		
		log.debug('Start h2fb process')
		mp = h2fb.MyHTMLParser()
		mp.process(params)
		descr = mp.get_descr()
		params['file_out'].close()
		log.debug('End of h2fb process')
	
	else:
		params = yah2fb.params_()
		params.source_files = source_files
		if is_img:
			params.skip_images = False
		else:
			params.skip_images = True
			
		if is_tab:
			params.skip_tables = False
		else:
			params.skip_tables = True
			
			
		params.descr = descr
		params.file_out = rez_file
		
		log.debug('Start yah2fb process')
		
		descr = yah2fb.htmls2fb2(params)
		
		log.debug('End of yah2fb process')
		
	valid = check_xml_valid(rez_file)
	return descr, valid
	#return descr, {'is_valid':True, 'msg':''}

def check_xml_valid(f_name):
	'''
	проверка валидности xml
	'''
	schema_doc = etree.parse(os.path.join(SCHEMA_DIR, SCHEMA_MAIN))
	schema = etree.XMLSchema(schema_doc)
	try:
		doc = etree.parse(f_name)
		schema.assertValid(doc)
	except etree.DocumentInvalid, er:
		log.info('fb2 not valid: %s' % str(er))
		return {'is_valid':False, 'msg':str(er)}
	except etree.XMLSyntaxError, er:
		log.info('fb2 syntax error: %s' % str(er))
		return {'is_valid':False, 'msg':str(er)}
	else:
		log.info('fb2 valid')
		return {'is_valid':True, 'msg':''}
	


def detect_lang(data):
	'''
	детектит язык
	'''
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
		old_h2fb2 = False,
		is_img = False
	)


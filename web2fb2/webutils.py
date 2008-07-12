#coding=utf-8
import os
import cgi, cgitb
cgitb.enable()
import traceback

import Cookie

import md5
import random

import log

headers = []

def print_page(data):
	global headers
	for h in headers:
		print h
	print "Content-Type: text/html; charset=UTF-8\n"
	print data


def set_sid(val):
	global headers
	cookie = Cookie.SimpleCookie()
	cookie['sid'] = val
	
	headers.append(cookie.output())

def get_sid():
	cookie = Cookie.SimpleCookie(os.environ.get('HTTP_COOKIE', None))
	if 'sid' in cookie:
		return cookie['sid'].value
	else:
		return None
		
def gen_sid():
	return md5.new(str(random.random())).hexdigest()[:16]
	
	
def sid_work():
	sid = get_sid()
	
	if not sid:
		sid = gen_sid()
		log.debug('new sid: %s' % sid)
	else:
		log.debug('sid: %s' % sid)
	set_sid(sid)
	
	return sid
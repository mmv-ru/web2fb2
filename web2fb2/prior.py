#!/usr/bin/python2.4
#coding=utf-8

# по хосту и рефереру определет приоритет пользователя VIP, user или аноним
#если вызван напрямую - печатает ип, реферер, приоритет

import cgi
import os

VIP_HOST_FNAME = 'vip_hosts.txt'
VIP_REF_FNAME =  'vip_ref.txt'

USER_HOST_FNAME = 'user_host.txt'
USER_REF_FNAME = 'user_ref.txt'

CFG_DIR = 'config'


priors = {0:'extra', 1:'vip', 2:'user', 3:'anonymous'}

def read2list(fname):
	'''
	считывает файл в список
	'''
	rez = []
	try:
		f = file(fname)
		for s in f:
			if s.strip():
				rez.append(s.strip())
		f.close()
	except IOError, er:
		return []
	else:
		return rez

def detect_prior():
	'''
	вычисляет приоритет, исходя из данных IP и referer
	'''
	host = os.environ.get('REMOTE_ADDR', None) #хост пользователя
	ref = os.environ.get('HTTP_REFERER', None) #реферер пользователя
	
	if host:
		for vip_host in vip_hosts:
			if vip_host in host:
				return 1
	
	if ref:
		for vip_ref in vip_refs:
			if vip_ref in ref:
				return 1
			
	if host:
		for user_host in user_hosts:
			if user_host in host:
				return 2
			
	if ref:
		for user_ref in user_refs:
			if user_refs in ref:
				return 2
	return 3
	
vip_hosts = read2list(os.path.join(CFG_DIR, VIP_HOST_FNAME))
vip_refs = read2list(os.path.join(CFG_DIR, VIP_REF_FNAME))

user_hosts = read2list(os.path.join(CFG_DIR, USER_HOST_FNAME))
user_refs = read2list(os.path.join(CFG_DIR, USER_REF_FNAME))
	
if __name__ == '__main__':
	print "Content-Type: text/html; charset=UTF-8\n"
	print "<pre>"
	print 'HOST: ', os.environ.get('REMOTE_ADDR', None)
	print 'REF: ',os.environ.get('HTTP_REFERER', None)
	print 'prior: ', detect_prior(), priors.get(detect_prior(), '')
	print "</pre>"
	
	
	
	
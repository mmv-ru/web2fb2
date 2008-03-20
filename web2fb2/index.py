#!/usr/bin/python2.4
#coding=utf-8

import cgi, cgitb
cgitb.enable()
import traceback

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-24s %(levelname)-8s %(message)s',
                    filename='web2fb2.log',
                    filemode='w')
log = logging.getLogger('web2fb2.web')
import process

def draw_header():
	'''
	вывод html хедера
	'''
	return """
<html>
<title>web2fb2</title>
<body>

</br></br></br></br></br></br></br>
<div align="center">
<h1>web2fb2</h1>
<h3 style="color: red;">attention! service on prototype phase! for developing and testing purpose only.</h3>
	"""

def draw_footer():
	'''
	вывод html футера ;)
	'''
	return """
</div>

<div align="center" style="position: absolute; bottom: 0px; left: 0px; width: 100%;">
<table width="100%" cellpadding="5">
<tr valign="bottom">
<td width="30%" align="left">developing: Ivan El'chin</td>
<td align="center" valign="middle">supporting & sponsoring:<br /><a href="http://www.iscriptum.com/"><img border="0" src="http://www.iscriptum.com/iscriptum_logo_136x37_tr.png" /></a></td>
<td width="30%" align="right">project management on assembla.com: <a href="http://www.assembla.com/spaces/web2fb2">web2fb2</a></td>
</tr>
</table>
</div>

</body>
</html>
	"""

def draw_error(er):
	'''
	вывод ошибки
	'''
	return "<font color = 'red'>ERROR: " + str(er).replace("<", "").replace(">", "") + "</font>"


def draw_form():
	'''
	вывод html формы
	'''
	return """
<form action="" method="get">
<strong>Enter url:</strong>
<input name="url" type="text" size="50" maxlength="256" value="http://" />
<input name="" type="submit" />
</form>
"""


def main():
	log.info('Start web')
	
	log.debug('Cleaning up')
	try:
		process.clean_up() #уборка территорий
	except:
		log.error('\n------------------------------------------------\n' + traceback.format_exc() + '------------------------------------------------\n')
	
	print "Content-Type: text/html; charset=UTF-8\n"
	print draw_header()

	#пытаемся получить url
	form = cgi.FieldStorage()
	url = form.getvalue('url')
	
	log.debug('Try to get url: %s' % url)

	if not url:
		print draw_form()
	else:
		log.info('We get url: %s' % url)

		log.debug('url: %s Start process' % url)
		try:
			rez = process.process().web(url)
		except:
			log.error('\n------------------------------------------------\n' + traceback.format_exc() + '------------------------------------------------\n')
			print draw_error('Internal error')
		
		else:
			log.debug('url: %s Stop process' % url)
			if rez[0] == 0:
				log.warning('url: %s Process return error' % (rez, ))
				print draw_error(rez[1])
				print draw_form()
			elif rez[0] == 1:
				log.info('url: %s Show link: %s' % (url, rez[1]))
				print "<b>Download link:</b> <a href = '" + rez[1] + "'>" + rez[2] + "</a>"

	print draw_footer()
	log.info('End web')

if __name__=='__main__':
	main()
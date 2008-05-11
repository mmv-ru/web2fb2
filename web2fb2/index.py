#!/usr/bin/python2.4
#coding=utf-8

import cgi, cgitb
cgitb.enable()
import traceback

import logging
import logging.handlers
from string import Template
import os

#настраиваем главный логгер
handler = logging.handlers.RotatingFileHandler('web2fb2.log', maxBytes = 1000000, backupCount = 1)
handler.setFormatter(logging.Formatter('%(asctime)s %(name)-24s %(levelname)-8s %(message)s'))
log = logging.root
log.addHandler(handler)
log.setLevel(logging.DEBUG)

import process
import sessions
import fb_utils

def print_utf8(s):
	'''
	вывод с перекодировкой в utf8
	'''
	print s.encode('UTF-8')

def draw_header():
	'''
	вывод html хедера
	'''
	return """
<html>
<head>
<meta http-equiv="Content-Style-Type" content="text/css" />
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

<title>web2fb2</title>
<head>
<body>

</br></br></br></br></br>
<div align="center">
<h1>web2fb2</h1>
<center>
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
var pageTracker = _gat._getTracker("UA-3495198-3");
pageTracker._initData();
pageTracker._trackPageview();
</script>

<form action="https://www.paypal.com/cgi-bin/webscr" method="post">
<input type="hidden" name="cmd" value="_s-xclick">
<input type="image" src="https://www.paypal.com/en_US/i/btn/x-click-but04.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
<img alt="" border="0" src="https://www.paypal.com/en_US/i/scr/pixel.gif" width="1" height="1">
<input type="hidden" name="encrypted" value="-----BEGIN PKCS7-----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-----END PKCS7-----
">
</form>
</center>
<h3 >Beta vertion.<br/> Please add bug (with URL and short description) <a href = 'http://trac2.assembla.com/web2fb2/newticket'>here.</a> </h3>
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
<td width="30%" align="left">Development: Ivan El'chin</td>
<td align="center" valign="middle">Support and Sponsorship:<br /><a href="http://www.iscriptum.com/"><img border="0" src="http://www.iscriptum.com/iscriptum_logo_136x37_tr.png" /><br />eReaders for fb2</a></td>
<td width="30%" align="right">Project management on assembla.com: <a href="http://www.assembla.com/spaces/web2fb2">web2fb2</a></td>
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
    <table>
      <tr>
        <td><strong>Enter url:</strong> </td>
        <td><input name="url" type="text" size="50" maxlength="256" value="http://" />
        </td>
        <td><input name="" type="submit" />
          <br/>
        </td>
      </tr>
      <tr>
        <td></td>
        <td><input name="img" type="checkbox" value="1" checked>
          with images</td>
        <td></td>
      </tr>
      <tr>
        <td></td>
        <td><input name="yah2fb" type="checkbox" value="1">
          yet another h2fb engine</td>
		<td></td>
      </tr>	
    </table>
  </form>
"""

def draw_result(stat):
	'''
	вывод результата
	'''
	r = ''
	
	r += '''
	<table><tr><td>&nbsp;</td><td>
	<div align='center'  style = 'position: relative; border: 1px dotted #999999; padding: 3px; font-size:13px; text-align: left;'>
	'''
	r += '''Generated from <i>%s </i>''' % stat.url
	
	if stat.img:
		r += '''( with images )'''
	else:
		r += '''( without images )'''
	r+= "<br/>"
	r += '''
	Generating time: %.1f sec<br/>
	''' % stat.work_time
	r += '''</div>
	</td><td>&nbsp;</td></tr></table>
	<br /><br />
	'''
	
	r += '''
		<b>Download link:</b> <a href = '%s/%s'>%s</a> - %s KB
		''' % (stat.path, stat.file_name, stat.file_name, stat.file_size // 1024)
	r += '''<br /><br />'''
	return r

def draw_descr(stat):
	'''
	вывод описания
	'''
	r = '''
	<br />
	<table><tr><td>&nbsp;</td><td>
	<div style="position:relative; border: 1px solid #000000;">
	<center><strong>Check description. If wrong fill in as you think fit.</strong></center>
	<form method="get" action="">
	  <table>
		<tr>
		  <td>Title:</td>
		  <td colspan="3"><input type="text" name="title" size="75" maxlength="256" value = '%(title)s' /></td>
		</tr>
		<tr>
		  <td>Author:</td>
		  <td><input type="text" name="author_first" size="25" maxlength="256" value = '%(author-first)s'/>
			<br />
			<label style="font-size:x-small">first name</label></td>
		  <td><input type="text" name="author_middle" size="25" maxlength="256" value = '%(author-middle)s' />
			<br />
			<label style="font-size:x-small">middle name</label></td>
		  <td><input type="text" name="author_last"  size="25" maxlength="256" value = '%(author-last)s' />
			<br />
			<label style="font-size:x-small">last name</label></td>
		</tr>
	''' % {
			'title': stat.descr.title,
			'author-first': stat.descr.author_first,
			'author-middle': stat.descr.author_middle,
			'author-last': stat.descr.author_last
			}

	#жанры рисуем
	r += '''
		<tr>
			<td>Genre</td>
			<td colspan="2">
			<select name="genre">
		'''

	for l in fb_utils.genres().get_genres_descrs():
		if isinstance(l, basestring):
			r += '''<optgroup label="%s">
			''' % l
		else:
			if stat.descr.genre == l[0]:
				r += '''<option value="%s" selected='selected'>%s</option>
							''' % (l[0], l[1])
				
			else:
				r += '''<option value="%s">%s</option>
				''' % (l[0], l[1])
		
	r+= '''
		</select>
		</td>
		<td></td>
	</tr>
	'''
	
	r += '''
		<tr>
		<td>Language:</td>
		<td align="left"><input type="text" name="lang" size="2" maxlength="2" value = '%s' /></td>
		<td></td>
		<td></td>
		</tr>
	''' % stat.descr.lang
	
	r += '''<tr>
		<td>&nbsp;</td>
		<td>&nbsp;</td>
		<td>&nbsp;</td>
		<td align="right"><input type="submit" value = "Apply"/></td>
		</tr>
	  </table>
	  <input name="set_descr" type="hidden" value="True">
	  <input name="url" type="hidden" value="%(url)s">
	''' % {
			'url': stat.url
    }
	
	if stat.img:
		r += '<input name="img" type="hidden" value="True">'
	  
	r += """
	</form>
	</div>
	</td><td>&nbsp;</td></tr></table>
	"""

	return r
	
def draw_try(url):
	'''
	вывод, если пользователей многовато
	'''
	return '''Sorry, too many users are generating ebookz. Please try again a little later.<br />
<h3><a href = '%s'> Press to continue (try again if fail)</a></h3>''' % url

def main():
	log.info('************************************')
	log.info('Start web')
	
	print "Content-Type: text/html; charset=UTF-8\n"
	print_utf8(draw_header()) #выводим хедер

	log.debug('Cleaning up')
	try:
		process.clean_up() #уборка территорий
	except:
		log.error('\n------------------------------------------------\n' + traceback.format_exc() + '------------------------------------------------\n')

	#пытаемся получить получить переменные из формы
	form = cgi.FieldStorage()
	url = form.getvalue('url')
	img = form.getvalue('img')
	yah2fb = form.getvalue('yah2fb')
	
	set_descr = form.getvalue('set_descr') #флаг, что надо передается описание
	
	log.debug('Try to get url: %s' % url)

	if not url:
		print_utf8(draw_form()) #форма для урла
	else:
		log.info('We get url: %s' % url)
	
		sess = sessions.session()
		log.debug('start session')
		if not sess.start(): #начинаем сессию
			#если не удачно - выводим try again и ссылку на запрашиваемый урл
			log.info('cant start session')
			print_utf8(draw_try(os.environ['REQUEST_URI'])) 
		else:
			log.info('Yes! new session')
			
			params = process.web_params()
			params.url = url
			params.yah2fb = yah2fb
			
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
				
			descr.url = url
				
			params.descr = descr
			
			#работаем с картинками или без
			if img:
				params.is_img = True # с картинками
				log.info('With images. for url: %s' % url)
			else:
				params.is_img = False # без картинок
				log.info('Without images. for url: %s' % url)

			#запускаем сам процесс, перехватываем все неперехваченые ошибки в лог
			log.debug('url: %s Start process' % url)
			try:
				rez = process.process().do_web(params) # с картинками
			except:
				log.error('\n------------------------------------------------\n' + traceback.format_exc() + '------------------------------------------------\n')
				print_utf8(draw_error('Internal error'))
		
			else:
				log.debug('url: %s Stop process' % url)
				if rez[0] == 0:
					log.warning('url: %s Process return error' % (rez, ))
					print_utf8(draw_error(rez[1]))
					print_utf8(draw_form())
				elif rez[0] == 1:
					stat = rez[1]
					#log.info('url: %s Stat: %s' % (url, stat))
					log.info('url: %s Draw result: %s' % (url, stat.path_with_file))
					print_utf8(draw_result(stat))
					print_utf8(draw_descr(stat))
			
			log.debug('end session')
			sess.end() #завершаем сессию
	
	print_utf8(draw_footer())
	log.info('End web')

if __name__=='__main__':
	main()
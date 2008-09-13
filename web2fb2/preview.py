#!/usr/bin/python
#coding=utf-8
import os.path
import base64

import lxml.etree
import time


XSL_DIR = 'schemas'
#XSL_MAIN = 'html.xsl'
XSL_MAIN = 'FB2_2_html.xsl'


def proc( file_in, file_out):

	try:
		doc = lxml.etree.parse(file_in) #парсим fb2
		
		#преобразуем файл
		transform = lxml.etree.XSLT( lxml.etree.parse( os.path.join(XSL_DIR, XSL_MAIN) ) ) #загружаем преобразователь
		
		rez = str( transform(doc) ) #трансформируем
		
		#сохраняем картинки
		r = doc.getroot()
		img_dir = os.path.dirname(file_out)
		for bin in r.iter():
			if not bin.tag.endswith('binary'):
				continue
			
			id = bin.get('id')
			if not id:
				continue
			
			data = bin.text
			if not data:
				continue
			
			file( os.path.join(img_dir, id), 'wb').write( base64.decodestring(data) )
		
	except lxml.etree.LxmlError, er: #если что-то у нас не так в преобразовании
		print er
		er_html = """
<html>
<head>
<title>Preview Error</title>
</head>
<body>
<h1>Preview error</h1><b>xslt transformation error</b>: %s
</body>
</html>
""" % (str(er))
		
		file(file_out, 'w').write(er_html) #запишем ошибку
	
	else:
		file(file_out, 'w').write(rez) #сохраняем результат
	
if __name__ == '__main__':
	proc('in.fb2', 'rez/out.htm')
	

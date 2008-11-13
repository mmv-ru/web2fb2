#!/usr/bin/python
#coding=utf-8

from lxml import etree
import zipfile
import os
import time
import base64

XSL_DIR = 'schemas'
XSL_MAIN = 'FB2_2_xhtml.xsl'

#словарь шрфитов с по паттернам
#паттерн  pat.
#pat[0]  m  моношириный, r  обычный
#pat[1]  b  жирный, - нежирный
#pat[2]  i  наклонный, - ненаклонный

FONTS = {
	'r--':'epub_misc/fonts/LiberationSans-Regular.ttf', #обычный
	'rb-':'epub_misc/fonts/LiberationSans-Bold.ttf', #жирный
	'r-i':'epub_misc/fonts/LiberationSans-Italic.ttf', #наклонный
	'rbi':'epub_misc/fonts/LiberationSans-BoldItalic.ttf', #жирный-наклонный
	'm--':'epub_misc/fonts/LiberationMono-Regular.ttf', #обычный, моноширинный
	'mb-':'epub_misc/fonts/LiberationMono-Bold.ttf', #жирный, моноширинный
	'm-i':'epub_misc/fonts/LiberationMono-Italic.ttf', #наклонный, моноширинный
	'mbi':'epub_misc/fonts/LiberationMono-BoldItalic.ttf' #жирный-наклонный, моноширинный
}

#то что содержится в epub в файле metainfo
EPUB_METAINFO = '''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>'''

class zip(object):
	'''
	класс, для упрощения создания и заполнения zip файла
	'''
	def __init__(self, name):
		self.zip_file = zipfile.ZipFile(name, 'w')
		
	def addFile(self, name, path):
		'''
		добавить файл из файловой системы
		'''
		self.zip_file.write(path, name)
	
	def addString(self, name, string):
		'''
		добавить файл из строки
		'''
		zip_info = zipfile.ZipInfo(name)
		zip_info.date_time = time.localtime(time.time())[:6]
		self.zip_file.writestr(zip_info, string)
		
	def close(self):
		self.zip_file.close()


class epub_descr(object):
	'''
	контейнер для toc метаи-нформации (автор, название и прочее)
	'''
	def __init__(self):
		self.title = ''
		self.id = ''
		self.lang = ''
		self.type = None
		self.creator = None
		self.publisher = None

class epub_opf(object):
	"""
	класс конструирования opf файла
	"""
	def __init__(self):
		#описываем XML неймспейсы
		NAMESPACE_IDPF = "http://www.idpf.org/2007/opf"
		NAMESPACE_DC = "http://purl.org/dc/elements/1.1/"
		self.IDPF = "{%s}" % NAMESPACE_IDPF
		self.DC = "{%s}" % NAMESPACE_DC
		self.NSMAP = { None: NAMESPACE_IDPF, 'dc': NAMESPACE_DC }
		
		self.package = etree.Element( self.IDPF + "package", nsmap = self.NSMAP)
		self.package.set("version", "2.0")
		
		self.metadata = etree.SubElement(self.package, self.IDPF + "metadata")
		self.manifest = etree.SubElement( self.package, self.IDPF + "manifest", nsmap = self.NSMAP)
		self.spine = etree.SubElement( self.package, self.IDPF + "spine", nsmap = self.NSMAP)
		
	def setMeta(self, meta):
		"""
		записывает автора, название и пр.
		принимает экземпляр класс epub_meta
		"""
		#tile
		if meta.title != None:
			title = etree.SubElement(self.metadata, self.DC + "title")
			title.text = meta.title
		
		#задаем id книги
		if meta.id != None:
			self.package.set("unique-identifier", "bookid")
			identifier = etree.SubElement(self.metadata, self.DC + "identifier")
			identifier.set('id','bookid')
			identifier.text = meta.id
		
		#язык
		if meta.lang != None:
			language = etree.SubElement(self.metadata, self.DC + "language")
			language.text = meta.lang
		
		#автор
		if meta.creator:
			creator = etree.SubElement(self.metadata, self.DC + "creator")
			creator.text = meta.creator
		
		#издатель
		if meta.publisher != None:
			publisher = etree.SubElement(self.metadata, self.DC + "publisher")
			publisher.text = meta.publisher
		
		#type
		if meta.type != None:
			typ = etree.SubElement(self.metadata, self.DC + "type")
			typ.text = meta.type
		
	def addMainfestItem(self, id, href, media_type):
		"""
		добавляет элемент в секцию manifest
		
		"""
		item = etree.SubElement(self.manifest, self.IDPF + "item")
		item.set("id", id)
		item.set("href", href)
		item.set("media-type", media_type)
	
	def setSpineToc(self, id):
		"""
		установка toc
		"""
		self.spine.set('toc', id)
	
	def addSpineItem(self, id):
		"""
		добавляет элемент в секцию spine
		"""
		item = etree.SubElement(self.spine, self.IDPF + "itemref")
		item.set("idref", id)
		
	def get(self):
		'''
		возвращает то что получилось
		'''
		return etree.tostring(self.package, pretty_print=True, encoding='UTF-8', xml_declaration=True)

class epub_ncx(object):
	"""
	класс для конструирования TOC
	"""
	
	def __init__(self):
		pass
		
	def addNavPoint(self, label, src):
		pass
		
	def setId(self, id):
		pass
		
	def setTitle(self, title):
		pass

class epub_style(object):
	"""
	класс создания css
	
	"""
	def __init__(self, style_file = None):
		if style_file:
			self.style_data = file(style_file).read()
		else:
			self.style_data = ''
			
		self.use_fonts = []
	
	def __plug_font(self, font):
		
		s = """
@font-face {
	font-family: "%s";
	font-weight: %s;
	font-style: %s;
	src:url(%s);
}
""" % (
		'mono' if font[0][0] == 'm' else 'regular', 
		'bold' if font[0][1] == 'b' else 'normal', 
		'italic' if font[0][2] == 'i' else 'normal',
		font[1]
		)
		
		self.style_data += s
	
	def addFont(self, font):
		self.use_fonts.append(font)
	
	def get(self):
		#добавляем шритфы
		#создаем теги и описания к ним, отдельно для body, отдельно для pre
		mono_flag = False
		for font in self.use_fonts:
			self.__plug_font(font)
			if font[0][0] == 'm':
				mono_flag = True

		if self.use_fonts:
			data = """
body {
	font-family: 'regular';
}
"""
			self.style_data += data
		
		if mono_flag:
			data = """
pre {
	font-family: 'mono';
}
"""
			self.style_data += data
		
		
		return self.style_data
		

class epub(object):
	"""
	класс для констурирования epub
	"""
	def __init__(self, name, style = None, fonts= []):
		"""
		name - имя выходного epub файла
		style - файл стилей, который запишутся
		font_files - файлы шрифтов, которые нужно интегрировать в epub
		"""
	
		#создаем zip файл
		self.zip = zip(name)
		
		#пишем mime
		self.zip.addString('mimetype', 'application/epub+zip')
		
		#пишем metainfo
		self.zip.addString('META-INF/container.xml', EPUB_METAINFO)
		
		#создаем opf
		self.opf = epub_opf()
		
		css = epub_style(style)
		
		#пишем шрифты
		for font in fonts:
			prop, font_file = font
			self.zip.addFile('OEBPS/fonts/'+ os.path.basename(font_file), font_file)
			css.addFont((font[0], 'fonts/' + os.path.basename(font_file)))
			
		#пишем css
		self.zip.addString('OEBPS/style.css', css.get())
		self.opf.addMainfestItem('css', 'style.css', "text/css")
		
	
	def close(self):
		'''
		заканчиваем все что не закончили =)
		'''
		self.zip.addString('OEBPS/content.opf', self.opf.get())
		self.zip.close()
		
	def addContent(self, data):
		"""
		добавить файл контента (на данный момент момент только один)
		"""
		id = 'content1'
		name = 'content1' + '.xhtml'
		
		self.zip.addString('OEBPS/' + name, data)
		
		self.opf.addMainfestItem(id, name, "application/xhtml+xml")
		
		self.opf.addSpineItem(id)
	
	def addImage(self, name, data, media_type):
		"""
		добавить в epub файл -картинку
		"""
		
		self.zip.addString('OEBPS/' + name, data)
		
		self.opf.addMainfestItem(name, name, media_type)
	
	def setDescr(self, meta):
		"""
		заполнить автора, название  и пр.
		"""
		self.opf.setMeta(meta)


def descr_trans(fb2_etree):
	"""
	парсит дескрипшн и заполняет напарсеной информацией экземпляр epub_descr, который и возвращает
	"""
	descr = epub_descr()
	
	#устнавливаем пространство имен
	ns = {'m':'http://www.gribuser.ru/xml/fictionbook/2.0'}
	
	#title
	title = ' '.join( fb2_etree.xpath("/m:FictionBook/m:description/m:title-info/m:book-title/text()", namespaces = ns) )
	if title:
		descr.title =  title

	#язык
	lang = ' '.join( fb2_etree.xpath("/m:FictionBook/m:description/m:title-info/m:lang/text()", namespaces = ns) )
	if lang:
		descr.lang = lang
	
	#id
	id = ' '.join( fb2_etree.xpath("/m:FictionBook/m:description/m:document-info/m:id/text()", namespaces = ns) )
	if lang:
		descr.id = id
	

	#автор
	creators = []
	for author in fb2_etree.xpath("/m:FictionBook/m:description/m:title-info/m:author", namespaces = ns):
		creator =  ' '.join( 
			author.xpath('m:first-name/text()', namespaces = ns) + 
			author.xpath('m:middle-name/text()', namespaces = ns) +
			author.xpath('m:last-name/text()', namespaces = ns)
		)
	
		if creator:
			creators.append(creator)
	creator = '; '.join(creators)
	if creator:
		descr.creator = creator

	#жанр
	type = '; '.join( fb2_etree.xpath("/m:FictionBook/m:description/m:title-info/m:genre/text()", namespaces = ns) )
	if type:
		descr.type = type
	
	#издатель
	publisher = '; '.join( fb2_etree.xpath("/m:FictionBook/m:description/m:publish-info/m:publisher/text()", namespaces = ns) )
	if publisher:
		descr.publisher = publisher
	
	return descr

def permutations(t):
	"""
	делает все возможные комбинации перестановок элементов в списке
	например если на вход подать [1, 2] получится [[1, 2], [2, 1]]
	"""
	if len(t) == 1:
		return [t]
	else:
		rezs = []
		for i in xrange( len(t) ):
			for ost in permutations( t[:i] + t[i+1:] ):
				rezs.append( t[i:i+1] + ost )
		return rezs

def comb(lis):
	'''
	делает хитрый перебор
	делает из [[1, 2], ['x', 'y']]
	[[1, 'x'], [1, 'y'], [2, 'x'], [2, 'y']]
	ограничено только списками длинны от 1 до 3
	'''

	rez = []
	
	if len(lis) == 3:
		for x in lis[0]:
			for y in lis[1]:
				for z in lis[2]:
					rez.append([x, y, z])
	elif len(lis) == 2:
		for x in lis[0]:
			for y in lis[1]:
				rez.append([x, y])
	elif len(lis) == 1:
		for x in lis[0]:
			rez.append([x])
	
	else:
		raise ValueError
	
	return rez
		

def xpath_comb(t):
	'''
	делает все нужные переборы, и склеивает их как пути в xpath 
	'''
	
	lol = []
	
	for l in  comb(t):
		lol +=  permutations( l )
	
	return ' | '.join(  [ '//' + '//'.join(x) for x in lol] )

def do( file_in, file_out, with_fonts):
	fb2 = etree.parse(file_in) #парсим fb2
	#преобразуем файл
	transform = etree.XSLT( etree.parse( os.path.join(XSL_DIR, XSL_MAIN) ) ) #загружаем преобразователь
	epub_etree = transform(fb2)
	rez = str( etree.tostring(epub_etree, pretty_print=True, encoding='UTF-8', xml_declaration=True) )
	
	#разбираем дискрипшн
	descr = descr_trans(fb2)
	
	#определяем, какие шрифты используюется в получившейся книге
	#список шрифтов должен заполнится парами (паттерн, путь к шрифту)
	#паттерны - см. в описании FONTS
	fonts_include = []
	if with_fonts:
		pat = 'r--'
		fonts_include.append( (pat, FONTS[pat]) )
		
		ns = {'xh':'http://www.w3.org/1999/xhtml'} #определяем нейм-спейс
		
		mono = ['xh:pre'] #теги, в которых моноширинный шрифт
		ital = ['xh:i'] #теги, в которых наклонный
		bold = ['xh:b', 'xh:th', 'xh:h1', 'xh:h3', 'xh:h5'] #теги в которых жирный
		
		if epub_etree.xpath( xpath_comb([bold]), namespaces = ns):
			pat = 'rb-'
			fonts_include.append( (pat, FONTS[pat]) )
			

		if epub_etree.xpath( xpath_comb([ital]), namespaces = ns):
			pat = 'r-i'
			fonts_include.append( (pat, FONTS[pat]) )

		if epub_etree.xpath( xpath_comb([bold, ital]), namespaces = ns):
			pat = 'rbi'
			fonts_include.append( (pat, FONTS[pat]) )

		if epub_etree.xpath( xpath_comb([mono]) , namespaces = ns):
			pat = 'm--'
			fonts_include.append( (pat, FONTS[pat]) )
		
		if epub_etree.xpath( xpath_comb([mono, bold]), namespaces = ns):
			pat = 'mb-'
			fonts_include.append( (pat, FONTS[pat]) )
			
		if epub_etree.xpath( xpath_comb([mono, ital]), namespaces = ns):
			pat = 'm-i'
			fonts_include.append( (pat, FONTS[pat]) )
		
		if epub_etree.xpath( xpath_comb([mono, bold, ital]), namespaces = ns):
			pat = 'mbi'
			fonts_include.append( (pat, FONTS[pat]) )
	
	
	e = epub(file_out, 'epub_misc/style.css', fonts_include) #создаем epub

	e.setDescr(descr) #заполняем описание
	e.addContent(rez) #добавляем контент
	
	#обрабатываем картинки
	r = fb2.getroot()
	for bin in r.iter():
		
		if not str(bin.tag).endswith('binary'):
			continue
			
		id = bin.get('id')
		if not id:
			continue
			
		content_type = bin.get('content-type')
		if not content_type:
			continue
			
		data = bin.text
		if not data:
			continue
			
		e.addImage(id, base64.decodestring(data), content_type)

	e.close()

if __name__ == '__main__':
	
	do('in.fb2', 'out.zip', True)
	do('in.fb2', 'out.epub', True)
	
	


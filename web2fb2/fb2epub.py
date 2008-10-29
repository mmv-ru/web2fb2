#!/usr/bin/python
#coding=utf-8

from lxml import etree
import zipfile
import os
import time

XSL_DIR = 'schemas'
XSL_MAIN = 'FB2_2_xhtml.xsl'

EPUB_METAINFO = '''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>'''

def proc_images():
	pass

class zip(object):
	def __init__(self, name):
		self.zip_file = zipfile.ZipFile(name, 'w')
		
	def addFile(self, name, path):
		self.zip_file.write(path, name)
	
	def addString(self, name, string):
		zip_info = zipfile.ZipInfo(name)
		zip_info.date_time = time.localtime(time.time())[:6]
		self.zip_file.writestr(zip_info, string)
		
	def close(self):
		self.zip_file.close()


class epub_descr(object):
	def __init__(self):
		self.title = ''
		self.id = ''
		self.lang = ''

class epub_opf(object):
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
		#tile
		title = etree.SubElement(self.metadata, self.DC + "title")
		title.text = meta.title
		
		#задаем id книги
		self.package.set("unique-identifier", "bookid")
		identifier = etree.SubElement(self.metadata, self.DC + "identifier")
		identifier.set('id','bookid')
		identifier.text = meta.id
		
		#язык
		language = etree.SubElement(self.metadata, self.DC + "title")
		language.text = meta.lang
		
	def addMainfestItem(self, id, href, media_type):
		item = etree.SubElement(self.manifest, self.IDPF + "item")
		item.set("id", id)
		item.set("href", href)
		item.set("media-type", media_type)
	
	def setSpineToc(self, id):
		self.spine.set('toc', id)
	
	def addSpineItem(self, id):
		item = etree.SubElement(self.spine, self.IDPF + "itemref")
		item.set("idref", id)
		
	def get(self):
		return etree.tostring(self.package, pretty_print=True, encoding='UTF-8', xml_declaration=True)

class epub_ncx(object):
	def __init__(self):
		pass
		
	def addNavPoint(self, label, src):
		pass
		
	def setId(self, id):
		pass
		
	def setTitle(self, title):
		pass


class epub(object):
	def __init__(self, name, style = None, font_files = []):
	
		self.zip = zip(name)
		
		#пишем mime
		self.zip.addString('mimetype', 'application/epub+zip')
		
		#пишем metainfo
		self.zip.addString('META-INF/container.xml', EPUB_METAINFO)
		
		#пишем css
		if style:
			self.zip.addFile('OEBPS/style.css', style)
		
		#пишем шрифты
		for font_file in font_files:
			self.zip.addFile('OEBPS/fonts/'+ os.path.basename(font_file), font_file)
		
		#создаем opf
		self.opf = epub_opf()
	
	def close(self):
		self.zip.addString('OEBPS/content.opf', self.opf.get())
		self.zip.close()
		
	def addContent(self, data):
		id = 'content1'
		name = 'content1' + '.xhtml'
		
		self.zip.addString('OEBPS/' + name, data)
		
		self.opf.addMainfestItem(id, name, "application/xhtml+xml")
		
		self.opf.addSpineItem(id)
	
	def setDescr(self, meta):
		self.opf.setMeta(meta)


def do( file_in, file_out, with_fonts):
	doc = etree.parse(file_in) #парсим fb2
	#преобразуем файл
	transform = etree.XSLT( etree.parse( os.path.join(XSL_DIR, XSL_MAIN) ) ) #загружаем преобразователь
	rez = str( transform(doc) )
	file('out.xhtml', 'w').write(rez)
	
	fonts = [
		#"epub_misc/fonts/LiberationMono-Bold.ttf",
		#"epub_misc/fonts/LiberationMono-BoldItalic.ttf",
		#"epub_misc/fonts/LiberationMono-Italic.ttf",
		#"epub_misc/fonts/LiberationMono-Regular.ttf",
		"epub_misc/fonts/LiberationSans-Bold.ttf",
		"epub_misc/fonts/LiberationSans-BoldItalic.ttf",
		"epub_misc/fonts/LiberationSans-Italic.ttf",
		"epub_misc/fonts/LiberationSans-Regular.ttf",
	]
	
	e = epub(file_out, 'epub_misc/style_font.css', fonts)
	descr = epub_descr()
	e.setDescr(descr)
	e.addContent(rez)
	e.close()

if __name__ == '__main__':
	do('in.fb2', 'out.epub', True)
	
	


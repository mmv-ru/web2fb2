#coding=utf-8
import pickle
class progress(object):

	msgs = [
		'Downloading web-page',
		'Preprocessing web-page',
		'Downloading additional media',
		'Converting to fb2'
	]
	def __init__(self, file_name):
		self.file_name = file_name
		
		self.done = None
		self.url = None
		self.error = None
		self.level = 0
		
		
	def save(self):
		dump = pickle.dumps(
			{
				'url':self.url,
				'done':self.done,
				'error':self.error,
				'level': self.level
			},
			0)
			
		file(self.file_name,'w').write(dump)
		
	def load(self):
		dump = file(self.file_name,).read()
		d = pickle.loads(dump)
		self.url = d['url']
		self.done = d['done']
		self.error = d['error']
		self.level = d['level']
		
if __name__ == '__main__':
	prog = progress('tmp.dump')
	prog.url = 'http://mail.ru'
	prog.save()
	
	prog1 = progress('tmp.dump')
	prog.load()
	print prog.url
	
	
	
	
	
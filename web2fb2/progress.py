#coding=utf-8
import pickle
import time

# прогресс. информация о ходе обработки книги


class progress(object):

	#этапы обработки
	msgs = [
		'Downloading web-page',
		'Preprocessing web-page',
		'Downloading additional media',
		'Converting to fb2'
	]
	
	def __init__(self, file_name):
		self.file_name = file_name
		
		self.done = None #готово
		self.url = None #урл
		self.error = None #ошибка
		self.level = 0 #этап обработки
		self.time = time.time() #время начала обработки
		
		
	def save(self):
		"""
		сохранить прогресс в файл
		"""
		
		dump = pickle.dumps(
			{
				'url':self.url,
				'done':self.done,
				'error':self.error,
				'level': self.level,
				'time': self.time
			},
			2)
			
		file(self.file_name,'w').write(dump)
		
	def load(self):
		"""
		загрузить прогресс из файла
		"""
		
		dump = file(self.file_name,).read()
		d = pickle.loads(dump)
		self.url = d['url']
		self.done = d['done']
		self.error = d['error']
		self.level = d['level']
		self.time = d['time']
		
if __name__ == '__main__':
	prog = progress('tmp.dump')
	prog.url = 'http://mail.ru'
	prog.save()
	
	prog1 = progress('tmp.dump')
	prog.load()
	print prog.url
	
	
	
	
	
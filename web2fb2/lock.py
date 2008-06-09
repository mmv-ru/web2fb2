#!/usr/bin/python2.4
import fcntl
import os

class lock():
	lock_folder = 'temp'
	def __init__(self, f_name):
		self.f = file(os.path.join(self.lock_folder, "." + f_name), 'w')
		fcntl.flock(self.f, fcntl.LOCK_EX)
		
	def unlock(self):
		self.f.close()

if __name__ == '__main__':
	import time
	l = lock('lala')
	print 'lock'
	time.sleep(5)
	l.unlock()
	print 'unlock'
	

	

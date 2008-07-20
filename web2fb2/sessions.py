#!/usr/bin/python2.5
#coding=utf-8

import time
try:
	import sqlite3 as sqlite
except ImportError:
	import pysqlite2.dbapi2 as sqlite
import sys
import pickle

PRIORS_FNAME = 'config/priors.cfg'

class sess(object):
	def __init__(self, sess_name):
		self.CLEAN_TIME = 600 #время в секундах, после которых происходит удаление сессии из очередей и сессий
		self.WORK_CLEAN_TIME = 60 #время в секундах, после которых происходит перенос сессси из рабочей зоны в послерабочую зону
		
		self.sess_path = 'sess/sess.db' #имя файла с данными сессий
		
		self.sess = sess_name #имя сессии
		
		
		
		self.priors = eval(file(PRIORS_FNAME).read()) #размеры рабочих зон, для каждого из приоритетов
		
		#self.db_connect()
		#self.clean_up()
		#self.db_disconnect()

		
	def db_connect(self):
	
		'''
		соединяемся с БД
		'''
		self.con = sqlite.connect(self.sess_path)#, isolation_level=None)
		self.cur = self.con.cursor()
		#если че не так с структурой БД - создаем новую
		self.cur.execute(
"""CREATE TABLE IF NOT EXISTS [sessions] 
(
    [sess] TEXT NOT NULL ON CONFLICT ABORT PRIMARY KEY ON CONFLICT ABORT UNIQUE ON CONFLICT ABORT,
    [prior] INTEGER NOT NULL ON CONFLICT ABORT,
    [q_time] TEXT NOT NULL ON CONFLICT ABORT,
    [work_zone] BOOLEAN DEFAULT 0,
    [in_work] BOOLEAN DEFAULT 0,
    [after_work] BOOLEAN DEFAULT 0,
    [last_update] TEXT NOT NULL ON CONFLICT ABORT
)
""")

	def db_disconnect(self):
		'''
		отсоединяемся от БД
		'''
		self.cur.close()
		self.con.close()
	
	
	def clean_up(self):
		'''
		очистка старых сессий
		'''
		#перемещаем из рабочей зоны сессии в after_work зону
		self.cur.execute('UPDATE sessions SET work_zone = 0, after_work = 1 WHERE work_zone == 1 AND in_work = 0 AND ? - last_update > ?', (time.time(), self.WORK_CLEAN_TIME))
		self.cur.execute('DELETE FROM sessions WHERE ? - last_update > ?', (time.time(), self.CLEAN_TIME))
		self.con.commit()
	
	
	def start(self, prior):
		'''
		и... поехали
		'''
		self.db_connect()
		
		self.clean_up()
		
		#разбираемся с сессией
		rez = self.cur.execute('SELECT sess, after_work FROM sessions WHERE sess = ?', (self.sess,)).fetchone()
		if rez:
			if rez[1]: #after work 
				#перемещаем в очередь с самым высоким приоритетом
				self.cur.execute("UPDATE sessions SET prior = 0, q_time = ?, after_work = 0 WHERE sess = ?", (time.time(), self.sess))
				
			#update time
			self.cur.execute("UPDATE sessions SET last_update = ? WHERE sess = ?", (time.time(), self.sess))
		else:
			#ставим в очередь согласно приоритету
			self.cur.execute("INSERT INTO sessions (sess, prior, q_time, last_update) values(?, ?, ?, ?)", (self.sess, prior, time.time(), time.time()))
		
		
		#разбираемся с очередями
		#переносим сессии из очередей в рабочую зону
		for i in xrange(len(self.priors)):
			#вычисляем кол-во свободных мест в очереди, для данного сессий с данным приоритетом
			free = self.priors[i] - self.cur.execute("SELECT count(sess) FROM sessions WHERE work_zone == 1 AND prior == ?", (i,)).fetchone()[0]
			
			#получаем сесии из очереди
			rez = self.cur.execute("SELECT sess FROM sessions WHERE work_zone == 0 AND after_work == 0 AND prior == ? ORDER BY q_time LIMIT ?", (i, free)).fetchall()
			rez = [x[0] for x in rez]
			
			#переносим сессии в рабочую зону
			self.cur.execute("UPDATE sessions SET work_zone = 1 WHERE sess IN ('%s')" % "', '".join(rez))
			
		#и наконец находим нашу сессию и делаем ее рабочей
		self.cur.execute('UPDATE sessions SET in_work = 1 WHERE work_zone = 1 AND sess = ?', (self.sess, ))
		
		#определяем время приоритет и зону нашей сессии
		pr, q_time, in_work = self.cur.execute("SELECT prior, q_time, in_work FROM sessions WHERE sess = ?", (self.sess, )).fetchone()
		if in_work: #сессия в работе
			ret = True
		else:
			#если нет, вычисляем ее местоположение
			place = self.cur.execute('SELECT count(sess) + 1 FROM sessions WHERE work_zone = 0 AND prior = ? AND q_time < ?', (pr, q_time)).fetchone()[0]
			ret = {'place': place, 'prior': pr}

		self.con.commit()
		self.db_disconnect()
		
		return ret
	
	def end(self):
		'''
		когда мы закончили обработку...
		'''
		self.db_connect()
		self.cur.execute("UPDATE sessions SET last_update = ? WHERE sess = ?", (time.time(), self.sess)) #апдейтим время
		self.cur.execute('UPDATE sessions SET work_zone = 0, in_work = 0, after_work = 1 WHERE sess = ?', (self.sess,)) #перемещаем из рабочей зоны в послербочую
		self.con.commit()
		self.db_disconnect()

if __name__ == '__main__':
	
	command_str = sys.stdin.read()

	try:
		rez = eval(command_str)
	except Exception, er:
		sys.stdout.write(pickle.dumps(er))
	else:
		sys.stdout.write(pickle.dumps(rez))
		
	
	#s = sess('0')
	
	#s.start()
	#s.end()
	
	#s = sess('1')
	#s.start()
	
	#s = sess('2')
	#s.start()
	
	#print time.time()
	
	




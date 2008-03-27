#coding=utf-8
'''
������, ��� ������ � �������� (���-�� ��������)
'''

import random
import md5
import os
import time

class session:
	def __init__(self):
		self.SEESION_DIR = 'sess' #���� � �������
		self.MAX_SESSIONS = 1 #������������ ���������� ������
		self.CLEAN_TIME = 600 #����� ����� ������� ������ ����� ��������
		
		self.clean_up() #��������� ������ ������
		 
		self.cur_session_name = md5.new(str(random.random())).hexdigest()[:10] #���������� ��� ������
		
	def start(self):
		'''
		������� ������, ���� ������ ������ ���������� False
		'''
	
		file(os.path.join(self.SEESION_DIR, self.cur_session_name), 'w').write('') #������� �� ����� ����
		
		names = os.listdir(self.SEESION_DIR) #������� ���-�� ������ (������)
		if len(names) > self.MAX_SESSIONS: #���� ������� �����
			self._delete_file(os.path.join(self.SEESION_DIR, self.cur_session_name)) #������� ����
			return False

		return True

	def _delete_file(self, path):
		'''
		�������� �����
		'''
		try:
			os.remove(os.path.join(self.SEESION_DIR, self.cur_session_name)) #�������� ������ ����
		except OSError, er: 
			if er.errno != 2: #���� ������ ����� ��� - ������ ��� ������� ������ ����� �������
				raise er #���� ������ �����-�� ������ - ��� ������ �������

	def end(self):
		'''
		��������� ������
		'''
		self._delete_file(os.path.join(self.SEESION_DIR, self.cur_session_name))
				
	def clean_up(self):
		'''
		��������� ������ ������ - ������� �� ��������� (�������� ������ ����� ����)
		'''
		for files in os.listdir(self.SEESION_DIR): 
			if time.time() - os.path.getmtime(os.path.join(self.SEESION_DIR, files)) > self.CLEAN_TIME: #���� ���� ������� ������
				self._delete_file(os.path.join(self.SEESION_DIR, files)) #���� ��� �����

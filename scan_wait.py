#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from telepot import Bot, glance
from telepot.loop import MessageLoop
from time import sleep
import telepot
import subprocess

def handle(msg):
	content_type, chat_type, chat_id = glance(msg)
	#print('CHAT_ID : %s' % chat_id)
	if content_type == 'text':
		str = msg['text']
		temp = str.split('|')
		if len(temp) == 3 and temp[0].startswith('SCAN'):
			try:
				if temp[1] == '0' or temp[1] == '3':
					path = temp[2].replace('/volume1/video/', 'Z:\\').replace('/', '\\')
				elif temp[1] == '1':
					path = temp[2].replace('/volume1/gdrive/', 'Y:\\').replace('/', '\\')
				elif temp[1] == '2':
					path = temp[2].replace('/volume1/video/download/GoogleDrive/', 'Y:\\video\\').replace('/', '\\')
				DoScan(path)
			except Exception as e:
				print(e)

def DoScan(path):
	print('SCAN : %s' % path)

	if path.find(u'\\4K\\') != -1: section = 44
	elif path.find(u'\\[영화]\\') != -1: section = 22
	elif path.find(u'\\드라마\\') != -1: section = 45
	elif path.find(u'\\교양\\') != -1: section = 26
	elif path.find(u'\\예능\\') != -1: section = 27
	elif path.find(u'\\뉴스\\') != -1: section = 40
	else:
		print('NO SECTION')
		return
	command = '"C:\Program Files (x86)\Plex\Plex Media Server\Plex Media Scanner.exe" --scan --refresh --section %s --directory "%s"' % (section, path.encode('euc-kr'))
	print('COMMAND : %s' % command)
	my = ''
	result = subprocess.check_output (command , shell=True)
	#print('RESULT : %s \n' % result)

def wait():
	bot = telepot.Bot('576948264:AAGvEdswYSqtOeh8jAS-f-wmKvMXPAP1B64')
	me = bot.getMe()
	print(me)
	MessageLoop(bot, handle).run_as_thread()
	print ('Listening ...')
	# Keep the program running.
	while True:
		sleep(10)

wait()

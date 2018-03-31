#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import shutil
import re
import subprocess
import time, datetime

class DownloadProcess:
	# 다운로드 파일 위치
	PATH_DOWNLOAD			= '/volume1/video/download/'

	# 복사할 폴더가 2개이상일 경우 저장될 파일 위치.
	PATH_MANUAL_MOVE		= '/volume1/video/download/manual/'

	# 파일 이동 위치.
	# 카테고리 폴더가 있고 카테고리 폴더안에 콘텐츠 폴더가 있어야한다.
	# 예) 예능/무한도전, 교양/인간극장
	PATH_LIBRARY_LOCAL		= '/volume1/video/한국/'
	PATH_LIBRARY_GOOGLEDRIVE	= '/volume1/video/download/GoogleDrive/[방송중]/'


	def __init__( self ):
		self.dirList = []
		self.MakeDirList()
		self.scanDirList = []


	def MakeDirList(self):
		for path in [self.PATH_LIBRARY_LOCAL, self.PATH_LIBRARY_GOOGLEDRIVE]:
			# 카테고리
			list = os.listdir(path)

			# 콘텐츠
			for var in list:
				contentPath = os.path.join(path,var)
				contentList = os.listdir(contentPath)
				for item in contentList:
					#self.dirList[item] = os.path.join(contentPath, item)
					#print(os.path.join(contentPath, item))
					self.dirList.append( [item, os.path.join(contentPath, item)] )

	def DoProcessDownloadFile(self):
		path = self.PATH_DOWNLOAD
		list = os.listdir(path)
		for var in list:
			strLog = ''
			try:
				contentPath = os.path.join(path,var)
				if os.path.isfile(contentPath) :
					strLog += '\n다운로드 파일처리 : %s\n\n' % var
					contentPath, l = self.ChangeFilename(path, var)
					strLog += l

					## 라이브러리 폴더로 이동
					# 폴더명이 파일명에 포함되어져 있다면 이동
					moveFlag = False

					findFlag = False
					findDir = []
					#for item in self.dirList.keys():
					for item in self.dirList:
						if var.find(item[0]) != -1:
							findDir.append(item[1])
							strLog += '폴더찾음\n%s\n%s\n\n' % (contentPath, item[1])
						# 공백을 제외하여 비교. ( '나 혼자 산다' 로 나올때가 있고 '나혼자산다'로 나올때도 있다 )
						elif var.replace(' ', '').find(item[0].replace(' ', '')) != -1:
							findDir.append(item[1])
							strLog += '폴더찾음.\n%s\n%s\n\n' % (contentPath, item[1])
						elif var.replace(' ', '').replace('-','').find(item[0].replace(' ', '').replace('-','')) != -1:
							findDir.append(item[1])
							strLog += '폴더찾음. 공백/- 제외\n%s\n%s\n\n' % (contentPath, item[1])
						elif var.replace(' ', '').replace('-','').replace('시즌', '').find(item[0].replace(' ', '').replace('-','').replace('시즌', '')) != -1:
							findDir.append(item[1])
							strLog += '폴더찾음. 공백/-/시즌 제외\n%s\n%s\n\n' % (contentPath, item[1])

					# 한폴더만 선택될 때 복사한다.
					# 같은 폴더 구글에 있을때 로컬에 복사
					if len(findDir) == 2 and findDir[0].split('/')[-1] == findDir[1].split('/')[-1]:
						findDir = findDir[:-1]

					if len(findDir) == 1:
						#shutil.move(contentPath, findDir) #덮어쓰기
						strLog += '폴더로 이동\n%s\n%s\n\n' % (contentPath, findDir[0])
						shutil.move(contentPath, os.path.join( findDir[0], os.path.basename(contentPath) ) )
						moveFlag = True
						if findDir[0].find(self.PATH_LIBRARY_LOCAL) != -1:
							sendScanMessage(0, findDir[0])
					elif len(findDir) > 0:
						if not os.path.isdir(self.PATH_MANUAL_MOVE):
							os.mkdir(self.PATH_MANUAL_MOVE)
						shutil.move(contentPath, self.PATH_MANUAL_MOVE)
						moveFlag = True
						strLog += '폴더가 2개 이상 : %s\n%s\n\n' % (len(findDir), contentPath)
					if moveFlag: continue

					## 다운로드내 폴더
					list = os.listdir(self.PATH_DOWNLOAD)
					for item in list:
						temp = os.path.join(self.PATH_DOWNLOAD, item)
						if os.path.isdir(temp) and contentPath.find(item) != -1:
							strLog += '파일이동. 다운로드내 폴더\n%s\n%s\n\n' % (contentPath, temp)
							shutil.move(contentPath, os.path.join(temp, os.path.basename(contentPath)))
							moveFlag = True
							break
					if moveFlag: continue


					## 라이브러리 폴더가 없다.
					# 폴더생성. 폴더명 : 확장자만 제외
					temp = var.split('.')
					if len(temp) == 1:
						newFolder = temp[0] + '_'
					else:
						newFolder = '.'.join(temp[:-1])
					newFolderPath = os.path.join(path,newFolder)
					if not os.path.isdir(newFolderPath):
						strLog += '다운로드 폴더에 새폴더 생성\n%s\n\n' % newFolderPath
						os.mkdir(newFolderPath)
					strLog += '파일이동. 새폴더\n%s\n%s\n\n' % (contentPath, newFolderPath)
					shutil.move(contentPath, newFolderPath)

			except Exception as e:
				print(e)
				strLog = '에러\n' + strLog
			finally:
				if strLog is not '': log(strLog)


	def DoDeleteGoogleSyncCompletedFile(self):
		GOOGLE_DRIVE_ROOT = '/volume1/video/download/GoogleDrive/'
		PLEXDRIVE_ROOT = '/volume1/gdrive/video/'
		# 폴더, has category = 'Y', delete folder = 'Y'
		SYNC_LIST = [
			['/volume1/video/download/GoogleDrive/[방송중]/', True, False],
			['/volume1/video/download/GoogleDrive/upload/', False, True],
			['/volume1/video/download/GoogleDrive/[영화]/', True, True]
		]
		str = ''
		total = 0
		for item in SYNC_LIST:
			path = item[0]
			gdrivePath = path.replace(GOOGLE_DRIVE_ROOT, PLEXDRIVE_ROOT)

			if item[1]:
				firstDepthlist = os.listdir(path)
			else:
				firstDepthlist = path.split('/')[-2:-1]
				path = GOOGLE_DRIVE_ROOT

			for firstDepth in firstDepthlist:
				firstDepthpath = os.path.join(path, firstDepth)
				contentFolderlist = os.listdir(firstDepthpath)
				count = 0
				for contentFolderName in contentFolderlist:
					contentFolderFullpath = os.path.join(firstDepthpath,contentFolderName)
					#print(contentFolderFullpath)
					fileNameList = os.listdir(contentFolderFullpath)
					for filename in fileNameList:
						contentFileFullpath = os.path.join(contentFolderFullpath, filename)
						gdriveFileFullpath = contentFileFullpath.replace(item[0], gdrivePath)
						if os.path.isfile(gdriveFileFullpath):
							# gdrive 에도 파일이 있다.
							# 동기화가 끝
							log('동기화 완료 파일삭제.\n%s\n' % (contentFileFullpath))
							os.remove(contentFileFullpath)
							######
							# 로컬에 서버가 있으면. 바로 스캔
							#self.DoScanLibrary(True, gdriveFileFullpath)
							# 방송중만
							if item[2] == False: sendScanMessage(1, os.path.join(gdrivePath, firstDepth, contentFolderName))
						else:
							count += 1
							print('MOVIE NOT SYNC : %s' % (gdriveFileFullpath))
				total += count
				if count != 0: str += '동기화 대기 : %s\n%s\n' % (count, firstDepthpath)

			# 파일이 없는 폴더 삭제
			if item[2]:
				for firstDepth in firstDepthlist:
					firstDepthpath = os.path.join(path, firstDepth)
					contentFolderlist = os.listdir(firstDepthpath)
					for contentFolderName in contentFolderlist:
						contentFolderFullpath = os.path.join(firstDepthpath,contentFolderName)
						fileNameList = os.listdir(contentFolderFullpath)
						if len(fileNameList) == 0:
							log('싱크 폴더 삭제.\n%s\n' % contentFolderFullpath)
							os.rmdir(contentFolderFullpath)
							if item != SYNC_LIST[1]: sendScanMessage(2, contentFolderFullpath)
		str += '동기화 대기 [전체] : %s\n' % (total)
		if total != 0: log(str)
		#else: log('동기화 파일 없음')

	def DoScanLibrary(self, isGoogle, path):
		# /volume1/@appstore/Plex Media Server/Plex Media Scanner --scan --refresh --section 27
		temp = path.split('/')
		folder = '/'.join(temp[:-1])
		#print(folder)
		command = '/volume1/@appstore/Plex Media Server/Plex Media Scanner --scan --refresh --section 27 --directory \"%s\"' % folder
		#result = subprocess.check_output (command , shell=True)
		#print(result)


	def MoveToGoogleSyncDir(self):
		list = [['/volume1/video/한국/교양/', '/volume1/video/download/GoogleDrive/[방송중]/교양/', 90],
			['/volume1/video/한국/예능/', '/volume1/video/download/GoogleDrive/[방송중]/예능/', 90],
			['/volume1/video/한국/뉴스/', '/volume1/video/download/GoogleDrive/[방송중]/뉴스/', 70]]
		now = datetime.datetime.now()
		for item in list:
			folderNameList = os.listdir(item[0])
			for folderName in folderNameList:
				folderPath = os.path.join(item[0], folderName)
				fileNameList = os.listdir(folderPath)
				for fileName in fileNameList:
					fileFullPath = os.path.join(folderPath, fileName)
					ctime = datetime.datetime.fromtimestamp(os.path.getctime(fileFullPath))
					timedelta = now - ctime
					if timedelta.days > item[2]:
						strLog = '싱크 폴더로 이동 : %s 일\n%s\n' % (timedelta.days, fileFullPath)
						targetFolder = os.path.join(item[1], folderName)
						if not os.path.isdir(targetFolder):
							strLog += '폴더 생성\n%s\n' % targetFolder
							os.mkdir(targetFolder)
						else:
							strLog += '폴더 있음\n%s\n' % targetFolder
						targetFile = os.path.join(targetFolder, fileName)
						shutil.move(fileFullPath, targetFile)
						sendScanMessage(3, os.path.dirname(fileFullPath))
						strLog += '이동 : %s\n' % targetFile
						log(strLog)

	def ChangeFilename(self, filepath, filename, filemove=True):
		try:
			filenamepath = os.path.join(filepath,filename)
			strLog = ''
			## 파일명 변경

			p = re.compile('[sS]\d+[eE]\d+')
			m = p.search(filename)
			if m:
				return filenamepath, ''

			# 에피소드 넘버 검사
			p = re.compile('\.E\d+')
			m = p.search(filename)
			if m is not None:
				# 천회 이상인 경우 에피소드 번호 앞에 S1 추가
				if m.end() - m.start() >= 6:
					newfilenamepath = filenamepath.replace(filename[m.start()+1:m.end()], 'S1'+filename[m.start()+1:m.end()])
					strLog += '파일명 변경. 천회이상\n%s\n%s\n\n' % (filenamepath, newfilenamepath)
					if filemove: shutil.move(filenamepath, newfilenamepath)
					filenamepath = newfilenamepath

			#회차 정보가 없음. 날짜를 180303 => S18E0303
			else:
				p = re.compile('\.\d+\.')
				m = p.search(filename)
				if m is not None:
					start = m.start()+1
					end = m.end()-1
					if end - start == 6 and filename[start] == '1': #날짜체크
						temp = 'S%sE%s' % (filename[start:start+2], filename[end-4:end])
						newfilenamepath = filenamepath.replace(filename[start:end], temp)
						strLog += '파일명 변경. 회차정보 없음\n%s\n%s\n\n' % (filenamepath, newfilenamepath)
						if filemove: shutil.move(filenamepath, newfilenamepath)
						filenamepath = newfilenamepath

			# 에피소드 제외 3~4자리 숫자가 포함되면 시즌으로 인식함.
			p = re.compile('(.*?)[^0-9a-z](?P<season>[0-9]{1,2})(?P<ep>[0-9]{2})([\.\-][0-9]+(?P<secondEp>[0-9]{2})([ \-_\.]|$)[\.\-]?)?([^0-9a-z%]|$)')
			## whackRx = ['([hHx][\.]?264)[^0-9]', '[^[0-9](720[pP])', '[^[0-9](1080[pP])', '[^[0-9](480[pP])']
			findList = p.findall(filename)
			newfile = os.path.basename(filenamepath)

			for temp in findList:

				str = temp[1] + temp[2]
				if newfile.upper().find('E'+str) != -1: continue
				elif str == '720' and newfile.upper().find(str+'P') != -1: continue
				elif str == '1080' and newfile.upper().find(str+'P') != -1: continue
				elif str == '480' and newfile.upper().find(str+'P') != -1: continue
				elif str == '264' and newfile.upper().find('H'+str) != -1: continue
				elif str == '264' and newfile.find('x'+str) != -1: continue
				else: newfile = newfile.replace(str, 'x%s' % str)

			if newfile != os.path.basename(filenamepath):
				target = os.path.join(os.path.dirname(filenamepath), newfile)
				strLog += '파일명변경. 숫자포함\n%s\n%s\n\n' % (filenamepath, target)
				if filemove: shutil.move(filenamepath, target)
				filenamepath = target
			return filenamepath, strLog
		except Exception as e:
			print(e)

	def ChangeFolder(self, path, filemove=False):
		#print(path)
		list = os.listdir(path)
		for item in list:
			temp = os.path.join(path, item)
			if os.path.isdir(temp):
				self.ChangeFolder(temp)
			else:
				ret1, ret2 = self.ChangeFilename(path, item, filemove)
				if ret2 is not '': print(ret2)


def log(str):
	print(str)
	sendTelegram(str)

def sendTelegram(str):
	#command = 'curl --data-urlencode text=\"%s\" https://api.telegram.org/bot255095157:AAEOhrQRv5vY6AFpeEQbQBVQhrV9nyuGHpo/sendMessage?chat_id=186485142' % str
	command = 'curl --data-urlencode text=\"%s\" https://api.telegram.org/bot255095157:AAEOhrQRv5vY6AFpeEQbQBVQhrV9nyuGHpo/sendMessage?chat_id=-1001387651151' % str
	result = subprocess.check_output (command , shell=True)

def sendScanMessage(type, str):
	text = 'SCAN|%s|%s' % (type, str)
	command = 'curl --data-urlencode text=\"%s\" https://api.telegram.org/bot255095157:AAEOhrQRv5vY6AFpeEQbQBVQhrV9nyuGHpo/sendMessage?chat_id=-1001387651151' % text
	result = subprocess.check_output (command , shell=True)
	#print(result)
	print(str)



def main():
	dp = DownloadProcess()

	argLen = len(sys.argv)
	if len(sys.argv) > 1:
		path = sys.argv[1]
		filemove = False
		if ( len(sys.argv) == 3 and sys.argv[2] == 'True'): filemove = True
		dp.ChangeFolder(path, filemove)
	else:
		dp.DoProcessDownloadFile()
		dp.DoDeleteGoogleSyncCompletedFile()
		dp.MoveToGoogleSyncDir()


main()

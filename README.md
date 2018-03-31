
# PLEX 라이브러리 관리

얼마 전 PLEX 서버를 Synology에서 NUC(Windows10)로 변경했습니다. 메타만 옮기는 작업이 여의치 않아 하는 김에 라이브러리 폴더도 싹 정리하고 대충 만들어 썼던 스크립트도 python으로 변경했습니다. 데이터가 20테라 정도인데 새로 스캔하는데 그다지 오래 걸리지는 않은 것 같습니다. NUC에서 돌리니 빠릿빠릿해서 좋네요. 영상 관련된 것은 모두 옮길 생각입니다.


하여튼 새로 정리하면서 알게 된 내용들을 까먹을까 봐 정리도 하고 python 코드 중심으로 제 방식을 소개해드리고자 합니다. 사용 환경은 모두 다를 테니 참고하셔서 직접 수정후 사용하시기 바랍니다.

### 사용환경
> 동영상 저장소 : Synology / 구글 GSuite 무제한
> #### Synology
> - 다운로드 : Download Station RSS 연동
> - 구글 업로드 : Cloud Sync 이용
> - 구글 GSuite 연동 : plexdrive 5.0
>
> #### NUC (Windows10)
> - PMS : Windows10 (pass user)
> - 나스 연결 : Windows 네트워크 드라이브 연결
> - 구글 연결 : raidrive 읽기 전용

##### 동영상 관리 방식

1. Synology 다운로드 스테이션을 이용하여 거의 모든 영상 파일을 받습니다. 주로 NEXT 릴입니다.
2. 다운로드 폴더 한곳에서만 받으며 스크립트가 매분마다 실행되면서 이 파일들을 처리합니다.
3. 지인들이 자주 보는 영상은 주로 NAS에 저장하며, 재생 빈도가 낮은 파일은 구글에 저장합니다.
4. 구글 업로드가 끝난 파일은 NAS에서 삭제하고, 구글 경로가 반영되도록 PMS 라이브러리 스캔을 해줍니다.
5. NAS 용량 확보를 위해 일정 기간이 지난 파일은 구글에 자동으로 업로드해주며, 이 파일들 역시 업로드 완료 후 NAS에서 삭제 / PMS 스캔을 해줍니다.
6. 이 모든 로그는 텔레그램으로 알려줍니다.

사실 PMS를 Windows 옮기고 나니 구글에 있는 영상 재생도 그리 오래 걸리지는 않아서 모두 옮기려고 했는데, 혹시나 하는 마음에 NAS에도 같이 저장하도록 했습니다.

최대한 자동화 시켰으며, 구글 업로드 시 바로 스캔되는 게 특징입니다.
참고로 스캔은 Windows10에서 성공했고, Synology는 한번 해보고 안되길래 자세히 살펴보지는 않았습니다. 비슷할테니 고수분이 해결해주시리라 생각되네요.


---
### 스케줄러 등록
<pre>
su - postgres -c 'psql -U postgres -d download -c "delete from Download_queue where status in ('5','7','8') or (status  = 101 and total_size = current_size)"'
python /volume1/homes/soju6jan/python/download_process.py
</pre>

제어판 > 작업 스케줄러 위 스크립트가 매분마다 실행되도록 등록합니다.

첫 줄은 많이들 쓰실 텐데, 다운로드 스테이션에서 완료된 항목을 삭제하는 명령입니다.
보통 where 문을  status in ('5','7','8') 만 사용하는데 저는 or (status  = 101 and total_size = current_size)를 추가하였습니다. 이 문장이 없으면 다운로드 스테이션에서 '완료'에서 '에러'로 변경되는 항목이 나타나는데, 이는 SQL이 커밋 되기 전에 파일이 이동해버려서 그런 것 같습니다. 이미 완료되었고 이동했기 때문에 다운로드 정상적으로 끝난 상태입니다.

두 번째 줄은 python 코드를 실행하라는 명령입니다. 자신의 환경에 맞게 파일을 위치시키고 경로로 변경하시면 됩니다.
download_process.py 코드를 기반으로 설명드릴 예정입니다.

---

### PLEX의 TV 쇼 스캔 방법

 가장 문제가 되는 게 에피소드 넘버링입니다. 응답하라 1988이 포함된 파일이 왜 19시즌 88화 인식하는지 먼저 설명드리겠습니다.

 PLEX 라이브러리를 추가할 때 보통 스캐너를 선택하는 항목 자체가 없고 에이전트만 선택하실 겁니다. 이는 내부적으로 TV 쇼 스캐너가 Plex Series Scanner 하나이기 때문에 화면에 표시되지 않은 거고, 스캐너도 추가할 수는 있습니다.

![nhg8xmax](https://i.imgur.com/E03pBhB.png)
<스캐너 목록>

Plex Series Scanner 파일 위치는 C:\Program Files (x86)\Plex\Plex Media Server\Resources\Plug-ins-1046ba85f\Scanners.bundle\Contents\Resources\Series\Plex Series Scanner.py입니다. (Plug-ins 뒤는 버전마다 다릅니다)

> ※참고 : 스캐너 추가 방법
> 이 파일을 C:\Users\[사용자]\AppData\Local\Plex Media Server\Scanners\Series 폴더 생성 후 화면에 나올 이름으로 변경하시고 복사하면 위의 스샷처럼 스캐너 파일도 선택할 수가 있습니다.

이 파일이 에피소드 파일명을 기준으로 시즌과 에피소드 넘버를 결정하는데 파일 내용 중 다음과 같은 정규식 표현이 나옵니다
<pre>
episode_regexps = [
    '(?P<show>.*?)[sS](?P<season>[0-9]+)[\._ ]*[eE](?P<ep>[0-9]+)[\._ ]*([- ]?[sS](?P<secondSeason>[0-9]+))?([- ]?[Ee+](?P<secondEp>[0-9]+))?', # S03E04-E05
    '(?P<show>.*?)[sS](?P<season>[0-9]{2})[\._\- ]+(?P<ep>[0-9]+)',                                                            # S03-03
    '(?P<show>.*?)([^0-9]|^)(?P<season>(19[3-9][0-9]|20[0-5][0-9]|[0-9]{1,2}))[Xx](?P<ep>[0-9]+)((-[0-9]+)?[Xx](?P<secondEp>[0-9]+))?',  # 3x03, 3x03-3x04, 3x03x04
    '(.*?)(^|[\._\- ])+(?P<season>sp)(?P<ep>[0-9]{2,3})([\._\- ]|$)+',  # SP01 (Special 01, equivalent to S00E01)
    '(.*?)[^0-9a-z](?P<season>[0-9]{1,2})(?P<ep>[0-9]{2})([\.\-][0-9]+(?P<secondEp>[0-9]{2})([ \-_\.]|$)[\.\-]?)?([^0-9a-z%]|$)' # .602.
  ]
....
just_episode_regexs = [
    '(?P<ep>[0-9]{1,3})[\. -_]*of[\. -_]*[0-9]{1,3}',       # 01 of 08
    '^(?P<ep>[0-9]{1,3})[^0-9]',                           # 01 - Foo
    'e[a-z]*[ \.\-_]*(?P<ep>[0-9]{2,3})([^0-9c-uw-z%]|$)', # Blah Blah ep234
    '.*?[ \.\-_](?P<ep>[0-9]{2,3})[^0-9c-uw-z%]+',         # Flah - 04 - Blah
    '.*?[ \.\-_](?P<ep>[0-9]{2,3})$',                      # Flah - 04
    '.*?[^0-9x](?P<ep>[0-9]{2,3})$',                       # Flah707
    '^(?P<ep>[0-9]{1,3})$'                                 # 01
  ]
....
</pre>

위 정규식을 사용한 코드를 보면 episode_regexps으로 먼저 찾아보고, 그다음에 just_episode_regexs로 에피소드 번호를 찾습니다. 가장 정확한 것은 S1E23 같은 표현인데 다운로드한 릴은 보통 E23 만 있기에, episode_regexps에서 찾을 수 없고 just_episode_regexs에서 찾게 됩니다.

문제가 되는 파일명은 차라리 just_episode_regexs에서만 찾으면 좋을 텐데, episode_regexps 마지막 항목에서 걸려버리기 때문에 이상한 번호로 매치되게 됩니다. 또, E23으로 단독으로 사용할 경우에는 'E'가 아무 의미 없습니다.

##### 문제가 되는 경우
1. 천회가 넘어갈 때
  just_episode_regexs 을 보면 {1,3}, {2,3} 등 3으로 끝나는데 이는 세 자리 숫자만 인식하라는 겁니다.  E1000 앞에 S1을 붙이면 됩니다. 스캐너를 고치는 거라면 {1,4} 혹은 {2,4}으로 변경하면 아마도 인식할 겁니다.

2. 에피소드 번호가 없을 때
  3~4자 숫자의 경우 뒤의 두 자리는 에피 번호 앞의 한, 두 자리는 시즌 번호로 인식하고, 파일의 처음이나 끝의 한, 두 자리는 에피로 인식하지만 5자 이상의 숫자는 인식하지 못합니다. 보통 방송일이 있기에 180320 의 숫자 6자리를 S18E0320으로 변경해줍니다.

3. 파일명에 포함된 3~4자리 숫자로 인해 이상한 번호로 매칭 될 경우
  episode_regexps 마지막 항목에 걸리지 않도록 미리 검사하여 숫자 앞에 특정 문자를 붙입니다

새로운 스캐너를 추가하여 국내 방송용으로 사용하면 더 간단할 텐데, 혹시 모를 side effect가 염려되기도 하고 이제껏 써왔던 방식이라 파일명을 변경하려고 합니다.


>※참고: Windows에서 라이브러리 폴더가 있는데 Plex에서 나오지 않을 경우
> Synology에서와는 다르게 폴더안에 정상 파일과 인식 못하는 파일이 같이 있을 때, 아예 Plex에 등록 안되는 문제가 있어서 확인해 봤더니, 스캐너가 뻗는(?) 문장이 있었습니다.
>
> <pre>
> if done == False:
>          print "Got nothing for:", file
> </pre>
> Plex Series Scanner.py 338라인이며 이 2문장 앞에 #을 넣어주시면, 정상 파일은 스캔이 이루어집니다.

---

### 파일명 변경
##### 코드
```
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
```
####

ChangeFilename 함수가 파일명 변경 역할을 합니다. 위에서 설명드린 것처럼 천회가 넘어갈 경우 S1을 넣고, 날짜만 있는 경우 S18E0328 형식으로 변경합니다. 3~4자리 숫자는 x를 붙여서 스캐너가 인식하지 못하게 변경합니다.


##### 기존파일명 일괄 변경
````
python download_process.py [폴더명]  --> 실제 변경은 안되고 어떻게 변경되는지만 print됩니다.
python download_process.py [폴더명] True --> 실제 변경

````

![2018-03-31 21;07;37](https://i.imgur.com/z86TEhS.png)

---
### 라이브러리 폴더 이동

사용환경이 모두 다를테니 대략적인 흐름만 파악하시고, 환경에 맞게 변경하셔야합니다.

 1. 로컬 폴더명을 리스트화 합니다.
 2. 구글의 폴더명을 리스트화 합니다.
 3. 파일명에 리스트된 폴더명이 포함되어져 있는지 검사합니다.
 3-1. 간혹 파일명의 공백 위치가 바뀌어서 나오기 때문에 공백을 제거하고 검사합니다.
 3-2. 같은 이유로 '-' , '시즌' 문자를 제거해서 검사합니다.
 3-3. 포함되어져 있다면 이동할 경로를 저장합니다.
 3-2. 중복될 수 있기 때문에 하나를 찾더라도 나머지 모든 폴더를 검사합니다.
 4. 라이브러리 폴더명을 찾을 경우
 4-1. 하나를 찾으면 바로 폴더로 이동
 4-2. 2개를 찾으면 폴더명이 같은 지 검사하여 일치하면 첫번째 폴더로 이동
   (같은 컨텐츠를 로컬에도 저장하고, 구글에도 저장한 경우입니다)
 4-4. 3개 이상을 찾으면 특정폴더로 이동 (PATH_MANUAL_MOVE)
  예) 시그널, 하트시그널 -> 이런 경우는 이상한 폴더로 가는 것 보다 수동으로 정리하는게 좋습니다.
 5. 라이브러리 폴더명을 못 찾은 경우에는 PATH_DOWNLOAD 안의 폴더들을 검사해서 파일명에 포함되어져 있다면 그 폴더로 이동합니다. (라이브러리화는 시키지 않고 모을때 사용합니다.)
 6. 마지막의 경우 폴더를 하나 만들고 파일을 이동합니다.
 7. 라이브러리 폴더로 이용할 경우 적절한 스캔명령을 전달합니다.

관련함수 : DoProcessDownloadFile()

---
### 구글 싱크 관련
저는 GSuite 무제한을 사용하고 있습니다.
Google Drive과 연결 방법은 많은데 제가 쓰고 있는 방법을 소개합니다.

 - Synology <-> Google Drive
업로드는 Cloud Sync를 사용하고, 읽기전용인 plex-drive 5.0을 사용하고 있습니다.

 - Windows10 <-> Google Drive
PMS에서는 raidrive를 읽기전용으로 마운트하여 사용하고 있습니다.
따로, DriveFileStream도 사용하고 있으나 raidrive보다 느리것 같더군요. NetDrive도 비슷할 거라 생각합니다. 다만 raidrive를 쓰기 모드에서는 텍스트 파일이 여거개 생기는 등의 문제가 있었는데  환경마다 다를것으로 생각됩니다.


#### 파일 싱크완료 타이밍
이 시점을 알아야 파일 삭제와 라이브러리 스캔을 할 수 있습니다.

- 업로드 폴더내의 파일을 모두 탐색합니다.
- 이 파일이 업로드 완료될 경우 plexdrive를 통해 접근 가능 할때, 이 파일은 업로드 완료된 것으로 판단합니다.

- 파일을 삭제하고 스캔명령을 채널에 noti합니다.

관련함수 :  DoDeleteGoogleSyncCompletedFile()




#### 특정 기간이 지난 파일 구글로 이동
관련함수 : MoveToGoogleSyncDir
```
list = [['/volume1/video/한국/교양/', '/volume1/video/download/GoogleDrive/[방송중]/교양/', 60],
  ['/volume1/video/한국/예능/', '/volume1/video/download/GoogleDrive/[방송중]/예능/', 60],
  ['/volume1/video/한국/뉴스/', '/volume1/video/download/GoogleDrive/[방송중]/뉴스/', 10]]
```
source path, target path, days 형태입니다.
source path에 있는 파일을 Cloud Sync에 설정된 target path로 days을 넘은 파일을 이용하는 의미입니다.



---
### 라이브러리 스캔을 위한 통신
Synology 와 Windows10 통신
여러가지 방법이 있겠으나 저는 간단히 텔레그램 채널을 통하도록 했습니다.
Windows10에서 NAS를 네트워크 연결 했기 때문에, NAS에 저장하더라도 실시간 스캔이 이루어지지 않습니다.

#### Plex 스캐너 문제
- PMS에서 스캐너를 실행할 경우 (라이브러리 파일 스캔) 하나의 instance만 실행됩니다.
- 이는 드라마를 스캔하고 있을 때 예능을 스캔하자면 드라마를 취소하거나 끝날때까지 기다려야 합니다.
- 가끔 하는 일 없이 한참을 멈춰있는 경우가 발생합니다. CPU 사용율은 0%로 아무 것도 안하지만 결국 끝나긴 하더군요.
- 수동으로 파일을 삭제할 때는 대비해서 하루에 한번 정도 파일을 스캔하도록 했습니다.


#### 텔레그램 봇
download_process는 따로 모듈을 쓰지않고 curl을 이용하도록 했습니다. 봇 토큰과 채널의 chat_id를 변경해주세요
```
command = 'curl --data-urlencode text=\"%s\" https://api.telegram.org/bot255095157:AAEOhrQRv5vY6AFpeEQbQBVQhrV9nyuGHpo/sendMessage?chat_id=-1001387651151' % str
```

1. 두 개의 텔레그램 봇을 만듭니다.
2. 채널을 생성합니다.
2-1. chat_id를 얻어야 합니다. scan_wait 12라인 주석을 풀고 실행한 후, 채널에 메시지를 입력하며 현재 채널의 id가 나옵니다.
3. 봇 2개를 채널에 관리자로 등록합니다.
4. 하나의 봇은 로그를 전송하는데 사용합니다. 2-1에서 얻은 채널의 chat_id를 넣어주어야합니다.
5. 다른 하나의 봇은 채널 메시지를 대기하는 데 사용합니다.
6. NAS에서 스캔이 필요한 경우, 스캔명령어를 채널에 보냅니다.
7. Windows에서는 스캔명령이 왔을 때, 적절한 라이브러리 section을 탐색하여 실제 명령을 실행합니다.



---
### PMS의 스캔 대기 (scan_wait.py)
 - telepot 모듈이 설치되어 있어야 합니다.
  ```pip install telepot ```

 - 실행
  ```python scan_wait.py ```

 - 코드 설명
   + def handle(msg) : SCAN 명령을 파싱합니다. download_process 쪽에서 넘겨준 path를 로컬에 맞는 경로로 변경하고 DoScan() 함수를 호출합니다.
   + def DoScan(path) : 경로에 맞는 section값을 찾고 스캐너를 실행합니다.
   + def wait() : 봇 토큰을 넣어줍니다.

 - 적용방법
   자신의 봇 토큰을 넣어주고. 전달받은 NAS 경로에 대응하는 로컬 경로로 변경해줍니다. 다시 스캐너에 필요한 section 값을 찾아서 실행하면 됩니다.

 - 코드
  ```
  #!/usr/bin/env python
  # -*- coding: UTF-8 -*-

  from telepot import Bot, glance
  from telepot.loop import MessageLoop
  from time import sleep
  import telepot
  import subprocess

  def handle(msg):
  	content_type, chat_type, chat_id = glance(msg)
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
  ```
---
### section 값 얻는 법
1. section 값을 얻기를 원하는 라이브러리 스캔합니다.
2. 스캔이 시작되면 로그파일을 메모장 같은 TEXT Viewer로 엽니다
  ```로그파일 위치 : C:\Users\soju6\AppData\Local\Plex Media Server\Logs\Plex Media Scanner.log```
3. 4번째 줄에 스캐너 실행 명령어에 section 번호가 표시되어 있습니다.
  ```
  Mar 31, 2018 20:45:50.980 [10424] INFO - Plex Media Scanner v1.12.1.4885-1046ba85f - Microsoft PC x64 - build: windows-i386 - GMT 09:00
  Mar 31, 2018 20:45:50.981 [10424] INFO - Windows version: 6.2 (Build 9200), language ko-KR
  Mar 31, 2018 20:45:50.981 [10424] INFO - 8 2592 MHz processor(s): Architecture=0, Level=6, Revision=24067 Processor Identifier=Intel64 Family 6 Model 94 Stepping 3, GenuineIntel
  Mar 31, 2018 20:45:50.981 [10424] DEBUG - "C:\Program Files (x86)\Plex\Plex Media Server\Plex Media Scanner.exe" --scan --refresh --section 22
  ```



---


### 스샷
- 구글에 업로드 후 라이브러리 등록
  + 다운로드 후 구글 싱크 폴더로 이동
  ![034oi5ec](https://i.imgur.com/KN9cf6v.png)
  + 6분후 업로드 완료. 파일 삭제하고 스캔 시작 명령 전달
  ![969n5z8e](https://i.imgur.com/vzDHUNa.png)
  + scan_wait에서 스캐너 실행
  ![qlpot1sn](https://i.imgur.com/Y3vf37P.png)
  + 스캔 수행
  ![osborm11](https://i.imgur.com/mv4yQx3.png)
  + PlexPy 라이브러리 등록 noti
  ![gju8qfyh](https://i.imgur.com/KDDmZlg.png)

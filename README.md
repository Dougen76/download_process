
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

#### 동영상 관리 방식

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

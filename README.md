# personalColor

### 나의 컬러는? - 퍼스널 컬러 웹페이지

https://tintycolor.com

- 앱 소개 페이지, 톤별 결과 공유 페이지(`/r/<톤ID>`), 개인정보처리방침(`privacy.html`), 이용약관(`terms.html`)
- 호스팅: Netlify (master 푸시 시 자동 배포), DNS: Cloudflare
- 예전 주소 `personalcolorotest.netlify.app`은 tintycolor.com으로 301 이동. 단, 앱 링크 검증(`/.well-known/*`)과 `app-ads.txt`는 예전 주소에서도 그대로 제공 (`_redirects`)
- 공유 페이지·OG 이미지 생성: `python3 tools/make_og.py` (틴티 그림은 `tools/tinty.py`)
- 개인정보처리방침을 고치면 앱의 `LegalDocuments.kt`도 같은 내용으로 고친다

<br>
이전 버전(React Native) : https://github.com/JungWooGeon/personal_color_app
<br>
최신 버전(Android) : https://github.com/JungWooGeon/PersonalColorAndroid

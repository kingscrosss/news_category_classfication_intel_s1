# 페이지를 클릭해야만 나오는 페이지, 스크롤을 내려야만 나오는 페이지 다양하기 때문에
# 크롤링하는 여러가지 방법을 배워야한다.

# [브라우저를 켜야만 띄우는 사이트를 크롤링 하는 방법]
# selenium webdriver: 크롬으로 들어가 chromedriver 검색 후 크롬 설정에서 버전 확인 후 맞는 프로그램 다운
#                   : 설치 x, 폴더에 add하지 말고
# => 이거 업뎃하면서 바껴서 필요 없어짐 아래 주소 참조
# Options 문제 해결법: https://youngkdevlog.tistory.com/57

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
import re
import time
import datetime

# 크롤링 하려는 페이지에 들어가 숫자 페이지 클릭하여 주소에 ~~page=1 되있는걸로 복사해옴
url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=100#&date=%2000:00:00&page=1'
options = ChromeOptions()
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
options.add_argument('user-agent=' + user_agent)    # 브라우저 아니면 응답 안 하니까...
options.add_argument("lang=ko_KR")
# options.add_argument('headless')      # 브라우저가 열리긴하는데 눈에 안 보이게 하는 역할, 이걸 안 하면 브라우저가 잠깐 떴다 사라짐
                                        # 크롤링하는덴 필요하진 않지만 우린 잘 작동하는지 확인하기 위해서 주석처리 해놓을거임.
# options.add_argument('window-size=1920x1080') # 윈도우 사이즈
# options.add_argument("disable-gpu")
# options.add_argument("--no-sandbox")      # 리눅스에서 사용

# 크롬 드라이버 최신 버전 설정
service = ChromeService(executable_path=ChromeDriverManager().install())

# chrome driver
driver = webdriver.Chrome(service=service, options=options)  # <- options로 변경

category = ['Politics', 'Economic', 'Social', 'Culture', 'World', 'IT']
# pages = [146, 328, 461, 75, 117, 72 ]   # 카테고리 별 마지막 페이지
pages = [110, 110, 110, 75, 110, 72 ]   # 세션 개수 조절
# 각 카테고리 별 섹션의 개수가 다르면 많은 쪽으로 답이 몰리기 때문에 학습에 문제가 된다.
# EX) 소셜은 99개인데 IT는 1개일 때 둘만 비교할 때 그냥 무조건 소셜이라고 답하면 정답률은 99퍼가 되니까...

# * Xpath
# 크롤링 할 곳 들어가서 f12-요소선택-선택된HTML우클릭 복사 Xpath 복사
# Xpath는 유니크해 요소마다 다 다른 값을 갖는다.
# //*[@id="section_body"]/ul[1]/li[1]/dl/dt[2]/a    <- 요런식으로...
# //*[@id="section_body"]/ul[1]/li[2]/dl/dt[2]/a
# ...
# //*[@id="section_body"]/ul[2]/li[1]/dl/dt[2]/a
# ...
# //*[@id="section_body"]/ul[4]/li[5]/dl/dt[2]/a    <- HTML과 비교해보면 section_body에 4번째 ul에 ... 있다는걸 대충 추측
# //*[@id="section_body"]/ul[1]/li[1]/dl/dt[2]/a
# 규칙: li가 1부터 5까지 5개씩 증가한 후 다시 1, ul은 1증가함. 나머지는 변함 없음
df_titles = pd.DataFrame()
for l in range(6):
    section_url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=10{}'.format(l)  # 섹션 url
    titles = []
    for k in range(1,3): #pages[l]+1):
        url = section_url + '#&date=%2000:00:00&page={}'.format(k)
        driver.get(url)
        time.sleep(0.5) # 새로운 페이지를 불러오는데 시간이 걸리니까
        for i in range(1,5):
            for j in range(1,6):
                title = driver.find_element('xpath','//*[@id="section_body"]/ul[{}]/li[{}]/dl/dt[2]/a'.format(i,j)).text
                title = re.compile('[^가-힣]').sub(' ', title)
                titles.append(titles)
    df_section_title = pd.DataFrame(titles, columns=['titles'])
    df_section_title['category'] = category[l]
    df_titles = pd.concat([df_titles, df_section_title], ignore_index=True)
df_titles.to_csv('./crawling_data/crawling_data.csv', index=False)


print(df_titles.head())
df_titles.info()
print(df_titles['category'].value_counts())

# print(titles)
# print(len(titles))
# selenium.common.exceptions.StaleElementReferenceException: Message: stale element reference: stale element not found
# 에러 발생: 크롤릴 하려했는데 페이지가 안 바꼈다! => 딜레이를 줘야지 뭐


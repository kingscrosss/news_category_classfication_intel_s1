# 프로젝트: 가상화면 설정부터 전부 다 함. 잘 기록해둘 것.
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import datetime

category = ['Politics', 'Economic', 'Social', 'Culture', 'World', 'IT']
# https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=102 <- 요끝의 번호 순으로 입력해줌 for문으로 돌릴거라
url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=100'

# 나 리퀘스트 아니고 브라우저야하고 속이려고 헤더정보를 같이 보냄
# 크롤링하려는 웹서버: f12 - 네트워크 - 아무거나 클릭 - User-Agent 내용 복사
# header는 딕셔너리 형태
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Whale/3.22.205.26 Safari/537.36"}
# resp =requests.get(url, headers=headers)      # requests: 주소를 주면 응답을 받아오는 함수. 요즘 크롤링을 막아봐서 웹브라우저인 척 해야함.
# # print(list(resp))                           # element의 내용, 난장판. 정리필요
# print(type(resp))                             # <class 'requests.models.Response'>
# soup = BeautifulSoup(resp.text, 'html.parser')   # 파싱, 사람이 읽을만하게 정리해 보여줌. html 문서를 그대로 받아왔다 생각하면 됨
# # print(soup)
# title_tags = soup.select('.sh_text_headline')
#     # f12 element에서 select element~(ctrl+shift+C) 누르고 헤드라인 제목 클릭
#     # 내용 보면 class sh_text_headline~로 제목 선언 된거 확인.
# print(title_tags)
# print(len(title_tags))
# print(type(title_tags[0]))
# titles = []
# for title_tag in title_tags:
#     # re: 내가 원하는 내용만 뽑아올 때 사용
#     titles.append(re.compile('[^가-힣|a-z|A-Z]').sub(' ', title_tag.text))    # ^: 처음부터라는 의미, sub: ()를 제외하고 ' '로 채워라 즉, 한글&영(대소문자) 빼고 전부 지워라
#     # <a class="sh_text_headline nclicks(cls_pol.clsart)" href="https://n.news.naver.com/mnews/article/029/0002829410?sid=100">이스라엘 체류 한국인 피해 없어...218명 항공편·육로 이용 빠져나와</a>
#     # ^ 하나의 엥커? 뭐라고 부른다함. 찾아봐
# print(titles)
# print(len(titles))

df_titles = pd.DataFrame()  # 빈 데이터 프레임 생성
re_title = re.compile('[^가-힣|a-z|A-Z]')

for i in range(6):      # for문을 이용해 정치, 사회, 경제.... 카테고리 별로 헤드라인을 다 불러옴
    resp = requests.get('https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=10{}'.format(i),headers=headers) # 주소 끝부분 100 -> 10{}로 변경
    soup = BeautifulSoup(resp.text, 'html.parser')
    title_tags = soup.select('.sh_text_headline')
    titles = []
    for title_tag in title_tags:
        titles.append(re.compile('[^가-힣|a-z|A-Z]').sub(' ', title_tag.text))
    df_section_titles = pd.DataFrame(titles, columns=['titles'])
    df_section_titles['category'] = category[i]
    df_titles = pd.concat([df_titles, df_section_titles], axis='rows', ignore_index=True)   # 위에서 만든 데이터 프레임에 이어붙이는 것

print(df_titles.head())
df_titles.info()
print(df_titles['category'].value_counts())
df_titles.to_csv('./crawling_data/naver_headline_news_{}.csv'.format(
    datetime.datetime.now().strftime('%Y%m%d')), index=False)       # datetime: 기본 패키지, Y만 대문자





























import pandas as pd
import glob     # 기본 패키지(개고양이에서 씀)
import datetime

# 팀별로 카테고리 별 크롤링한 파일과 개별로 헤드라인 뉴스 크롤링 한 것을 하나로 합치는 것.
# (우리팀은 카테고리별 안 하고 한번에 싹 처리해서 파일 1개 밖에 없음)

data_path = glob.glob('./crawling_data/*.csv')      # crawling_data 폴더에 있는 파일명 다 내놔라
print(data_path)                                # ['./crawling_data\\crawling_data_KEN.csv', './crawling_data\\naver_headline_news_20231011.csv']

df = pd.DataFrame()
for path in data_path:
    df_temp = pd.read_csv(path)                 # 인덱스가 있는 경우: pd.read_csv('주소+파일명', index_col=0)
    df = pd.concat(([df, df_temp]))
print(df.head())
print(df['category'].value_counts())
df.info()
df.to_csv('./crawling_data/naver_news_titles_{}.csv'.format(
    datetime.datetime.now().strftime('%y%m%d%H%M')), index = False)     # 두자리수년,월,일,24시,분



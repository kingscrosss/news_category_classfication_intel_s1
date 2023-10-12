# 자연어는 계산을 할 수 없다. 즉, 숫자로 바꿔줘야함
# 하지만 자연어는 의미를 가지기 때문에 그것을 잘 살려야함
# 이를 위한 전처리 과정

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split    # scikit-learn 설치
from konlpy.tag import Okt
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
import pickle
# 버전 이슈로 tensorflow==2.7.0로 설치(아니면 파이썬은 3.7.4 이상으로 설치 해야 함.)

pd.set_option('display.unicode.east_asian_width', True)     # 데이터 왼쪽 정렬
df = pd.read_csv('./crawling_data/naver_news_titles_20231012.csv')
# print(df.head())
# df.info()

X = df['titles']
Y = df['category']

# 카테고리
## 라벨링: 문자열(Politics, ...)을 숫자로 바꿔줌 & onehot
encoder = LabelEncoder()
labeled_y = encoder.fit_transform(Y)
# print(labeled_y[:3])    # 앞에 3개만 보고 확인. [3 3 3]
label = encoder.classes_
# print(label)            # ['Culture' 'Economic' 'IT' 'Politics' 'Social' 'World']
with open('./models/encoder.pickle','wb') as f:     # f: 저장?, wb: w-write, b-binary, 바이너리로 저장할 때, rb는 읽을 때.
    pickle.dump(encoder,f)
onehot_y = to_categorical(labeled_y)
# print(onehot_y)

# 타이틀(자연어)
## 토크나이져?: 형태로소 분리(okt)하고 라벨링 해주는 것.
## 영어는 이미 많이 연구가 되어있지만 한국은 아니어서 한글을 따로 연구해야했음. 그걸 연구해 모은 것 KoNLPy
## Hannanum Class, Kkma Class, Komoran Class, Mecab Class, Okt Class
## KoNLPy: https://konlpy.org/ko/latest/index.html
### JAVA 설치(KoNLPy 패키지 사용을 위한...)
# https://www.oracle.com/java/technologies/downloads/#java17
# JDK Development Kit 17.0.8 downloads (버전 21 말고) Windows - x64 MSI Installer 다운 및 설치
# [고급 시스템 설정 - 환경변수 - 시스템 변수: 새로만들기 -> 변수이름: JAVA_HOME 변수값: 자바폴더(C:\Program Files\Java\jdk-17)
#                                     : 변수 path에 편집 들어가서 %JAVA_HOME%\bin 추가 (보통 bin 폴더에 실행 파일 들어있음)
# 환경 시스템 변수는 시스템에서 변수를 입력하면 맨처음 실행 폴더에서 찾고 그 다음 시스템 변수에서 찾는게 그걸 추가해주는 것
# 변수를 추가하면 path에 들어가서 같이 추가를 해줘야한다.

okt = Okt()

for i in range(len(X)):
    X[i] = okt.morphs(X[i], stem=True)      # 현재 타이틀로 들어가있는 데이터를 형태소의 형태로 변환
                                            # stem: 각 단어에서 어간을 추출하는 기능, norm: normalize의 약자로 문장을 정규화하는 역할
# print(X)

## 불용어(stopwords) 제거
# 범주형 데이터니까 onehot 해줘야함
# 한 글자 형태의 단어는 동의어가 많고 '그'와 같은 대명사, 감탄사, 단위 등은 학습하기에 오히려 방해가 된다.
# => 한글자짜리 불용어(stopwords)를 뺀다 stopwords 파일 참조
stopwords = pd.read_csv('./datasets/stopwords.csv', index_col=0)
for j in range(len(X)):
    words = []
    for i in range(len(X[j])):
        if (len(X[j][i]) > 1):
            if X[j][i] not in list(stopwords['stopword']):
                words.append(X[j][i])
    X[j] = ' '.join(words)  # 띄어쓰기를 기준으로 이어붙여줌
# print(X)

token = Tokenizer()
token.fit_on_texts(X)        # 형태소 하나하나에 라벨을 붙여주는 것. 아직 바꿔주진 x, 라벨링한 숫자값은 토큰이 가지고 있음
tokened_X = token.texts_to_sequences(X)     # 토큰을 이용해서 라벨로 X 내용을 바꿔주는 것.
wordsize = len(token.word_index)+1  # 라벨링을 할 때는 0을 안 붙여주는데 우리는 0을 쓸거라 1 더해줌
# print(tokened_X)
# print(wordsize)     # fit_on_texts(X)를 하면 X 안에 들어간 모든걸 라벨링 해주는데 그것에 대한 갯수

# 피클: 파이썬 기본 패키지, 인코딩 하지 않고 값 그대로 저장하는 것.
# 피클 할 것들: encoder, Tokenizer(token),
with open('./models/news_token.pickle','wb') as f:  # w: write, b: binary
    pickle.dump(token, f)

# 문장의 길이가 다 다름 => 길이를 맞춰줘야함. how? 제일 긴걸 기준으로 맞춰 작은거에 빈값을 앞에 채워준다
# LSTM에서 앞에 있는게 학습이 덜 되는걸 이용해서 앞에 의미가 없는 빈 값을 배정한다.
max = 0
for i in range(len(tokened_X)):
    if max < len(tokened_X[i]):
        max = len(tokened_X[i])
# print(max)
x_pad = pad_sequences(tokened_X, max)       # max에 맞춰 앞에다 0을 채워라
# print(x_pad[:3])

X_train, X_test, Y_train, Y_test = train_test_split(
    x_pad, onehot_y, test_size=0.2)
print(X_train.shape, Y_train.shape)
print(X_test.shape, Y_test.shape)

xy = X_train, X_test, Y_train, Y_test
np.save('./crawling_data/news_data_max_{}_wordsize_{}'.format(max, wordsize), xy)

# 데이터 파일은 commit하지 말 것. 100MB 넘는건 안 올리고 구글드라이브에 저장하고 링크를 따로 걸어준다.



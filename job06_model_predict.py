import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split    # scikit-learn 설치
from konlpy.tag import Okt
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
import pickle
from tensorflow.keras.models import load_model

df = pd.read_csv('./crawling_data/naver_headline_news_20231012.csv')    # 테스트할 데이터
print(df.head())
df.info()

X = df['titles']
Y = df['category']

with open('../models/encoder.pickle', 'rb') as f:    # 이번엔 바이너리로 읽어들여오는거(rb)
    encoder = pickle.load(f)
labeled_y = encoder.transform(Y)    # fit.transform 아니고 그냥 transform. 전자는 새로만드는 것이다
label = encoder.classes_

onehot_y = to_categorical(labeled_y)
print(onehot_y)

okt = Okt()

for i in range(len(X)):
    X[i] = okt.morphs(X[i], stem=True)
stopwords = pd.read_csv('datasets/stopwords.csv', index_col=0)

for j in range(len(X)):
    words = []
    for i in range(len(X[j])):
        if (len(X[j][i]) > 1):
            if X[j][i] not in list(stopwords['stopword']):
                words.append(X[j][i])
    X[j] = ' '.join(words)

with open('../models/news_token.pickle', 'rb') as f:
    token = pickle.load(f)

tokened_x = token.texts_to_sequences(X)
# 기존 모델이 21개짜리인데 오늘 뉴스는 길이가 어떤지 알 수 없으니까 길면 잘라버려줘야한다.
for i in range(len(tokened_x)):
    if len(tokened_x) > 21:
        tokened_x[i] = tokened_x[i][:22]
x_pad = pad_sequences(tokened_x,21)

model = load_model('../models/news_category_classification_model_0.6978723406791687.h5')
preds = model.predict(x_pad)
predicts = []
for pred in preds:
    most = label[np.argmax(pred)]   # 가장 큰 값을 라벨로 가져와
    pred[np.argmax(pred)] = 0       # 가장 큰 값을 0으로 만듬 즉 두번째 큰 값이 1이 되겠지
    second = label[np.argmax(pred)]
    predicts.append([most, second])
df['predict'] = predicts
print(df.head(30))

df['OX'] = 0
for i in range(len(df)):
    if df.loc[i,'category'] in df.loc[i,'predict']:
        df.loc[i,'OX']= 'O'
    else:
        df.loc[i, 'OX'] = 'X'
print(df['OX'].value_counts())
print(df['OX'].value_counts()/len(df))
for i in range(len(df)):
    if df['category'][i] not in df['predict'][i]:
        print(df.iloc[i])






import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import *
from tensorflow.keras.layers import *

X_train, X_test, Y_train, Y_test = np.load(
    './crawling_data/news_data_max_21_wordsize_12387.npy', allow_pickle=True)
print(X_train.shape, Y_train.shape)
print(X_test.shape, Y_test.shape)

model = Sequential()
model.add(Embedding(12387, 300, input_length=21))
# Embedding( 1)레이어 추가, 2)그 레이어를 차원 축소, )
# : Embedding: 형태소 별 하나의 차원(백터)을 만든다.
# 1) 의미 공간상의 벡터
# 2) 차원은 늘어났는데 데이터의 개수는 작아져서 데이터가 희소해지기 때문에 모델학습이 안 된다.(차원의 저주) 데이터를 늘릴 수 없으니 차원을 줄인다.
# 3) 파일 개수의 최대값
model.add(Conv1D(32,kernel_size=5, padding='same', activation='relu'))  # 문장은 1줄이니까 1D
model.add(MaxPooling1D(pool_size=1))
model.add(LSTM(128, activation='tanh',return_sequences=True))   # return_sequences 결과값을 하나하나 저장해서 시퀀셜한 출력값을 보내주는거
model.add(Dropout(0.3))
model.add(LSTM(64, activation='tanh', return_sequences = True))
model.add(Dropout(0.3))
model.add(LSTM(64, activation='tanh'))  # 다음 레이어로 Flatten으로 들아고 Dense로 해버리니까 return_sequences 필요X
model.add(Dropout(0.3))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dense(6, activation='softmax'))
model.summary()

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
fit_hist = model.fit(X_train, Y_train, batch_size=128, epochs=10, validation_data=(X_test, Y_test))
model.save('./models/news_category_classification_model_{}.h5'.format(fit_hist.history['val_accuracy'][-1]))
plt.plot(fit_hist.history['val_accuracy'], label='validation accuracy')
plt.plot(fit_hist.history['accuracy'], label='accuracy')
plt.legend()
plt.show()






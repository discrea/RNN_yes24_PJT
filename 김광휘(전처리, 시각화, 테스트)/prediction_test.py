import pandas as pd
import numpy as np
from tensorflow.keras.models import *
import pickle
from konlpy.tag import Okt
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Data(X) token load
with open('./pre_process_data/book_token_cat_12_max_196_size_218318.pickle', 'rb') as f:
    token = pickle.load(f)

# Target(Y) label encoder load
with open('./pre_process_data/category_encoder.pickle', 'rb') as f:
    encoder = pickle.load(f)
category = encoder.classes_
print(category)

# Model load
model = load_model('./for_test/book_classification_cat_12_0.8087338209152222.h5')

# Test data load
test_data = pd.read_csv('./for_test/yes24_new_book_test_data.csv', index_col=0)

test_data.drop(['Unnamed: 0.1', 'Unnamed: 0.1.1', 'Small_category'], axis=1, inplace=True)
test_data.reset_index(drop=True, inplace=True)
# print(test_data.head())
print(test_data.info())

X = test_data['Introduction']
Y = test_data['Medium_category']


# 형태소 분석
print('형태소 분석 중', end='')
okt = Okt()
for i in range(len(X)):
    X[i] = okt.morphs(X[i])
    if (i % 20 == 0) and (i>1):
      print('.', end='')
    if (i % 200 == 0) and (i > 1):
      print('{} / {}'.format(i, len(X)))
print('형태소 분석 완료')


# stopwords 제거
print('Stopwords 제거 중', end='')

stopwords = pd.read_csv('./datasets/stopwords.csv')

for i in range(len(X)) :
  result = []
  for j in range(len(X[i])):
    if len(X[i][j]) > 1:
      if X[i][j] not in list(stopwords['stopword']):
        result.append(X[i][j])
  X[i] = ' '.join(result)
  if (i % 20 == 0) and (i>1):
    print('.', end='')
  if (i % 200 == 0) and (i>1):
    print('{} / {}'.format(i, len(X)))
print('Stopwords 제거 완료')


# tokenization
tokened_X = token.texts_to_sequences(X)
print('Tokenization 완료')

# padding
X_pad = pad_sequences(tokened_X, 196)
print('Padding 완료')

# prediction
print('Model에서 예측 중')
predict = model.predict(X_pad)
print(type(predict))

predict_category = []
for pred in predict:
    predict_category.append(category[np.argmax(pred)])
print(predict_category)


df_chk = pd.DataFrame()
df_chk['Title'] = test_data['Title']
df_chk['Introduction'] = test_data['Introduction']
df_chk['Target'] = test_data['Medium_category']
df_chk['Predict'] = predict_category
df_chk['OX'] = None


for i in range(len(df_chk)):
    if df_chk.Target[i] == df_chk.Predict[i]:
        df_chk.OX[i] = 'O'
    else:
        df_chk.OX[i] = 'X'

print(df_chk.head())
print(df_chk.info())


print(df_chk.OX.value_counts() / len(df_chk.OX))

accuracy = df_chk.OX.value_counts()[0] / len(df_chk.OX)

print('Accuracy is ', accuracy)

df_chk.to_csv('./for_test/test_complete_{}.csv'.format(accuracy))
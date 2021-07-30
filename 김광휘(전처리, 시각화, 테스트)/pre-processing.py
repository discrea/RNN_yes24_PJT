import pandas as pd
import numpy as np
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import *
from tensorflow.keras.preprocessing.sequence import pad_sequences
from konlpy.tag import Okt
import pickle


pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_columns', 6)


file_path = './datasets/book_raw_data.csv'
data = pd.read_csv(file_path)

print('initial', data.info())

data.drop(['Unnamed: 0', 'Small_category', 'cnt'], axis=1, inplace=True)
data = data.dropna()

print('after dropna',data.info())

for i in range(len(data)):
  for j in range(5, 1, -1):
      data.iloc[i,2] = data.iloc[i,2].replace(' '*j, ' ')


print('space remove',data.info())

# # 결측처리 및 column 지정 n
data.dropna(subset=['Medium_category'], axis=0, inplace=True)

data.drop_duplicates(subset=['Introduction'], inplace=True)
data.reset_index(drop=True, inplace=True)
print(data.info())


''' 가은님 코드

# sum_dup = data.Introduction.duplicated().sum()
# print(sum_dup)
#
# df = data.drop_duplicates(subset=['Introduction'])
# sum_dup = df.Introduction.duplicated().sum()
# print(sum_dup)
# print(len(df))
# print('='*50)


# print(data.iloc[11690:11700, 2])


# print(data.info())
# print(data.head(5))
'''

X = data['Introduction']
Y = data['Medium_category']


'''
    Target - label encoding
'''
encoder = LabelEncoder()
labeled_Y = encoder.fit_transform(Y)
label = encoder.classes_
print(label)

# encoding mapping 정보를 저장
with open('./datasets/category_encoder.pickle', 'wb') as f:
  pickle.dump(encoder, f)

print(labeled_Y)

# label을 onehotencoding 으로 변환
onehot_Y = to_categorical(labeled_Y)
print(onehot_Y)

print(X[309])
print(type(X))


'''
  X data
'''


'''
  morphs separation
'''
from konlpy.tag import Okt
okt = Okt()
print('형태소 분리')
for i in range(len(X)):
  X[i] = okt.morphs(X[i])
  if (i % 250 == 0) and (i>1):
    print('.', end='')
  if i % 5000 == 0:
    print('{} / {}'.format(i, len(X)))
print(X)

# method 1
X.to_csv('./datasets/morphs_sep_X_1st.csv')

# method 2
# with open('./datasets/morphs_sep_X.csv', 'a', encoding='utf-8', newline='') as save:
#     fieldnames = ['idx', 'title', 'genre', 'context']
#     writer = csv.DictWriter(save, fieldnames=fieldnames)
#     writer.writerow(append_data)


'''
  stopwords remove
'''

print('stopwords 제거')

stopwords = pd.read_csv('./datasets/stopwords.csv')

for i in range(len(X)) :
  result = []
  for j in range(len(X[i])):
    if len(X[i][j]) > 1:
      if X[i][j] not in list(stopwords['stopword']):
        result.append(X[i][j])
  X[i] = ' '.join(result)
  if (i % 250 == 0) and (i>1):
    print('.', end='')
  if i % 5000 == 0:
    print('{} / {}'.format(i, len(X)))
print(X)

X.to_csv('./datasets/stopword_removed_X_2nd.csv')


'''
  tokenizing
'''

# 단어 tokenizing : 각 단어별로 숫자를 배정
token = Tokenizer()
token.fit_on_texts(X) # 형태소에 어떤 숫자를 배정할 것인지 배정
tokened_X = token.texts_to_sequences(X) # 토큰에 저장된 정보를 바탕으로 문장을 변환
print(tokened_X[0])

tokened_X.to_csv('./datasets/tokened_X_3rd.csv')

import pickle  # 데이터 형태 그대로 저장할 수 있도록함

with open('./datasets/news_token.pickle', 'wb') as f:
  pickle.dump(token, f)



'''
  dataset info check
'''

# 형태소 개수 확인
wordsize = len(token.word_index) +1

print('word index : ', token.word_index)

print('wordsize is : ', wordsize)  # index 0를 padding 으로 추가 예정


# 1. 가장 긴 문자의 길이 확인
max = 0
for i in range(len(tokened_X)):
  if max < len(tokened_X[i]):
    max = len(tokened_X[i])

print('max is : ', max) # 16


'''
  padding
'''
# 앞쪽을 0으로 채움
X_pad = pad_sequences(tokened_X, max)

X_pad.to_csv('./datasets/padded_X_4th.csv')

print(X_pad[:10])


'''
   Train / test set split
'''
X_train, X_test, Y_train, Y_test = train_test_split(X_pad, onehot_Y, test_size=0.2)
print(X_train.shape)
print(X_test.shape)
print(Y_train.shape)
print(Y_test.shape)


'''
  train / test set을 저장
'''
xy = X_train, X_test, Y_train, Y_test
np.save('./datasets/book_data_max_{}_size_{}'.format(max, wordsize), xy)
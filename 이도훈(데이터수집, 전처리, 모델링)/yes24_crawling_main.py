import os
import re
import time
import requests
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from urllib.request import urlopen

cat_dict = {
    '가정 살림': '001001001',
    '건강 취미': '001001011',
    '경제 경영': '001001025',
    '국어 외국어 사전': '001001004',
    '대학교재': '001001014',
    '만화/라이트노벨': '001001008',
    '사회 정치': '001001022',
    '소설/시/희곡': '001001046',
    '수험서 자격증': '001001015',
    '어린이': '001001016',
    '에세이': '001001047',
    '여행': '001001009',
    '역사': '001001010',
    '예술': '001001007',
    '유아': '001001027',
    '인문': '001001019',
    '인물': '001001020',
    '자기계발': '001001026',
    '자연과학': '001001002',
    '잡지': '001001024',
    '전집': '001001023',
    '종교': '001001021',
    '청소년': '001001005',
    'IT 모바일': '001001003',
    '초등참고서': '001001044',
    '중고등참고서': '001001013'
}
link_info = pd.read_csv('../data_backup/address_info')          # 주소 정보가 있는 dataframe 가져오기
file_name_format = re.compile('[^ a-z A-Z \uac00-\ud7a3 ]+')  # 파일 저장을 위한 중분류 이름 변환

# 주소
url_format = 'http://www.yes24.com/24/category/bestseller?CategoryNumber={}{}&sumgb=06&PageNumber={}'
# 나 콤퓨타 아니다. 나 휴먼이다.
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'}

error_url = []          # 예
error_book_url = []     # 외
error_msg = []          # 처
error_flag = False      # 리
cnt = 0

for mid_cat_name, mid_cat_link_part in cat_dict.items():    # 중분류 별 순회
    name = []               # 중분류 별 책이름 데이터
    medium_category = []    # 중분류 별 중분류 데이터
    small_category = []     # 중분류 별 소분류 데이터
    introduction = []       # 중분류 별 책소개 데이터
    mid_link_info = link_info[link_info['medium_category'] == mid_cat_name][['category_number', 'small_category', 'page_amount']]
    for i in range(len(mid_link_info)):                             # 중분류 당 소분류 개수 만큼 반복
        small_cat_num = mid_link_info.iloc[i]['category_number']    # 소분류 주소조각 저장1
        small_cat_name = mid_link_info.iloc[i]['small_category']    # 소분류 이름 저장
        link_part = '{:0>3}'.format(small_cat_num)                  # 소분류 주소조각 저장2
        for j in range(mid_link_info.iloc[i]['page_amount']):           # 소분류 당 페이지 개수만큼 반복
            try:
                url = url_format.format(cat_dict.get(mid_cat_name), link_part, j+1)
                html = requests.get(url, headers=headers)       # html로 가져오고
                soup = BeautifulSoup(html.text, 'html.parser')  # bs4로 읽어서
                title_tags = soup.select('.goodsTxtInfo')       # 한 페이지에 모든 책 정보를 리스트로 가져온다

                for book_info in title_tags:  # 리스트를 순회하며
                    try:
                        title = book_info.select_one('p > a').get_text()        # 책 제목
                        book_link_part = book_info.select_one('p > a')['href']  # 해당책의 링크 조각을 가져온 후

                        book_url = 'http://www.yes24.com' + book_link_part          # 책의 링크로 들어가서
                        book_html = requests.get(book_url, headers=headers)         # 들어가서
                        book_soup = BeautifulSoup(book_html.text, 'html.parser')    # 이제 진짜 들어가서
                        book_summary_soup = book_soup.select('.infoWrap_txtInner')  # 책 소개 및 줄거리 부분
                        text = ''
                        for summary in book_summary_soup:  # 여러 br태그에 쪼개져서 들어있다
                            text += summary.getText()

                        name.append(title)
                        medium_category.append(mid_cat_name)
                        small_category.append(small_cat_name)
                        introduction.append(text)
                        cnt += 1

                        print(cnt, '@' * 40)
                        print('book title :', title)
                        print('book category :', mid_cat_name, '||', small_cat_name)
                        print('book introduction number of characters :', len(text))

                    except Exception as e:
                        print('예외가 발생했습니다.', e)
                        error_flag = True
                        error_url.append(url)
                        error_book_url.append(book_url)
                        error_msg.append(e)

            except Exception as e:
                print('예외가 발생했습니다.', e)
                error_flag = True
                error_url.append(url)
                error_book_url.append(book_url)
                error_msg.append(e)

    file_name = file_name_format.sub('', mid_cat_name).replace(' ', '_')  # 슬래쉬 제거, 띄어쓰기는 언더바로 치환
    # 파일 이름에는 슬래쉬나 띄어쓰기 있으면 안좋아
    temp_data = pd.DataFrame({'Title': name,                            # 중분류 별 데이터 저장
                              'Medium_category': medium_category,
                              'Small_category': small_category,
                              'Introduction': introduction
                              })
    temp_data.to_csv('../data_backup/data_{}'.format(file_name))
    if error_flag:                                                      # 에러 발생 시 에러 내용 저장
        error_data = pd.DataFrame({'url':error_url,
                                  'error_book_url': book_url,
                                  'error_msg': error_msg
                                   })
        error_data.to_csv('../data_backup/error_{}'.format(file_name))
        error_url = []
        error_book_url = []
        error_msg = []
        error_flag = False
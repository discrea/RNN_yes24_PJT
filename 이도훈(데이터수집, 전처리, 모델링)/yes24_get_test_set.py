import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

cat_dict = {
    '가정 살림': '001001001',
    '건강 취미': '001001011',
    '경제 경영': '001001025',
    '국어 외국어 사전': '001001004',
    '만화/라이트노벨': '001001008',
    '사회 정치': '001001022',
    '소설/시/희곡': '001001046',
    '수험서 자격증': '001001015',
    '어린이': '001001016',
    '유아': '001001027',
    '인문': '001001019',
    '청소년': '001001005',
}

# 주소
url_format = 'http://www.yes24.com/24/Category/NewProductList/{}?sumGb=04&ParamSortTp=04'
# 나 콤퓨타 아니다. 나 휴먼이다.
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'}

cnt = 0
fail_flag = True
name = []               # 책이름 데이터
medium_category = []    # 중분류 데이터
small_category = []     # 소분류 데이터
introduction = []       # 책소개 데이터

for mid_cat_name, mid_cat_link_part in cat_dict.items():    # 중분류 별 순회
    try:
        url = url_format.format(mid_cat_link_part)
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
                book_category_soup = book_soup.select('.yesAlertLi > li > a')  # 카테고리 부분

                text = ''
                for summary in book_summary_soup:  # 여러 br태그에 쪼개져서 들어있다
                    text += summary.getText()

                for j in range(5):  # 카테고리가 대, 중, 소 분류로 나뉘어 있다
                    if book_category_soup[j].get_text() == '국내도서':
                        name.append(title)
                        medium_category.append(book_category_soup[j+1].get_text())
                        small_category.append(book_category_soup[j+2].get_text())
                        introduction.append(text)
                        cnt += 1
                        fail_flag = False
                        break

                print(cnt, '@' * 40)
                if fail_flag:
                    fail_flag = True
                    print('EXCEPTION : CATEGORIZING FAIL')
                else:
                    print('book title :', title)
                    print('book category :', book_category_soup[j+1].get_text(), '||', book_category_soup[j+2].get_text())
                    print('book introduction number of characters :', len(text))

            except Exception as e:
                print('예외가 발생했습니다.', e)

    except Exception as e:
        print('예외가 발생했습니다.', e)

df = pd.DataFrame({'Title': name,
                         'Medium_category': medium_category,
                         'Small_category': small_category,
                         'Introduction': introduction
                         })

df.dropna(inplace=True)                   # 널값 제거
df.drop_duplicates(inplace=True)                            # 중복 제거 1
df.drop_duplicates(subset=['Introduction'],inplace=True)    # 중복 제거 2
# 책 소개 부분의 기호, 널값, 개행 삭제
df['Introduction'] = df['Introduction'].apply(lambda x: re.compile('[^가-힣 | a-z | A-Z | 0-9 ]').sub(' ', x))
df.to_csv('../data/yes24_new_book_test_data.csv')
"""
# Yes24 웹 베스트샐러 문류별 링크 추출 #

yes24의 분류 각각의 책 내용 크롤링은 편하나
링크는 규칙성을 발견하지 못해 수작업을 하다 빡쳐서 만들어봤다
"""

import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

"""
고영익 조원님의 코드를 조금이라도 유심히 봤다면 내 인생에 5시간을 허비하지 않았.. 크흡
yes24 베스트 셀러 중 소분류 링크의 CategoryNumber는 총 12개의 숫자로 이루어 져있다.
XXX XXX XXX XXX 이렇게 4개 섹션으로 구분하여 두번째 색션부터 대분류, 중분류, 소분류의 숫자로 나뉜다.
소분류는 느낌상 40을 넘지 않는다
그럼 우린 중분류의 링크조각을 딕셔너리로 만들어 소분류는 자동화로 찾음 된다
십만번 반복할거 1040번으로 줄임
"""

# 주소
url_format = 'http://www.yes24.com/24/category/bestseller?CategoryNumber={}{:0>3}&sumgb=06&PageNumber=1'
# 나 콤퓨타 아니다. 나 휴먼이다.
headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'}

# 반복문에 필요한 중분류의 주소조각 딕셔너리 화
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
total_medium_category = []      # 중분류 전체 저장 리스트
total_small_category = []       # 소분류 전체 저장 리스트
total_category_number = []      # 소분류 주소조각 전체 저장 리스트
total_page_amount = []          # 소분류 별 사이트 페이지 개수 전체 저장 리스트

for mid_cat_name, mid_cat_link_part in cat_dict.items():    # 중분류 별로 순회
    true_flag = False       # 에러 발생 여부 확인 1
    t = 0                   # 검증된 사이트
    e = False               # 에러 발생 여부 확인 2
    medium_category = []        # 중분류
    small_category = []         # 소분류
    category_number = []        # 소분류 주소조각
    page_amount = []            # 소분류 별 사이트 페이지 개수
    error_page = []             # 에러 발생 시 저장할 리스트

    print('{:<10}({}) : '.format(mid_cat_name, mid_cat_link_part), end='')
    for i in range(40):                                             # 소분류 링크조각은 000~999사이, 대부분은 000~030 사이에 분포
                                                                    # 넉넉히 000~040까지 순회
        url = url_format.format(mid_cat_link_part, i)   # 해당 url을
        html = requests.get(url, headers=headers)       # html로 가져오고
        soup = BeautifulSoup(html.text, 'html.parser')  # bs4로 읽어서
        random_book = soup.select_one('.goodsTxtInfo')  # 아무거나 책 찍고
        if not random_book:                     # 이 주소가 유효한지 확인하는 작업
            print('F', end='')                  # 유효하지 않으면 F 출력후 다음 주소 순회
        else:
            try:
                regex = re.compile('(\d+)(?!.*\d)')  # 마지막 페이지 정보를 가져오기 위한 정규식

                last_page_link = soup.select_one('.page > img').select('.hover')[1]['href']
                last_page = regex.findall(last_page_link)[0]  # 패턴과 매칭되는 문자를 리스트로 반환

                link_part = random_book.select_one('p > a')['href']         # 해당책의 링크 조각을 가져온 후
                book_url = 'http://www.yes24.com' + link_part               # 책의 링크로 들어가서
                book_html = requests.get(book_url, headers=headers)         # 들어가서
                book_soup = BeautifulSoup(book_html.text, 'html.parser')    # 이제 진짜 들어가서

                book_category_soup = book_soup.select('.yesAlertLi > li > a')  # 카테고리 관련 테그 긁어오고
                for j in range(5):                                                      # 몇번째 child부터 분류를 표시할지는 random
                    if book_category_soup[j].get_text() == '국내도서':                  # 순회하면서 대분류 찾은 뒤
                        medium_category.append(book_category_soup[j + 1].get_text())    # 중분류
                        small_category.append(book_category_soup[j + 2].get_text())     # 소분류 추출
                        category_number.append('{:0>3}'.format(i))                      # 소분류 주소조각 추출
                        page_amount.append(last_page)                                   # 마지막 페이지 추출

                        print('T', end='')
                        t += 1
                        true_flag = True
                        break
                if not true_flag:
                    true_flag = False
                    print('O', end='')  # 국내도서가 아닐 경우


            except IndexError:              # 서비스 중지된 링크 예외처리
                e = True
                error_page.append('{}{:0>3}'.format(mid_cat_link_part, i))
                print('E', end='')


    print(' || Exist Page = ', t, end='')
    info = pd.DataFrame({'medium_category': medium_category,
                         'small_category': small_category,
                         'category_number': category_number,
                         'page_amount': page_amount
                         })
    info.to_csv('../data_backup/{}'.format(mid_cat_link_part))
    total_medium_category += medium_category
    total_small_category += small_category
    total_category_number += category_number
    total_page_amount += page_amount

    if e:
        print(' || Error Occured On = ', error_page)
        error_page = []
        e = False
    else:
        print('')

result = pd.DataFrame({'medium_category': total_medium_category,
                       'small_category': total_small_category,
                       'category_number': total_category_number,
                       'page_amount': total_page_amount
                       })
result.to_csv('../data_backup/address_info')

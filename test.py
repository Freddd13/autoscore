import requests
import os
from datetime import datetime

BASE_URL = 'https://www.mymusicsheet.com'
GRAPHQL_URL = 'https://mms.pd.mapia.io/mms/graphql'
EXCHANGE_RATE_URL = 'https://payport.pd.mapia.io/v2/currency'
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'templates/description.art')

def get_exchange_rates():
    params = {
        'serviceProvider': 'mms',
        'ngsw-bypass': 'true',
        'no-cache': str(int(datetime.now().timestamp())),
        'skipHeaders': 'true'
    }
    response = requests.get(EXCHANGE_RATE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def load_artist_sheets(username, iso='USD', free_only=False):
    # 获取汇率
    rates = get_exchange_rates()
    print("rates:" , rates)
    if rates is None:
        raise Exception("Failed to get exchange rates")
    
    # GraphQL 请求
    payload = {
        'operationName': 'loadArtistSheets',
        'query': """
        query loadArtistSheets($data: SheetSearchInput!) {
            sheetSearch(data: $data) {
                list {
                    productId
                    productType
                    metaSong
                    metaMaker
                    metaMusician
                    metaMemo
                    instruments
                    level
                    price
                    sheetId
                    status
                    author {
                        name
                        artistUrl
                        profileUrl
                    }
                    youtubeId
                    title
                    supportCountry
                    excludeCountries
                    __typename
                }
                total
                current
                listNum
            }
        }""",
        'variables': {
            'data': {
                'listNum': 10,
                'paginate': 'page',
                'includeChord': None,
                'includeLyrics': None,
                'page': 1,
                'level': None,
                'instruments': [],
                'orderBy': {
                    'createdAt': 'DESC'
                },
                'isFree': False,
                'category': None,
                'artistUrl': username,
                'aggregationKeywords': ['PACKAGE_IDS', 'TAG_IDS', 'INSTRUMENTS', 'SHEET_TYPE', 'INCLUDE_CHORD', 'INCLUDE_LYRICS', 'INSTRUMENTATION', 'LEVEL', 'CATEGORY'],
                'aggregationKeySize': 20
            }
        }
    }

    response = requests.post(GRAPHQL_URL, json=payload)
    print('-'*50)
    if response.status_code != 200:
        print(response.text)
        raise Exception("GraphQL request failed")

    sheet_search = response.json().get('data', {}).get('sheetSearch', {}).get('list', [])
    print(response.json())
    print('-'*50)
    
    items = []
    for item in sheet_search:
        final_price = 'Unknown'
        price = float(item.get('price', -1))
        print(price)
        if abs(price) < 1e-6:
            final_price = 'Free'
        print("price: ", final_price)
        print('title:', f"{item['author']['name']} | {item['title']} | {final_price}")
        print('link:', f"{BASE_URL}/{username}/{item['sheetId']}")

load_artist_sheets('HalcyonMusic')
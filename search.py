import os, sys, datetime
import requests, re
from bs4 import BeautifulSoup

"""

TODO:
    - Move search/scrape logic to a class
    - Command line arguments
    - Cache search results in database
        - Have a process automatically cleanup stale results (older than a few hours)
    - Ability to add product based on search result

Scrape URL:
http://www.amazon.com/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords=shin%20megami

"""

class SearchDefault(object):
    def __init__(self):
        self.url_base = 'http://www.amazon.com/s/ref=nb_sb_noss_2'

    def download_search_page(self, keywords, page=1):
        url_params = {
            'url': 'search-alias',
            'field-keywords': keywords,
            'page': page
        }

        r = requests.get(self.url_base, params=url_params)
        return r.text

    def parse_products(self, page):
        pass

if __name__ == '__main__':
    """
    if not os.path.exists('search.html'):
        r = requests.get('http://www.amazon.com/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords=shin%20megami')
    
        fp = open('search.html', 'w')
        fp.write(r.text.encode('utf8'))
        fp.close()
    
    fp = open('search.html', 'r')
    content = fp.read()
    fp.close()
    """
    
    sd = SearchDefault()
    content = sd.download_search_page('shin megami')
    
    soup = BeautifulSoup(content)
    lists = soup.findAll('div', attrs={'class': 'listView'})
    products = []

    category_pattern = re.compile('[\W]$')
    sub_category_pattern = re.compile('^(\s\-)')

    for l in lists:
        for p in l.findAll('div', attrs={'class': 'product'}):
            product = {}
            
            title = p.find('div', attrs={'class': 'productTitle'})
            if title is None:
                continue
        
            try:
                category = category_pattern.sub('', p.find('div', attrs={'class': 'store'}).find('span').text)
            except Exception:
                category = None
        
            try:
                sub_category = sub_category_pattern.sub('', title.findAll('span', attrs={'class': 'binding'})[-1].text).strip()
            except Exception:
                sub_category = None
            
            try:
                newSalePrice = p.find('div', attrs={'class': 'newPrice'}).find('span').text
            except Exception:
                newSalePrice = None
            
            try:
                newRegPrice = p.find('div', attrs={'class': 'newPrice'}).find('strike').text
            except Exception:
                newRegPrice = None
            
            #pData = p.find('div', attrs={'class': 'productData'})
            
            product['title'] = title.a.text
            product['url'] = title.a.get('href')
            product['category'] = category
            product['sub_category'] = sub_category
            product['price_sale'] = newSalePrice
            product['price_regular'] = newRegPrice

            print(product)
            #print(product)
            #print(pData)

    #print(results)
    
    sys.exit(0)


import datetime, requests, re
from bs4 import BeautifulSoup
from app.db import *

"""
    
    #resultCount
        Showing 1 - 16 of 1,675 Results
    
"""

class ProductSearcher(object):
    def __init__(self, session):
        self.session = session
        self.url_base = 'http://www.amazon.com/s/ref=nb_sb_noss_2'

    def sanitize_keywords(self, keywords):
        return re.sub(r'\s+', ' ', keywords.lower()).strip()

    def prune_cache(self, hours=3):
        session = self.session
        now = datetime.datetime.utcnow()
        diff = datetime.timedelta(hours=hours)
        age_filter = now - diff
        
        results = session.query(SearchResultCached)\
                         .filter(SearchResultCached.created < age_filter)
    
        for r in results:
            session.delete(r)

        session.flush()
        session.commit()

    def search(self, keywords, category=None, page=1):
        session = self.session
        keywords = self.sanitize_keywords(keywords)
        results = session.query(SearchResultCached)\
                         .filter(SearchResultCached.search_keywords == keywords,
                                 SearchResultCached.page_num == page).all()
    
        if len(results) > 0:
            return results

        content = self.download_search_page(keywords, category=category, page=page)
        products = self.parse_products(content)
        results = []
        
        for i in range(len(products)):
            p = products[i]
            p.update(   sort_index=i+1,
                        page_num=page,
                        search_keywords=keywords,
                        created=datetime.datetime.utcnow())
            
            sr = SearchResultCached(**p)
            session.add(sr)
            results.append(sr)
        
        session.flush()
        session.commit()
        return results

    def download_search_page(self, keywords, category=None, page=1):
        url_params = {
            'url': 'search-alias',
            'field-keywords': keywords,
            'page': page
        }
        
        if category is not None:
            url_params['url'] += '=' + category

        r = requests.get(self.url_base, params=url_params)
        return r.text

    def parse_products(self, content):
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
        
                #
                # TODO: Cleanup
                #
        
                try:
                    category = category_pattern.sub('', p.find('div', attrs={'class': 'store'}).find('span').text)
                except Exception:
                    category = None
        
                try:
                    sub_category = sub_category_pattern.sub('', title.findAll('span', attrs={'class': 'binding'})[-1].text).strip()
                except Exception:
                    sub_category = None
            
                try:
                    new_sale_price = p.find('div', attrs={'class': 'newPrice'}).find('span').text
                except Exception:
                    new_sale_price = None
            
                try:
                    new_reg_price = p.find('div', attrs={'class': 'newPrice'}).find('strike').text
                except Exception:
                    new_reg_price = None
                
                if new_sale_price is None and new_reg_price is None:
                    continue

                product['title'] = title.a.text
                product['url'] = title.a.get('href')
                product['category'] = category
                product['sub_category'] = sub_category
                product['price_sale'] = new_sale_price
                product['price_regular'] = new_reg_price
                products.append(product)

        return products

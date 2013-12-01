
import os, sys, datetime
import sqlite3
import requests
from bs4 import BeautifulSoup

from app.pricefuncs import price_to_int

class Scraper(object):
    def __init__(self, db_path='./products.db', run_every=3):
        self.run_every = run_every
        self.db_path = db_path

    def db_factory(self):
        return sqlite3.connect(self.db_path)

    @staticmethod
    def datetime_now():
        return datetime.datetime.utcnow()

    def get_products_list(self, ALL=False):
        """ Get list of products to scrape. By default, this fetches only products
            that haven't been scraped in self.run_every hours.  If ALL=True, then
            it will return all products. """
    
        db = self.db_factory()
        cursor = db.cursor()
    
        now = self.datetime_now()
        td = datetime.timedelta(hours=self.run_every)

        cursor.execute('SELECT * FROM products')
        results = cursor.fetchall()
        product_keys = [i[0] for i in cursor.description]
    
        to_scrape = []
    
        for res in results:
            p = dict(zip(product_keys, res))
            cursor.execute('SELECT * FROM product_prices ORDER BY created DESC LIMIT 1')
            pp_res = cursor.fetchone()
        
            if ALL:
                to_scrape.append(p)
            elif pp_res is None:
                to_scrape.append(p)
            else:
                pp = dict(zip([i[0] for i in cursor.description], pp_res))
                ts = datetime.datetime.strptime(
                    pp['created'],
                    '%Y-%m-%d %H:%M:%S.%f'
                )
            
                if (now - ts) >= td:
                    to_scrape.append(p)

        cursor.close()
        db.close()

        return to_scrape

    def scrape_product_info(self, title, url):
        try:
            r = requests.get(url)
            if not r.status_code == 200:
                sys.stderr.write('Failed to download product page for: %s\n' % (title))
                return None, None, None
        
            text = r.text
        except Exception:
            return None, None, None

        soup = BeautifulSoup(text)

        # Get actual/sale price
        try:
            price_span = soup.find('span', id='actualPriceValue')
            price = str(price_span.contents[0].text)
        except Exception:
            price = None

        # Get list/regular price
        try:
            price_value_span = soup.find('span', id='listPriceValue')
            price_value = str(price_value_span.contents[0])
        except Exception:
            price_value = None

        # Get number available
        try:
            form_node = soup.find('form', id='handleBuy')
            buying_divs = form_node.findAll('div', attrs={'class': 'buying'})
            for div in buying_divs:
                avail_green = div.find('span', attrs={'class': 'availGreen'})
                if avail_green is not None:
                    break

            if avail_green is None:
                available = None
            else:
                avail = str(avail_green.text).lower().strip()
                if avail[0:4] == 'only':
                    parts = avail.split(' ')
                    available = int(parts[1])
                else:
                    available = None
        except Exception:
            available = None

        # Shipping has a few different HTML layouts
        shipping = None
        for fn in [self.scrape_shipping1, self.scrape_shipping2]:
            shipping = fn(soup)
            if shipping is not None:
                break

        return price, price_value, available, shipping

    def scrape_shipping1(self, soup):
        try:
            price_qty = soup.find('span', id='pricePlusShippingQty')
            plus_shipping = price_qty.find('span', attrs={'class': 'plusShippingText'})
            shipping = self._filter_shipping1(plus_shipping.text)
        except Exception as e:
            return None
        
        return shipping

    def scrape_shipping2(self, soup):
        try:
            sold_by = soup.find('div', id='soldByThirdParty')
            shipping_span = sold_by.find('span', attrs={'class': 'shipping3P'})
            shipping = self._filter_shipping1(shipping_span.text)
        except Exception as e:
            return None

        return shipping

    @staticmethod
    def _filter_shipping1(value):
        chars = set(['$', '.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
        filtered = ''
        
        for i in range(len(value)):
            v = value[i]
            if v in chars:
                filtered += v

        if len(filtered) == 0:
            return None

        return filtered

    def get_prices(self, wp, products):
        """ Download price data for specified products, and write output to
            WireProtocol object ('wp' parameter). """
    
        now = self.datetime_now()
        for p in products:
            price, price_regular, items_left, shipping = (
                self.scrape_product_info(p['title'], p['url']))
            
            if price is None:
                continue
        
            price_int = price_to_int(price)
            price_regular_int = price_to_int(price_regular)
            shipping_int = price_to_int(shipping)
    
            values = [
                p['id'],
                price_int,
                price_regular_int,
                items_left,
                shipping_int,
                now
            ]
        
            wp.write_tuple(values)
        wp.write_finished()

    def save_prices(self, wp):
        """ Read product prices from WireProtocol object ('wp' parameter), and save
            them to the database. """
    
        items = wp.read_stream()
        db = self.db_factory()
        cursor = db.cursor()

        keys = [
            'product_id',
            'price_sale',
            'price_regular',
            'items_left',
            'shipping',
            'created'
        ]
    
        query = 'INSERT INTO product_prices (%s) VALUES (%s)' % (
            ', '.join(keys),
            ', '.join(['?' for i in keys])
        )

        for values in items:
            try:
                cursor.execute(query, values)
            except sqlite3.Error as e:
                sys.stderr.write('Failed to write item %s' % (values))

        db.commit()
        cursor.close()
        db.close()

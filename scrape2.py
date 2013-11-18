#!/usr/bin/python

import os, sys, math, datetime, time
import requests
import products, config
from bs4 import BeautifulSoup

from app.db import *
session = None

def chunks(source, n):
    for i in xrange(0, len(source), n):
        yield source[i:i+n]

def get_product_price(title, url):
    try:
        r = requests.get(url)
        if not r.status_code == 200:
            sys.stderr.write('Failed to download product page for: %s\n' % (title))
            return None, None, None
    except Exception:
        return None, None, None

    soup = BeautifulSoup(r.text)

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

    return price, price_value, available

def price_to_int(price_text):
    if price_text[0] == '$':
        price_text = price_text[1:]
    price_parts = price_text.split('.')
    return int(price_parts[0]) * 100 + int(price_parts[1])

def downloader(queue, id, title, url):
    queue.put((id, get_product_price(title, url)))

def fetch_products_list():
    def res2dict(res):
        return dict([i for i in res.__dict__.items() if not i[0][0] == '_'])

    now = datetime.datetime.utcnow()
    td = datetime.timedelta(hours=config.scraper['run_every'])
    
    products = session.query(Product).all()
    to_scrape = []
    
    for p in products:
        ll = session.query(ProductPrice)\
                    .filter(ProductPrice.product_id == p.id)\
                    .order_by(ProductPrice.created.desc())\
                    .first()
        
        to_scrape.append(res2dict(p))
        
        #pool.apply_async(downloader, (download_queue, p.id, p.title, p.url))
        #downloader(download_queue, p.id, p.title, p.url)
        
        """
        # Fetch new price data
        price, price_regular, num_available = get_product_price(p.title, p.url)
        if price is None:
            continue
        
        price_int = price_to_int(price)
        if price_regular is None:
            price_regular_int = 0
        else:
            price_regular_int = price_to_int(price_regular)
        """

    """
    sum = 0
    for group in chunks(to_scrape, int(math.ceil(len(to_scrape) / 4.0))):
        print(len(group))
    """

    return to_scrape

def downloader2(args):
    id, title, url = args
    result = get_product_price(title, url)
    print(result)

"""

    def prune_inactive_pids(self):
        pids = []
        for i in xrange(0, len(self.active_pids)):
            pid = self.active_pids[i]
            
            # Kill PID with signal 0, which does nothing.
            # If it fails, the child has already quit
            try:
                os.kill(pid, 0)
                pids.append(pid)
            except: pass
        
        self.active_pids = pids

"""

def main():
    global session
    
    manager = SessionManager('sqlite:///products.db')
    session = manager.session
    
    products = fetch_products_list()
    del manager
    
    n_workers = int(config.scraper['workers'])
    n_groups = int(math.ceil(len(products) / float(n_workers)))
    groups = list(chunks(products, n_groups))
    
    worker_num = 0
    pids = []
    
    for i in range(n_workers):
        pid = os.fork()
        if not pid:
            print('CHILD')
            os._exit(0)

        pids.append(pid)
    
    time.sleep(5)

    sys.exit(0)

if __name__ == '__main__':
    # Auto-change directory
    name = sys.argv[0]
    dir_path = os.path.dirname(name)
    os.chdir(dir_path)
    
    main()

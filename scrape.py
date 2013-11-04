#!/usr/bin/python

import os, sys, datetime
import requests
import products
from bs4 import BeautifulSoup

from app.db import *
session = None

def auto_load_products():
    groups_lk = {}

    for group_name, title, url in products.data:
        if group_name not in groups_lk:
            pg = session.query(ProductGroup)\
                        .filter(ProductGroup.name == group_name)\
                        .first()
        
            if pg is None:
                pg = ProductGroup(name=group_name)
                session.add(pg)
                session.flush()
            
            groups_lk[group_name] = pg
        else:
            pg = groups_lk[group_name]
    
        test = session.query(Product).filter(Product.title == title).first()
        if test is None:
            product = Product(title=title, url=url, group_id=pg.id)
            session.add(product)

    session.flush()
    session.commit()

def get_product_price(title, url):
    try:
        r = requests.get(url)
        if not r.status_code == 200:
            sys.stderr.write('Failed to download product page for: %s\n' % (title))
            return None, None
    except Exception:
        return None, None

    soup = BeautifulSoup(r.text)

    try:
        price_span = soup.find('span', id='actualPriceValue')
        price = str(price_span.contents[0].text)
    except Exception:
        price = None

    try:
        price_value_span = soup.find('span', id='listPriceValue')
        price_value = str(price_value_span.contents[0])
    except Exception:
        price_value = None

    return price, price_value

def price_to_int(price_text):
    if price_text[0] == '$':
        price_text = price_text[1:]
    price_parts = price_text.split('.')
    return int(price_parts[0]) * 100 + int(price_parts[1])

def download_price_data():
    now = datetime.datetime.now()
    td = datetime.timedelta(hours=6)
    fetch_date = now - td
    
    products = session.query(Product).all()
    for p in products:
        ll = session.query(ProductPrice)\
                    .filter(ProductPrice.product_id == p.id)\
                    .order_by(ProductPrice.created.desc())\
                    .first()
        
        if ll is None or (ll.created - fetch_date) <= td:
            # Fetch new price data
            price, price_regular = get_product_price(p.title, p.url)
            if price is None:
                continue
        
            price_int = price_to_int(price)
            if price_regular is None:
                price_regular_int = 0
            else:
                price_regular_int = price_to_int(price_regular)
            
            pp = ProductPrice(  product_id=p.id,
                                price_sale=price_int,
                                price_regular=price_regular_int)
        
            session.add(pp)
    session.commit()

def main():
    global session
    
    manager = SessionManager('sqlite:///products.db')
    session = manager.session
    
    auto_load_products()
    download_price_data()
    sys.exit(0)

if __name__ == '__main__':
    # Auto-change directory
    name = sys.argv[0]
    dir_path = os.path.dirname(name)
    os.chdir(dir_path)
    
    main()

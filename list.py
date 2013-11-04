#!/usr/bin/python

import os, sys, datetime
import products

from operator import itemgetter
from app.db import *
session = None

def price_int_to_str(price_int):
    a = price_int / 100
    b = price_int - (a * 100)
    return '%s.%s' % (a, b)

def best_deals(products):
    def sortfn(item):
        return item[1] - item[2]

    return sorted(products, key=sortfn, reverse=False)

def cheapest_deals(products):
    return sorted(products, key=itemgetter(1))

def print_products(title, products):
    print('-'*80)
    print(title)
    print('-'*80)
    for i in products:
        print('$%s\t$%s\t- %s' % (i[3], i[4], i[0]))

def main():
    global session
    
    """
    
    TODO: Find products with prices trending up/down
    TODO: List items by group
    
    """
    
    manager = SessionManager('sqlite:///products.db')
    session = manager.session
    
    res = session.query(Product)\
                      .order_by(Product.title)\
                      .all()
    
    products = []
    groups = {}
    
    for p in res:
        if p.group_id not in groups:
            pg = session.query(ProductGroup)\
                        .filter(ProductGroup.id == p.group_id)\
                        .first()
            groups[p.group_id] = pg
        
        pg = groups[p.group_id]
        pp = session.query(ProductPrice)\
                    .filter(ProductPrice.product_id == p.id)\
                    .order_by(ProductPrice.created.desc())\
                    .first()
        
        products.append((   p.title,
                            pp.price_sale,
                            pp.price_regular,
                            price_int_to_str(pp.price_sale),
                            price_int_to_str(pp.price_regular),
                            pg.name))
    
    items = [
        ('Cheapest Deals', cheapest_deals(products)),
        ('Best Deals', best_deals(products)),
    ]
    
    for title, plist in items:
        print_products(title, plist)

    sys.exit(0)

if __name__ == '__main__':
    main()

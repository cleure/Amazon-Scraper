#!/usr/bin/python

import os, sys, datetime, argparse

from operator import itemgetter
from app.db import *
session = None

def str_align(string, align, separator=' ', mode='prefix'):
    out = str(string)
    buf = ''
    align = align - len(string)
    
    for i in range(align):
        buf += str(separator)
    
    if mode == 'prefix':
        return buf + out

    return out + buf

def price_int_to_str(price_int):
    a = price_int / 100
    b = str(price_int - (a * 100))
    
    return '%d.%s' % (a, str_align(b, 2, '0'))

def best_deals(products, number=10):
    return sorted(products, key=itemgetter('price_diff'), reverse=True)[0:number]

def cheapest_deals(products, number=8):
    return sorted(products, key=itemgetter('price_sale'))[0:number]

def print_products(title, group, products, num=8):
    print('-'*80)
    print('%s in %s' % (title, group))
    print('-'*80)
    
    for p in products:
        print('$%s$%s%s- %s' % (
            str_align(price_int_to_str(p['price_sale']), 8, mode='suffix'),
            str_align(price_int_to_str(p['price_regular']), 8, mode='suffix'),
            str_align('($'+price_int_to_str(p['price_diff'])+')', 8, mode='suffix'),
            p['title']
        )
    )

def main():
    global session
    
    functions = [
        ('Cheapest Deals', cheapest_deals),
        ('Best Deals', best_deals),
    ]
    
    parser = argparse.ArgumentParser()
    parser.add_argument(    '-n', '--number',
                            help='Number of items per group to print',
                            type=int,
                            default=10)
    
    args = parser.parse_args()
    print_number = args.number
    
    if args.number is not None:
        print_number = args.number
    
    manager = SessionManager('sqlite:///products.db')
    session = manager.session

    groups = session.query(ProductGroup)\
                    .order_by(ProductGroup.name)

    for group in groups:
        products = []
        queryobj = session.query(Product)\
                          .filter(Product.group_id == group.id)\
                          .order_by(Product.title)

        for pr in queryobj:
            pp = session.query(ProductPrice)\
                        .filter(ProductPrice.product_id == pr.id)\
                        .order_by(ProductPrice.created.desc())\
                        .first()

            item = {
                'title': pr.title,
                'price_sale': pp.price_sale,
            }
            
            if pp.price_regular == 0:
                item['price_diff'] = 0
                item['price_regular'] = pp.price_sale
            else:
                item['price_diff'] = pp.price_regular - pp.price_sale
                item['price_regular'] = pp.price_regular

            products.append(item)

        for title, fn in functions:
            print_products(title, group.name, fn(products, args.number))

    sys.exit(0)

if __name__ == '__main__':
    main()

#!/usr/bin/python

import os, sys, datetime, argparse

from app.pricefuncs import price_int_to_str, str_align
from app.db import *
session = None

def print_group(title, group):
    print('-'*80)
    print('%s in %s' % (title, group))
    print('-'*80)

def print_product(p):
    savings = 0
    if p.price_savings is not None:
        savings = int(p.price_savings)

    print('$%s$%s%s - %s' % (
        str_align(price_int_to_str(p.price_sale), 8, mode='suffix'),
        str_align(price_int_to_str(p.price_regular), 8, mode='suffix'),
        str_align('($'+price_int_to_str(savings)+')', 8, mode='suffix'),
        p.title
        )
    )

def main():
    global session
    
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

    sort_modes = [
        ('Cheapest Deals', Product.sort_price),
        ('Best Deals', Product.sort_savings.desc())
    ]

    for group in groups:
        products = []
        
        for sort_title, sort_ctx in sort_modes:
            queryobj = session.query(Product)\
                              .filter(Product.group_id == group.id)\
                              .order_by(sort_ctx)\
                              .limit(print_number)
        
            print_group(sort_title, group.name)
            for p in queryobj:
                print_product(p)

    sys.exit(0)

if __name__ == '__main__':
    main()

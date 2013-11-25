#!/usr/bin/python

import os, sys, datetime, argparse
from operator import itemgetter

from app.pricefuncs import price_int_to_str, str_align
from app.db import *
session = None

def reindex_products():
    global session

    now = datetime.datetime.utcnow()
    td = datetime.timedelta(days=7)

    products = session.query(Product)
    for p in products:
        pp = session.query(ProductPrice)\
                    .filter(ProductPrice.product_id == p.id)\
                    .order_by(ProductPrice.created.desc())\
                    .first()

        # Update broken field
        if pp.created < (now - td):
            p.broken = 1
        else:
            p.broken = 0

        price = pp.price_sale
        regular = pp.price_regular

        # Add shipping
        if pp.shipping is not None and pp.shipping > 0:
            price += pp.shipping
            if regular is not None and regular > 0:
                regular += pp.shipping

        # Calculate savings
        if regular is not None and regular > price:
            savings = regular - price
        else:
            regular = int(price)
            savings = 0
    
        p.price_sale = price
        p.price_regular = regular
        p.price_savings = savings
        p.sort_price = price
        p.sort_savings = savings
        session.add(p)
    
    session.flush()
    session.commit()

def reindex_history():
    # TODO: Reindex product prices, over time.
    return

def main():
    global session
    
    manager = SessionManager('sqlite:///products.db')
    session = manager.session
    
    reindex_products()
    reindex_history()

if __name__ == '__main__':
    main()

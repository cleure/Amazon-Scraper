#!/usr/bin/python

import os, sys, datetime, argparse
from operator import itemgetter
from app.db import *

session = None

def most_common(values):
    """ Mode filter, which falls back to Median when there are multiple items
        which are 'most common'. """
    
    counts = {v: 0 for v in values}
    for v in values:
        counts[v] += 1

    _sorted = sorted(list(counts.items()), key=itemgetter(1), reverse=True)
    last = _sorted[0][1]
    median = []

    for i in _sorted:
        if not i[1] == last:
            break
        median.append(i[0])

    median.sort()
    return median[int(len(median)//2)]

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

def index_daily_history():
    global session

    products = session.query(Product)
    for p in products:
        most_recent = session.query(ProductPriceHistory.date_of)\
                             .filter(   ProductPriceHistory.product_id == p.id,
                                        ProductPriceHistory.date_range == 'D')\
                             .order_by(ProductPriceHistory.date_of.desc())\
                             .limit(1)\
                             .first()
    
        if most_recent is None:
            # Does not contain any entries... Create them.
            
            pps = session.query(ProductPrice.price_sale,
                                ProductPrice.shipping,
                                ProductPrice.created)\
                         .order_by(ProductPrice.created.desc())\
                         .filter(ProductPrice.product_id == p.id)
        else:
            # Contains previous entries. Calculate previous day, if not
            # already processed.
            
            where = (   'product_id = :id AND '
                        'created > :date_of')
            
            where_date_of = datetime.date(most_recent.date_of.year,
                                          most_recent.date_of.month,
                                          most_recent.date_of.day)
            
            where_date_of += datetime.timedelta(days=1)
            
            pps = session.query(ProductPrice.price_sale,
                                ProductPrice.shipping,
                                ProductPrice.created)\
                         .order_by(ProductPrice.created.desc())\
                         .filter(where)\
                         .params(id=p.id, date_of=str(where_date_of))
        
        daily = {}
        for pp in pps:
            idx = (pp.created.year, pp.created.month, pp.created.day)
            if idx not in daily:
                daily[idx] = []
            daily[idx].append(pp)

        for k, v in daily.items():
            v = most_common(v)
            ph = ProductPriceHistory(
                product_id=p.id,
                price=(v.price_sale + v.shipping),
                date_range='D',
                date_of = datetime.datetime(*k)
            )

            session.add(ph)

        session.flush()
        session.commit()

def index_weekly_history():
    global session
    
    """
    
    Bucket items based on week of month...
        - First week of month starts on first day of month, and spans 7 days.
        - Repeats until last day of month reached.
    
    """
    
    now = datetime.datetime.utcnow()
    day_of_week = int(now.strftime('%w'))
    tmp = now - datetime.timedelta(days=day_of_week)
    last_week = datetime.datetime(tmp.year, tmp.month, tmp.day)
    
    print(last_week)

def index_monthly_history():
    global session
    pass

def index_history():


    """
    
    TODO: Calculate weekly:
                - Select daily items from product_price_history for given (past) week.
                - Perform most_common() for each result list.
                - Result of most_common() is weekly.
        
          Calculate monthly:
                - select weekly items from product_price_history for given (past) month.
                - Perform most_common() for each result list.
                - Result of most_common() is monthly.
    
    """

    index_daily_history()
    index_weekly_history()
    index_monthly_history()

def main():
    global session
    
    manager = SessionManager('sqlite:///products.db')
    session = manager.session
    
    reindex_products()
    index_history()

if __name__ == '__main__':
    main()

#!/usr/bin/python

import os, sys, datetime, argparse
from operator import itemgetter
from app.db import *
import config

session = None

def most_common(values, keyidx=None):
    """ Mode filter, which falls back to Median when there are multiple items
        which are 'most common'. """
    
    counts = {v: 0 for v in values}
    for v in values:
        counts[v] += 1

    if keyidx is None or not isinstance(keyidx, int):
        _sorted = sorted(list(counts.items()), reverse=True)
    else:
        _sorted = sorted(list(counts.items()), key=itemgetter(keyidx), reverse=True)

    last = _sorted[0][1]
    median = []

    for i in _sorted:
        if not i[1] == last:
            break
        median.append(i[0])

    median.sort()
    return median[int(len(median)//2)]

def get_trending(history):
    """ Get current trend, and its distance. history parameter should be a list
        of numbers, ordered by time descending. Returns tuple(trend, dist). """

    a = history[0]
    dist = 0
    trend = None
    _cur_trend = None
    
    for b in history[1:]:
        _cur_trend = 'U' if a > b else 'D' if a < b else 'S'
        if trend is None:
            trend = _cur_trend
        elif not _cur_trend == trend:
            break
        
        dist += 1

    return (trend, dist)

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
    
        # Calculate Trending
        res = session.query(ProductPriceHistory)\
                     .filter(ProductPriceHistory.product_id == p.id)\
                     .order_by(ProductPriceHistory.date_of.desc())\
                     .limit(30)\
                     .all()

        if res is not None:
            trending, trending_dist = get_trending([i.price for i in res])
        else:
            trending = None
            trending_dist = 0
            
        p.trending = trending
        p.trending_dist = trending_dist
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
            v = most_common(v, keyidx=1)
            ph = ProductPriceHistory(
                product_id=p.id,
                price=(v.price_sale + v.shipping),
                date_range='D',
                date_of = datetime.datetime(*k)
            )

            session.add(ph)

        session.flush()
        session.commit()

def prune_price_data():
    global session

    # Don't prune data?
    if (not isinstance(config.scraper['prune_days'], int) or
        config.scraper['prune_days'] <= 0):
        return
    
    td = datetime.timedelta(days=config.scraper['prune_days'])
    ts = datetime.datetime.utcnow() - td
    rows = 0

    for p in session.query(Product):
        pph = session.query(ProductPriceHistory)\
                     .filter(ProductPriceHistory.date_range == 'D')\
                     .order_by(ProductPriceHistory.date_of.desc())\
                     .first()

        # Check that item has been processed
        if pph is None or pph.date_of < ts:
            continue

        # Delete old ProductPrice entries
        res = session.query(ProductPrice)\
                     .filter(ProductPrice.product_id == p.id,
                             ProductPrice.created < ts).delete()
        
        # Increment deleted rows
        if isinstance(res, int):
            rows += res
    
    return rows

def index_monthly_history():
    global session
    pass

def index_history():


    """
    
    TODO:
          Calculate monthly:
                - select weekly items from product_price_history for given (past) month.
                - Perform most_common() for each result list.
                - Result of most_common() is monthly.
    
    """

    index_daily_history()

def main():
    global session
    
    manager = SessionManager('sqlite:///products.db')
    session = manager.session
    
    index_history()
    reindex_products()
    prune_price_data()

if __name__ == '__main__':
    main()

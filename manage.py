#!/usr/bin/python

import os, sys, argparse, datetime
from app.db import *

session = None

def error_exit(msg):
    sys.stderr.write(msg + '\n')
    sys.exit(1)

def action_add(args):
    global session

    if args.title is None or args.url is None or args.group is None:
        error_exit('Arguments title, group, and url are required for action "add"')

    pg = session.query(ProductGroup)\
                .filter(ProductGroup.name == args.group)\
                .first()

    if pg is None:
        pg = ProductGroup(name=str(args.group))
        session.add(pg)
        session.flush()

    product = Product(title=args.title, url=args.url, group_id=pg.id)
    session.add(product)
    session.commit()

def action_update(args):
    global session

    if args.id is None:
        error_exit('--id is required for action "update"')

    if args.title is None and args.group is None and args.url is None:
        error_exit('One of title, url, group is required for action "update"')

    product = session.query(Product)\
                     .filter(Product.id == args.id)\
                     .first()

    if args.group is not None:
        pg = session.query(ProductGroup)\
                    .filter(ProductGroup.name == args.group)\
                    .first()

        if pg is None:
            pg = ProductGroup(name=args.group)
            session.add(pg)
            session.flush()
        
        product.group_id = pg.id
    
    if args.url is not None:
        product.url = args.url
    
    if args.title is not None:
        product.title = args.title

    session.add(product)
    session.commit()

def action_remove(args):
    global session

    if args.id is None:
        error_exit('--id is required for action "remove"')

    product = session.query(Product)\
                     .filter(Product.id == args.id)\
                     .first()

    if product is None:
        error_exit('No such product titled "%s"' % (args.title))

    session.delete(product)
    session.commit()

def action_list(args):
    global session

    queryobj = session.query(Product, ProductGroup)\
                      .join(ProductGroup, Product.group_id == ProductGroup.id)\
                      .order_by(ProductGroup.name, Product.title)

    if args.group is not None:
        queryobj = queryobj.filter(ProductGroup.name == str(args.group))

    products = queryobj.all()
    last_group = None
    for p, g in products:
        pp = session.query(ProductPrice)\
                    .filter(ProductPrice.product_id == p.id)\
                    .order_by(ProductPrice.created.desc())\
                    .limit(1)\
                    .first()
        
        if not g.name == last_group:
            print('-'*80)
            last_group = g.name

        last_fetch = '       N/A'
        if pp is not None:
            last_fetch = pp.created.strftime('%Y-%m-%d')

        print('%s\t| %s | %s | %s' % (p.id, last_fetch, g.name, p.title))

def action_prune(args):
    """ Delete hanging references to deleted objects. """
    global session
    
    # Prune Product Groups
    pgs = session.query(ProductGroup).all()
    for pg in pgs:
        test = session.query(Product)\
                      .filter(Product.group_id == pg.id)\
                      .first()
        
        if test is None:
            session.delete(pg)

    # Prune Product Price data
    pps = session.query(ProductPrice).all()
    for pp in pps:
        test = session.query(Product)\
                      .filter(Product.id == pp.product_id)\
                      .first()

        if test is None:
            session.delete(pp)
    
    session.commit()

def main():
    global session
    
    fntable = {
        'add': action_add,
        'update': action_update,
        'remove': action_remove,
        'list': action_list,
        'prune': action_prune
    }
    
    manager = SessionManager('sqlite:///products.db')
    session = manager.session
    
    parser = argparse.ArgumentParser()
    parser.add_argument(    'action',
                            help='Available Actions: add, update, remove, list, prune',
                            choices=['add', 'update', 'remove', 'list', 'prune'])

    parser.add_argument('--id', help='ID of Product (for update/remove)')
    parser.add_argument('--title', help='Title of Product')
    parser.add_argument('--group', help='Name of Group product should be in')
    parser.add_argument('--url', help='URL of Product')
    #parser.add_argument('--broken', help='URL of Product')

    args = parser.parse_args()
    fntable[args.action](args)
    sys.exit(0)

if __name__ == '__main__':
    main()

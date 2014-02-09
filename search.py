import os, sys, datetime, argparse
import requests, re
from bs4 import BeautifulSoup
from app.db import *
from app.searcher import *
import config

"""

TODO:
    - Show number of search results/pages
    - Ability to add product based on search result
    - Search Terms needs its own table, to not break caching between departments.

"""

session = None
product_searcher = None

def action_search(args):
    global session, product_searcher
    
    if args.keywords is None:
        raise ArgumentError('Action search requires --keywords argument')
    
    if args.page is not None:
        page = int(args.page)
    else:
        page = 1
    
    keywords = args.keywords
    results = product_searcher.search(
        keywords,
        category=args.category,
        page=page)

    columns = [
        ('id', 'SEARCH RESULT ID'),
        ('price_sale', 'Price (Sale)'),
        ('price_regular', 'Price'),
        ('category', 'Category'),
        ('sub_category', 'Sub-Category'),
        ('url', 'URL'),
    ]

    for r in results:
        print('')
        print(r.title.strip())
        print('=' * 80)
        for field, label in columns:
            print('%s: %s' % (label, getattr(r, field)))

def action_add(args):
    global session, product_searcher

def action_prune(args):
    global session, product_searcher

def main():
    global session, product_searcher

    fntable = {
        'search': action_search,
        'add': action_add,
        'prune': action_prune
    }
    
    parser = argparse.ArgumentParser()
    parser.add_argument(    'action',
                            help='Available Actions: search, add, prune',
                            choices=['search', 'prune', 'add'])

    parser.add_argument('--id', help='ID for Search Result to add')
    parser.add_argument('--keywords', help='Keywords to search for')
    parser.add_argument('--category', help='Category/Department to perform search in')
    parser.add_argument('--page', help='Page of search results')
    args = parser.parse_args()

    manager = SessionManager('sqlite:///products.db')
    session = manager.session
    
    product_searcher = ProductSearcher(session)
    product_searcher.prune_cache(config.search['prune_cache'])
    
    fntable[args.action](args)
    sys.exit(0)

if __name__ == '__main__':
    main()

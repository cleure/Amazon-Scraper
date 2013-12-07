#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, datetime, argparse
from operator import itemgetter
from app.db import *
from PIL import Image, ImageDraw, ImageFont

try:
    import queue
except ImportError:
    import Queue as queue

session = None

def price2str(price):
    a = price / 100
    b = price - (a * 100)
    return '$' + str(a) + '.' + str(b)

def plot_days(product, width=640):
    def itox(i):
        return int(int(i * x_scale) * woff[0] + (height * woff[1]))

    def price2y(price):
        c = int((price - _min) * y_scale)
        return int((abs(c - height) - 1) * hoff[0] + (height * hoff[1]))

    path = os.path.join('private/days', str(product.id) + '.png')
    
    product_group = session.query(ProductGroup)\
                           .filter(ProductGroup.id == product.group_id)\
                           .first()
    
    most_recent = session.query(ProductPrice)\
                         .filter(ProductPrice.product_id == product.id)\
                         .order_by(ProductPrice.created.desc())\
                         .limit(1)\
                         .first()
    
    pps = session.query(ProductPriceHistory)\
                 .filter(ProductPriceHistory.product_id == product.id)\
                 .order_by(ProductPriceHistory.date_of.desc())\
                 .limit(30).all()

    pps.reverse()
    _min = pps[0].price
    _max = pps[0].price
    _min_pp = pps[0]
    _max_pp = pps[0]
    
    for pp in pps:
        if pp.price < _min:
            _min = pp.price
            _min_pp = pp
        if pp.price > _max:
            _max = pp.price
            _max_pp = pp

    # Graph title
    graph_title_color = (255, 255, 255)
    graph_subtitle_color = graph_title_color
    graph_title = '(%s) %s' % (product_group.name, product.title)
    graph_sub_title = ''

    # Sub title
    if most_recent is not None:
        mrp = most_recent.price_sale
        if most_recent.shipping:
            try:
                mrp += int(most_recent.shipping)
            except ValueError: pass

        if product.trending == 'U':
            trending_text = 'up +%s' % (product.trending_dist)
            graph_subtitle_color = (255, 32, 32)
        elif product.trending == 'D':
            trending_text = 'down -%s' % (product.trending_dist)
            graph_subtitle_color = (32, 255, 32)
        else:
            trending_text = 'stable %s' % (product.trending_dist)
            graph_subtitle_color = (192, 192, 192)
        
        graph_sub_title = ' Most Recent: %s (%s)' % (price2str(mrp), trending_text)

    # Date start/end labels
    date_st = pps[0].date_of.strftime('%Y-%m-%d')
    date_en = pps[-1].date_of.strftime('%Y-%m-%d')

    # Calculate dimensions
    height = int(width * 0.5)
    font_size_sm = int(width * 0.0171875)
    font_size_lg = int(width * 0.025)
    point_radius = int(width * 0.0046875)
    line_width = int(width * 0.0015625)

    padding = (
        font_size_sm * 4,
        font_size_sm // 2,
        font_size_sm * 6,
        font_size_sm * 0.7272727272727273,
        width * 0.00625,                            # Text X/Y Padding (left align)
        width * 0.00625 + font_size_lg * 1.05,      # Sub-Title Y Padding
    )

    # Draw offsets
    draw_height = int(height / 2)
    woff = (0.92, 0.17)
    hoff = (0.5, 0.25)

    # Scales
    min_max = (float(_max) - float(_min)) + 1
    x_scale = float(width) / float(len(pps))
    y_scale = float(height) / min_max
    
    # Create image/draw/font instances
    b = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(b)
    font_sm = ImageFont.truetype('font/BPG_Courier.ttf', font_size_sm)
    font_lg = ImageFont.truetype('font/BPG_Courier.ttf', font_size_lg)
    
    min_y = price2y(_min)
    max_y = price2y(_max)

    # Draw graph background
    for x in range(len(pps)):
        xx = itox(x)
        draw.line((xx, min_y, xx, max_y), (64, 64, 64), width=line_width)

    # Graph corner x/y pairs
    xs = itox(0), itox(len(pps)-1)
    ys = min_y, max_y

    # Draw graph border
    draw.line((xs[0], ys[0], xs[1], ys[0]), (128, 128, 128), width=line_width)
    draw.line((xs[0], ys[1], xs[1], ys[1]), (128, 128, 128), width=line_width)
    draw.line((xs[0], ys[0], xs[0], ys[1]), (128, 128, 128), width=line_width)
    draw.line((xs[1], ys[0], xs[1], ys[1]), (128, 128, 128), width=line_width)

    # Render title and labels
    draw.text((padding[4], padding[4]), graph_title, font=font_lg, fill=graph_title_color)
    draw.text((padding[4], padding[5]), graph_sub_title, font=font_lg, fill=graph_subtitle_color)
    draw.text((padding[4], ys[0]-padding[1]), price2str(_min_pp.price), font=font_sm)
    draw.text((padding[4], ys[1]-padding[1]), price2str(_max_pp.price), font=font_sm)
    draw.text((xs[0], ys[0]+padding[3]), date_st, font=font_sm)
    draw.text((xs[1]-padding[2], ys[0]+padding[3]), date_en, font=font_sm)

    # Process x/y points
    points = queue.Queue()
    for x in range(len(pps)):
        pp = pps[x]
        xx = itox(x)
        yy = price2y(pp.price)
        points.put((xx, yy))

        # Plot graph points at x/y
        ellipse_box = (
            xx-point_radius, yy-point_radius,
            xx+point_radius, yy+point_radius)
        
        draw.ellipse(ellipse_box, outline=(255, 255, 255))

    # Plot graph lines
    pa = points.get()
    while not points.empty():
        pb = points.get()
        draw.line((pa[0], pa[1], pb[0], pb[1]), (255, 255, 255), width=line_width)
        pa = pb

    b.save(path)

def main():
    global session
    
    manager = SessionManager('sqlite:///products.db')
    session = manager.session

    for p in session.query(Product):
        plot_days(p, width=1000)

    sys.exit(0)

if __name__ == '__main__':
    main()

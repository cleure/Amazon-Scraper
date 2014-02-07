import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy import ForeignKey, Table, UniqueConstraint, Index
from sqlalchemy.orm import relationship, backref, validates
from base import *

class ProductGroup(Base):
    __tablename__ = 'product_groups'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(64), index=True, unique=True, nullable=False)

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, nullable=False)
    group_id = Column(Integer, ForeignKey('product_groups.id'), index=True)
    title = Column(String(64), nullable=False)
    url = Column(Text, nullable=False)
    broken = Column(Integer, index=True, default=0)
    
    price_sale = Column(Integer)
    price_regular = Column(Integer)
    price_savings = Column(Integer)
    trending = Column(String, index=True)
    trending_dist = Column(Integer)
    sort_price = Column(Integer, index=True)
    sort_savings = Column(Integer, index=True)

    __table_args__ = (
        UniqueConstraint('title', 'group_id', name='products_title_group_id_uc'),
        Index('products_title_group_id_idx', 'title', 'group_id'),
    )

    @validates(trending)
    def validate_trending(self, key, value):
        assert value in set(['U', 'D', 'S'])

class ProductPrice(Base):
    __tablename__ = 'product_prices'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), index=True)
    price_sale = Column(Integer)
    items_left = Column(Integer)
    price_regular = Column(Integer)
    shipping = Column(Integer)
    created = Column(DateTime, default=created_modified_default, index=True)

class ProductPriceHistory(Base):
    __tablename__ = 'product_price_history'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), index=True)
    price = Column(Integer)
    date_range = Column(String(1), index=True)
    date_of = Column(DateTime, index=True)
    
    @validates(date_range)
    def validate_date_range(self, key, value):
        assert value in set(['D', 'W', 'M'])
        return value

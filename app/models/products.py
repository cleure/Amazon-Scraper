import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy import ForeignKey, Table, UniqueConstraint, Index
from sqlalchemy.orm import relationship, backref, validates
from base import *

def created_modified_default():
    return datetime.datetime.utcnow()

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
    sort_price = Column(Integer, index=True)
    sort_savings = Column(Integer, index=True)

    __table_args__ = (
        UniqueConstraint('title', 'group_id', name='products_title_group_id_uc'),
        Index('products_title_group_id_idx', 'title', 'group_id'),
    )

class ProductPrice(Base):
    __tablename__ = 'product_prices'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), index=True)
    price_sale = Column(Integer)
    items_left = Column(Integer)
    price_regular = Column(Integer)
    shipping = Column(Integer)
    created = Column(DateTime, default=created_modified_default, index=True)
    modified = Column(DateTime, default=created_modified_default,
                      onupdate=created_modified_default,
                      index=True)

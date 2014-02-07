import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy import ForeignKey, Table, UniqueConstraint, Index
from sqlalchemy.orm import relationship, backref, validates
from base import *

class SearchResultCached(Base):
    __tablename__ = 'search_results_cache'

    id = Column(Integer, primary_key=True, nullable=False)
    sort_index = Column(Integer)
    search_keywords = Column(String(64), index=True)
    
    # Product Details
    title = Column(String(128))
    url = Column(String(128))
    category = Column(String(64))
    sub_category = Column(String(64))
    price_sale = Column(String(32))
    price_regular = Column(String(32))
    created = Column(DateTime, default=created_modified_default, index=True)

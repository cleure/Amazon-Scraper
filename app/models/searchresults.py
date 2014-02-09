import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy import ForeignKey, Table, UniqueConstraint, Index
from sqlalchemy.orm import relationship, backref, validates
from base import *

class SearchResultCached(Base):
    __tablename__ = 'search_results_cache'

    id = Column(Integer, primary_key=True, nullable=False)
    sort_index = Column(Integer)
    page_num = Column(Integer)
    search_keywords = Column(String(64))
    
    # Product Details
    title = Column(String(128))
    url = Column(String(128))
    category = Column(String(64))
    sub_category = Column(String(64))
    price_sale = Column(String(32))
    price_regular = Column(String(32))
    created = Column(DateTime, default=created_modified_default, index=True)

    __table_args__ = (
        Index('search_results_cache_num_keyw_idx', 'search_keywords', 'page_num'),
    )

class SearchTerm(Base):
    __tablename__ = 'search_terms'

    id = Column(Integer, primary_key=True, nullable=False)
    search_keywords = Column(String(64))
    pages = Column(Integer)
    results = Column(Integer)
    created = Column(DateTime, default=created_modified_default, index=True)

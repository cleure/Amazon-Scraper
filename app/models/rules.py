import datetime
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import ForeignKey, Table, UniqueConstraint, Index
from sqlalchemy.orm import relationship, backref, validates
from base import *

class ListRule(Base):
    __tablename__ = 'list_rules'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), index=True, nullable=False)
    rule_type = Column(String(64), nullable=False)
    rule_amount_int = Column(Integer)
    rule_amount_float = Column(Float)

    @validates('rule_type')
    def validate_rule_type(self, key, value):
        assert value in set(['price_below', 'savings_above'])
        return value

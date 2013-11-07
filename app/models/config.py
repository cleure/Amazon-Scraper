import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy import ForeignKey, Table, UniqueConstraint, Index
from sqlalchemy.orm import relationship, backref, validates
from base import *

class ConfigOption(Base):
    __tablename__ = 'config_options'

    id = Column(Integer, primary_key=True)
    section = Column(String(64), index=True)
    name = Column(String(64))
    value = Column(Text)

    __table_args__ = (
        UniqueConstraint('section', 'name', name='config_options_section_name_uc'),
        Index('config_options_name_value_idx', 'section', 'name'),
    )

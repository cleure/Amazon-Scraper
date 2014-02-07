from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

def created_modified_default():
    return datetime.datetime.utcnow()

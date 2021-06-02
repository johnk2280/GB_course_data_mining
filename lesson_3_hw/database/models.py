from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    Table
)

from datetime import datetime

Base = declarative_base()

tag_post = Table(
    'tag_post',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    url = Column(String(2048), nullable=False, unique=True)
    title = Column(String, nullable=False, unique=False)
    img_link = Column(String, nullable=True, unique=False)
    post_date = Column(DateTime)
    author_id = Column(Integer, ForeignKey('author.id'), nullable=False)
    author = relationship('Author', backref='posts')


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    url = Column(String(2048), nullable=False, unique=True)
    name = Column(String(250), nullable=False, unique=False)
    gb_id = Column(Integer, nullable=False, unique=True)


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    url = Column(String(2048), nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)


class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True, unique=True)
    parent_id = Column(Integer, ForeignKey('comment.id'), nullable=False)
    likes_count = Column(Integer)
    body = Column(String)
    created_at = Column(DateTime, nullable=False)
    hidden = Column(Boolean)
    deep = Column(Integer)
    time_now = Column(DateTime)
    author_id = Column(Integer, ForeignKey('author.id'), nullable=False)
    author = relationship('Author', backref='comments')
    post_id = Column(Integer, ForeignKey('post.id'), nullable=False)
    post = relationship('Post', backref='posts')

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.parent_id = kwargs['parent_id']  # зачем нужен если это foreign key
        self.likes_count = kwargs['likes_count']
        self.body = kwargs['body']
        self.created_at = datetime.fromisoformat(kwargs['created_at'])
        self.hidden = kwargs['hidden']
        self.deep = kwargs['deep']
        self.time_now = datetime.fromisoformat(kwargs['time_now'])


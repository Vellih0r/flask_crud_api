import pytest
from db import *

del_table(tb = 'books')
create(tb = 'books')

insert(data = {"id" : 2, "title" : "aboba2", "rating" : 3})
res = read(tb = 'books')
print(res)
print(isinstance(res, list))

def test_insert():
    out = insert(data = {"id" : 1, "title" : "Harry Potter", "rating" : 4})
    assert out == True

def test_insert_many():
    out = insert(data = [{"id" : 2, "title" : "aboba2", "rating" : 3}, {"id" : 3, "title" : "aboba3", "rating" : 5}])
    assert out == True

def test_read():
    out = read()
    print(out)
    assert out != None

def test_read_one():
    out = read_one(id = 2)
    print(out)
    assert out != None

def test_update_one():
    out = update(tb = 'books', data = {"id" : 1, "title" : "aaa", "rating" : 1}, id = 1)
    assert out == True
    print(read_one(id = 2))

def test_update_many():
    out = update(tb = 'books', data = [{"id" : 2, "title" : "bbb", "rating" : 1}, {"id" : 3, "title" : "vvv", "rating" : 1}], id = 2)
    assert out == True
    print(read())

def test_del():
    out = del_one(tb = 'books', id = 2)
    assert out == True
    print(read())
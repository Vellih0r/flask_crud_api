from flask import Flask, request, jsonify
from json import dumps
from decimal import Decimal
from cache import *
from db.db import *

app = Flask(__name__)

def dumps_default(data):
    converter = lambda el : float(el) if isinstance(el, Decimal) else str(el)
    return dumps(data, default=converter)

@app.route('/<table>', methods = ['POST'])
def init(table):
    result = create(table)
    return jsonify(f"Table {table} created", 201)

@app.route('/<table>', methods = ['GET'])
def get_all(table):
    if out :=  get_keys():
        return jsonify(out, 200)
    result = read(table)
    if not result:
        return jsonify(f"Table {table} not found", 404)
    for row in result:
        setex_key(f'{table}:{row.get("id")}', dumps_default(row))
    return jsonify(result, 200)

@app.route('/<table>/<int:id>', methods = ['GET'])
def get_one(table, id):
    if out := get_key(f'{table}:{id}'):
        return jsonify(out, 200)
    result = read_one(table, id)
    if not result:
        return jsonify(f"Row {id} not found", 404)
    setex_key(f'{table}:{id}', dumps_default(result))
    return jsonify(result, 200)

@app.route('/<table>/<int:id>', methods = ['POST'])
def add(table, id):
    data = request.json
    if isinstance(data, dict):
        insert(table, data, id)
        setex_key(f'{table}:{id}', dumps_default(data))
    if isinstance(data, list):
        for row in data:
            insert(table, row, row.get("id"))
            setex_key(f'{table}:{row.get("id")}', dumps_default(row))
    return jsonify("Success add row(s)", 200)

@app.route('/<table>/<int:id>', methods = ['PATCH'])
def update(table, id):
    data = request.json
    if isinstance(data, dict):
        update_db(table, data, id)
        setex_key(f'{table}:{id}', dumps_default(data))
    if isinstance(data, list):
        for row in data:
            update_db(table, row, row.get("id"))
            setex_key(f'{table}:{row.get("id")}', dumps_default(row))
    return jsonify("Success update row(s)", 200)

@app.route('/<table>', methods = ['DELETE'])
def delete_all(table):
    del_table(table)
    del_keys()
    return jsonify(f"Success delete table {table}", 200)

@app.route('/<table>/<int:id>', methods = ['DELETE'])
def delete_row(table, id):
    del_one(table, id)
    del_key(f'{table}:{id}')
    return jsonify(f"Success delete table row {id} from {table}", 200)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000)
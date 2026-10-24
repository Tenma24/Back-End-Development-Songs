import json
import os
from pathlib import Path
from urllib.parse import quote_plus
from bson import json_util
from flask import jsonify, request
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from . import app

server = os.environ.get('MONGODB_SERVICE', '127.0.0.1:27017')
username = os.environ.get('MONGODB_USERNAME')
password = os.environ.get('MONGODB_PASSWORD', '')
auth = f'{quote_plus(username)}:{quote_plus(password)}@' if username else ''
client = MongoClient(os.environ.get('MONGODB_URI', f'mongodb://{auth}{server}'), serverSelectionTimeoutMS=5000)
db = client[os.environ.get('MONGODB_DATABASE', 'capstone_songs')]
db.songs.create_index('id', unique=True)
for song in json.loads((Path(__file__).parent / 'data/songs.json').read_text(encoding='utf-8')):
    db.songs.update_one({'id': song['id']}, {'$setOnInsert': song}, upsert=True)

def parse_json(value):
    return json.loads(json_util.dumps(value))

@app.errorhandler(PyMongoError)
def database_error(error):
    app.logger.error('MongoDB operation failed: %s', type(error).__name__)
    return jsonify(message='Database unavailable'), 503

@app.get('/health')
def health():
    client.admin.command('ping')
    return jsonify(status='OK')

@app.get('/count')
def count():
    return jsonify(count=db.songs.count_documents({}))

@app.get('/song')
def songs():
    return jsonify(songs=parse_json(list(db.songs.find().sort('id', 1))))

@app.get('/song/<int:id>')
def get_song(id):
    song = db.songs.find_one({'id': id})
    return (jsonify(parse_json(song)), 200) if song else (jsonify(message=f'song with id {id} not found'), 404)

def valid(data, partial=False):
    return (isinstance(data, dict) and bool(data) and not (set(data) - {'id', 'title', 'lyrics'})
            and (partial or type(data.get('id')) is int)
            and all(isinstance(data.get(k), str) and data[k].strip() for k in ('title', 'lyrics') if not partial or k in data))

@app.post('/song')
def post_song():
    data = request.get_json(silent=True)
    if not valid(data):
        return jsonify(message='Provide integer id and nonempty title and lyrics'), 400
    try:
        result = db.songs.insert_one(data)
    except DuplicateKeyError:
        return jsonify(Message=f"song with id {data['id']} already present"), 302
    return jsonify({'inserted id': parse_json(result.inserted_id)}), 201

@app.put('/song/<int:id>')
def put_song(id):
    if not db.songs.find_one({'id': id}):
        return jsonify(message='song not found'), 404
    data = request.get_json(silent=True)
    if not valid(data, partial=True) or ('id' in data and (type(data['id']) is not int or data['id'] != id)):
        return jsonify(message='Invalid update'), 400
    result = db.songs.update_one({'id': id}, {'$set': data})
    if not result.modified_count:
        return jsonify(message='song found, but nothing updated'), 200
    return jsonify(parse_json(db.songs.find_one({'id': id}))), 201

@app.delete('/song/<int:id>')
def delete_song(id):
    if db.songs.delete_one({'id': id}).deleted_count:
        return '', 204
    return jsonify(message='song not found'), 404

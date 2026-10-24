import uuid
from backend.routes import db

def test_crud_and_validation(client):
    song_id = uuid.uuid4().int % 1000000000 + 1000
    data = {'id': song_id, 'title': 'Capstone test', 'lyrics': 'An original test verse.'}
    try:
        assert client.post('/song', json=data).status_code == 201
        assert client.post('/song', json=data).status_code == 302
        assert client.get(f'/song/{song_id}').json['title'] == data['title']
        assert client.put(f'/song/{song_id}', json={'title': 'Updated'}).status_code == 201
        assert client.put(f'/song/{song_id}', json={'$set': {'title': 'bad'}}).status_code == 400
        assert client.put(f'/song/{song_id}', json={'id': song_id + 1}).status_code == 400
        assert client.delete(f'/song/{song_id}').status_code == 204
        assert client.get(f'/song/{song_id}').status_code == 404
        assert client.delete(f'/song/{song_id}').status_code == 404
        assert client.post('/song', json={'id': 'bad'}).status_code == 400
        assert isinstance(client.get('/song').json['songs'], list)
        assert client.get('/count').json['count'] >= 1
    finally:
        db.songs.delete_one({'id': song_id})

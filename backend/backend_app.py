from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    # Hole die Sortierparameter aus der URL
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction', 'asc')

    # Validiere die Parameter
    valid_sort_fields = ['title', 'content']
    valid_directions = ['asc', 'desc']

    if sort_field and sort_field not in valid_sort_fields:
        return jsonify({
            'error': f'Invalid sort field. Must be one of: {", ".join(valid_sort_fields)}'
        }), 400

    if sort_direction not in valid_directions:
        return jsonify({
            'error': f'Invalid sort direction. Must be one of: {", ".join(valid_directions)}'
        }), 400

    # Kopiere die Posts-Liste, um die Originaldaten nicht zu verändern
    sorted_posts = POSTS.copy()

    # Sortiere die Posts, wenn ein Sortierfeld angegeben wurde
    if sort_field:
        sorted_posts.sort(
            key=lambda x: x[sort_field],
            reverse=(sort_direction == 'desc')
        )

    return jsonify(sorted_posts)


@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()

    # Überprüfe ob title und content vorhanden sind
    if not data or 'title' not in data or 'content' not in data:
        missing_fields = []
        if not data or 'title' not in data:
            missing_fields.append('title')
        if not data or 'content' not in data:
            missing_fields.append('content')
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    # Generiere eine neue eindeutige ID
    new_id = max([post['id'] for post in POSTS]) + 1

    # Erstelle neuen Post
    new_post = {
        'id': new_id,
        'title': data['title'],
        'content': data['content']
    }

    # Füge den Post zur Liste hinzu
    POSTS.append(new_post)

    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    # Finde den Post mit der gegebenen ID
    post_index = None
    for index, post in enumerate(POSTS):
        if post['id'] == post_id:
            post_index = index
            break

    # Wenn kein Post gefunden wurde, gebe 404 zurück
    if post_index is None:
        return jsonify({'error': f'Post with id {post_id} not found'}), 404

    # Lösche den Post aus der Liste
    POSTS.pop(post_index)

    return jsonify({'message': f'Post with id {post_id} has been deleted successfully.'}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()

    # Finde den Post mit der gegebenen ID
    post = None
    for p in POSTS:
        if p['id'] == post_id:
            post = p
            break

    # Wenn kein Post gefunden wurde, gebe 404 zurück
    if post is None:
        return jsonify({'error': f'Post with id {post_id} not found'}), 404

    # Aktualisiere die Felder, wenn sie im Request vorhanden sind
    if data.get('title') is not None:
        post['title'] = data['title']
    if data.get('content') is not None:
        post['content'] = data['content']

    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    # Hole die Suchparameter aus der URL
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    # Filtere die Posts nach den Suchkriterien
    matching_posts = [
        post for post in POSTS
        if (title_query and title_query in post['title'].lower()) or
           (content_query and content_query in post['content'].lower())
    ]

    return jsonify(matching_posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)

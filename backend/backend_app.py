"""
Backend application for the Masterblog API.
Provides RESTful endpoints for managing blog posts, comments, and likes.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# File path for JSON storage
JSON_FILE = os.path.join(os.path.dirname(__file__), 'data', 'posts.json')

# Swagger Configuration
SWAGGER_URL = '/api/docs'
API_URL = '/static/masterblog.json'

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)

app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

def load_posts() -> list:
    """
    Load posts from JSON file. Creates file with empty posts list if it doesn't exist.

    Returns:
        list: List of blog posts
    """
    try:
        with open(JSON_FILE, 'r') as file:
            data = json.load(file)
            return data.get('posts', [])
    except FileNotFoundError:
        os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)
        with open(JSON_FILE, 'w') as file:
            json.dump({'posts': []}, file)
        return []
    except json.JSONDecodeError:
        return []

def save_posts(posts: list) -> None:
    """
    Save posts to JSON file.

    Args:
        posts (list): List of blog posts to save
    """
    os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)
    with open(JSON_FILE, 'w') as file:
        json.dump({'posts': posts}, file, indent=4)

@app.route('/static/<path:path>')
def send_static(path):
    """
    Serve static files for Swagger documentation.

    Args:
        path (str): Path to the static file

    Returns:
        Response: Static file response
    """
    return send_from_directory('static', path)

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Retrieve all blog posts with optional sorting.

    Query Parameters:
        sort (str): Field to sort by ('id', 'title', 'content', 'author', or 'date')
        direction (str): Sort direction ('asc' or 'desc')

    Returns:
        tuple: JSON response with posts and HTTP status code
    """
    posts = load_posts()
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction', 'asc')

    valid_sort_fields = ['id', 'title', 'content', 'author', 'date']
    valid_directions = ['asc', 'desc']

    if sort_field and sort_field not in valid_sort_fields:
        return jsonify({
            'error': f'Invalid sort field. Must be one of: {", ".join(valid_sort_fields)}'
        }), 400

    if sort_direction not in valid_directions:
        return jsonify({
            'error': f'Invalid sort direction. Must be one of: {", ".join(valid_directions)}'
        }), 400

    if sort_field:
        reverse = sort_direction == 'desc'
        if sort_field == 'date':
            posts.sort(
                key=lambda x: datetime.strptime(x[sort_field], '%Y-%m-%d'),
                reverse=reverse
            )
        else:
            posts.sort(
                key=lambda x: x[sort_field],
                reverse=reverse
            )

    return jsonify(posts)

@app.route('/api/posts', methods=['POST'])
def add_post():
    """
    Create a new blog post.

    Request Body:
        title (str): Title of the post
        content (str): Content of the post
        author (str): Author of the post
        date (str): Date of the post in YYYY-MM-DD format (optional)

    Returns:
        tuple: JSON response with created post and HTTP status code
    """
    data = request.get_json()
    posts = load_posts()

    required_fields = ['title', 'content', 'author']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    if 'date' in data:
        try:
            datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Date must be in YYYY-MM-DD format'}), 400
    else:
        data['date'] = datetime.now().strftime('%Y-%m-%d')

    new_id = max([post['id'] for post in posts], default=0) + 1

    new_post = {
        'id': new_id,
        'title': data['title'],
        'content': data['content'],
        'author': data['author'],
        'date': data['date']
    }

    posts.append(new_post)
    save_posts(posts)

    return jsonify(new_post), 201

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Update a blog post by its ID.

    Parameters:
        post_id (int): ID of the post to update

    Request Body:
        title (str, optional): New title for the post
        content (str, optional): New content for the post
        author (str, optional): New author for the post
        date (str, optional): New date for the post in YYYY-MM-DD format

    Returns:
        JSON: Updated post object
        int: HTTP status code
    """
    data = request.get_json()
    posts = load_posts()

    post = None
    for p in posts:
        if p['id'] == post_id:
            post = p
            break

    if post is None:
        return jsonify({'error': f'Post with id {post_id} not found'}), 404

    if 'date' in data:
        try:
            datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Date must be in YYYY-MM-DD format'}), 400

    updateable_fields = ['title', 'content', 'author', 'date']
    for field in updateable_fields:
        if field in data:
            post[field] = data[field]

    save_posts(posts)
    return jsonify(post), 200

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Delete a blog post by its ID.

    Parameters:
        post_id (int): ID of the post to delete

    Returns:
        JSON: Success/error message
        int: HTTP status code
    """
    posts = load_posts()

    post_index = None
    for index, post in enumerate(posts):
        if post['id'] == post_id:
            post_index = index
            break

    if post_index is None:
        return jsonify({'error': f'Post with id {post_id} not found'}), 404

    posts.pop(post_index)
    save_posts(posts)

    return jsonify({'message': f'Post with id {post_id} has been deleted successfully.'}), 200

@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Search for blog posts by id, title, content, author, or date.

    Query Parameters:
        id (str): Search term for ID
        title (str): Search term for title
        content (str): Search term for content
        author (str): Search term for author
        date (str): Search term for date (YYYY-MM-DD format)

    Returns:
        JSON: List of matching posts
        int: HTTP status code
    """
    posts = load_posts()

    search_params = {
        'id': request.args.get('id', ''),
        'title': request.args.get('title', '').lower(),
        'content': request.args.get('content', '').lower(),
        'author': request.args.get('author', '').lower(),
        'date': request.args.get('date', '')
    }

    matching_posts = [
        post for post in posts
        if (search_params['id'] and str(post['id']) == search_params['id']) or  # ID search added
           (search_params['title'] and search_params['title'] in post['title'].lower()) or
           (search_params['content'] and search_params['content'] in post['content'].lower()) or
           (search_params['author'] and search_params['author'] in post['author'].lower()) or
           (search_params['date'] and search_params['date'] in post['date'])
    ]

    return jsonify(matching_posts)

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id: int):
    """
    Increment the like counter for a specific post.

    Args:
        post_id (int): ID of the post to like

    Returns:
        tuple: JSON response with updated like count and HTTP status code
    """
    posts = load_posts()

    for post in posts:
        if post['id'] == post_id:
            if 'likes' not in post:
                post['likes'] = 0
            post['likes'] += 1
            save_posts(posts)
            return jsonify({'likes': post['likes']}), 200

    return jsonify({'error': 'Post not found'}), 404

@app.route('/api/posts/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id: int):
    """
    Add a comment to a blog post.

    Args:
        post_id (int): ID of the post to comment on

    Request Body:
        author (str): Author of the comment
        content (str): Content of the comment

    Returns:
        tuple: JSON response with updated post and HTTP status code
    """
    data = request.get_json()
    posts = load_posts()

    if not data or 'content' not in data or 'author' not in data:
        return jsonify({'error': 'Comment must include author and content'}), 400

    post = next((p for p in posts if p['id'] == post_id), None)

    if post is None:
        return jsonify({'error': f'Post with id {post_id} not found'}), 404

    if 'comments' not in post:
        post['comments'] = []

    comment = {
        'author': data['author'],
        'content': data['content'],
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    post['comments'].append(comment)

    save_posts(posts)
    return jsonify(post), 200

if __name__ == '__main__':
    # Ensure posts.json exists when starting the server
    load_posts()
    app.run(host="0.0.0.0", port=5002, debug=True)

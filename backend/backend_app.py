from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

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

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files for Swagger documentation."""
    return send_from_directory('static', path)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Retrieve all blog posts with optional sorting.

    Query Parameters:
        sort (str): Field to sort by ('title' or 'content')
        direction (str): Sort direction ('asc' or 'desc')

    Returns:
        JSON: List of blog posts
        int: HTTP status code
    """
    # Get sorting parameters from URL
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction', 'asc')

    # Validate parameters
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

    # Copy posts list to avoid modifying the original
    sorted_posts = POSTS.copy()

    # Sort posts if sort field is provided
    if sort_field:
        sorted_posts.sort(
            key=lambda x: x[sort_field],
            reverse=(sort_direction == 'desc')
        )

    return jsonify(sorted_posts)

@app.route('/api/posts', methods=['POST'])
def add_post():
    """
    Create a new blog post.

    Request Body:
        title (str): Title of the post
        content (str): Content of the post

    Returns:
        JSON: Created post object
        int: HTTP status code
    """
    data = request.get_json()

    # Check if title and content are provided
    if not data or 'title' not in data or 'content' not in data:
        missing_fields = []
        if not data or 'title' not in data:
            missing_fields.append('title')
        if not data or 'content' not in data:
            missing_fields.append('content')
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    # Generate new unique ID
    new_id = max([post['id'] for post in POSTS]) + 1

    # Create new post
    new_post = {
        'id': new_id,
        'title': data['title'],
        'content': data['content']
    }

    # Add post to the list
    POSTS.append(new_post)

    return jsonify(new_post), 201

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
    # Find post with given ID
    post_index = None
    for index, post in enumerate(POSTS):
        if post['id'] == post_id:
            post_index = index
            break

    # Return 404 if post not found
    if post_index is None:
        return jsonify({'error': f'Post with id {post_id} not found'}), 404

    # Remove post from list
    POSTS.pop(post_index)

    return jsonify({'message': f'Post with id {post_id} has been deleted successfully.'}), 200

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Update a blog post by its ID.

    Parameters:
        post_id (int): ID of the post to update

    Request Body:
        title (str, optional): New title for the post
        content (str, optional): New content for the post

    Returns:
        JSON: Updated post object
        int: HTTP status code
    """
    data = request.get_json()

    # Find post with given ID
    post = None
    for p in POSTS:
        if p['id'] == post_id:
            post = p
            break

    # Return 404 if post not found
    if post is None:
        return jsonify({'error': f'Post with id {post_id} not found'}), 404

    # Update fields if provided in request
    if data.get('title') is not None:
        post['title'] = data['title']
    if data.get('content') is not None:
        post['content'] = data['content']

    return jsonify(post), 200

@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Search for blog posts by title or content.

    Query Parameters:
        title (str): Search term for title
        content (str): Search term for content

    Returns:
        JSON: List of matching posts
        int: HTTP status code
    """
    # Get search parameters from URL
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    # Filter posts based on search criteria
    matching_posts = [
        post for post in POSTS
        if (title_query and title_query in post['title'].lower()) or
           (content_query and content_query in post['content'].lower())
    ]

    return jsonify(matching_posts)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)

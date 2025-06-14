from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime

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
    {
        "id": 1,
        "title": "First post",
        "content": "This is the first post.",
        "author": "John Doe",
        "date": "2025-06-15"
    },
    {
        "id": 2,
        "title": "Second post",
        "content": "This is the second post.",
        "author": "Jane Smith",
        "date": "2025-06-14"
    }
]

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Retrieve all blog posts with optional sorting.

    Query Parameters:
        sort (str): Field to sort by ('title', 'content', 'author', or 'date')
        direction (str): Sort direction ('asc' or 'desc')

    Returns:
        JSON: List of blog posts
        int: HTTP status code
    """
    # Get sorting parameters from URL
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction', 'asc')

    # Validate parameters
    valid_sort_fields = ['title', 'content', 'author', 'date']
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
        # Special handling for date field
        if sort_field == 'date':
            sorted_posts.sort(
                key=lambda x: datetime.strptime(x[sort_field], '%Y-%m-%d'),
                reverse=(sort_direction == 'desc')
            )
        else:
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
        author (str): Author of the post
        date (str): Date of the post in YYYY-MM-DD format

    Returns:
        JSON: Created post object
        int: HTTP status code
    """
    data = request.get_json()

    # Check if required fields are provided
    required_fields = ['title', 'content', 'author']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    # Validate date format if provided, otherwise use current date
    if 'date' in data:
        try:
            datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Date must be in YYYY-MM-DD format'}), 400
    else:
        data['date'] = datetime.now().strftime('%Y-%m-%d')

    # Generate new unique ID
    new_id = max([post['id'] for post in POSTS]) + 1

    # Create new post
    new_post = {
        'id': new_id,
        'title': data['title'],
        'content': data['content'],
        'author': data['author'],
        'date': data['date']
    }

    # Add post to the list
    POSTS.append(new_post)

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

    # Find post with given ID
    post = None
    for p in POSTS:
        if p['id'] == post_id:
            post = p
            break

    # Return 404 if post not found
    if post is None:
        return jsonify({'error': f'Post with id {post_id} not found'}), 404

    # Validate date format if provided
    if 'date' in data:
        try:
            datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Date must be in YYYY-MM-DD format'}), 400

    # Update fields if provided in request
    updateable_fields = ['title', 'content', 'author', 'date']
    for field in updateable_fields:
        if field in data:
            post[field] = data[field]

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

@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Search for blog posts by title, content, author, or date.

    Query Parameters:
        title (str): Search term for title
        content (str): Search term for content
        author (str): Search term for author
        date (str): Search term for date (YYYY-MM-DD format)

    Returns:
        JSON: List of matching posts
        int: HTTP status code
    """
    # Get search parameters from URL
    search_params = {
        'title': request.args.get('title', '').lower(),
        'content': request.args.get('content', '').lower(),
        'author': request.args.get('author', '').lower(),
        'date': request.args.get('date', '')
    }

    # Filter posts based on search criteria
    matching_posts = [
        post for post in POSTS
        if (search_params['title'] and search_params['title'] in post['title'].lower()) or
           (search_params['content'] and search_params['content'] in post['content'].lower()) or
           (search_params['author'] and search_params['author'] in post['author'].lower()) or
           (search_params['date'] and search_params['date'] in post['date'])
    ]

    return jsonify(matching_posts)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)

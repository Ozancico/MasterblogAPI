/**
 * Main JavaScript file for the blog frontend application.
 * Handles all client-side functionality including post management,
 * comments, likes, and UI interactions.
 */

// Initialize the application when the window loads
window.onload = function() {
    // Load posts immediately when page loads
    loadPosts();

    // Set default date to today for the date input
    document.getElementById('post-date').valueAsDate = new Date();
}

/**
 * Toggle visibility of dropdown menus
 * @param {string} dropdownId - ID of the dropdown to toggle
 */
function toggleDropdown(dropdownId) {
    event.stopPropagation();  // Prevent event bubbling

    // Close all other dropdowns first
    const dropdowns = document.getElementsByClassName("dropdown-content");
    Array.from(dropdowns).forEach(dropdown => {
        if (dropdown.id !== dropdownId) {
            dropdown.classList.remove('show');
        }
    });

    // Toggle the selected dropdown
    document.getElementById(dropdownId).classList.toggle("show");
}

// Close dropdowns when clicking outside
window.onclick = function(event) {
    // Don't close if clicking on form elements
    if (['SELECT', 'OPTION', 'INPUT'].includes(event.target.tagName)) {
        return;
    }

    // Don't close if clicking inside dropdown content
    if (event.target.closest('.dropdown-content')) {
        return;
    }

    // Close all open dropdowns
    const dropdowns = document.getElementsByClassName("dropdown-content");
    Array.from(dropdowns).forEach(dropdown => {
        if (dropdown.classList.contains('show')) {
            dropdown.classList.remove('show');
        }
    });
}

/**
 * Toggle visibility of comments section for a post
 * @param {number} postId - ID of the post
 */
function toggleComments(postId) {
    const commentsSection = document.getElementById(`comments-section-${postId}`);
    const toggleButton = document.getElementById(`toggle-comments-${postId}`);

    if (commentsSection.style.display === 'none') {
        commentsSection.style.display = 'block';
        toggleButton.innerHTML = '<i class="fas fa-chevron-up"></i>';
    } else {
        commentsSection.style.display = 'none';
        toggleButton.innerHTML = '<i class="fas fa-chevron-down"></i>';
    }
}

/**
 * Load and display all blog posts
 */
function loadPosts() {
    const baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    fetch(`${baseUrl}/posts`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            data.sort((a, b) => new Date(b.date) - new Date(a.date));

            data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';
                const formattedDate = new Date(post.date).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });

                // Initialize likes and comments if not present
                const likes = post.likes || 0;
                const comments = post.comments || [];
                const hasLiked = localStorage.getItem(`liked-post-${post.id}`) === 'true';

                const commentsHtml = comments.map(comment => `
                    <div class="comment">
                        <p class="comment-content">${comment.content}</p>
                        <p class="comment-meta">By ${comment.author} on ${comment.date}</p>
                    </div>
                `).join('');

                postDiv.innerHTML = `
                    <div class="post-content">
                        <h2>${post.title}</h2>
                        <p>${post.content}</p>
                        <p class="post-meta">By ${post.author} on ${formattedDate}</p>
                        <p class="post-id">ID: ${post.id}</p>
                    </div>

                    <div class="post-actions">
                        <div class="action-group-left">
                            <button onclick="updatePost(${post.id})" class="update-btn" title="Edit Post">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button onclick="likePost(${post.id})" id="like-btn-${post.id}"
                                    class="like-btn ${hasLiked ? 'liked' : ''}"
                                    ${hasLiked ? 'disabled' : ''}
                                    title="${hasLiked ? 'Already liked' : 'Like post'}">
                                👍 <span class="like-count">${likes}</span>
                            </button>
                            <button onclick="openCommentModal(${post.id})" class="comment-btn" title="Add Comment">
                                <i class="far fa-comment"></i> <span class="comment-count">${comments.length}</span>
                            </button>
                            <button id="toggle-comments-${post.id}"
                                    onclick="toggleComments(${post.id})"
                                    class="toggle-comments-btn"
                                    title="Toggle Comments">
                                <i class="fas fa-chevron-down"></i>
                            </button>
                        </div>
                        <div class="action-group-right">
                            <button onclick="deletePost(${post.id})" class="delete-btn" title="Delete Post">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>

                    <div id="comments-section-${post.id}" class="comments-section" style="display: none;">
                        <h3><i class="far fa-comments"></i> Comments (${comments.length})</h3>
                        ${commentsHtml}
                    </div>`;

                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to load posts. Please check your API URL.');
        });
}

/**
 * Add a new blog post
 */
function addPost() {
    const baseUrl = document.getElementById('api-base-url').value;
    const postTitle = document.getElementById('post-title').value.trim();
    const postContent = document.getElementById('post-content').value.trim();
    const postAuthor = document.getElementById('post-author').value.trim();
    const postDate = document.getElementById('post-date').value;

    if (!postTitle || !postContent || !postAuthor) {
        alert('Please fill in all required fields (Title, Content, and Author)');
        return;
    }

    fetch(`${baseUrl}/posts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: postTitle,
            content: postContent,
            author: postAuthor,
            date: postDate
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(post => {
        console.log('Post added:', post);
        document.getElementById('post-title').value = '';
        document.getElementById('post-content').value = '';
        loadPosts();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to add post. Please try again.');
    });
}

/**
 * Delete a blog post
 * @param {number} postId - ID of the post to delete
 */
function deletePost(postId) {
    if (!confirm('Are you sure you want to delete this post?')) {
        return;
    }

    const baseUrl = document.getElementById('api-base-url').value;

    fetch(`${baseUrl}/posts/${postId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        console.log('Post deleted:', postId);
        loadPosts();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to delete post. Please try again.');
    });
}

/**
 * Search posts based on selected criteria
 */
function searchPosts() {
    const baseUrl = document.getElementById('api-base-url').value;
    const searchField = document.getElementById('search-field').value;
    const searchTerm = document.getElementById('search-term').value.trim();

    if (!searchField || !searchTerm) {
        alert('Please select a search field and enter a search term');
        return;
    }

    const searchUrl = `${baseUrl}/posts/search?${searchField}=${encodeURIComponent(searchTerm)}`;

    fetch(searchUrl)
        .then(response => response.json())
        .then(data => {
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            if (data.length === 0) {
                postContainer.innerHTML = '<p>No matching posts found.</p>';
                return;
            }

            data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';
                const formattedDate = new Date(post.date).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });

                // Initialize likes and comments if not present
                const likes = post.likes || 0;
                const comments = post.comments || [];
                const hasLiked = localStorage.getItem(`liked-post-${post.id}`) === 'true';

                const commentsHtml = comments.map(comment => `
                    <div class="comment">
                        <p class="comment-content">${comment.content}</p>
                        <p class="comment-meta">By ${comment.author} on ${comment.date}</p>
                    </div>
                `).join('');

                postDiv.innerHTML = `
                    <div class="post-content">
                        <h2>${post.title}</h2>
                        <p>${post.content}</p>
                        <p class="post-meta">By ${post.author} on ${formattedDate}</p>
                        <p class="post-id">ID: ${post.id}</p>
                    </div>

                    <div class="post-actions">
                        <div class="action-group-left">
                            <button onclick="updatePost(${post.id})" class="update-btn" title="Edit Post">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button onclick="likePost(${post.id})" id="like-btn-${post.id}" class="like-btn">
                                👍 <span class="like-count">${likes}</span>
                            </button>
                            <button onclick="openCommentModal(${post.id})" class="comment-btn" title="Add Comment">
                                <i class="far fa-comment"></i> <span class="comment-count">${comments.length}</span>
                            </button>
                            <button id="toggle-comments-${post.id}"
                                    onclick="toggleComments(${post.id})"
                                    class="toggle-comments-btn"
                                    title="Toggle Comments">
                                <i class="fas fa-chevron-down"></i>
                            </button>
                        </div>
                        <div class="action-group-right">
                            <button onclick="deletePost(${post.id})" class="delete-btn" title="Delete Post">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>

                    <div id="comments-section-${post.id}" class="comments-section" style="display: none;">
                        <h3><i class="far fa-comments"></i> Comments (${comments.length})</h3>
                        ${commentsHtml}
                    </div>`;

                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error searching posts. Please try again.');
        });
}

/**
 * Sort posts based on selected field and direction
 */
function sortPosts() {
    var baseUrl = document.getElementById('api-base-url').value;
    var sortField = document.getElementById('sort-field').value;
    var sortDirection = document.getElementById('sort-direction').value;

    if (!sortField) {
        alert('Please select a sort field');
        return;
    }

    // Build the sort URL with query parameters
    var sortUrl = `${baseUrl}/posts?sort=${sortField}&direction=${sortDirection}`;

    fetch(sortUrl)
        .then(response => response.json())
        .then(data => {
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';
                const formattedDate = new Date(post.date).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });

                // Initialize likes and comments if not present
                const likes = post.likes || 0;
                const comments = post.comments || [];
                const hasLiked = localStorage.getItem(`liked-post-${post.id}`) === 'true';

                const commentsHtml = comments.map(comment => `
                    <div class="comment">
                        <p class="comment-content">${comment.content}</p>
                        <p class="comment-meta">By ${comment.author} on ${comment.date}</p>
                    </div>
                `).join('');

                postDiv.innerHTML = `
                    <div class="post-content">
                        <h2>${post.title}</h2>
                        <p>${post.content}</p>
                        <p class="post-meta">By ${post.author} on ${formattedDate}</p>
                        <p class="post-id">ID: ${post.id}</p>
                    </div>

                    <div class="post-actions">
                        <div class="action-group-left">
                            <button onclick="updatePost(${post.id})" class="update-btn" title="Edit Post">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button onclick="likePost(${post.id})" id="like-btn-${post.id}" class="like-btn">
                                👍 <span class="like-count">${likes}</span>
                            </button>
                            <button onclick="openCommentModal(${post.id})" class="comment-btn" title="Add Comment">
                                <i class="far fa-comment"></i> <span class="comment-count">${comments.length}</span>
                            </button>
                            <button id="toggle-comments-${post.id}"
                                    onclick="toggleComments(${post.id})"
                                    class="toggle-comments-btn"
                                    title="Toggle Comments">
                                <i class="fas fa-chevron-down"></i>
                            </button>
                        </div>
                        <div class="action-group-right">
                            <button onclick="deletePost(${post.id})" class="delete-btn" title="Delete Post">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>

                    <div id="comments-section-${post.id}" class="comments-section" style="display: none;">
                        <h3><i class="far fa-comments"></i> Comments (${comments.length})</h3>
                        ${commentsHtml}
                    </div>`;

                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error sorting posts. Please try again.');
        });
}

/**
 * Like a post
 * @param {number} postId - ID of the post to like
 */
async function likePost(postId) {
    // Check if the user has already liked this post
    if (localStorage.getItem(`liked-post-${postId}`) === 'true') {
        alert('You have already liked this post!');
        return;
    }

    const baseUrl = document.getElementById('api-base-url').value;
    try {
        const response = await fetch(`${baseUrl}/posts/${postId}/like`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        // Save the like status in localStorage
        localStorage.setItem(`liked-post-${postId}`, 'true');

        // Update the like counter in the DOM
        const likeButton = document.querySelector(`#like-btn-${postId}`);
        const likeCount = likeButton.querySelector('.like-count');
        likeCount.textContent = data.likes;

        // Disable the button and add the 'liked' class
        likeButton.disabled = true;
        likeButton.classList.add('liked');

    } catch (error) {
        console.error('Error:', error);
        alert('Error liking the post');
    }
}

let currentPostId = null;

/**
 * Open the comment modal for a post
 * @param {number} postId - ID of the post
 */
function openCommentModal(postId) {
    currentPostId = postId;
    const modal = document.getElementById('comment-modal');
    modal.style.display = 'block';

    // Close modal when clicking on X
    const closeBtn = document.getElementsByClassName('close')[0];
    closeBtn.onclick = function() {
        modal.style.display = 'none';
    }

    // Close modal when clicking outside
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
}

/**
 * Submit a new comment to the API
 */
function submitComment() {
    if (!currentPostId) return;

    const author = document.getElementById('comment-author').value.trim();
    const content = document.getElementById('comment-content').value.trim();
    const baseUrl = document.getElementById('api-base-url').value;

    if (!author || !content) {
        alert('Please fill in both name and comment');
        return;
    }

    fetch(`${baseUrl}/posts/${currentPostId}/comment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ author, content })
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(() => {
        // Clear form and close modal
        document.getElementById('comment-author').value = '';
        document.getElementById('comment-content').value = '';
        document.getElementById('comment-modal').style.display = 'none';

        // Reload posts to show new comment
        loadPosts();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to add comment. Please try again.');
    });
}

let postToUpdate = null;

/**
 * Open the update modal for a post
 * @param {number} postId - ID of the post to update
 */
function updatePost(postId) {
    postToUpdate = postId;
    const baseUrl = document.getElementById('api-base-url').value;

    // Fetch current post data
    fetch(baseUrl + '/posts')
        .then(response => response.json())
        .then(data => {
            const post = data.find(p => p.id === postId);
            if (post) {
                // Fill the update form with current values
                document.getElementById('update-title').value = post.title;
                document.getElementById('update-content').value = post.content;
                document.getElementById('update-author').value = post.author;
                document.getElementById('update-date').value = post.date;

                // Show the modal
                document.getElementById('update-modal').style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to load post data for update.');
        });
}

/**
 * Close the update modal
 */
function closeUpdateModal() {
    document.getElementById('update-modal').style.display = 'none';
    postToUpdate = null;
}

/**
 * Submit the updated post data to the API
 */
function submitUpdate() {
    if (!postToUpdate) return;

    const baseUrl = document.getElementById('api-base-url').value;
    const updatedData = {
        title: document.getElementById('update-title').value.trim(),
        content: document.getElementById('update-content').value.trim(),
        author: document.getElementById('update-author').value.trim(),
        date: document.getElementById('update-date').value
    };

    // Validate required fields
    if (!updatedData.title || !updatedData.content || !updatedData.author) {
        alert('Please fill in all required fields (Title, Content, and Author)');
        return;
    }

    fetch(`${baseUrl}/posts/${postToUpdate}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedData)
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(() => {
        closeUpdateModal();
        loadPosts();  // Reload all posts to show the update
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to update post. Please try again.');
    });
}

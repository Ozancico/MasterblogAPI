// Function that runs once the window is fully loaded
window.onload = function() {
    // Attempt to retrieve the API base URL from the local storage
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');
    // If a base URL is found in local storage, load the posts
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }

    // Set default date to today for the date input
    document.getElementById('post-date').valueAsDate = new Date();
}

// Function to toggle dropdown menus
function toggleDropdown(dropdownId) {
    event.stopPropagation();  // Prevent event from bubbling up

    // Close all dropdowns first
    var dropdowns = document.getElementsByClassName("dropdown-content");
    for (var i = 0; i < dropdowns.length; i++) {
        if (dropdowns[i].id !== dropdownId) {
            dropdowns[i].classList.remove('show');
        }
    }

    // Toggle the selected dropdown
    document.getElementById(dropdownId).classList.toggle("show");
}

// Close dropdown if user clicks outside
window.onclick = function(event) {
    // Don't close if clicking on a select element or its options
    if (event.target.tagName === 'SELECT' ||
        event.target.tagName === 'OPTION' ||
        event.target.tagName === 'INPUT') {
        return;
    }

    // Don't close if clicking inside the dropdown content
    if (event.target.closest('.dropdown-content')) {
        return;
    }

    // Close all dropdowns if clicking outside
    var dropdowns = document.getElementsByClassName("dropdown-content");
    for (var i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        if (openDropdown.classList.contains('show')) {
            openDropdown.classList.remove('show');
        }
    }
}

// Function to fetch all the posts from the API and display them on the page
function loadPosts() {
    // Retrieve the base URL from the input field and save it to local storage
    var baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    // Use the Fetch API to send a GET request to the /posts endpoint
    fetch(baseUrl + '/posts')
        .then(response => response.json())  // Parse the JSON data from the response
        .then(data => {  // Once the data is ready, we can use it
            // Clear out the post container first
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            // Sort posts by date in descending order (newest first)
            data.sort((a, b) => new Date(b.date) - new Date(a.date));

            // For each post in the response, create a new post element and add it to the page
            data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';
                // Format the date for better readability
                const formattedDate = new Date(post.date).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
                postDiv.innerHTML = `
                    <h2>${post.title}</h2>
                    <p>${post.content}</p>
                    <p class="post-meta">By ${post.author} on ${formattedDate}</p>
                    <button onclick="deletePost(${post.id})">Delete</button>`;
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to load posts. Please check your API URL.');
        });
}

// Function to send a POST request to the API to add a new post
function addPost() {
    // Retrieve the values from the input fields
    var baseUrl = document.getElementById('api-base-url').value;
    var postTitle = document.getElementById('post-title').value.trim();
    var postContent = document.getElementById('post-content').value.trim();
    var postAuthor = document.getElementById('post-author').value.trim();
    var postDate = document.getElementById('post-date').value;

    // Validate required fields
    if (!postTitle || !postContent || !postAuthor) {
        alert('Please fill in all required fields (Title, Content, and Author)');
        return;
    }

    // Use the Fetch API to send a POST request to the /posts endpoint
    fetch(baseUrl + '/posts', {
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
        // Clear the input fields after successful post
        document.getElementById('post-title').value = '';
        document.getElementById('post-content').value = '';
        // Don't clear author as it's likely to be reused
        loadPosts(); // Reload the posts after adding a new one
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to add post. Please try again.');
    });
}

// Function to send a DELETE request to the API to delete a post
function deletePost(postId) {
    if (!confirm('Are you sure you want to delete this post?')) {
        return;
    }

    var baseUrl = document.getElementById('api-base-url').value;

    // Use the Fetch API to send a DELETE request to the specific post's endpoint
    fetch(baseUrl + '/posts/' + postId, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        console.log('Post deleted:', postId);
        loadPosts(); // Reload the posts after deleting one
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to delete post. Please try again.');
    });
}

// Function to search posts based on selected field and search term
function searchPosts() {
    var baseUrl = document.getElementById('api-base-url').value;
    var searchField = document.getElementById('search-field').value;
    var searchTerm = document.getElementById('search-term').value.trim();

    if (!searchField || !searchTerm) {
        alert('Please select a field and enter a search term');
        return;
    }

    // Build the search URL with query parameters
    var searchUrl = `${baseUrl}/posts/search?${searchField}=${encodeURIComponent(searchTerm)}`;

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
                postDiv.innerHTML = `
                    <h2>${post.title}</h2>
                    <p>${post.content}</p>
                    <p class="post-meta">By ${post.author} on ${formattedDate}</p>
                    <button onclick="deletePost(${post.id})">Delete</button>`;
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to search posts. Please try again.');
        });
}

// Function to sort posts based on selected field and direction
function sortPosts() {
    var baseUrl = document.getElementById('api-base-url').value;
    var sortField = document.getElementById('sort-field').value;
    var sortDirection = document.getElementById('sort-direction').value;

    if (!sortField) {
        alert('Please select a field to sort by');
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
                postDiv.innerHTML = `
                    <h2>${post.title}</h2>
                    <p>${post.content}</p>
                    <p class="post-meta">By ${post.author} on ${formattedDate}</p>
                    <button onclick="deletePost(${post.id})">Delete</button>`;
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to sort posts. Please try again.');
        });
}

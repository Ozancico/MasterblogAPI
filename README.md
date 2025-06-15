# Masterblog API

A modern blog platform built with Flask, featuring a RESTful API backend and an interactive frontend.

## Features

- Create, Read, Update, and Delete blog posts
- Comment system
- Like functionality
- Search and sort posts
- Dark mode support
- Pagination
- Responsive design
- Interactive UI with animations

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Masterblog-API
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install flask flask-cors flask-swagger-ui
```

## Running the Application

1. Start the backend server:
```bash
python backend/backend_app.py
```
The backend will run on http://localhost:5002

2. In a new terminal, start the frontend server:
```bash
python frontend/frontend_app.py
```
The frontend will run on http://localhost:5004

3. Open your browser and navigate to http://localhost:5004

## API Documentation

API documentation is available at http://localhost:5002/api/docs when the backend server is running.

## Technologies Used

- Backend:
  - Flask
  - Flask-CORS
  - Flask-Swagger-UI
  - JSON for data storage

- Frontend:
  - HTML5
  - CSS3
  - JavaScript (ES6+)
  - Font Awesome
  - Google Fonts (Poppins)

## Features

- **Post Management:**
  - Create new posts
  - Edit existing posts
  - Delete posts
  - View all posts with pagination

- **Interaction:**
  - Like posts
  - Add comments
  - Search posts
  - Sort posts by various criteria

- **UI/UX:**
  - Dark/Light mode
  - Responsive design
  - Loading animations
  - Interactive feedback
  - Tooltips

## License

This project is licensed under the MIT License - see the LICENSE file for details.

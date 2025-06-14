from flask import Flask, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    """
    Render the main page of the blog application.

    Returns:
        str: Rendered HTML template
    """
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)

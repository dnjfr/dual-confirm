from flask import redirect, url_for
from extensions import app


# Home page route
@app.route('/')
def home():
    return redirect(url_for('login'))
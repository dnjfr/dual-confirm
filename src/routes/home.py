from flask import redirect, url_for
from extensions import app


@app.route('/')
def home():
    """
    Redirects the root URL to the login page.
    
    Returns:
        Response: Redirect to login route.
    """
    
    return redirect(url_for('login'))
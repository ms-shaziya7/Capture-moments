# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' # Replace with a strong secret key

# Dummy user data for demonstration
users = {
    "test@example.com": {"password": "password123", "name": "Test User"}
}

# Dummy booking data for demonstration
bookings_db = []

@app.route('/')
def index():
    """Renders the landing page."""
    return render_template('index.html')

@app.route('/home')
def home():
    """Renders the home page with login/signup options."""
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email]['password'] == password:
            session['logged_in'] = True
            session['user_email'] = email
            session['user_name'] = users[email]['name']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handles user registration."""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
        elif email in users:
            flash('Email already registered. Please login.', 'warning')
        else:
            users[email] = {"password": password, "name": name}
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Handles forgot password requests."""
    if request.method == 'POST':
        email = request.form['email']
        if email in users:
            flash('A password reset link has been sent to your email (dummy action).', 'success')
        else:
            flash('Email not found.', 'danger')
    return render_template('forgot_password.html')

@app.route('/dashboard')
def dashboard():
    """Renders the user dashboard."""
    if not session.get('logged_in'):
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    user_name = session.get('user_name', 'Guest')
    return render_template('dashboard.html', user_name=user_name)

@app.route('/about_us')
def about_us():
    """Renders the about us page."""
    return render_template('about_us.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    """Handles booking a photographer."""
    if not session.get('logged_in'):
        flash('Please log in to book a photographer.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        date = request.form['date']
        photography_type = request.form['type']

        # Dummy price calculation based on type
        price_map = {
            "Wedding": 25000,
            "Events": 15000,
            "Birthday": 10000,
            "Tour": 12000,
            "Wildlife": 20000,
            "Adventure": 18000
        }
        price = price_map.get(photography_type, 0)

        # Store booking details (dummy storage)
        booking_details = {
            "name": name,
            "location": location,
            "date": date,
            "type": photography_type,
            "price": price,
            "message": "Your booking has been confirmed!"
        }
        bookings_db.append({
            "event_type": photography_type,
            "booking_date": date,
            "booking_time": "N/A", # Not collected in form
            "photographer_name": "Assigned Soon", # Dummy
            "status": "Pending",
            "price": price
        })
        return render_template('booking.html', **booking_details)
    return render_template('booking.html')

@app.route('/profile')
def profile():
    """Renders the photographer profiles page."""
    return render_template('profile.html')

@app.route('/booking_history')
def booking_history():
    """Renders the user's booking history."""
    if not session.get('logged_in'):
        flash('Please log in to view your booking history.', 'warning')
        return redirect(url_for('login'))
    return render_template('booking_history.html', bookings=bookings_db)

@app.route('/user_reviews')
def user_reviews():
    """Renders the user reviews page."""
    return render_template('user_reviews.html')

@app.route('/photographer_categories')
def photographer_categories():
    """Renders the photographer categories page."""
    return render_template('photographer_categories.html')

@app.route('/logout')
def logout():
    """Logs out the user."""
    session.pop('logged_in', None)
    session.pop('user_email', None)
    session.pop('user_name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

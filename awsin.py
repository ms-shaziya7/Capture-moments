import os
import uuid
from datetime import datetime
import json # For pretty printing DynamoDB responses (optional)

from flask import Flask, request, jsonify, session, redirect, url_for, render_template, flash
import boto3
from boto3.dynamodb.conditions import Key, Attr

# --- Flask App Configuration ---
app = Flask(__name__)
# Generate a strong secret key for session management.
# In production, load this from an environment variable or a secure config.
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_very_strong_and_random_secret_key_for_capture_moments_app_12345')

# --- AWS DynamoDB Configuration ---
# It's best practice to let boto3 pick up region and credentials from
# environment variables or IAM roles on EC2.
# You can explicitly set region if needed, but generally not required on EC2 with IAM role.
# AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1') # Example region
# dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
dynamodb = boto3.resource('dynamodb') # boto3 will auto-configure region/credentials

# DynamoDB Table Names (ensure these match your actual table names in AWS)
USERS_TABLE = os.environ.get('USERS_TABLE', 'CaptureMomentsUsers')
BOOKINGS_TABLE = os.environ.get('BOOKINGS_TABLE', 'CaptureMomentsBookings')

users_table = dynamodb.Table(USERS_TABLE)
bookings_table = dynamodb.Table(BOOKINGS_TABLE)

# --- Helper Functions ---

def is_logged_in():
    """Checks if a user is logged in."""
    return 'user_email' in session

def get_current_user_email():
    """Returns the email of the currently logged-in user."""
    return session.get('user_email')

def get_user_name_from_email(email):
    """Fetches user's name from DynamoDB based on email."""
    try:
        response = users_table.get_item(Key={'email': email})
        return response.get('Item', {}).get('name', 'Guest')
    except Exception as e:
        print(f"Error fetching user name for {email}: {e}")
        return "Guest"

# --- Routes ---

@app.route('/')
def index():
    """Landing page."""
    return render_template('index.html')

@app.route('/home')
def home():
    """Welcome page with login/signup options."""
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if is_logged_in():
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            response = users_table.get_item(Key={'email': email})
            user = response.get('Item')

            if user and user['password'] == password: # In production, use password hashing (e.g., bcrypt)
                session['user_email'] = user['email']
                session['user_name'] = user['name']
                flash('Logged in successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
        except Exception as e:
            flash(f'An error occurred during login: {e}', 'danger')
            print(f"Login error: {e}")

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup page."""
    if is_logged_in():
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.', 'warning')
            return render_template('signup.html')

        try:
            # Check if user already exists
            response = users_table.get_item(Key={'email': email})
            if response.get('Item'):
                flash('Email already registered. Please login.', 'warning')
                return render_template('signup.html')

            # Create new user (In production, hash password before storing)
            users_table.put_item(
                Item={
                    'email': email,
                    'name': name,
                    'password': password, # Store hashed password in production!
                    'created_at': datetime.now().isoformat()
                }
            )
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'An error occurred during signup: {e}', 'danger')
            print(f"Signup error: {e}")

    return render_template('signup.html')

@app.route('/forgot_password')
def forgot_password():
    """Forgot password page (dummy for now)."""
    flash('Password reset functionality is not implemented in this demo.', 'warning')
    return render_template('forgot_password.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard."""
    if not is_logged_in():
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    
    user_name = session.get('user_name', get_user_name_from_email(get_current_user_email()))
    return render_template('dashboard.html', user_name=user_name)

@app.route('/about_us')
def about_us():
    """About Us page."""
    return render_template('about_us.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    """Book a Photographer page."""
    if not is_logged_in():
        flash('Please log in to book a photographer.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        date_str = request.form['date']
        booking_type = request.form['type']

        # Dummy price calculation based on type
        price_map = {
            'Wedding': 25000,
            'Events': 15000,
            'Birthday': 10000,
            'Tour': 12000,
            'Wildlife': 18000,
            'Adventure': 20000
        }
        price = price_map.get(booking_type, 10000) # Default price

        booking_id = str(uuid.uuid4()) # Generate unique booking ID
        user_email = get_current_user_email()
        booking_time = datetime.now().isoformat() # Timestamp of booking creation

        try:
            bookings_table.put_item(
                Item={
                    'booking_id': booking_id,
                    'user_email': user_email, # Used for GSI
                    'name': name,
                    'location': location,
                    'booking_date': date_str,
                    'event_type': booking_type,
                    'price': price,
                    'status': 'Pending', # Initial status
                    'booking_time': booking_time,
                    'photographer_name': 'Assigned Soon' # Placeholder
                }
            )
            flash('Booking confirmed successfully!', 'success')
            return render_template('booking.html',
                                   message='Booking Confirmed!',
                                   name=name,
                                   location=location,
                                   date=date_str,
                                   type=booking_type,
                                   price=price)
        except Exception as e:
            flash(f'An error occurred during booking: {e}', 'danger')
            print(f"Booking error: {e}")

    return render_template('booking.html')

@app.route('/profile')
def profile():
    """Photographer Profiles page."""
    # No login required for this page in the original template, but can be added.
    # if not is_logged_in():
    #     flash('Please log in to view profiles.', 'warning')
    #     return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/booking_history')
def booking_history():
    """User's booking history."""
    if not is_logged_in():
        flash('Please log in to view your booking history.', 'warning')
        return redirect(url_for('login'))

    user_email = get_current_user_email()
    bookings = []
    try:
        # Query the GSI to get bookings for the current user
        response = bookings_table.query(
            IndexName='user_email-index', # Name of your GSI
            KeyConditionExpression=Key('user_email').eq(user_email),
            ScanIndexForward=False # Get latest bookings first
        )
        bookings = response.get('Items', [])
        # print(f"Fetched bookings for {user_email}: {json.dumps(bookings, indent=2)}") # For debugging
    except Exception as e:
        flash(f'Error fetching booking history: {e}', 'danger')
        print(f"Booking history error for {user_email}: {e}")

    return render_template('booking_history.html', bookings=bookings)

@app.route('/user_reviews')
def user_reviews():
    """User Reviews page."""
    return render_template('user_reviews.html')

@app.route('/photographer_categories')
def photographer_categories():
    """Photographer Categories page."""
    return render_template('photographer_categories.html')

@app.route('/logout')
def logout():
    """User logout."""
    session.pop('user_email', None)
    session.pop('user_name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# --- Run the Flask App ---
if __name__ == '__main__':
    # In a production EC2 environment, you would use Gunicorn or uWSGI
    # and Nginx as a reverse proxy.
    # For local development, app.run() is fine.
    # To make it accessible from external IPs (like 3.94.128.66),
    # the host must be '0.0.0.0'.
    app.run(debug=True, host='0.0.0.0', port=5000)

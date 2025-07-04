from flask import Flask, render_template, redirect, url_for, request, session, flash
import boto3
from botocore.exceptions import ClientError
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ------------------ DynamoDB Connection ------------------
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')  # Use your correct AWS region

# Ensure the tables exist (users and bookings)
users_table = dynamodb.Table('Users')
bookings_table = dynamodb.Table('Bookings')

# ------------------ Routes ------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            try:
                response = users_table.get_item(Key={'email': email})
                user = response.get('Item')
                # --- CRITICAL LOGIC HERE ---
                if user and user.get('password') == password:
                    # Authentication successful
                    session['user_email'] = email
                    session['user_name'] = user.get('name', 'Guest')
                    session['logged_in'] = True # Set this for dashboard check
                    flash("Login successful!", "success")
                    return redirect(url_for('dashboard'))
                else:
                    # Authentication failed (user not found or password mismatch)
                    flash("Invalid username or password!", "danger")
                    # No redirect here, just let it fall through to re-render login.html
            except ClientError as e:
                # Database access error
                flash(f"Database error: {e.response['Error']['Message']}", "danger")
                # No redirect here, just let it fall through to re-render login.html
# This line is reached if:
        # 1. It's a GET request (initial page load)
        # 2. It's a POST request and authentication failed (invalid credentials or DB error)
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Placeholder for signup logic
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        # In a real app, you'd create a new user in your database
        # and handle password hashing, etc.
        print(f"New user signup: {name}, {email}")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    # Placeholder for forgot password logic
    if request.method == 'POST':
        email = request.form['email']
        print(f"Password reset requested for: {email}")
        # In a real app, you'd send a reset link to the email
    return render_template('forgot_password.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_name = session.get('user_name', 'Guest')
    return render_template('dashboard.html', user_name=user_name)

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    message = None
    booking_details = {} # Dictionary to hold details for confirmation
    if request.method == 'POST':
        booking_details['name'] = request.form['name']
        booking_details['location'] = request.form['location']
        booking_details['date'] = request.form['date']
        booking_details['type'] = request.form['type']
        booking_details['user_email'] = session.get('user_email') # Link booking to user
        # Simulate price calculation based on type
        if booking_details['type'] == 'Wedding':
            booking_details['price'] = 12000
        elif booking_details['type'] == 'Events':
            booking_details['price'] = 9000
        elif booking_details['type'] == 'Birthday':
            booking_details['price'] = 7500
        elif booking_details['type'] == 'Tour':
            booking_details['price'] = 11500
        elif booking_details['type'] == 'Wildlife':
            booking_details['price'] = 18000
        elif booking_details['type'] == 'Adventure':
            booking_details['price'] = 18000
        else:
            booking_details['price'] = 5000 # Default price
        # Simulate photographer assignment and status
        booking_details['photographer'] = "Assigned Photographer" # In a real app, this would be dynamic
        booking_details['status'] = "Upcoming"
        # Add the booking to our global list
        all_bookings.append(booking_details)
        message = "Your booking has been confirmed!"
        return render_template('booking.html', message=message, **booking_details)
    return render_template('booking.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/booking_history')
def booking_history():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    current_user_email = session.get('user_email')
    # Filter bookings for the current logged-in user
    user_bookings = [
        booking for booking in all_bookings
        if booking.get('user_email') == current_user_email
    ]
    # Sort bookings by date (most recent first, or upcoming first)
    # Assuming date is in 'YYYY-MM-DD' format for easy comparison
    user_bookings.sort(key=lambda x: x['date'], reverse=True)
    return render_template('booking_history.html', bookings=user_bookings)
@app.route('/user_reviews')
def user_reviews():
    return render_template('user_reviews.html')

@app.route('/photographer_categories')
def photographer_categories():
    return render_template('photographer_categories.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_name', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

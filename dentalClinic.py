from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import re
import hashlib

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('login.html')
app.secret_key = 'your_secret_key'  # Required for flashing messages


# Function to validate email format
def is_valid_email(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zAZH0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None

# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to check if email and password match and return user type
def check_email_password(email, password):
    # Hash the input password
    hashed_password = hash_password(password)

    # Connect to the database
    connection = connect_db()
    cursor = connection.cursor()

    # Prepare and execute the SQL query
    query = "SELECT UserType FROM Users WHERE Email = %s AND PasswordHash = %s"
    cursor.execute(query, (email, hashed_password))

    # Fetch the result
    result = cursor.fetchone()

    # Close the connection
    cursor.close()
    connection.close()

    if result:
        user_type = result[0]  # Extract the UserType
        return user_type
    else:
        return None  # Invalid email or password

# MySQL database connection setup
def connect_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='your_password',  # Replace with your MySQL password
        database='ClinicManagement'
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Validate email format
        if not is_valid_email(email):
            flash('Invalid email format', 'error')
            return render_template('login.html')

        # Check if email and password match and get user type
        user_type = check_email_password(email, password)

        if user_type:
            flash(f'Login successful! User type: {user_type}', 'success')
            
            # Redirect based on user type
            if user_type == 'Doctor':
                return redirect(url_for('doctor_dashboard'))  # Redirect to doctor dashboard
            elif user_type == 'Secretary':
                return redirect(url_for('secretary_dashboard'))  # Redirect to secretary dashboard
            else:
                flash('You cannot access the system', 'error')
                return render_template('login.html')
        else:
            flash('Invalid email or password', 'error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/doctor_dashboard')
def doctor_dashboard():
    return "Welcome to the Doctor's Dashboard!"  # Redirect to doctor's dashboard

@app.route('/secretary_dashboard')
def secretary_dashboard():
    return "Welcome to the Secretary's Dashboard!"  # Redirect to secretary's dashboard

if __name__ == '__main__':
    app.run(debug=True)

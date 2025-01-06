from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For storing messages securely

# Connect to the database
def connect_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='0569458641#2003',
        database='ClinicManagement',
        cursorclass=pymysql.cursors.DictCursor  # This ensures that results are returned as dictionaries
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Connect to the database and verify user
        conn = connect_db()  # Corrected function call
        cursor = conn.cursor()

        query = "SELECT Email, PasswordHash, UserType FROM users WHERE Email=%s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            email_from_db = user['Email']
            pass_from_db = user['PasswordHash']

            # Verify the password
            if email_from_db == email and pass_from_db == password:
                return redirect(url_for('dashboard'))  # Redirect to dashboard on successful login
            else:
                flash('Wrong password. Please try again.', 'danger')  # Flash error message for incorrect password
        else:
            flash('Email does not exist.', 'danger')  # Flash error message if email is not found

    return render_template('login.html')  # Render login page

@app.route('/')
def dashboard():
    return render_template('dashboard.html')  # Main dashboard page after successful login
    

if __name__ == '__main__':
    app.run(debug=True)

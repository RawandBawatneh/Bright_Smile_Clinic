from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': '0569458641#2003',  # Replace with your MySQL password
    'database': 'ClinicManagement'
}

# Helper function to validate user credentials
def validate_user(email, password, user_type):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Query to check user credentials and type
    query = "SELECT * FROM users WHERE email = %s AND password = %s AND user_type = %s"
    cursor.execute(query, (email, password, user_type))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user is not None

# Login route (GET to render the login page and POST to validate credentials)
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # Render the login page when the user visits the login page
        return render_template("login.html")

    # Handle POST request to validate login credentials
    email = request.form.get("email")
    password = request.form.get("password")
    user_type = request.form.get("user_type")

    if validate_user(email, password, user_type):
        if user_type == "doctor":
            return redirect(url_for("doctor_home"))  # Redirect to doctor home
        elif user_type == "secretary":
            return redirect(url_for("dashboard"))  # Redirect to secretary dashboard
    else:
        return render_template("login.html", error="Invalid credentials or user type")

@app.route("/doctor_home")
def doctor_home():
    return render_template("doctor_home.html")  # Ensure this file exists

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")
@app.route("/myClinic")
def myClinic():
    return render_template("myClinic.html")
# Main entry point
if __name__ == "__main__":  
    app.run(debug=True)

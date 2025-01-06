from flask import Flask, render_template, url_for
import pymysql
from datetime import datetime

app = Flask(__name__)

# MySQL database connection setup
def connect_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='0569458641#2003',  # Replace with your MySQL password
        database='ClinicManagement'
    )

# Function to fetch doctor shifts and calculate total hours worked
@app.route('/')
def dashboard():
    # Initialize a connection to the database
    connection = None
    cursor = None
    doctor_shifts = {}

    try:
        # Connect to the database
        connection = connect_db()
        cursor = connection.cursor()

        # Prepare and execute the SQL query to fetch the shifts
        query = """
        SELECT d.Name, ds.StartTime, ds.EndTime
        FROM DoctorShifts ds
        JOIN Doctor d ON ds.DoctorID = d.DoctorID
        """
        cursor.execute(query)

        # Fetch all shift data
        shifts = cursor.fetchall()

        # Process each shift data
        for shift in shifts:
            doctor_name = shift[0]
            start_time = shift[1]
            end_time = shift[2]

            # Convert start_time and end_time to datetime objects
            start_time_obj = datetime.strptime(str(start_time), '%H:%M:%S')
            end_time_obj = datetime.strptime(str(end_time), '%H:%M:%S')

            # Calculate the duration of the shift
            duration = end_time_obj - start_time_obj

            # Convert the duration to hours
            total_hours = duration.total_seconds() / 3600.0  # Convert seconds to hours

            # Store shift data in dictionary
            if doctor_name not in doctor_shifts:
                doctor_shifts[doctor_name] = {
                    'shifts': [],
                    'total_hours': 0
                }

            # Append shift details
            doctor_shifts[doctor_name]['shifts'].append(f"Shift: {start_time} - {end_time}")
            doctor_shifts[doctor_name]['total_hours'] += total_hours

    except Exception as e:
        print(f"Error fetching data: {e}")
    finally:
        # Ensure that the database connection is closed
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    # Pass the doctor shifts and total hours to the template
    return render_template('dashboard.html', doctor_shifts=doctor_shifts)

# Route for adding patient
@app.route('/add_patient')
def add_patient():
    return render_template('add_patient.html')
@app.route('/add_appointment')
def add_appointment():
    return render_template('add_appointment.html')



# Route for adding doctor
@app.route('/add_doctor')
def add_doctor():
    return render_template('add_doctor.html')

# Route for my clinic page
@app.route('/myClinic')
def myClinic():
    return render_template('myClinic.html')

if __name__ == '__main__':
    app.run(debug=True)

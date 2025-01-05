from flask import Flask, render_template
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

def home():
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

    # List to store shift details and total hours worked by doctors
    doctor_shifts = {}

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

    # Close the connection
    cursor.close()
    connection.close()

    # Pass the doctor shifts and total hours to the template
    return render_template('dashboard.html', doctor_shifts=doctor_shifts)

if __name__ == '__main__':
    app.run(debug=True)

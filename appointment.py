from flask import Flask, render_template, request, redirect, url_for, jsonify
import pymysql
from invoice import execute_query

app = Flask(__name__)

# MySQL database connection setup
def connect_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='0569458641#2003',  
        database='ClinicManagement'
    )

@app.route('/')
def add_appointment():
    # Fetch patients and doctors to display in the form
    patients = execute_query("SELECT PatientID, FirstName, LastName FROM Patient", fetch=True)
    doctors = execute_query("SELECT DoctorID, Name FROM Doctor", fetch=True)
    return render_template('add_appointment.html', patients=patients, doctors=doctors)

@app.route('/insert_appointment', methods=['POST'])
def insert_appointment():
    # Extract form data
    patient_id = request.form['patient_id']
    doctor_id = request.form['doctor_id']
    appointment_date = request.form['appointment_date']
    appointment_time = request.form['appointment_time']
    notes = request.form['notes']

    connection = connect_db()
    cursor = connection.cursor()

    # Insert appointment data into database
    cursor.execute('''INSERT INTO Appointment (PatientID, DoctorID, AppointmentDate, AppointmentTime, Notes)
                      VALUES (%s, %s, %s, %s, %s)''',
                   (patient_id, doctor_id, appointment_date, appointment_time, notes))
    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for('add_appointment'))  # Redirect to the homepage after insertion

@app.route('/update_appointment', methods=['POST'])
def update_appointment():
    patient_id = request.form['patient_id']
    doctor_id = request.form['doctor_id']
    appointment_date = request.form.get('appointment_date')  # Optional field
    appointment_time = request.form.get('appointment_time')  # Optional field
    status = request.form.get('status')  # Optional field
    notes = request.form.get('notes')  # Optional field

    connection = connect_db()
    cursor = connection.cursor()

    # Dynamically build the update query based on provided fields
    update_query = "UPDATE Appointment SET "
    updates = []

    # Append the fields to be updated to the query
    if appointment_date:
        updates.append("AppointmentDate = %s")
    if appointment_time:
        updates.append("AppointmentTime = %s")
    if status:
        updates.append("Status = %s")
    if notes:
        updates.append("Notes = %s")
    
    # If there are any fields to update, finalize the query
    if updates:
        update_query += ", ".join(updates) + " WHERE PatientID = %s AND DoctorID = %s"
        values = [value for value in [appointment_date, appointment_time, status, notes] if value]
        values.extend([patient_id, doctor_id])  # Append patient and doctor ids at the end

        # Execute the query
        cursor.execute(update_query, tuple(values))
        connection.commit()

    cursor.close()
    connection.close()

    return jsonify({"message": "Appointment updated successfully"})


@app.route('/delete_appointment', methods=['POST'])
def delete_appointment():
    patient_id = request.form['patient_id']
    doctor_id = request.form['doctor_id']

    connection = connect_db()
    cursor = connection.cursor()

    # Delete the appointment record
    cursor.execute("DELETE FROM Appointment WHERE PatientID = %s AND DoctorID = %s", (patient_id, doctor_id))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({"message": "Appointment deleted successfully"})

@app.route('/fetch_patient_names')
def fetch_patient_names():
    query = "SELECT PatientID, FirstName, LastName FROM Patient"
    patients = execute_query(query, fetch=True)
    return jsonify(patients)


if __name__ == '__main__':
    app.run(debug=True)

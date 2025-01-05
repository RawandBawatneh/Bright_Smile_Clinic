from flask import Flask, request, jsonify
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for
import pymysql


app = Flask(__name__)

# Database connection configuration
def connect_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='0569458641#2003',
        database='ClinicManagement'
    )

def execute_query(query, params=None):
    """Helper function to execute database queries."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor
    except pymysql.MySQLError as err:
        print(f"Error: {err}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

@app.route('/')
def home():
    return render_template('test.html')
@app.route('/insert_shift', methods=['POST'])
def insert_shift():
    data = request.form

    # Step 1: Fetch DoctorID based on Doctor's Name
    doctor_name_query = "SELECT DoctorID FROM Doctor WHERE Name = %s"
    doctor_name_params = (data['doctor_name'],)  # 'doctor_name' comes from the frontend
    doctor_id_result = execute_query(doctor_name_query, doctor_name_params)

    if not doctor_id_result:
        return jsonify({'message': f"Doctor '{data['doctor_name']}' not found."}), 400

    doctor_id = doctor_id_result[0]['DoctorID']  # Fetch the DoctorID

    # Step 2: Insert Shift with Resolved DoctorID
    query = """
        INSERT INTO DoctorShifts (DoctorID, DayOfWeek, StartTime, EndTime) 
        VALUES (%s, %s, %s, %s)
    """
    params = (doctor_id, data['day_of_week'], data['start_time'], data['end_time'])
    result = execute_query(query, params)

    if result:
        return jsonify({'message': 'Shift inserted successfully.'}), 201
    return jsonify({'message': 'Failed to insert shift.'}), 400
@app.route('/get_doctors', methods=['GET'])
def get_doctors():
    query = """
        SELECT DISTINCT Doctor.Name 
        FROM Doctor
        INNER JOIN DoctorShifts ON Doctor.DoctorID = DoctorShifts.DoctorID
    """
    result = execute_query(query)
    if result:
        # Convert result into a list of dictionaries for JSON response
        doctors = [{'Name': row[0]} for row in result]
        return jsonify(doctors), 200
    return jsonify({'message': 'Failed to fetch doctors.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
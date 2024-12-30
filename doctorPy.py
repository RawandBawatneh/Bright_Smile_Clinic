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
    return render_template('add_doctor.html')

# Insert doctor
@app.route('/insert_doctor', methods=['POST'])
def insert_doctor():
    data = request.form
    query = """
        INSERT INTO Doctor (Name, Specialization, Salary) 
        VALUES (%s, %s, %s)
    """
    params = (data['name'], data['specialization'], data['salary'])
    result = execute_query(query, params)
    if result:
        message = 'Doctor inserted successfully.'
        message_type = 'success'
    else:
        message = 'Failed to insert Doctor.'
        message_type = 'error'
    
    return render_template('add_doctor.html', message=message, message_type=message_type)

# Update doctor
@app.route('/update_doctor', methods=['POST'])
def update_doctor():
    data = request.form
    query = """
        UPDATE Doctor 
        SET {attribute} = %s 
        WHERE DoctorID = %s
    """.format(attribute=data['attribute'])
    params = (data['new_value'], data['doctor_id'])
    result = execute_query(query, params)
    if result:
        message = 'Doctor updated successfully.'
        message_type = 'success'
    else:
        message = 'Failed to update Doctor.'
        message_type = 'error'
    
    return render_template('add_doctor.html', message=message, message_type=message_type)
# Delete doctor
@app.route('/delete_doctor', methods=['POST'])
def delete_doctor():
    data = request.form
    query = "DELETE FROM Doctor WHERE DoctorID = %s"
    params = (data['doctor_id'],)
    result = execute_query(query, params)
    if result:
        message = 'Doctor inserted successfully.'
    else:
        message = 'Failed to insert Doctor.'
    
    return render_template('add_doctor.html', message=message)

# Insert doctor shift
@app.route('/insert_shift', methods=['POST'])
def insert_shift():
    data = request.form
    query = """
        INSERT INTO DoctorShifts (DoctorID, DayOfWeek, StartTime, EndTime) 
        VALUES (%s, %s, %s, %s)
    """
    params = (data['doctor_id'], data['day_of_week'], data['start_time'], data['end_time'])
    result = execute_query(query, params)
    if result:
        return jsonify({'message': 'Shift inserted successfully.'}), 201
    return jsonify({'message': 'Failed to insert shift.'}), 400

# Update doctor shift
@app.route('/update_shift', methods=['POST'])
def update_shift():
    data = request.form
    query = f"""
        UPDATE DoctorShifts 
        SET {data['attribute']} = %s 
        WHERE DoctorID = %s AND DayOfWeek = %s
    """
    params = (data['new_value'], data['doctor_id'], data['day_of_week'])
    result = execute_query(query, params)
    if result:
        return jsonify({'message': 'Shift updated successfully.'}), 200
    return jsonify({'message': 'Failed to update shift.'}), 400

# Delete doctor shift
@app.route('/delete_shift', methods=['POST'])
def delete_shift():
    data = request.form
    query = """
        DELETE FROM DoctorShifts 
        WHERE DoctorID = %s AND DayOfWeek = %s
    """
    params = (data['doctor_id'], data['day_of_week'])
    result = execute_query(query, params)
    if result:
        return jsonify({'message': 'Shift deleted successfully.'}), 200
    return jsonify({'message': 'Failed to delete shift.'}), 400

# Insert doctor leave
@app.route('/insert_leave', methods=['POST'])
def insert_leave():
    data = request.form
    query = """
        INSERT INTO DoctorLeaves (DoctorID, LeaveStart, LeaveEnd, Reason) 
        VALUES (%s, %s, %s, %s)
    """
    params = (data['doctor_id'], data['leave_start'], data['leave_end'], data.get('reason'))
    result = execute_query(query, params)
    if result:
        return jsonify({'message': 'Leave inserted successfully.'}), 201
    return jsonify({'message': 'Failed to insert leave.'}), 400

# Update doctor leave
@app.route('/update_leave', methods=['POST'])
def update_leave():
    data = request.form
    query = """
        UPDATE DoctorLeaves 
        SET LeaveStart = %s, LeaveEnd = %s, Reason = %s 
        WHERE DoctorID = %s
    """
    params = (data['leave_start'], data['leave_end'], data.get('reason'), data['doctor_id'])
    result = execute_query(query, params)
    if result:
        return jsonify({'message': 'Leave updated successfully.'}), 200
    return jsonify({'message': 'Failed to update leave.'}), 400

# Delete doctor leave
@app.route('/delete_leave', methods=['POST'])
def delete_leave():
    data = request.form
    query = """
        DELETE FROM DoctorLeaves 
        WHERE DoctorID = %s AND LeaveStart = %s
    """
    params = (data['doctor_id'], data['leave_start'])
    result = execute_query(query, params)
    if result:
        return jsonify({'message': 'Leave deleted successfully.'}), 200
    return jsonify({'message': 'Failed to delete leave.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
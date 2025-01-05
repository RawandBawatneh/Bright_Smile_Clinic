from flask import Flask, request, jsonify, render_template
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

def execute_query(query, params=None, fetch=False):
    """Helper function to execute database queries."""
    conn = connect_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # Use DictCursor for dictionary-like rows
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()  # Fetch results if needed
        else:
            result = cursor.rowcount
        conn.commit()
        return result
    except pymysql.MySQLError as err:
        print(f"Database Error: {err}")
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
        return render_template('add_doctor.html', message='Doctor inserted successfully.', message_type='success')
    return render_template('add_doctor.html', message='Failed to insert Doctor.', message_type='error')

# Fetch doctor names for dropdown
@app.route('/fetch_doctor_names', methods=['GET'])
def fetch_doctor_names():
    query = "SELECT Name FROM Doctor"
    result = execute_query(query, fetch=True)
    if result:
        doctors = [{'Name': row['Name']} for row in result]
        return jsonify(doctors), 200
    return jsonify({'message': 'Failed to fetch doctor names.'}), 400

# Update doctor using Name
@app.route('/update_doctor', methods=['POST'])
def update_doctor():
    data = request.form

    # Fetch DoctorID based on Doctor's Name
    doctor_name_query = "SELECT DoctorID FROM Doctor WHERE Name = %s"
    doctor_id_result = execute_query(doctor_name_query, (data['doctor_name'],), fetch=True)

    if not doctor_id_result:
        print(f"Doctor '{data['doctor_name']}' not found.")  # Debugging
        return render_template('add_doctor.html', message=f"Doctor '{data['doctor_name']}' not found.", message_type='error')

    doctor_id = doctor_id_result[0]['DoctorID']  # Fetch the DoctorID
    print(f"DoctorID to update: {doctor_id}")  # Debugging

    # Update doctor information
    update_query = f"""
        UPDATE Doctor 
        SET {data['attribute']} = %s 
        WHERE DoctorID = %s
    """
    params = (data['new_value'], doctor_id)
    result = execute_query(update_query, params)

    if result:
        return render_template('add_doctor.html', message='Doctor updated successfully.', message_type='success')
    return render_template('add_doctor.html', message='Failed to update Doctor.', message_type='error')

# Delete doctor using Name
@app.route('/delete_doctor', methods=['POST'])
def delete_doctor():
    data = request.form

    # Fetch DoctorID based on Doctor's Name
    doctor_name_query = "SELECT DoctorID FROM Doctor WHERE Name = %s"
    doctor_id_result = execute_query(doctor_name_query, (data['doctor_name'],), fetch=True)

    if not doctor_id_result:
        print(f"Doctor '{data['doctor_name']}' not found.")  # Debugging
        return render_template('add_doctor.html', message=f"Doctor '{data['doctor_name']}' not found.", message_type='error')

    doctor_id = doctor_id_result[0]['DoctorID']  # Fetch the DoctorID
    print(f"DoctorID to delete: {doctor_id}")  # Debugging

    # Delete doctor record
    delete_query = "DELETE FROM Doctor WHERE DoctorID = %s"
    result = execute_query(delete_query, (doctor_id,))

    if result > 0:  # Check if rows were affected
        return render_template('add_doctor.html', message='Doctor deleted successfully.', message_type='success')
    else:
        print(f"Delete query failed, no rows affected.")  # Debugging
        return render_template('add_doctor.html', message='Failed to delete Doctor.', message_type='error')

# Insert doctor shift
@app.route('/insert_shift', methods=['POST'])
def insert_shift():
    data = request.form

    # Step 1: Fetch DoctorID based on Doctor's Name
    doctor_name_query = "SELECT DoctorID FROM Doctor WHERE Name = %s"
    doctor_id_result = execute_query(doctor_name_query, (data['doctor_name'],), fetch=True)

    if not doctor_id_result:
        return jsonify({'message': f"Doctor '{data['doctor_name']}' not found."}), 400

    doctor_id = doctor_id_result[0]['DoctorID']  # Fetch the DoctorID

    # Step 2: Insert Shift with Resolved DoctorID
    shift_exists_query = """
        SELECT * FROM DoctorShifts 
        WHERE DoctorID = %s AND DayOfWeek = %s
    """
    existing_shift = execute_query(shift_exists_query, (doctor_id, data['day_of_week']), fetch=True)

    if existing_shift:
        return jsonify({'message': 'A shift for this doctor on the selected day already exists.'}), 400

    insert_query = """
        INSERT INTO DoctorShifts (DoctorID, DayOfWeek, StartTime, EndTime) 
        VALUES (%s, %s, %s, %s)
    """
    params = (doctor_id, data['day_of_week'], data['start_time'], data['end_time'])
    result = execute_query(insert_query, params)

    if result:
        return jsonify({'message': 'Shift inserted successfully.'}), 201
    return jsonify({'message': 'Failed to insert shift.'}), 400

# Get doctors
@app.route('/get_doctors', methods=['GET'])
def get_doctors():
    query = """
        SELECT DISTINCT Doctor.Name 
        FROM Doctor
        INNER JOIN DoctorShifts ON Doctor.DoctorID = DoctorShifts.DoctorID
    """
    result = execute_query(query, fetch=True)
    if result:
        doctors = [{'Name': row['Name']} for row in result]
        return jsonify(doctors), 200
    return jsonify({'message': 'Failed to fetch doctors.'}), 400

# Update doctor shift
@app.route('/update_shift', methods=['POST'])
def update_shift():
    data = request.form

    # Step 1: Fetch DoctorID based on Doctor's Name
    doctor_name_query = "SELECT DoctorID FROM Doctor WHERE Name = %s"
    doctor_id_result = execute_query(doctor_name_query, (data['doctor_name'],), fetch=True)

    if not doctor_id_result:
        return jsonify({'message': f"Doctor '{data['doctor_name']}' not found."}), 400

    doctor_id = doctor_id_result[0]['DoctorID']  # Fetch the DoctorID

    # Step 2: Update Shift with Resolved DoctorID
    update_query = f"""
        UPDATE DoctorShifts 
        SET {data['attribute']} = %s 
        WHERE DoctorID = %s AND DayOfWeek = %s
    """
    params = (data['new_value'], doctor_id, data['day_of_week'])
    result = execute_query(update_query, params)

    if result:
        return jsonify({'message': 'Shift updated successfully.'}), 200
    return jsonify({'message': 'Failed to update shift.'}), 400

# Delete doctor shift
@app.route('/delete_shift', methods=['POST'])
def delete_shift():
    data = request.form

    # Step 1: Fetch DoctorID based on Doctor's Name
    doctor_name_query = "SELECT DoctorID FROM Doctor WHERE Name = %s"
    doctor_id_result = execute_query(doctor_name_query, (data['doctor_name'],), fetch=True)

    if not doctor_id_result:
        return jsonify({'message': f"Doctor '{data['doctor_name']}' not found."}), 400

    doctor_id = doctor_id_result[0]['DoctorID']  # Fetch the DoctorID

    # Step 2: Delete Shift with Resolved DoctorID
    delete_query = """
        DELETE FROM DoctorShifts 
        WHERE DoctorID = %s AND DayOfWeek = %s
    """
    params = (doctor_id, data['day_of_week'])
    result = execute_query(delete_query, params)

    if result:
        return jsonify({'message': 'Shift deleted successfully.'}), 200
    return jsonify({'message': 'Failed to delete shift.'}), 400

# Get shifts for the current week
@app.route('/get_current_week_shifts', methods=['GET'])
def get_current_week_shifts():
    query = """
        SELECT Doctor.Name, DayOfWeek, StartTime, EndTime 
        FROM DoctorShifts
        INNER JOIN Doctor ON DoctorShifts.DoctorID = Doctor.DoctorID
        WHERE WEEK(CURDATE()) = WEEK(STR_TO_DATE(CONCAT(YEAR(CURDATE()), '-', DayOfWeek), '%X-%V-%W'))
    """
    result = execute_query(query, fetch=True)
    if result:
        return jsonify(result), 200
    return jsonify({'message': 'No shifts found for the current week.'}), 400

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
   
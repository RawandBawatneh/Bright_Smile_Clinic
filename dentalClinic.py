
from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
import pymysql
import mysql.connector
from datetime import datetime, date, timedelta


app = Flask(__name__)
db_config = {
    'host': 'localhost',
    'user': 'root',  
    'password': '0569458641#2003', 
    'database': 'ClinicManagement'
}
# MySQL database connection setup
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
    cursor = conn.cursor(pymysql.cursors.DictCursor)  
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()  
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

# Login route 
@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    # Handle POST request to validate login credentials
    email = request.form.get("email")
    password = request.form.get("password")
    user_type = request.form.get("user_type")

    if validate_user(email, password, user_type):
        if user_type == "doctor":
            return redirect(url_for("doctor_home"))
        elif user_type == "secretary":
            return redirect(url_for("dashboard"))  
    else:
        return render_template("login.html", error="Invalid credentials or user type")
def get_dashboard_data():
    connection = None
    cursor = None
    doctor_shifts = {}
    today_appointments = []
    upcoming_appointments = []

    try:
        # Connect to the database
        connection = connect_db()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # Fetch doctor shifts
        query = """
        SELECT d.Name, ds.StartTime, ds.EndTime
        FROM DoctorShifts ds
        JOIN Doctor d ON ds.DoctorID = d.DoctorID
        """
        cursor.execute(query)

        # Fetch all shift data
        shifts = cursor.fetchall()

        # Process each shift
        for shift in shifts:
            doctor_name = shift['Name']
            start_time = shift['StartTime']
            end_time = shift['EndTime']

            # Convert start_time and end_time to datetime objects
            start_time_obj = datetime.strptime(str(start_time), '%H:%M:%S')
            end_time_obj = datetime.strptime(str(end_time), '%H:%M:%S')

            # Calculate the duration of the shift
            duration = end_time_obj - start_time_obj

            # Convert the duration to hours
            total_hours = duration.total_seconds() / 3600.0  # Convert seconds to hours

            # Store shift data in the dictionary
            if doctor_name not in doctor_shifts:
                doctor_shifts[doctor_name] = {
                    'shifts': [],
                    'total_hours': 0
                }

            # Append shift details
            doctor_shifts[doctor_name]['shifts'].append(f"Shift: {start_time} - {end_time}")
            doctor_shifts[doctor_name]['total_hours'] += total_hours

        # Fetch today's date
        today_date = date.today()

        # Fetch today's appointments
        today_query = '''
            SELECT AppointmentID, PatientID, DoctorID, AppointmentTime, AppointmentDate, Notes
            FROM Appointment
            WHERE AppointmentDate = %s
        '''
        cursor.execute(today_query, (today_date,))
        today_appointments = cursor.fetchall()

        # Fetch upcoming appointments
        upcoming_query = '''
            SELECT AppointmentID, PatientID, DoctorID, AppointmentTime, AppointmentDate, Notes
            FROM Appointment
            WHERE AppointmentDate > %s
        '''
        cursor.execute(upcoming_query, (today_date,))
        upcoming_appointments = cursor.fetchall()

    except Exception as e:
        print(f"Error fetching data: {e}")
    finally:
        # Ensure that the database connection is closed
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    # Return the fetched data
    return doctor_shifts, today_appointments, upcoming_appointments
def get_patient_data():
    connection = None
    cursor = None
    total_patients = 0
    upcoming_birthdays = []

    try:
        # Connect to the database
        connection = connect_db()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # Fetch total number of patients
        total_patients_query = "SELECT COUNT(*) AS total_patients FROM Patient"
        cursor.execute(total_patients_query)
        total_patients = cursor.fetchone()['total_patients']

        # Fetch upcoming birthdays within the next 7 days
        today = datetime.today()
        upcoming = today + timedelta(days=7)
        upcoming_birthdays_query = '''
            SELECT CONCAT(FirstName, ' ', LastName) AS Name, DateOfBirth 
            FROM Patient 
            WHERE DATE_FORMAT(DateOfBirth, '2000-%m-%d') 
                  BETWEEN DATE_FORMAT(%s, '2000-%m-%d') AND DATE_FORMAT(%s, '2000-%m-%d')
        '''
        cursor.execute(upcoming_birthdays_query, (today, upcoming))
        upcoming_birthdays = cursor.fetchall()

    except Exception as e:
        print(f"Error fetching patient data: {e}")
    finally:
        # Ensure that the database connection is closed
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    # Return total patients and upcoming birthdays
    return total_patients, upcoming_birthdays

@app.route("/dashboard", methods=["GET", "POST"])

def dashboard():
    

    doctor_shifts, today_appointments, upcoming_appointments = get_dashboard_data()

    total_patients, upcoming_birthdays = get_patient_data()

    return render_template(
        'dashboard.html',
        doctor_shifts=doctor_shifts,
        today_appointments=today_appointments,
        upcoming_appointments=upcoming_appointments,
        total_patients=total_patients,
        upcoming_birthdays=upcoming_birthdays
    )
################################################ Patient Table ############################################################
@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    try:
        connection = connect_db()  
        with connection.cursor() as cursor:
            cursor.execute("SELECT PatientID, CONCAT(FirstName, ' ', LastName) AS PatientName FROM Patient")
            patients = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching patients: {e}")
        patients = []  
    finally:
        if connection:
            connection.close()  

    if request.method == 'POST':
        first_name = request.form['FirstName']
        last_name = request.form['LastName']
        date_of_birth = request.form['DateOfBirth']
        phone_number = request.form['PhoneNumber']
        emergency_contact = request.form['EmergencyContact']
        drug_allergy = request.form['DrugAllergy']
        infectious_diseases = request.form['InfectiousDiseases']
        gender = request.form['Gender']
        insurance_status = request.form['InsuranceStatus']
        constant_status = request.form['ConstantStatus']
        referral_status = request.form['ReferralStatus']
        medical_history = request.form['MedicalHistory']
        
        # Set default balance to 0.0
        balance = 0.0

        try:
            connection = connect_db()
            with connection.cursor() as cursor:
                # Prepare the insert query
                query = """
                    INSERT INTO Patient (FirstName, LastName, DateOfBirth, Balance, PhoneNumber, EmergencyContact, 
                                         DrugAllergy, InfectiousDiseases, Gender, InsuranceStatus, ConstantStatus, 
                                         ReferralStatus, MedicalHistory)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                data = (first_name, last_name, date_of_birth, balance, phone_number, emergency_contact, 
                        drug_allergy, infectious_diseases, gender, insurance_status, constant_status, 
                        referral_status, medical_history)
                
                # Execute the query
                cursor.execute(query, data)
                connection.commit()

                print("Patient inserted successfully!")
        except Exception as e:
            print(f"Error inserting patient: {e}")
        finally:
            if connection:
                connection.close()  

        return redirect(url_for('add_patient'))

    return render_template('add_patient.html', patients=patients)


@app.route('/update_patient', methods=['POST'])
def update_patient():
    patient_id = request.form['patient_id']
    attribute = request.form['attribute']
    new_value = request.form['new_value']

    connection = connect_db()
    cursor = connection.cursor()

    # Update the patient attribute
    update_query = f"UPDATE Patient SET {attribute} = %s WHERE PatientID = %s"
    cursor.execute(update_query, (new_value, patient_id))
    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for('add_patient'))


@app.route('/delete_patient', methods=['POST'])
def delete_patient():
    patient_id = request.form['patient_id']

    connection = connect_db()
    cursor = connection.cursor()

    # Delete the patient record
    cursor.execute("DELETE FROM Patient WHERE PatientID = %s", (patient_id,))
    connection.commit()

    # Close connection
    cursor.close()
    connection.close()

    return redirect(url_for('add_patient'))
#######################################################Patient Table END ################################################
####################################################Doctoe Table #######################################################
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

    # Debugging
    print(f"Doctor name provided: '{data['doctor_name']}'")

    # Fetch all doctors with the same name
    doctor_name_query = "SELECT DoctorID, Name FROM Doctor WHERE Name = %s"
    doctor_id_result = execute_query(doctor_name_query, (data['doctor_name'],), fetch=True)

    if not doctor_id_result:
        print(f"Doctor '{data['doctor_name']}' not found.")  # Debugging
        return render_template('add_doctor.html', message=f"Doctor '{data['doctor_name']}' not found.", message_type='error')

    # Print all doctors with the same name
    print(f"Doctors found with the same name: {doctor_id_result}")  # Debugging

    # If multiple doctors are found, let the user specify which one to delete
    if len(doctor_id_result) > 1:
        return render_template('add_doctor.html', message=f"Multiple doctors found with the name '{data['doctor_name']}'. Please specify the correct one.", message_type='error')

    doctor_id = doctor_id_result[0]['DoctorID']  # Fetch the DoctorID of the first doctor
    print(f"DoctorID to delete: {doctor_id}")  # Debugging

    # Check if Doctor has any related shifts or appointments
    check_shifts_query = "SELECT * FROM DoctorShifts WHERE DoctorID = %s"
    shifts = execute_query(check_shifts_query, (doctor_id,), fetch=True)
    if shifts:
        print(f"Doctor '{data['doctor_name']}' has related shifts. Cannot delete.")  # Debugging
        return render_template('add_doctor.html', message=f"Doctor '{data['doctor_name']}' has related shifts and cannot be deleted.", message_type='error')

    # Delete doctor record
    delete_query = "DELETE FROM Doctor WHERE DoctorID = %s"
    result = execute_query(delete_query, (doctor_id,))

    # Check the result of the DELETE query
    print(f"Result of DELETE query: {result}")  # Debugging

    if result is not None and result > 0:  # Check if rows were affected
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


####################################################Doctoe Table END#######################################################
################################################Appointment table ################################################
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
    status = request.form['status']  

    connection = connect_db()
    cursor = connection.cursor()

    # Insert appointment data into the database
    cursor.execute('''INSERT INTO Appointment (PatientID, DoctorID, AppointmentDate, AppointmentTime, Notes, Status)
                      VALUES (%s, %s, %s, %s, %s, %s)''',
                   (patient_id, doctor_id, appointment_date, appointment_time, notes, status))
    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for('add_appointment')) 

@app.route('/update_appointment', methods=['POST'])
def update_appointment():
    patient_id = request.form['patient_id']
    doctor_id = request.form['doctor_id']
    appointment_date = request.form.get('appointment_date')  
    appointment_time = request.form.get('appointment_time')  
    status = request.form.get('status')  
    notes = request.form.get('notes')  

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
    try:
        # Get data from the form
        patient_name = request.form['patient_name']  # Now it matches the form field name
        doctor_name = request.form['doctor_name']    # Now it matches the form field name
        appointment_date = request.form['appointment_date']  # Get appointment date from the form

        # Fetch PatientID from Patient table using patient name
        patient_query = "SELECT PatientID FROM Patient WHERE CONCAT(FirstName, ' ', LastName) = %s"
        patient_id_result = execute_query(patient_query, (patient_name,), fetch=True)

        if not patient_id_result:
            return jsonify({"message": f"Patient '{patient_name}' not found in the database."}), 404

        patient_id = patient_id_result[0]['PatientID']  # Fetch PatientID

        # Fetch DoctorID from Doctor table using doctor name
        doctor_name_query = "SELECT DoctorID FROM Doctor WHERE Name = %s"
        doctor_id_result = execute_query(doctor_name_query, (doctor_name,), fetch=True)

        if not doctor_id_result:
            return jsonify({"message": f"Doctor '{doctor_name}' not found in the database."}), 404

        doctor_id = doctor_id_result[0]['DoctorID']  # Fetch DoctorID

        connection = connect_db()
        cursor = connection.cursor()

        # Delete appointment record based on patient_id, doctor_id, and appointment_date
        cursor.execute("DELETE FROM Appointment WHERE PatientID = %s AND DoctorID = %s AND AppointmentDate = %s", 
                       (patient_id, doctor_id, appointment_date))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "Appointment deleted successfully"})

    except KeyError as e:
        return jsonify({"message": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        print("Unexpected error:", str(e))  # Debugging
        return jsonify({"message": f"An unexpected error occurred: {str(e)}"}), 500
################################################### Invoice table #############################################################


@app.route('/insert_invoice', methods=['POST'])
def insert_invoice():

    data = request.form
    full_name = data['patient_name']  # Get the full name from the form
    
    # Split the full name into first and last names
    name_parts = full_name.split(' ', 1)
    
    if len(name_parts) < 2:
        return render_template('add_invoice.html', message='Please provide both first and last names.', message_type='error', patients=get_patient_names())

    first_name, last_name = name_parts  # Unpack the split name
    
    # Get PatientID based on full name (FirstName + LastName)
    query = """
        SELECT PatientID 
        FROM Patient 
        WHERE FirstName = %s AND LastName = %s
    """
    params = (first_name, last_name)
    result = execute_query(query, params, fetch=True)
    
    if result:
        patient_id = result[0]['PatientID']
    else:
        return render_template('add_invoice.html', message='Patient not found.', message_type='error', patients=get_patient_names())
    
    # Get the total paid, total amount, discount applied, and payment method
    try:
        # Trim any whitespace from the inputs and check if they're not empty
        total_paid_str = data['total_paid'].strip() if data['total_paid'] else ''
        total_amount_str = data['total_amount'].strip() if data['total_amount'] else ''
        
        if total_paid_str and total_amount_str:
            total_paid = float(total_paid_str)
            total_amount = float(total_amount_str)
        else:
            raise ValueError("Invalid input: Total Amount or Total Paid is empty.")
        
        discount_applied = float(data.get('discount_applied', '0.00').strip())  # Default to 0 if not provided
        
    except ValueError as e:
        return render_template('add_invoice.html', message=f'Invalid input for Total Amount or Total Paid. Error: {str(e)}', message_type='error', patients=get_patient_names())
    
    payment_method = data['payment_method']
    
    # Insert the invoice with the discount applied and total amount
    query = """
        INSERT INTO Invoice (PatientID, TotalAmount, TotalPaid, DiscountApplied, PaymentMethod)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (patient_id, total_amount, total_paid, discount_applied, payment_method)
    
    # Debugging - print query and parameters to ensure they're correct
    print("Executing query:", query)
    print("With parameters:", params)
    
    result = execute_query(query, params)
    
    if result:
        print("Insert successful")
        return render_template('add_invoice.html', message='Invoice inserted successfully.', message_type='success', patients=get_patient_names())
    else:
        print("Insert failed")
        return render_template('add_invoice.html', message='Failed to insert invoice.', message_type='error', patients=get_patient_names())

@app.route('/update_invoice', methods=['GET', 'POST'])
def update_invoice():
    if request.method == 'GET':
        # Fetch all patients for the dropdown
        patient_query = "SELECT PatientID, FirstName, LastName FROM Patient"
        patients = execute_query(patient_query, fetch=True)
        
        return render_template('add_invoice.html', patients=patients)
    
    elif request.method == 'POST':
        data = request.form
        
        patient_id = data.get('patient_name')
        
        if not patient_id:
            return render_template('add_invoice.html', message='Please select a patient.', message_type='error')

        patient_query = "SELECT FirstName, LastName FROM Patient WHERE PatientID = %s"
        patient = execute_query(patient_query, (patient_id,), fetch=True)

        if not patient:
            return render_template('add_invoice.html', message='Patient not found.', message_type='error')

        update_fields = []
        params = []

        # Check if TotalAmount is provided and add it to the update list
        if 'total_amount' in data and data['total_amount'].strip():
            total_amount = float(data['total_amount'].strip())
            update_fields.append("TotalAmount = %s")
            params.append(total_amount)
        
        # Check if TotalPaid is provided and add it to the update list
        if 'total_paid' in data and data['total_paid'].strip():
            total_paid = float(data['total_paid'].strip())
            update_fields.append("TotalPaid = %s")
            params.append(total_paid)
        
        # Check if DiscountApplied is provided and add it to the update list
        if 'discount_applied' in data and data['discount_applied'].strip():
            discount_applied = float(data['discount_applied'].strip())
            update_fields.append("DiscountApplied = %s")
            params.append(discount_applied)
        
        # Check if PaymentMethod is provided and add it to the update list
        if 'payment_method' in data and data['payment_method'].strip():
            payment_method = data['payment_method'].strip()
            update_fields.append("PaymentMethod = %s")
            params.append(payment_method)

        # If no fields were provided to update, return an error message
        if not update_fields:
            return render_template('add_invoice.html', message='No fields to update provided.', message_type='error')

        # Add the condition to update the specific invoice based on PatientID
        update_query = f"""
            UPDATE Invoice
            SET {', '.join(update_fields)}
            WHERE PatientID = %s
        """
        params.append(patient_id) 

        # Execute the query to update the invoice
        result = execute_query(update_query, tuple(params))
        
        if result:
            return render_template('add_invoice.html', message='Invoice updated successfully.', message_type='success')
        else:
            return render_template('add_invoice.html', message='Failed to update invoice.', message_type='error')

@app.route('/delete_invoice', methods=['POST'])
def delete_invoice():
    try:
        data = request.form
        patient_id = data['patient_id'] 
        
        # Attempt to delete the invoice based on the patient_id
        query = "DELETE FROM Invoice WHERE PatientID = %s"
        params = (patient_id,)
        result = execute_query(query, params)
        
        # Fetch patients list after attempting deletion
        patients = execute_query("SELECT PatientID, FirstName, LastName FROM Patient", fetch=True)

        if result:
            # Invoice deleted successfully
            return render_template('add_invoice.html', message='Invoice deleted successfully.', message_type='success', patients=patients)
        else:
            # Failed to delete invoice
            return render_template('add_invoice.html', message='Failed to delete invoice.', message_type='error', patients=patients)

    except Exception as e:
        print(f"Error: {e}")
        return render_template('add_invoice.html', message='An error occurred while deleting the invoice.', message_type='error', patients=[])
########################################################### Report for Invoice###########################################
@app.route('/invoice')
def income_report():
    query = """

    SELECT p.PatientID, CONCAT(p.FirstName, ' ', p.LastName) AS PatientName,
           i.TotalAmount, i.TotalPaid, (i.TotalAmount - i.TotalPaid) AS RemainingBalance
    FROM Patient p
    JOIN Invoice i ON p.PatientID = i.PatientID
"""

    income_data = execute_query(query, fetch=True)
    return render_template('invoice.html', income_data=income_data)
######################################### Medical procesure table ##########################################
@app.route('/MedicalProcedure')
def MedicalProcedure():
    try:
        db = connect_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT PatientID, CONCAT(FirstName, ' ', LastName) AS PatientName FROM Patient")
            patients = cursor.fetchall()

            # Fetch Patients who have procedures
            cursor.execute("""
                SELECT DISTINCT p.PatientID, CONCAT(p.FirstName, ' ', p.LastName) AS PatientName
                FROM MedicalProcedure mp
                JOIN Patient p ON mp.PatientID = p.PatientID
            """)
            patientsMed = cursor.fetchall()

            # Fetch Doctors
            cursor.execute("SELECT DoctorID, Name FROM Doctor")
            doctors = cursor.fetchall()

            # Fetch Procedures
            cursor.execute("SELECT ProcedureID, ProcedureName FROM MedicalProcedure")
            procedures = cursor.fetchall()

        db.close()  

        return render_template(
            'MedicalProcedure.html',
            patientsMed=patientsMed,
            patients=patients,
            doctors=doctors,
            procedures=procedures
        )
    except Exception as e:
        return f"Error: {str(e)}"

# Insert Procedure
@app.route('/insert', methods=['POST'])
def insert_procedure():
    try:
        data = request.form
        db = connect_db()  
        with db.cursor() as cursor:
            query = """
            INSERT INTO MedicalProcedure (DoctorID, PatientID, ProcedureName, ProcedureCost, 
                                           InsuranceCoverage, TreatmentName, TreatmentCost, 
                                           InsuranceDiscount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                data['doctor_name'],
                data['patient_name'],
                data['procedure_name'],
                data['procedure_cost'],
                data.get('insurance_coverage', 0),
                data['treatment_name'],
                data['treatment_cost'],
                data.get('insurance_discount', 0)
            ))
            db.commit()

        db.close()  
        return "Procedure inserted successfully!" 
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/update', methods=['POST'])
def update_procedure():
    try:
        data = request.form
        patient_id = data['patient_name']
        procedure_name = data['procedure_name_update']
        new_cost = data.get('procedure_cost_update')
        new_coverage = data.get('insurance_coverage_update')
        new_treatment_name = data.get('treatment_name_update')
        new_treatment_cost = data.get('treatment_cost_update')
        new_discount = data.get('insurance_discount_update')

        db = connect_db()  
        with db.cursor() as cursor:
           
            cursor.execute("""
                SELECT mp.ProcedureID 
                FROM MedicalProcedure mp
                WHERE mp.PatientID = %s AND mp.ProcedureName = %s
            """, (patient_id, procedure_name))
            result = cursor.fetchone()

            if result:
                procedure_id = result[0]

                update_query = "UPDATE MedicalProcedure SET "
                params = []

                if new_cost:
                    update_query += "ProcedureCost = %s, "
                    params.append(new_cost)
                if new_coverage:
                    update_query += "InsuranceCoverage = %s, "
                    params.append(new_coverage)
                if new_treatment_name:
                    update_query += "TreatmentName = %s, "
                    params.append(new_treatment_name)
                if new_treatment_cost:
                    update_query += "TreatmentCost = %s, "
                    params.append(new_treatment_cost)
                if new_discount:
                    update_query += "InsuranceDiscount = %s, "
                    params.append(new_discount)

                # Clean up the trailing comma
                update_query = update_query.rstrip(', ')

                # Add the WHERE clause to ensure we update the correct row
                update_query += " WHERE ProcedureID = %s AND PatientID = %s"
                params.extend([procedure_id, patient_id])

                # Execute the update
                cursor.execute(update_query, tuple(params))
                db.commit()
                db.close()  # Close the database connection
                return f"Procedure '{procedure_name}' for patient '{patient_id}' updated successfully!"
            else:
                db.close()  # Close the database connection
                return f"No matching procedure found for patient '{patient_id}' and procedure '{procedure_name}'."
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/delete', methods=['POST'])
def delete_procedure():
    try:
        data = request.form
        patient_id = data['patient_name']
        procedure_name = data['procedure_name_delete']

        db = connect_db()  # Open a new connection
        with db.cursor() as cursor:
            # Find the ProcedureID based on PatientID and ProcedureName
            cursor.execute("""
                SELECT mp.ProcedureID 
                FROM MedicalProcedure mp
                WHERE mp.PatientID = %s AND mp.ProcedureName = %s
            """, (patient_id, procedure_name))
            result = cursor.fetchone()

            if result:
                procedure_id = result[0]

                # Delete the procedure
                cursor.execute("""
                    DELETE FROM MedicalProcedure 
                    WHERE ProcedureID = %s AND PatientID = %s
                """, (procedure_id, patient_id))
                db.commit()
                db.close()  # Close the database connection
                return f"Procedure '{procedure_name}' for patient '{patient_id}' deleted successfully!"
            else:
                db.close()  # Close the database connection
                return f"No matching procedure found for patient '{patient_id}' and procedure '{procedure_name}'."
    except Exception as e:
        return f"Error: {str(e)}"
###################################### Medical procedure END ############################################################
###################################### Xray image table ##############################################################

# Route to insert X-ray image
@app.route('/insert_xray_image', methods=['POST'])
def insert_xray_image():
    data = request.form
    patient_id = data.get('patient_id')
    xray_image_path = data.get('xray_image_path')
    
    query = "INSERT INTO XrayImage (PatientID, PhotoPath) VALUES (%s, %s)"
    params = (patient_id, xray_image_path)
    
    result = execute_query(query, params)
    
    if result:
        message = 'X-ray image inserted successfully.'
        message_type = 'success'
    else:
        message = 'Failed to insert X-ray image.'
        message_type = 'error'
    
    # Fetch patient names after insertion
    patients = execute_query("SELECT PatientID, CONCAT(FirstName, ' ', LastName) AS PatientName FROM Patient", fetch=True)
    return render_template('XrayImage.html', message=message, message_type=message_type, patients=patients)

# Route to update X-ray image
@app.route('/update_xray_image', methods=['POST'])
def update_xray_image():
    data = request.form
    patient_id = data.get('patient_id')
    xray_image_path_old = data.get('xray_image_path_old')
    xray_image_path_new = data.get('xray_image_path')

    query = """
        UPDATE XrayImage 
        SET PhotoPath = %s 
        WHERE PatientID = %s AND PhotoPath = %s
    """
    params = (xray_image_path_new, patient_id, xray_image_path_old)

    result = execute_query(query, params)

    if result:
        message = 'X-ray image updated successfully.'
        message_type = 'success'
    else:
        message = 'Failed to update X-ray image.'
        message_type = 'error'

    # Fetch patient names after update
    patients = execute_query("SELECT PatientID, CONCAT(FirstName, ' ', LastName) AS PatientName FROM Patient", fetch=True)
    return render_template('XrayImage.html', message=message, message_type=message_type, patients=patients)

# Route to delete X-ray image
@app.route('/delete_xray_image', methods=['POST'])
def delete_xray_image():
    data = request.form
    patient_id = data.get('patient_id')
    xray_image_path = data.get('xray_image_path')

    query = "DELETE FROM XrayImage WHERE PatientID = %s AND PhotoPath = %s"
    params = (patient_id, xray_image_path)

    result = execute_query(query, params)

    if result:
        message = 'X-ray image deleted successfully.'
        message_type = 'success'
    else:
        message = 'Failed to delete X-ray image.'
        message_type = 'error'

    # Fetch patient names after delete
    patients = execute_query("SELECT PatientID, CONCAT(FirstName, ' ', LastName) AS PatientName FROM Patient", fetch=True)
    return render_template('XrayImage.html', message=message, message_type=message_type, patients=patients)

@app.route('/add_appointment')
def add_appointment():
    # Fetch patients and doctors to display in the form
    patients = execute_query("SELECT PatientID, FirstName, LastName FROM Patient", fetch=True)
    doctors = execute_query("SELECT DoctorID, Name FROM Doctor", fetch=True)
    return render_template('add_appointment.html', patients=patients, doctors=doctors)

# Route for adding patient
@app.route('/add_patient')
def addpatient():
    return render_template('add_patient.html')

# Route for adding doctor
@app.route('/add_doctor')
def add_doctor():
    return render_template('add_doctor.html')

# Route for my clinic page
@app.route('/myClinic')
def myClinic():
    return render_template('myClinic.html')
@app.route('/add_invoice')
def add_invoice():
    patients = get_patient_names()
    return render_template('add_invoice.html', patients=patients)
@app.route('/invoice')
def invoice():
    return render_template('invoice.html')

@app.route('/XrayImage')
def XrayImage():
    query = "SELECT PatientID, CONCAT(FirstName, ' ', LastName) AS PatientName FROM Patient"
    patients = execute_query(query, fetch=True)
    return render_template('XrayImage.html', patients=patients)
@app.route('/fetch_patient_names')
def fetch_patient_names():
    query = "SELECT PatientID, FirstName, LastName FROM Patient"
    patients = execute_query(query, fetch=True)
    return jsonify(patients)

@app.route('/fetch_doctor_names', methods=['GET'])
def get_doctor_names():
    query = "SELECT DoctorID, Name FROM Doctor"
    doctors = execute_query(query, fetch=True)
    return jsonify(doctors)
def get_patient_names():
    query = "SELECT PatientID, FirstName, LastName FROM Patient"
    return execute_query(query, fetch=True)
@app.route("/doctor_home")
def doctor_home():
    connection = None
    cursor = None
    doctor_shifts = {}

    try:
        # Connect to the database
        connection = connect_db()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # Fetch doctor shifts
        query = """
        SELECT d.Name, ds.StartTime, ds.EndTime
        FROM DoctorShifts ds
        JOIN Doctor d ON ds.DoctorID = d.DoctorID
        """
        cursor.execute(query)

        # Fetch all shift data
        shifts = cursor.fetchall()

        # Process each shift
        for shift in shifts:
            doctor_name = shift['Name']
            start_time = shift['StartTime']
            end_time = shift['EndTime']

            # Convert start_time and end_time to datetime objects
            start_time_obj = datetime.strptime(str(start_time), '%H:%M:%S')
            end_time_obj = datetime.strptime(str(end_time), '%H:%M:%S')

            # Calculate the duration of the shift
            duration = end_time_obj - start_time_obj

            # Convert the duration to hours
            total_hours = duration.total_seconds() / 3600.0  # Convert seconds to hours

            # Store shift data in the dictionary
            if doctor_name not in doctor_shifts:
                doctor_shifts[doctor_name] = {
                    'shifts': [],
                    'total_hours': 0
                }

            # Append shift details
            doctor_shifts[doctor_name]['shifts'].append(f"Shift: {start_time} - {end_time}")
            doctor_shifts[doctor_name]['total_hours'] += total_hours

        # Query to fetch doctor details along with shifts
        query = """
            SELECT Doctor.Name, Doctor.Specialization, Doctor.Salary, DoctorShifts.DayOfWeek, DoctorShifts.StartTime, DoctorShifts.EndTime
            FROM Doctor
            LEFT JOIN DoctorShifts ON Doctor.DoctorID = DoctorShifts.DoctorID
        """
        cursor.execute(query)
        result = cursor.fetchall()

        doctors = []
        for row in result:
            doctor = {
                'Name': row['Name'],
                'Specialization': row['Specialization'],
                'Salary': row['Salary'],
                'DayOfWeek': row['DayOfWeek'],
                'StartTime': row['StartTime'],
                'EndTime': row['EndTime'],
                'Shifts': doctor_shifts.get(row['Name'], {'shifts': [], 'total_hours': 0})
            }
            doctors.append(doctor)

        return render_template('doctor_home.html', doctors=doctors, doctor_shifts=doctor_shifts)

    except Exception as e:
        # Handle any errors that occur during the database connection or query execution
        print(f"Error: {e}")
        return render_template('doctor_home.html', message='Error fetching doctor data.', message_type='error')

@app.route("/home")
def home():
    return render_template("home.html")  
@app.route('/patient_info', methods=['GET', 'POST'])
def patient_info():
    # Connect to MySQL
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    # Initialize an empty result list
    result = []
    
    # If the form is submitted (searching for a patient)
    if request.method == 'POST':
        search_name = request.form.get('search_name', '')

        # Query to get patient information along with their x-ray images and medical procedures
        query = """
            SELECT 
                p.PatientID,
                p.FirstName,
                p.LastName,
                p.DateOfBirth,
                p.Balance,
                p.PhoneNumber,
                p.EmergencyContact,
                p.DrugAllergy,
                p.InfectiousDiseases,
                p.ConstantStatus AS PatientStatus,
                p.ReferralStatus AS Referral,
                p.Gender,
                p.InsuranceStatus,
                p.MedicalHistory,
                x.PhotoPath AS XrayImage,
                mp.ProcedureName,
                mp.ProcedureCost,
                mp.InsuranceCoverage,
                mp.TreatmentName,
                mp.TreatmentCost,
                mp.InsuranceDiscount
            FROM 
                Patient p
            LEFT JOIN 
                XrayImage x ON p.PatientID = x.PatientID
            LEFT JOIN 
                MedicalProcedure mp ON p.PatientID = mp.PatientID
            WHERE 
                p.FirstName LIKE %s OR p.LastName LIKE %s;
        """
        
        cursor.execute(query, ('%' + search_name + '%', '%' + search_name + '%'))
        result = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('patient_info.html', patient_data=result)


if __name__ == '__main__':
    app.run(debug=True)
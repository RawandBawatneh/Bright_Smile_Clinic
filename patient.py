from flask import Flask, render_template, request, redirect, url_for
import pymysql

app = Flask(__name__)

# MySQL database connection setup
def connect_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='0569458641#2003',  # Replace with your MySQL password
        database='ClinicManagement'
    )

@app.route('/')

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    connection = connect_db()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    
    if request.method == 'POST':
        first_name = request.form['FirstName']
        last_name = request.form['LastName']
        date_of_birth = request.form['DateOfBirth']
        balance = request.form['Balance']
        phone_number = request.form['PhoneNumber']
        emergency_contact = request.form['EmergencyContact']
        drug_allergy = request.form['DrugAllergy']
        gender = request.form['Gender']
        insurance_status = request.form['InsuranceStatus']
        medical_history = request.form['MedicalHistory']
        address = request.form['Address']  # New field for address
        
        # Insert the new patient into the database
        cursor.execute('''INSERT INTO Patient (FirstName, LastName, DateOfBirth, Balance, PhoneNumber, 
                        EmergencyContact, DrugAllergy, Gender, InsuranceStatus, MedicalHistory)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                        (first_name, last_name, date_of_birth, balance, phone_number, emergency_contact, 
                         drug_allergy, gender, insurance_status, medical_history))
        connection.commit()
        
        # Fetch the newly inserted PatientID (this assumes PatientID is auto-incremented)
        patient_id = cursor.lastrowid
        
        # Insert the patient's address into the PatientAddress table
        cursor.execute('''INSERT INTO PatientAddress (PatientID, Address) VALUES (%s, %s)''', 
                        (patient_id, address))
        connection.commit()
        
        # Redirect to the same page after insertion
        return redirect(url_for('add_patient'))
    
    # Fetch patients for update and delete forms
    cursor.execute("SELECT * FROM Patient")
    patients = cursor.fetchall()

    # Close connection
    cursor.close()
    connection.close()

    return render_template('add_patient.html', patients=patients)


@app.route('/update_patient', methods=['POST'])
def update_patient():
    patient_id = request.form['patient_id']
    attribute = request.form['attribute']
    new_value = request.form['new_value']

    # Connect to the database
    connection = connect_db()
    cursor = connection.cursor()

    # Update the patient attribute
    update_query = f"UPDATE Patient SET {attribute} = %s WHERE PatientID = %s"
    cursor.execute(update_query, (new_value, patient_id))
    connection.commit()

    # Update address if the attribute to update is 'Address'
    if attribute == 'Address':
        cursor.execute("UPDATE PatientAddress SET Address = %s WHERE PatientID = %s", 
                       (new_value, patient_id))
        connection.commit()

    # Close connection
    cursor.close()
    connection.close()

    # Redirect back to the page after update
    return redirect(url_for('add_patient'))


@app.route('/delete_patient', methods=['POST'])
def delete_patient():
    patient_id = request.form['patient_id']

    # Connect to the database
    connection = connect_db()
    cursor = connection.cursor()

    # Delete the patient's address first to avoid foreign key issues
    cursor.execute("DELETE FROM PatientAddress WHERE PatientID = %s", (patient_id,))
    connection.commit()

    # Delete the patient record
    cursor.execute("DELETE FROM Patient WHERE PatientID = %s", (patient_id,))
    connection.commit()

    # Close connection
    cursor.close()
    connection.close()

    # Redirect back to the page after deletion
    return redirect(url_for('add_patient'))


if __name__ == '__main__':
    app.run(debug=True)

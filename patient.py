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
    if request.method == 'POST':
        # Fetch form data
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
            cursor = connection.cursor()

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
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return redirect(url_for('add_patient'))

    return render_template('add_patient.html')
@app.route('/update_patient', methods=['POST'])
def update_patient():
    patient_id = request.form['patient_id']
    attribute = request.form['attribute']
    new_value = request.form['new_value']

    try:
        connection = connect_db()
        cursor = connection.cursor()

        query = f"UPDATE Patient SET {attribute} = %s WHERE PatientID = %s"
        cursor.execute(query, (new_value, patient_id))
        connection.commit()
        print("Patient updated successfully!")
    except Exception as e:
        print(f"Error updating patient: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return redirect(url_for('manage_patients'))

@app.route('/delete_patient', methods=['POST'])
def delete_patient():
    patient_id = request.form['patient_id']

    try:
        connection = connect_db()
        cursor = connection.cursor()

        query = "DELETE FROM Patient WHERE PatientID = %s"
        cursor.execute(query, (patient_id,))
        connection.commit()
        print("Patient deleted successfully!")
    except Exception as e:
        print(f"Error deleting patient: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return redirect(url_for('manage_patients'))


if __name__ == '__main__':
    app.run(debug=True)

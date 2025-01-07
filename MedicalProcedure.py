from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql

app = Flask(__name__)
app.secret_key = "secret_key"

# MySQL connection configuration
db = pymysql.connect(
    host="localhost",
    user="root",
    password="0569458641#2003",
    database="ClinicManagement"
)

# Home route
@app.route('/')
def MedicalProcedure():
    try:
        # Fetch Patients 
        with db.cursor() as cursor:
            cursor.execute("SELECT PatientID, CONCAT(FirstName, ' ', LastName) AS PatientName FROM Patient")
            patients = cursor.fetchall()
        # Fetch Patients from MedicalProcedure table (those who have procedures)
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT p.PatientID, CONCAT(p.FirstName, ' ', p.LastName) AS PatientName
                FROM MedicalProcedure mp
                JOIN Patient p ON mp.PatientID = p.PatientID
            """)
            patientsMed = cursor.fetchall()

        # Fetch Doctors
        with db.cursor() as cursor:
            cursor.execute("SELECT DoctorID, Name FROM Doctor")
            doctors = cursor.fetchall()

        # Fetch Procedures
        with db.cursor() as cursor:
            cursor.execute("SELECT ProcedureID, ProcedureName FROM MedicalProcedure")
            procedures = cursor.fetchall()

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
        flash("Procedure inserted successfully!")
    except Exception as e:
        flash(f"Error: {str(e)}")
    return redirect(url_for('MedicalProcedure'))

# Update Procedure
@app.route('/update', methods=['POST'])
def update_procedure():
    try:
        data = request.form
        patient_name = data['patient_name']
        procedure_name = data['procedure_name_update']
        new_cost = data.get('procedure_cost_update')
        new_coverage = data.get('insurance_coverage_update')
        new_treatment_name = data.get('treatment_name_update')
        new_treatment_cost = data.get('treatment_cost_update')
        new_discount = data.get('insurance_discount_update')

        with db.cursor() as cursor:
            # First, find the PatientID and ProcedureID
            cursor.execute("""
                SELECT p.PatientID, mp.ProcedureID 
                FROM MedicalProcedure mp
                JOIN Patient p ON mp.PatientID = p.PatientID
                WHERE CONCAT(p.FirstName, ' ', p.LastName) = %s AND mp.ProcedureName = %s
            """, (patient_name, procedure_name))
            result = cursor.fetchone()

            if result:
                patient_id = result[0]
                procedure_id = result[1]

                # Build the update query
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
                flash("Procedure updated successfully!")
            else:
                flash(f"No matching procedure found for {patient_name} and {procedure_name}.")
    except Exception as e:
        flash(f"Error: {str(e)}")

    return redirect(url_for('MedicalProcedure'))

# Delete Procedure
@app.route('/delete', methods=['POST'])
def delete_procedure():
    try:
        data = request.form
        patient_name = data['patient_name']
        procedure_name = data['procedure_name_delete']

        with db.cursor() as cursor:
            # Find the PatientID and ProcedureID for the given patient and procedure
            cursor.execute("""
                SELECT p.PatientID, mp.ProcedureID 
                FROM MedicalProcedure mp
                JOIN Patient p ON mp.PatientID = p.PatientID
                WHERE CONCAT(p.FirstName, ' ', p.LastName) = %s AND mp.ProcedureName = %s
            """, (patient_name, procedure_name))
            result = cursor.fetchone()

            if result:
                patient_id = result[0]
                procedure_id = result[1]

                # Delete the procedure
                cursor.execute("""
                    DELETE FROM MedicalProcedure 
                    WHERE ProcedureID = %s AND PatientID = %s
                """, (procedure_id, patient_id))
                db.commit()
                flash("Procedure deleted successfully!")
            else:
                flash(f"No matching procedure found for {patient_name} and {procedure_name}.")
    except Exception as e:
        flash(f"Error: {str(e)}")

    return redirect(url_for('MedicalProcedure'))


if __name__ == '__main__':
    app.run(debug=True)

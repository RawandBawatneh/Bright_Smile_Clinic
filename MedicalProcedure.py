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

# Insert Medical Procedure
@app.route('/insert_procedure', methods=['POST'])
def insert_procedure():
    data = request.form
    query = """
        INSERT INTO MedicalProcedure (DoctorID, ProcedureName, ProcedureCost, InsuranceCoverage) 
        VALUES (%s, %s, %s, %s)
    """
    params = (data['doctor_id'], data['procedure_name'], data['procedure_cost'], data.get('insurance_coverage', 0.00))
    result = execute_query(query, params)
    if result:
        return jsonify({'message': 'Procedure inserted successfully.'}), 201
    return jsonify({'message': 'Failed to insert procedure.'}), 400

# Update Medical Procedure
@app.route('/update_procedure', methods=['POST'])
def update_procedure():
    data = request.form

    # Step 1: Fetch ProcedureID based on ProcedureName
    procedure_name_query = "SELECT ProcedureID FROM MedicalProcedure WHERE ProcedureName = %s"
    procedure_id_result = execute_query(procedure_name_query, (data['procedure_name'],), fetch=True)

    if not procedure_id_result:
        return jsonify({'message': f"Procedure '{data['procedure_name']}' not found."}), 400

    procedure_id = procedure_id_result[0]['ProcedureID']  # Fetch the ProcedureID

    # Step 2: Update Procedure with Resolved ProcedureID
    update_query = f"""
        UPDATE MedicalProcedure 
        SET {data['attribute']} = %s 
        WHERE ProcedureID = %s
    """
    params = (data['new_value'], procedure_id)
    result = execute_query(update_query, params)

    if result:
        return jsonify({'message': 'Procedure updated successfully.'}), 200
    return jsonify({'message': 'Failed to update procedure.'}), 400

# Delete Medical Procedure
@app.route('/delete_procedure', methods=['POST'])
def delete_procedure():
    data = request.form

    # Step 1: Fetch ProcedureID based on ProcedureName
    procedure_name_query = "SELECT ProcedureID FROM MedicalProcedure WHERE ProcedureName = %s"
    procedure_id_result = execute_query(procedure_name_query, (data['procedure_name'],), fetch=True)

    if not procedure_id_result:
        return jsonify({'message': f"Procedure '{data['procedure_name']}' not found."}), 400

    procedure_id = procedure_id_result[0]['ProcedureID']  # Fetch the ProcedureID

    # Step 2: Delete Procedure with Resolved ProcedureID
    delete_query = "DELETE FROM MedicalProcedure WHERE ProcedureID = %s"
    result = execute_query(delete_query, (procedure_id,))

    if result > 0:  # Check if rows were affected
        return jsonify({'message': 'Procedure deleted successfully.'}), 200
    return jsonify({'message': 'Failed to delete procedure.'}), 400

# Fetch doctor names for dropdown
@app.route('/fetch_doctor_names', methods=['GET'])
def fetch_doctor_names():
    query = "SELECT Name FROM Doctor"
    result = execute_query(query, fetch=True)
    if result:
        doctors = [{'Name': row['Name']} for row in result]
        return jsonify(doctors), 200
    return jsonify({'message': 'Failed to fetch doctor names.'}), 400

if __name__ == '__main__':
    app.run(debug=True)

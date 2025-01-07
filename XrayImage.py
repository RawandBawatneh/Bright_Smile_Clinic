from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)

# Function to connect to the database
def connect_db():
    return {
        'host': 'localhost',
        'user': 'root',
        'password': '0569458641#2003',
        'database': 'ClinicManagement'
    }

# Function to execute a query
def execute_query(query, params=None, fetch=False):
    conn = mysql.connector.connect(**connect_db())
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        result = cursor.fetchall() if fetch else cursor.rowcount
        conn.commit()
        return result
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

# Function to get all patients
def get_patients():
    query = "SELECT PatientID, CONCAT(FirstName, ' ', LastName) AS PatientName FROM Patient"
    return execute_query(query, fetch=True)

# Route for home page (with forms)
@app.route('/')
def home():
    patients = get_patients()
    return render_template('XrayImage.html', patients=patients)

# Route to fetch patient names as JSON for the dropdowns
@app.route('/fetch_patient_names', methods=['GET'])
def fetch_patient_names():
    patients = get_patients()
    return jsonify(patients) if patients else jsonify({'error': 'Failed to fetch patient names'})

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
    
    patients = get_patients()
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

    patients = get_patients()
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

    patients = get_patients()
    return render_template('XrayImage.html', message=message, message_type=message_type, patients=patients)

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)

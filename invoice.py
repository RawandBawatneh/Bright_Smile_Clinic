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
    query = "SELECT PatientID, FirstName, LastName FROM Patient"
    patients = execute_query(query, fetch=True)
    return render_template('add_invoice.html', patients=patients)

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

# Update invoice
@app.route('/update_invoice', methods=['POST'])
def update_invoice():
    data = request.form
    patient_id = data['patient_id']  # Use patient_id from the form
    
    # Formulate dynamic update query based on the attribute
    query = """
        UPDATE Invoice 
        SET {attribute} = %s 
        WHERE PatientID = %s
    """.format(attribute=data['attribute'])
    params = (data['new_value'], patient_id)
    result = execute_query(query, params)
    
    patients = execute_query("SELECT PatientID, FirstName, LastName FROM Patient", fetch=True)  # Fetch patients again
    
    if result:
        return render_template('add_invoice.html', message='Invoice updated successfully.', message_type='success', patients=patients)
    return render_template('add_invoice.html', message='Failed to update invoice.', message_type='error', patients=patients)

# Delete invoice
@app.route('/delete_invoice', methods=['POST'])
def delete_invoice():
    data = request.form
    patient_id = data['patient_id']  # Use patient_id from the form
    
    query = "DELETE FROM Invoice WHERE PatientID = %s"
    params = (patient_id,)
    result = execute_query(query, params)
    
    patients = execute_query("SELECT PatientID, FirstName, LastName FROM Patient", fetch=True)  # Fetch patients again
    
    if result:
        return render_template('add_invoice.html', message='Invoice deleted successfully.', message_type='success', patients=patients)
    return render_template('add_invoice.html', message='Failed to delete invoice.', message_type='error', patients=patients)

def get_patient_names():
    query = "SELECT PatientID, FirstName, LastName FROM Patient"
    return execute_query(query, fetch=True)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect("saf_printings.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key support
    return conn


### ROUTES ###

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", 
                       (product_name, price, quantity))
        conn.commit()
        conn.close()

        return redirect(url_for('view_products'))

    return render_template('add_product.html')

@app.route('/view_products')
def view_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    
    return render_template('view_products.html', products=products)

@app.route('/generate_invoice', methods=['GET', 'POST'])
def generate_invoice():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        contact = request.form['contact_number']
        address = request.form['address']
        total_price = 0

        cursor.execute("INSERT INTO invoices (customer_name, contact, address, total_price) VALUES (?, ?, ?, ?)", 
                       (customer_name, contact, address, total_price))
        invoice_id = cursor.lastrowid  # Get last inserted invoice ID

        for i in range(len(request.form.getlist('product_name[]'))):
            product_name = request.form.getlist('product_name[]')[i]
            quantity = int(request.form.getlist('quantity[]')[i])
            price = float(request.form.getlist('price[]')[i])
            discount = float(request.form.getlist('discount[]')[i])

            total_price += quantity * price * (1 - discount / 100)

            cursor.execute("INSERT INTO invoice_items (invoice_id, product_name, quantity, price, discount) VALUES (?, ?, ?, ?, ?)", 
                           (invoice_id, product_name, quantity, price, discount))

        cursor.execute("UPDATE invoices SET total_price = ? WHERE id = ?", (total_price, invoice_id))
        conn.commit()
        conn.close()

        return redirect(url_for('view_invoices'))

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    return render_template('generate_invoice.html', products=products)

@app.route('/view_invoices')
def view_invoices():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM invoices")
    invoices = cursor.fetchall()
    invoice_data = []

    for invoice in invoices:
        cursor.execute("SELECT product_name, quantity, price, discount FROM invoice_items WHERE invoice_id = ?", (invoice["id"],))
        products = cursor.fetchall()
        
        invoice_data.append({
            'id': invoice["id"],
            'customer_name': invoice["customer_name"],
            'contact': invoice["contact"],
            'address': invoice["address"],
            'total_price': invoice["total_price"],
            'products': products
        })

    conn.close()
    return render_template('view_invoices.html', invoices=invoice_data)
@app.route('/delete_invoice/<int:invoice_id>', methods=['DELETE'])
def delete_invoice(invoice_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # First, delete related invoice items
        cursor.execute("DELETE FROM invoice_items WHERE invoice_id=?", (invoice_id,))

        # Then, delete the invoice itself
        cursor.execute("DELETE FROM invoices WHERE id=?", (invoice_id,))

        conn.commit()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
@app.route('/remove_product/<int:product_id>', methods=['POST', 'GET'])
def remove_product(product_id):
    conn = get_db_connection()  # Use the correct database
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('view_products'))



if __name__ == '__main__':
    app.run(debug=True)

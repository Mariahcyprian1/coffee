from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Use environment variable for security

# PostgreSQL connection
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="myuser",
        password="mypassword"
    )

@app.route('/')
def index():
    error = request.args.get('error')  # Retrieve the error message from query parameters (if any)
    print(f"Error received: {error}")  # Debugging line
    return render_template('index.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            error = "Please enter both username and password"
        else:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM login WHERE username = %s AND password = %s", (username, password))
                user = cursor.fetchone()
                conn.close()

                if user:
                    session['user'] = username
                    return redirect(url_for('dashboard'))
                else:
                    error = "Invalid credentials. Please try again."
            except Exception as e:
                error = f"Error during login: {str(e)}"
    return render_template('index.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', username=session['user'])
    else:
        return redirect(url_for('index'))

@app.route('/about')
def about():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('about.html')

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Fetch all menu items from the database
        cursor.execute("SELECT coffee_id, special_coffee, price, quantity FROM menu")
        menu_items = cursor.fetchall()

        # Handle adding a new coffee item
        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            quantity = request.form['quantity']

            # Insert the new coffee into the database
            cursor.execute(
                "INSERT INTO menu (special_coffee, price, quantity) VALUES (%s, %s, %s)",
                (name, price, quantity)
            )
            conn.commit()
            conn.close()
            flash("Coffee added successfully!", "success")
            return redirect(url_for('menu'))

        conn.close()
        return render_template('menu.html', menu_items=menu_items)
    except Exception as e:
        flash("Error loading menu: " + str(e), "error")
        return redirect(url_for('dashboard'))

@app.route('/delete_coffee/<int:coffee_id>', methods=['GET'])
def delete_coffee(coffee_id):
    if 'user' not in session:
        return redirect(url_for('index'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Delete the coffee item from the database
        cursor.execute("DELETE FROM menu WHERE coffee_id = %s", (coffee_id,))
        conn.commit()
        conn.close()
        flash("Coffee deleted successfully!", "success")
    except Exception as e:
        flash("Error deleting coffee: " + str(e), "error")
    
    return redirect(url_for('menu'))

@app.route('/edit_coffee/<int:coffee_id>', methods=['GET', 'POST'])
def edit_coffee(coffee_id):
    if 'user' not in session:
        return redirect(url_for('index'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            # Update the price and availability
            new_price = float(request.form['price'])
            new_quantity = int(request.form['quantity'])
            cursor.execute(
                "UPDATE menu SET price = %s, quantity = %s WHERE coffee_id = %s",
                (new_price, new_quantity, coffee_id)
            )
            conn.commit()
            conn.close()
            flash("Coffee details updated successfully!", "success")
            return redirect(url_for('menu'))

        # Fetch the current coffee details
        cursor.execute("SELECT coffee_id, special_coffee, price, quantity FROM menu WHERE coffee_id = %s", (coffee_id,))
        coffee = cursor.fetchone()
        conn.close()

        if coffee:
            return render_template('edit_coffee.html', coffee=coffee)
        else:
            flash("Coffee not found.", "error")
            return redirect(url_for('menu'))
    except Exception as e:
        flash("Error editing coffee: " + str(e), "error")
        return redirect(url_for('menu'))

# Define the generate_pdf function
def generate_pdf(booking_id, customer_name, phone, no_of_guests, coffee_id, quantity):
    pdf_file = f"receipt_{booking_id}.pdf"
    c = canvas.Canvas(pdf_file)
    c.drawString(100, 750, f"Booking Receipt")
    c.drawString(100, 730, f"Booking ID: {booking_id}")
    c.drawString(100, 710, f"Customer Name: {customer_name}")
    c.drawString(100, 690, f"Phone: {phone}")
    c.drawString(100, 670, f"No. of Guests: {no_of_guests}")
    c.drawString(100, 650, f"Coffee ID: {coffee_id}")
    c.drawString(100, 630, f"Quantity: {quantity}")
    c.save()
    flash(f"Receipt generated: {pdf_file}", "success")

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'user' not in session:
        return redirect(url_for('index'))  # Redirect to login if the user is not logged in

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch menu items for the dropdown
        cursor.execute("SELECT coffee_id, special_coffee, price, quantity FROM menu")
        menu_items = cursor.fetchall()

        if request.method == 'POST':
            # Retrieve form data
            customer_name = request.form['customer_name']
            phone = request.form['phone']
            no_of_guests = int(request.form['no_of_guests'])
            coffee_id = int(request.form['coffee_id'])
            quantity = int(request.form['quantity'])

            # Check if enough quantity is available
            cursor.execute("SELECT quantity FROM menu WHERE coffee_id = %s", (coffee_id,))
            result = cursor.fetchone()
            if not result:
                flash("Invalid coffee selection!", "error")
                conn.close()
                return render_template('booking.html', menu_items=menu_items)

            available_quantity = result[0]
            if quantity > available_quantity:
                flash("Not enough quantity available!", "error")
                conn.close()
                return render_template('booking.html', menu_items=menu_items)

            # Insert booking into the booking table
            cursor.execute(
                "INSERT INTO booking (customer_name, no_of_guests, phone, coffee_id, quantity) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (customer_name, no_of_guests, phone, coffee_id, quantity)
            )
            booking_id = cursor.fetchone()[0]

            # Reduce the quantity in the menu table
            cursor.execute(
                "UPDATE menu SET quantity = quantity - %s WHERE coffee_id = %s",
                (quantity, coffee_id)
            )
            conn.commit()

            # Generate a PDF receipt
            generate_pdf(booking_id, customer_name, phone, no_of_guests, coffee_id, quantity)

            flash("Booking successful!", "success")
            conn.close()
            return redirect(url_for('receipt', booking_id=booking_id))

        conn.close()
        return render_template('booking.html', menu_items=menu_items)
    except Exception as e:
        flash("Error processing booking: " + str(e), "error")
        return redirect(url_for('dashboard'))

@app.route('/receipt/<int:booking_id>')
def receipt(booking_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT customer_name, phone, no_of_guests, coffee_id, quantity FROM booking WHERE id = %s", (booking_id,))
        booking = cursor.fetchone()
        conn.close()

        if booking:
            customer_name = booking[0]
            phone = booking[1]
            no_of_guests = booking[2]
            coffee_id = booking[3]
            quantity = booking[4]
            return render_template('receipt.html', booking_id=booking_id, customer_name=customer_name, phone=phone, no_of_guests=no_of_guests, coffee_id=coffee_id, quantity=quantity)
        else:
            flash("Booking not found.", "error")
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash("Error fetching booking details: " + str(e), "error")
        return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
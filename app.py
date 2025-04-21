import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from reportlab.pdfgen import canvas

# Initialize Flask and SQLAlchemy
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Use environment variable for security

# Use environment variable for DB URL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgres://myuser:mypassword@localhost:5432/postgres')

# Disable track modifications warning (optional)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the models
class Login(db.Model):
    __tablename__ = 'login'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Menu(db.Model):
    __tablename__ = 'menu'
    coffee_id = db.Column(db.Integer, primary_key=True)
    special_coffee = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    no_of_guests = db.Column(db.Integer, nullable=False)
    coffee_id = db.Column(db.Integer, db.ForeignKey('menu.coffee_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Define your routes
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
                # Use SQLAlchemy to query the database
                user = Login.query.filter_by(username=username, password=password).first()
                
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
        # Fetch all menu items from the database using SQLAlchemy
        menu_items = Menu.query.all()

        # Handle adding a new coffee item
        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            quantity = request.form['quantity']

            # Insert the new coffee into the database
            new_coffee = Menu(special_coffee=name, price=price, quantity=quantity)
            db.session.add(new_coffee)
            db.session.commit()

            flash("Coffee added successfully!", "success")
            return redirect(url_for('menu'))

        return render_template('menu.html', menu_items=menu_items)
    except Exception as e:
        flash("Error loading menu: " + str(e), "error")
        return redirect(url_for('dashboard'))

@app.route('/delete_coffee/<int:coffee_id>', methods=['GET'])
def delete_coffee(coffee_id):
    if 'user' not in session:
        return redirect(url_for('index'))
    
    try:
        # Delete the coffee item from the database using SQLAlchemy
        coffee_to_delete = Menu.query.get(coffee_id)
        if coffee_to_delete:
            db.session.delete(coffee_to_delete)
            db.session.commit()
            flash("Coffee deleted successfully!", "success")
        else:
            flash("Coffee not found.", "error")
    except Exception as e:
        flash("Error deleting coffee: " + str(e), "error")
    
    return redirect(url_for('menu'))

@app.route('/edit_coffee/<int:coffee_id>', methods=['GET', 'POST'])
def edit_coffee(coffee_id):
    if 'user' not in session:
        return redirect(url_for('index'))

    try:
        coffee = Menu.query.get(coffee_id)

        if request.method == 'POST':
            # Update the price and availability
            coffee.price = float(request.form['price'])
            coffee.quantity = int(request.form['quantity'])
            db.session.commit()

            flash("Coffee details updated successfully!", "success")
            return redirect(url_for('menu'))

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
        return redirect(url_for('index'))

    try:
        menu_items = Menu.query.all()

        if request.method == 'POST':
            customer_name = request.form['customer_name']
            phone = request.form['phone']
            no_of_guests = int(request.form['no_of_guests'])
            coffee_id = int(request.form['coffee_id'])
            quantity = int(request.form['quantity'])

            coffee = Menu.query.get(coffee_id)
            if not coffee:
                flash("Invalid coffee selection!", "error")
                return render_template('booking.html', menu_items=menu_items)

            if quantity > coffee.quantity:
                flash("Not enough quantity available!", "error")
                return render_template('booking.html', menu_items=menu_items)

            # Insert booking
            new_booking = Booking(customer_name=customer_name, no_of_guests=no_of_guests, phone=phone, coffee_id=coffee_id, quantity=quantity)
            db.session.add(new_booking)
            db.session.commit()

            # Reduce the quantity in the menu
            coffee.quantity -= quantity
            db.session.commit()

            # Generate PDF
            generate_pdf(new_booking.id, customer_name, phone, no_of_guests, coffee_id, quantity)

            flash("Booking successful!", "success")
            return redirect(url_for('receipt', booking_id=new_booking.id))

        return render_template('booking.html', menu_items=menu_items)
    except Exception as e:
        flash("Error processing booking: " + str(e), "error")
        return redirect(url_for('dashboard'))

@app.route('/receipt/<int:booking_id>')
def receipt(booking_id):
    try:
        booking = Booking.query.get(booking_id)
        if booking:
            return render_template('receipt.html', booking=booking)
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

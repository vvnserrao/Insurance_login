from flask import render_template, flash, redirect, url_for, request
from werkzeug.utils import secure_filename
import os
import pandas as pd
from app import app, db  # Import app and db object from app package
from app.forms import LoginForm, RegistrationForm, AddDetailsForm
from app.models import User  # Import User model from app.models
from werkzeug.security import generate_password_hash, check_password_hash
from zipfile import BadZipFile

# Configure upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Specify the path to the Excel file (relative to your app's root directory)
EXCEL_FILE = os.path.join(os.getcwd(), 'user_details.xlsx')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not check_password_hash(user.password_hash, form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        flash(f'Login successful for user {form.username.data}', 'success')
        return redirect(url_for('dashboard'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', title='Dashboard')


@app.route('/capture_face', methods=['POST'])
def capture_face():
    if request.method == 'POST':
        image_data = request.form['image_data']
        # Example: Process image data (store in database, etc.)
        # You might want to save the image_data or process it further
        flash('Image captured successfully!', 'success')
        return redirect(url_for('dashboard'))  # Redirect to dashboard or another page
    else:
        flash('Error capturing image', 'error')
        return redirect(url_for('dashboard'))  # Redirect to dashboard or another page


@app.route('/add_details', methods=['GET', 'POST'])
def add_details():
    form = AddDetailsForm()
    if form.validate_on_submit():
        name = form.name.data
        age = form.age.data
        photo = form.photo.data

        # Save the photo
        filename = secure_filename(photo.filename)
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path)

        # Save details to Excel file
        try:
            if os.path.exists(EXCEL_FILE):
                df = pd.read_excel(EXCEL_FILE, engine='openpyxl')  # Specify engine as 'openpyxl'
            else:
                df = pd.DataFrame(columns=['Name', 'Age', 'Photo'])

            new_entry = {'Name': name, 'Age': age, 'Photo': photo_path}

            # Append new entry to DataFrame and save to Excel file
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')  # Specify engine for saving too

            flash('Details added successfully!', 'success')
        except (BadZipFile, ValueError) as e:
            flash('Error with the Excel file. It might be corrupted.', 'error')

        return redirect(url_for('dashboard'))

    return render_template('add_details.html', title='Add Details', form=form)

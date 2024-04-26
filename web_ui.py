from flask import Flask, render_template, request, redirect, url_for, flash
from subprocess import run
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database initialization
conn = sqlite3.connect('students.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        school TEXT,
        department TEXT,
        matric_number TEXT,
        gender TEXT,
        fingerprint_data TEXT
    )
''')
conn.commit()
conn.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        school = request.form.get('school')
        department = request.form.get('department')
        matric_number = request.form.get('matric_number')
        gender = request.form.get('gender')
        fingerprint_data = request.form.get('fingerprint_data')  # Retrieve fingerprint data
        
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()

        # Check if the matric number already exists
        cursor.execute("SELECT id FROM students WHERE matric_number = ?", (matric_number,))
        existing_student = cursor.fetchone()

        if existing_student:
            conn.close()
            flash('A user with the same matric number already exists.', 'error')
            return redirect(url_for('register'))

        # If the matric number doesn't exist, proceed with the registration
        cursor.execute('''
            INSERT INTO students (name, school, department, matric_number, gender, fingerprint_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, school, department, matric_number, gender, fingerprint_data))
        conn.commit()
        conn.close()

        flash('Registration successful! You can now capture an image.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/capture_image')
def capture_image():
    run(["python", "get_faces_from_camera_tkinter.py"])
    flash('Image Captured!')
    return redirect(url_for('index'))


@app.route('/process_image')
def process_image():
    run(["python", "features_extraction_to_csv.py"])
    flash('Image Processed!')
    return redirect(url_for('index'))


@app.route('/login')
def login():
    run(["python", "attendance_taker.py"])
    flash('Attendance Taken``')
    return redirect(url_for('index'))


@app.route('/view_attendance', methods=['GET', 'POST'])
def view_attendance():
    if request.method == 'POST':
        selected_date = request.form.get('selected_date')
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
        formatted_date = selected_date_obj.strftime('%Y-%m-%d')

        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()

        cursor.execute("SELECT name, time FROM attendance WHERE date = ?", (formatted_date,))
        attendance_data = cursor.fetchall()

        conn.close()

        if not attendance_data:
            return render_template('index.html', selected_date=selected_date, no_data=True)

        return render_template('main.html', selected_date=selected_date, attendance_data=attendance_data)

    return render_template('main.html', selected_date='', no_data=False)

@app.route('/fingerprint', methods=['GET'])
def fingerprint():
    import subprocess
    command = "C:/Users/user/Documents/Face-Recognition-Based-Attendance-System/fingerprint/New_Verifiier/New_Verifiier\setup.exe"
    subprocess.Popen(command)
    flash('Fingerprint software launched.')
    return redirect(url_for('index'))



@app.route('/verify_fingerprint', methods=['POST'])
def verify_fingerprint():
    fingerprint_data = request.form.get('fingerprint_data')

    # Retrieve the saved fingerprint data for the logged-in user from the database
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, fingerprint_data FROM students WHERE fingerprint_data = ?", (fingerprint_data,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        # If fingerprint matches, return user's name
        return jsonify({'success': True, 'name': user_data[0]})
    else:
        # If fingerprint doesn't match, return error
        return jsonify({'success': False, 'error': 'Fingerprint verification failed'})


@app.route('/query_students_by_name', methods=['POST'])
def query_students_by_name():
    student_name = request.form.get('student_name')

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE name LIKE ?", ('%' + student_name + '%',))
    student_query_data = cursor.fetchall()

    conn.close()

    return render_template('main.html', student_query_data=student_query_data, **request.form)


if __name__ == "__main__":
    app.run(debug=True)

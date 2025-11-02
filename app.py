from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
from config import Config
import datetime
import pandas as pd
from io import BytesIO
from flask import send_file

# Create Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Database connection function
def get_db_connection():
    """
    Establishes connection to MySQL database using XAMPP default settings
    """
    try:
        conn = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            port=app.config['MYSQL_PORT']
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None

# Initialize database tables
def init_db():
    """
    Creates the voters table if it doesn't exist
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Table creation SQL (same as in schema.sql)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS voters (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(100) NOT NULL,
                    surname VARCHAR(100) NOT NULL,
                    sin VARCHAR(20) NOT NULL UNIQUE,
                    program ENUM('Computer Science', 'Computer Engineering') NOT NULL,
                    phone_number VARCHAR(15) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    province ENUM(
                        'Central Province', 'Copperbelt Province', 'Eastern Province', 
                        'Western Province', 'Lusaka Province', 'Muchinga Province', 
                        'Northern Province', 'North Western Province', 
                        'Luapula Province', 'Southern Province'
                    ) NOT NULL,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed BOOLEAN DEFAULT FALSE
                )
            ''')
            conn.commit()
            cursor.close()
            print("Database initialized successfully")
        except mysql.connector.Error as e:
            print(f"Database initialization error: {e}")
        finally:
            conn.close()

@app.route('/admin/export')
def export_data():
    """Export all voter data to Excel (without names)"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Get all data EXCEPT first_name and surname
            cursor.execute('''
                SELECT sin, program, phone_number, email, province, registration_date 
                FROM voters 
                ORDER BY registration_date DESC
            ''')
            voters = cursor.fetchall()
            cursor.close()
            
            # Create DataFrame
            df = pd.DataFrame(voters)
            
            # Create Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Census Data', index=False)
            
            output.seek(0)
            
            # Send file
            filename = f"census_data_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
            
        except mysql.connector.Error as e:
            flash(f'Database error: {e}', 'error')
            return redirect(url_for('admin_dashboard'))
        finally:
            conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/export/recent')
def export_recent():
    """Export recent voter data to Excel (without names)"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Get recent data EXCEPT first_name and surname
            cursor.execute('''
                SELECT sin, program, phone_number, email, province, registration_date 
                FROM voters 
                WHERE registration_date >= NOW() - INTERVAL 1 DAY
                ORDER BY registration_date DESC
            ''')
            voters = cursor.fetchall()
            cursor.close()
            
            # Create DataFrame
            df = pd.DataFrame(voters)
            
            # Create Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Recent Census Data', index=False)
            
            output.seek(0)
            
            # Send file
            filename = f"recent_census_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
            
        except mysql.connector.Error as e:
            flash(f'Database error: {e}', 'error')
            return redirect(url_for('admin_dashboard'))
        finally:
            conn.close()
    
    return redirect(url_for('admin_dashboard'))

# Routes for the census form
@app.route('/')
def index():
    """Redirect to personal details page"""
    return redirect(url_for('personal_details'))

@app.route('/personal', methods=['GET', 'POST'])
def personal_details():
    """Handle personal information page"""
    if request.method == 'POST':
        # Store personal details in session
        session['first_name'] = request.form['first_name']
        session['surname'] = request.form['surname']
        session['sin'] = request.form['sin']
        return redirect(url_for('academic_details'))
    
    return render_template('personal.html')

@app.route('/academic', methods=['GET', 'POST'])
def academic_details():
    """Handle academic information page"""
    if request.method == 'POST':
        # Store academic details in session
        session['program'] = request.form['program']
        return redirect(url_for('contact_details'))
    
    # Check if user came from personal details
    if 'first_name' not in session:
        return redirect(url_for('personal_details'))
    
    return render_template('academic.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact_details():
    """Handle contact information page and final submission"""
    if request.method == 'POST':
        # Get all data from session and form
        personal_data = {
            'first_name': session.get('first_name'),
            'surname': session.get('surname'),
            'sin': session.get('sin'),
            'program': session.get('program'),
            'phone_number': request.form['phone_number'],
            'email': request.form['email'],
            'province': request.form['province']
        }
        
        # Save to database
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO voters 
                    (first_name, surname, sin, program, phone_number, email, province, completed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    personal_data['first_name'],
                    personal_data['surname'],
                    personal_data['sin'],
                    personal_data['program'],
                    personal_data['phone_number'],
                    personal_data['email'],
                    personal_data['province'],
                    True
                ))
                conn.commit()
                cursor.close()
                
                # Clear session after successful submission
                session.clear()
                return redirect(url_for('complete'))
                
            except mysql.connector.IntegrityError:
                flash('Error: SIN or Email already exists in our system!', 'error')
            except mysql.connector.Error as e:
                flash(f'Database error: {e}', 'error')
            finally:
                conn.close()
    
    # Check if user came from academic details
    if 'program' not in session:
        return redirect(url_for('academic_details'))
    
    return render_template('contact.html')

@app.route('/complete')
def complete():
    """Show completion message"""
    return render_template('complete.html')

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard with real-time statistics"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    stats = {}
    recent_voters = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Total registrations
            cursor.execute("SELECT COUNT(*) as total FROM voters")
            stats['total'] = cursor.fetchone()['total']
            
            # Registrations by program
            cursor.execute("SELECT program, COUNT(*) as count FROM voters GROUP BY program")
            stats['by_program'] = cursor.fetchall()
            
            # Registrations by province
            cursor.execute("SELECT province, COUNT(*) as count FROM voters GROUP BY province")
            stats['by_province'] = cursor.fetchall()
            
            # Recent registrations (last 24 hours)
            cursor.execute("SELECT COUNT(*) as recent FROM voters WHERE registration_date >= NOW() - INTERVAL 1 DAY")
            stats['recent'] = cursor.fetchone()['recent']
            
            # Get recent voter details (without names)
            cursor.execute('''
                SELECT sin, program, phone_number, email, province, registration_date 
                FROM voters 
                WHERE registration_date >= NOW() - INTERVAL 1 DAY 
                ORDER BY registration_date DESC 
                LIMIT 50
            ''')
            recent_voters = cursor.fetchall()
            
            # Daily registration trend (last 7 days)
            cursor.execute('''
                SELECT DATE(registration_date) as date, COUNT(*) as count 
                FROM voters 
                WHERE registration_date >= NOW() - INTERVAL 7 DAY
                GROUP BY DATE(registration_date) 
                ORDER BY date
            ''')
            stats['daily_trend'] = cursor.fetchall()
            
            cursor.close()
            
        except mysql.connector.Error as e:
            flash(f'Database error: {e}', 'error')
        finally:
            conn.close()
    
    # Calculate max daily count for trend visualization
    max_daily_count = 0
    if stats.get('daily_trend'):
        max_daily_count = max(day['count'] for day in stats['daily_trend'])
    
    # Estimate class size (you can adjust this number)
    class_size = 200  # Change this to your actual class size estimate
    
    return render_template('admin.html', 
                         stats=stats, 
                         recent_voters=recent_voters,
                         current_time=datetime.datetime.now(),
                         max_daily_count=max_daily_count,
                         class_size=class_size)

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

# API endpoint for real-time data
@app.route('/api/stats')
def api_stats():
    """JSON API endpoint for real-time statistics"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    stats = {}
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as total FROM voters")
            stats['total'] = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as recent FROM voters WHERE registration_date >= NOW() - INTERVAL 1 DAY")
            stats['recent_24h'] = cursor.fetchone()['recent']
            
            cursor.close()
        except mysql.connector.Error:
            pass
        finally:
            conn.close()
    
    return jsonify(stats)

# Initialize database when app starts
if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
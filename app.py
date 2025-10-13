from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from data_handler import DataHandler
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this in production!

# Initialize data handler
data_handler = DataHandler()

# Available time slots for booking
TIME_SLOTS = [
    "09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
    "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"
]

@app.route('/')
def home():
    """Home page"""
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        
        # Validate input
        if not all([name, email, password, phone]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))
        
        # Check if user already exists
        if data_handler.get_user_by_email(email):
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        user_data = {
            'id': str(uuid.uuid4()),
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'phone': phone,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        data_handler.add_user(user_data)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = data_handler.get_user_by_email(email)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('doctors_list'))
        else:
            flash('Invalid email or password!', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/doctors')
def doctors_list():
    """List all doctors with search functionality"""
    if 'user_id' not in session:
        flash('Please login to view doctors.', 'warning')
        return redirect(url_for('login'))
    
    search_query = request.args.get('search', '')
    doctors = data_handler.search_doctors(search_query)
    
    return render_template('doctors_list.html', doctors=doctors, search_query=search_query)

@app.route('/doctor/<doctor_id>')
def doctor_detail(doctor_id):
    """View doctor profile details"""
    if 'user_id' not in session:
        flash('Please login to view doctor details.', 'warning')
        return redirect(url_for('login'))
    
    doctor = data_handler.get_doctor_by_id(doctor_id)
    
    if not doctor:
        flash('Doctor not found!', 'danger')
        return redirect(url_for('doctors_list'))
    
    return render_template('doctor_detail.html', doctor=doctor)

@app.route('/book/<doctor_id>', methods=['GET', 'POST'])
def book_appointment(doctor_id):
    """Book an appointment with a doctor"""
    if 'user_id' not in session:
        flash('Please login to book an appointment.', 'warning')
        return redirect(url_for('login'))
    
    doctor = data_handler.get_doctor_by_id(doctor_id)
    
    if not doctor:
        flash('Doctor not found!', 'danger')
        return redirect(url_for('doctors_list'))
    
    if request.method == 'POST':
        date = request.form.get('date')
        time = request.form.get('time')
        reason = request.form.get('reason')
        
        # Validate input
        if not all([date, time, reason]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('book_appointment', doctor_id=doctor_id))
        
        # Check if slot is already booked
        if data_handler.is_slot_booked(doctor_id, date, time):
            flash('This time slot is already booked. Please select another slot.', 'danger')
            return redirect(url_for('book_appointment', doctor_id=doctor_id))
        
        # Create appointment
        appointment_data = {
            'id': str(uuid.uuid4()),
            'user_id': session['user_id'],
            'user_email': session['user_email'],
            'user_name': session['user_name'],
            'doctor_id': doctor_id,
            'doctor_name': doctor['name'],
            'date': date,
            'time': time,
            'reason': reason,
            'status': 'confirmed',
            'booked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        data_handler.add_appointment(appointment_data)
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('appointment_confirmation', appointment_id=appointment_data['id']))
    
    # Generate available dates (next 30 days)
    today = datetime.now().date()
    available_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 31)]
    
    # Get booked slots for this doctor
    doctor_appointments = data_handler.get_appointments_by_doctor(doctor_id)
    booked_slots = {}
    for appt in doctor_appointments:
        key = f"{appt['date']}_{appt['time']}"
        booked_slots[key] = True
    
    return render_template('book_appointment.html', 
                         doctor=doctor, 
                         available_dates=available_dates,
                         time_slots=TIME_SLOTS,
                         booked_slots=booked_slots)

@app.route('/appointment/confirmation/<appointment_id>')
def appointment_confirmation(appointment_id):
    """Show appointment confirmation"""
    if 'user_id' not in session:
        flash('Please login to view appointment details.', 'warning')
        return redirect(url_for('login'))
    
    appointment = data_handler.get_appointment_by_id(appointment_id)
    
    if not appointment or appointment['user_id'] != session['user_id']:
        flash('Appointment not found!', 'danger')
        return redirect(url_for('my_appointments'))
    
    return render_template('appointment_confirmation.html', appointment=appointment)

@app.route('/my-appointments')
def my_appointments():
    """View user's appointments"""
    if 'user_id' not in session:
        flash('Please login to view your appointments.', 'warning')
        return redirect(url_for('login'))
    
    appointments = data_handler.get_appointments_by_user(session['user_email'])
    
    # Sort by date and time (most recent first)
    appointments.sort(key=lambda x: (x['date'], x['time']), reverse=True)
    
    return render_template('my_appointments.html', appointments=appointments)

# Symptom to specialization mapping
SYMPTOM_SPECIALIZATION_MAP = {
    'fever': ['General Physician', 'Pediatrician'],
    'chest pain': ['Cardiologist', 'General Physician'],
    'heart problems': ['Cardiologist'],
    'breathing difficulty': ['Cardiologist', 'General Physician'],
    'skin rash': ['Dermatologist'],
    'acne': ['Dermatologist'],
    'skin problems': ['Dermatologist'],
    'hair loss': ['Dermatologist'],
    'anxiety': ['Psychiatrist'],
    'depression': ['Psychiatrist'],
    'stress': ['Psychiatrist'],
    'mental health': ['Psychiatrist'],
    'back pain': ['Orthopedic Surgeon', 'General Physician'],
    'joint pain': ['Orthopedic Surgeon'],
    'bone fracture': ['Orthopedic Surgeon'],
    'knee pain': ['Orthopedic Surgeon'],
    'headache': ['Neurologist', 'General Physician'],
    'migraine': ['Neurologist'],
    'seizures': ['Neurologist'],
    'numbness': ['Neurologist'],
    'child fever': ['Pediatrician'],
    'child cough': ['Pediatrician'],
    'vaccination': ['Pediatrician'],
    'pregnancy': ['Gynecologist'],
    'menstrual problems': ['Gynecologist'],
    'womens health': ['Gynecologist'],
    'cold': ['General Physician'],
    'cough': ['General Physician'],
    'diabetes': ['General Physician'],
    'blood pressure': ['General Physician', 'Cardiologist'],
}

@app.route('/find-doctor', methods=['GET', 'POST'])
def find_doctor():
    """Find doctor based on symptoms"""
    if 'user_id' not in session:
        flash('Please login to use symptom checker.', 'warning')
        return redirect(url_for('login'))
    
    recommended_doctors = []
    symptom_input = ''
    recommended_specializations = []
    possible_causes = []
    
    if request.method == 'POST':
        symptom_input = request.form.get('symptom', '').lower().strip()
        
        if symptom_input:
            # Find matching specializations
            matched_specs = set()
            for symptom_key, specs in SYMPTOM_SPECIALIZATION_MAP.items():
                if symptom_key in symptom_input or symptom_input in symptom_key:
                    matched_specs.update(specs)
            
            if matched_specs:
                recommended_specializations = list(matched_specs)
                
                # Get all doctors
                all_doctors = data_handler.get_doctors()
                
                # Filter doctors by specialization
                for doctor in all_doctors:
                    if doctor['specialization'] in matched_specs:
                        recommended_doctors.append(doctor)
                
                # Generate possible causes based on symptom
                possible_causes = generate_possible_causes(symptom_input)
                
                if not recommended_doctors:
                    flash('No doctors found for this symptom. Showing all doctors.', 'info')
                    recommended_doctors = all_doctors
            else:
                flash('No specific specialization found. Showing general physicians.', 'info')
                all_doctors = data_handler.get_doctors()
                for doctor in all_doctors:
                    if 'general' in doctor['specialization'].lower():
                        recommended_doctors.append(doctor)
                
                if not recommended_doctors:
                    recommended_doctors = all_doctors
    
    # Get predefined symptoms for the UI
    predefined_symptoms = list(SYMPTOM_SPECIALIZATION_MAP.keys())
    
    return render_template('find_doctor.html',
                         recommended_doctors=recommended_doctors,
                         symptom_input=symptom_input,
                         recommended_specializations=recommended_specializations,
                         possible_causes=possible_causes,
                         predefined_symptoms=predefined_symptoms)

def generate_possible_causes(symptom):
    """Generate possible causes for symptoms"""
    causes_map = {
        'fever': ['Viral infection', 'Bacterial infection', 'Flu', 'COVID-19'],
        'chest pain': ['Heart disease', 'Anxiety', 'Muscle strain', 'Acid reflux'],
        'skin rash': ['Allergic reaction', 'Eczema', 'Contact dermatitis', 'Fungal infection'],
        'anxiety': ['Stress', 'Depression', 'Panic disorder', 'PTSD'],
        'back pain': ['Muscle strain', 'Poor posture', 'Herniated disk', 'Arthritis'],
        'headache': ['Tension', 'Migraine', 'Dehydration', 'Eye strain'],
        'cough': ['Cold', 'Flu', 'Allergies', 'Asthma'],
        'joint pain': ['Arthritis', 'Injury', 'Overuse', 'Infection'],
    }
    
    # Find matching causes
    for key, causes in causes_map.items():
        if key in symptom or symptom in key:
            return causes
    
    return ['Please consult a doctor for accurate diagnosis']

if __name__ == '__main__':
    app.run(debug=True, port=5000)


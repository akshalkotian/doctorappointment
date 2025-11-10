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

# Helper functions for time-based logic
def parse_time_slot(time_str):
    """Convert time slot string (e.g., '09:00 AM') to datetime.time object"""
    return datetime.strptime(time_str, '%I:%M %p').time()

def is_slot_in_past(date_str, time_str):
    """Check if a slot is in the past"""
    try:
        slot_datetime = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %I:%M %p')
        return slot_datetime < datetime.now()
    except:
        return False

def is_slot_within_hour(date_str, time_str):
    """Check if a slot is within the next hour"""
    try:
        slot_datetime = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %I:%M %p')
        time_diff = slot_datetime - datetime.now()
        return timedelta(0) < time_diff <= timedelta(hours=1)
    except:
        return False

def get_appointment_status(appointment):
    """
    Classify appointment status based on current time:
    - 'upcoming': future appointment
    - 'completed': past appointment with confirmed status
    - 'missed': past appointment that was not cancelled
    """
    date_str = appointment['date']
    time_str = appointment['time']
    status = appointment['status']
    
    if is_slot_in_past(date_str, time_str):
        if status == 'cancelled':
            return 'cancelled'
        elif status == 'no_show':
            return 'missed'
        elif status in ['confirmed', 'pending_payment']:
            # If past and not marked as no_show, consider it completed
            return 'completed'
        else:
            return 'missed'
    else:
        return 'upcoming'

def get_future_slots_for_date(date_str, all_slots):
    """
    Get available future slots for a specific date.
    If date is today, filter out past slots.
    If date is future, return all slots.
    """
    today = datetime.now().date()
    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    if selected_date < today:
        # Past date - no slots available
        return []
    elif selected_date == today:
        # Today - filter out past slots
        current_time = datetime.now().time()
        future_slots = []
        for slot in all_slots:
            slot_time = parse_time_slot(slot)
            if slot_time > current_time:
                future_slots.append(slot)
        return future_slots
    else:
        # Future date - all slots available
        return all_slots

@app.route('/')
def home():
    """Home page with city selection"""
    cities = data_handler.get_cities()
    return render_template('home.html', cities=cities)

@app.route('/api/hospitals/<city_id>')
def get_hospitals_api(city_id):
    """API endpoint to get hospitals by city"""
    from flask import jsonify
    hospitals = data_handler.get_hospitals_by_city(city_id)
    return jsonify(hospitals)

@app.route('/api/doctors/<hospital_id>')
def get_doctors_api(hospital_id):
    """API endpoint to get doctors by hospital"""
    from flask import jsonify
    doctors = data_handler.get_doctors_by_hospital(hospital_id)
    return jsonify(doctors)

@app.route('/select-location', methods=['POST'])
def select_location():
    """Handle city, hospital, doctor selection from homepage"""
    city_id = request.form.get('city_id')
    hospital_id = request.form.get('hospital_id')
    doctor_id = request.form.get('doctor_id')
    
    if doctor_id:
        # Direct to booking page
        return redirect(url_for('book_appointment', doctor_id=doctor_id))
    elif hospital_id:
        # Show doctors for this hospital
        return redirect(url_for('doctors_by_hospital', hospital_id=hospital_id))
    else:
        flash('Please complete the selection.', 'warning')
        return redirect(url_for('home'))

@app.route('/hospital/<hospital_id>/doctors')
def doctors_by_hospital(hospital_id):
    """Show all doctors in a specific hospital"""
    if 'user_id' not in session:
        flash('Please login to view doctors.', 'warning')
        return redirect(url_for('login'))
    
    hospital = data_handler.get_hospital_by_id(hospital_id)
    if not hospital:
        flash('Hospital not found!', 'danger')
        return redirect(url_for('home'))
    
    city = data_handler.get_city_by_id(hospital['city_id'])
    doctors = data_handler.get_doctors_by_hospital(hospital_id)
    
    return render_template('doctors_by_hospital.html', 
                         doctors=doctors, 
                         hospital=hospital,
                         city=city)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Patient registration"""
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
        
        # Create new patient user
        user_data = {
            'id': str(uuid.uuid4()),
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'phone': phone,
            'role': 'patient',  # Default role is patient
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        data_handler.add_user(user_data)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Patient login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = data_handler.get_user_by_email(email)
        
        if user and check_password_hash(user['password'], password):
            # Ensure patient users only
            user_role = user.get('role', 'patient')  # Default to patient for existing users
            if user_role == 'admin':
                flash('Please use admin login page.', 'warning')
                return redirect(url_for('admin_login'))
            
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user_role
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

# Admin Routes
@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    """Admin registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        admin_code = request.form.get('admin_code')
        
        # Validate admin code (simple security measure)
        if admin_code != 'ADMIN2024':  # Change this in production
            flash('Invalid admin code!', 'danger')
            return redirect(url_for('admin_register'))
        
        # Validate input
        if not all([name, email, password, phone]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('admin_register'))
        
        # Check if user already exists
        if data_handler.get_user_by_email(email):
            flash('Email already registered!', 'danger')
            return redirect(url_for('admin_register'))
        
        # Create new admin user
        user_data = {
            'id': str(uuid.uuid4()),
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'phone': phone,
            'role': 'admin',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        data_handler.add_user(user_data)
        flash('Admin registration successful! Please login.', 'success')
        return redirect(url_for('admin_login'))
    
    return render_template('admin_register.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = data_handler.get_user_by_email(email)
        
        if user and check_password_hash(user['password'], password):
            # Ensure admin users only
            if user.get('role') != 'admin':
                flash('Access denied. Admin credentials required.', 'danger')
                return redirect(url_for('admin_login'))
            
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = 'admin'
            flash(f'Welcome, Admin {user["name"]}!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password!', 'danger')
            return redirect(url_for('admin_login'))
    
    return render_template('admin_login.html')

def admin_required(f):
    """Decorator to require admin authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with filters and statistics"""
    # Get filter parameters
    doctor_filter = request.args.get('doctor', '')
    date_filter = request.args.get('date', '')
    payment_status_filter = request.args.get('payment_status', '')
    
    # Get all appointments
    appointments = data_handler.get_appointments()
    
    # Apply filters and add time-based status
    filtered_appointments = []
    for appt in appointments:
        if doctor_filter and appt['doctor_id'] != doctor_filter:
            continue
        if date_filter and appt['date'] != date_filter:
            continue
        if payment_status_filter and appt.get('payment_status') != payment_status_filter:
            continue
        # Add time-based status to appointment
        appt['time_status'] = get_appointment_status(appt)
        filtered_appointments.append(appt)
    
    # Sort by date and time (most recent first)
    filtered_appointments.sort(key=lambda x: (x['date'], x['time']), reverse=True)
    
    # Calculate statistics
    total_bookings = len(appointments)
    confirmed_bookings = len([a for a in appointments if a['status'] == 'confirmed'])
    cancelled_bookings = len([a for a in appointments if a['status'] == 'cancelled'])
    pending_payments = len([a for a in appointments if a.get('payment_status') == 'Pending'])
    successful_payments = len([a for a in appointments if a.get('payment_status') == 'Success'])
    
    # Booking count per doctor
    doctor_counts = {}
    for appt in appointments:
        doctor_name = appt['doctor_name']
        doctor_counts[doctor_name] = doctor_counts.get(doctor_name, 0) + 1
    
    # Get all doctors for filter dropdown
    doctors = data_handler.get_doctors()
    
    stats = {
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'pending_payments': pending_payments,
        'successful_payments': successful_payments,
        'doctor_counts': doctor_counts
    }
    
    return render_template('admin_dashboard.html', 
                         appointments=filtered_appointments,
                         stats=stats,
                         doctors=doctors,
                         doctor_filter=doctor_filter,
                         date_filter=date_filter,
                         payment_status_filter=payment_status_filter)

@app.route('/admin/timetable')
@admin_required
def admin_timetable():
    """Admin timetable view showing all slots"""
    # Get filter parameters
    doctor_id = request.args.get('doctor', '')
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Get all doctors
    doctors = data_handler.get_doctors()
    
    # If no doctor selected, use first doctor
    if not doctor_id and doctors:
        doctor_id = doctors[0]['id']
    
    # Get selected doctor
    selected_doctor = data_handler.get_doctor_by_id(doctor_id) if doctor_id else None
    
    # Get appointments for selected doctor and date
    all_appointments = data_handler.get_appointments_by_doctor(doctor_id) if doctor_id else []
    
    # Create slot status map
    slot_status = {}
    for time_slot in TIME_SLOTS:
        slot_key = f"{date}_{time_slot}"
        
        # Check if slot is in the past
        if is_slot_in_past(date, time_slot):
            slot_status[time_slot] = {
                'status': 'Past',
                'appointment': None
            }
        else:
            slot_status[time_slot] = {
                'status': 'Available',
                'appointment': None
            }
        
        # Check if slot is booked
        for appt in all_appointments:
            if appt['date'] == date and appt['time'] == time_slot:
                if appt['status'] in ['confirmed', 'pending_payment']:
                    appt['time_status'] = get_appointment_status(appt)
                    slot_status[time_slot] = {
                        'status': 'Booked',
                        'appointment': appt
                    }
                    break
    
    # Count bookings for selected doctor and date
    booking_count = sum(1 for slot in slot_status.values() if slot['status'] == 'Booked')
    
    # Generate available dates (30 days range: -15 to +15)
    today = datetime.now().date()
    available_dates = []
    for i in range(-15, 16):
        date_obj = today + timedelta(days=i)
        available_dates.append(date_obj.strftime('%Y-%m-%d'))
    
    return render_template('admin_timetable.html',
                         doctors=doctors,
                         selected_doctor=selected_doctor,
                         doctor_id=doctor_id,
                         date=date,
                         time_slots=TIME_SLOTS,
                         slot_status=slot_status,
                         booking_count=booking_count,
                         available_dates=available_dates)

@app.route('/admin/action/cancel/<appointment_id>', methods=['POST'])
@admin_required
def admin_cancel_appointment(appointment_id):
    """Admin action: Cancel appointment"""
    success = data_handler.cancel_appointment(appointment_id)
    if success:
        flash('Appointment cancelled successfully.', 'success')
    else:
        flash('Failed to cancel appointment.', 'danger')
    return redirect(request.referrer or url_for('admin_dashboard'))

@app.route('/admin/action/no-show/<appointment_id>', methods=['POST'])
@admin_required
def admin_mark_no_show(appointment_id):
    """Admin action: Mark appointment as no-show"""
    success = data_handler.mark_no_show(appointment_id)
    if success:
        flash('Appointment marked as no-show.', 'warning')
    else:
        flash('Failed to mark appointment as no-show.', 'danger')
    return redirect(request.referrer or url_for('admin_dashboard'))

@app.route('/admin/action/refund/<appointment_id>', methods=['POST'])
@admin_required
def admin_process_refund(appointment_id):
    """Admin action: Process refund"""
    success = data_handler.process_refund(appointment_id)
    if success:
        flash('Refund processed successfully.', 'success')
    else:
        flash('Failed to process refund.', 'danger')
    return redirect(request.referrer or url_for('admin_dashboard'))

@app.route('/admin/action/mark-paid/<appointment_id>', methods=['POST'])
@admin_required
def admin_mark_paid(appointment_id):
    """Admin action: Mark payment as paid (for Pay-at-Clinic)"""
    success = data_handler.mark_payment_paid(appointment_id)
    if success:
        flash('Payment marked as paid.', 'success')
    else:
        flash('Failed to mark payment as paid.', 'danger')
    return redirect(request.referrer or url_for('admin_dashboard'))

@app.route('/doctors')
def doctors_list():
    """List all doctors with search functionality (Browse All)"""
    if 'user_id' not in session:
        flash('Please login to view doctors.', 'warning')
        return redirect(url_for('login'))
    
    search_query = request.args.get('search', '')
    doctors = data_handler.search_doctors(search_query)
    
    # Add hospital and city info to each doctor
    hospitals = {h['id']: h for h in data_handler.get_hospitals()}
    cities = {c['id']: c for c in data_handler.get_cities()}
    
    for doctor in doctors:
        hospital_id = doctor.get('hospital_id')
        if hospital_id and hospital_id in hospitals:
            hospital = hospitals[hospital_id]
            doctor['hospital_name'] = hospital['name']
            city_id = hospital.get('city_id')
            if city_id and city_id in cities:
                doctor['city_name'] = cities[city_id]['name']
    
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
    
    # Add hospital and city info
    hospital = data_handler.get_hospital_by_id(doctor.get('hospital_id'))
    city = None
    if hospital:
        city = data_handler.get_city_by_id(hospital.get('city_id'))
    
    return render_template('doctor_detail.html', doctor=doctor, hospital=hospital, city=city)

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
    
    # Get hospital and city info
    hospital = data_handler.get_hospital_by_id(doctor.get('hospital_id'))
    city = None
    if hospital:
        city = data_handler.get_city_by_id(hospital.get('city_id'))
    
    if request.method == 'POST':
        date = request.form.get('date')
        time = request.form.get('time')
        reason = request.form.get('reason')
        
        # Validate input
        if not all([date, time, reason]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('book_appointment', doctor_id=doctor_id))
        
        # Create appointment with pending_payment status
        appointment_data = {
            'id': str(uuid.uuid4()),
            'user_id': session['user_id'],
            'user_email': session['user_email'],
            'user_name': session['user_name'],
            'doctor_id': doctor_id,
            'doctor_name': doctor['name'],
            'hospital_id': doctor.get('hospital_id'),
            'hospital_name': hospital['name'] if hospital else None,
            'city_id': hospital.get('city_id') if hospital else None,
            'city_name': city['name'] if city else None,
            'date': date,
            'time': time,
            'reason': reason,
            'status': 'pending_payment',
            'booked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'payment_status': 'Pending',
            'payment_method': None,
            'payment_input': None,
            'transaction_id': None,
            'paid_at': None
        }
        
        # Use atomic booking to prevent race conditions
        success, message, appointment_id = data_handler.atomic_book_slot(
            doctor_id, date, time, appointment_data
        )
        
        if success:
            # Store appointment ID in session for payment
            session['pending_appointment_id'] = appointment_id
            return redirect(url_for('payment_page', appointment_id=appointment_id))
        else:
            flash(message, 'danger')
            return redirect(url_for('book_appointment', doctor_id=doctor_id))
    
    # Generate available dates (next 30 days, starting from today)
    today = datetime.now().date()
    available_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, 30)]
    
    # Get booked slots for this doctor
    doctor_appointments = data_handler.get_appointments_by_doctor(doctor_id)
    booked_slots = {}
    slot_counts = {}
    past_slots = {}
    urgent_slots = {}
    
    for appt in doctor_appointments:
        if appt['status'] in ['confirmed', 'pending_payment']:
            key = f"{appt['date']}_{appt['time']}"
            booked_slots[key] = True
            
            # Count bookings per day for status badges
            date_key = appt['date']
            slot_counts[date_key] = slot_counts.get(date_key, 0) + 1
    
    # Mark past slots and urgent slots for all dates
    for date_str in available_dates:
        for slot in TIME_SLOTS:
            slot_key = f"{date_str}_{slot}"
            if is_slot_in_past(date_str, slot):
                past_slots[slot_key] = True
            elif is_slot_within_hour(date_str, slot):
                urgent_slots[slot_key] = True
    
    return render_template('book_appointment.html', 
                         doctor=doctor,
                         hospital=hospital,
                         city=city,
                         available_dates=available_dates,
                         time_slots=TIME_SLOTS,
                         booked_slots=booked_slots,
                         slot_counts=slot_counts,
                         past_slots=past_slots,
                         urgent_slots=urgent_slots)

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
    
    # Classify appointments by status
    upcoming_appointments = []
    completed_appointments = []
    missed_appointments = []
    cancelled_appointments = []
    
    for appt in appointments:
        time_status = get_appointment_status(appt)
        appt['time_status'] = time_status  # Add to appointment for template use
        
        if time_status == 'upcoming':
            upcoming_appointments.append(appt)
        elif time_status == 'completed':
            completed_appointments.append(appt)
        elif time_status == 'missed':
            missed_appointments.append(appt)
        elif time_status == 'cancelled':
            cancelled_appointments.append(appt)
    
    # Sort each category by date and time
    upcoming_appointments.sort(key=lambda x: (x['date'], x['time']))
    completed_appointments.sort(key=lambda x: (x['date'], x['time']), reverse=True)
    missed_appointments.sort(key=lambda x: (x['date'], x['time']), reverse=True)
    cancelled_appointments.sort(key=lambda x: (x['date'], x['time']), reverse=True)
    
    return render_template('my_appointments.html', 
                         upcoming_appointments=upcoming_appointments,
                         completed_appointments=completed_appointments,
                         missed_appointments=missed_appointments,
                         cancelled_appointments=cancelled_appointments)

@app.route('/appointment/cancel/<appointment_id>', methods=['POST'])
def cancel_appointment_user(appointment_id):
    """Cancel an appointment (patient action)"""
    if 'user_id' not in session:
        flash('Please login to cancel appointments.', 'warning')
        return redirect(url_for('login'))
    
    appointment = data_handler.get_appointment_by_id(appointment_id)
    
    if not appointment or appointment['user_id'] != session['user_id']:
        flash('Appointment not found!', 'danger')
        return redirect(url_for('my_appointments'))
    
    # Check if appointment is in the future
    if is_slot_in_past(appointment['date'], appointment['time']):
        flash('Cannot cancel past appointments.', 'danger')
        return redirect(url_for('my_appointments'))
    
    # Cancel the appointment
    success = data_handler.cancel_appointment(appointment_id)
    if success:
        flash('Appointment cancelled successfully.', 'success')
    else:
        flash('Failed to cancel appointment.', 'danger')
    
    return redirect(url_for('my_appointments'))

@app.route('/appointment/reschedule/<appointment_id>', methods=['GET', 'POST'])
def reschedule_appointment(appointment_id):
    """Reschedule an appointment"""
    if 'user_id' not in session:
        flash('Please login to reschedule appointments.', 'warning')
        return redirect(url_for('login'))
    
    appointment = data_handler.get_appointment_by_id(appointment_id)
    
    if not appointment or appointment['user_id'] != session['user_id']:
        flash('Appointment not found!', 'danger')
        return redirect(url_for('my_appointments'))
    
    # Check if appointment is in the future
    if is_slot_in_past(appointment['date'], appointment['time']):
        flash('Cannot reschedule past appointments.', 'danger')
        return redirect(url_for('my_appointments'))
    
    doctor = data_handler.get_doctor_by_id(appointment['doctor_id'])
    
    if request.method == 'POST':
        new_date = request.form.get('date')
        new_time = request.form.get('time')
        
        if not all([new_date, new_time]):
            flash('Please select both date and time.', 'danger')
            return redirect(url_for('reschedule_appointment', appointment_id=appointment_id))
        
        # Check if new slot is available
        if data_handler.is_slot_booked(appointment['doctor_id'], new_date, new_time):
            flash('Selected time slot is not available. Please choose another slot.', 'danger')
            return redirect(url_for('reschedule_appointment', appointment_id=appointment_id))
        
        # Update appointment with new date and time
        update_data = {
            'date': new_date,
            'time': new_time,
            'rescheduled_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        success = data_handler.update_appointment(appointment_id, update_data)
        
        if success:
            flash('Appointment rescheduled successfully!', 'success')
            return redirect(url_for('my_appointments'))
        else:
            flash('Failed to reschedule appointment.', 'danger')
    
    # Generate available dates (next 30 days, starting from today)
    today = datetime.now().date()
    available_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, 30)]
    
    # Get booked slots for this doctor
    doctor_appointments = data_handler.get_appointments_by_doctor(appointment['doctor_id'])
    booked_slots = {}
    past_slots = {}
    urgent_slots = {}
    
    for appt in doctor_appointments:
        # Exclude current appointment from booked slots (since it will be released)
        if appt['id'] == appointment_id:
            continue
            
        if appt['status'] in ['confirmed', 'pending_payment']:
            key = f"{appt['date']}_{appt['time']}"
            booked_slots[key] = True
    
    # Mark past slots
    for date_str in available_dates:
        for slot in TIME_SLOTS:
            slot_key = f"{date_str}_{slot}"
            if is_slot_in_past(date_str, slot):
                past_slots[slot_key] = True
            elif is_slot_within_hour(date_str, slot):
                urgent_slots[slot_key] = True
    
    return render_template('reschedule_appointment.html',
                         appointment=appointment,
                         doctor=doctor,
                         available_dates=available_dates,
                         time_slots=TIME_SLOTS,
                         booked_slots=booked_slots,
                         past_slots=past_slots,
                         urgent_slots=urgent_slots)

# Payment Routes
@app.route('/payment/<appointment_id>')
def payment_page(appointment_id):
    """Show payment options page"""
    if 'user_id' not in session:
        flash('Please login to continue.', 'warning')
        return redirect(url_for('login'))
    
    appointment = data_handler.get_appointment_by_id(appointment_id)
    
    if not appointment or appointment['user_id'] != session['user_id']:
        flash('Appointment not found!', 'danger')
        return redirect(url_for('doctors_list'))
    
    # Check if already paid
    if appointment.get('payment_status') == 'Success':
        flash('This appointment has already been paid for.', 'info')
        return redirect(url_for('appointment_confirmation', appointment_id=appointment_id))
    
    doctor = data_handler.get_doctor_by_id(appointment['doctor_id'])
    
    return render_template('payment.html', appointment=appointment, doctor=doctor)

@app.route('/payment/process/<appointment_id>', methods=['POST'])
def process_payment(appointment_id):
    """Process payment for appointment"""
    if 'user_id' not in session:
        flash('Please login to continue.', 'warning')
        return redirect(url_for('login'))
    
    appointment = data_handler.get_appointment_by_id(appointment_id)
    
    if not appointment or appointment['user_id'] != session['user_id']:
        flash('Appointment not found!', 'danger')
        return redirect(url_for('doctors_list'))
    
    payment_method = request.form.get('payment_method')
    
    if not payment_method:
        flash('Please select a payment method!', 'danger')
        return redirect(url_for('payment_page', appointment_id=appointment_id))
    
    # Get payment input based on method
    payment_input = None
    if payment_method == 'upi':
        payment_input = request.form.get('upi_id')
    elif payment_method == 'card':
        card_number = request.form.get('card_number')
        card_expiry = request.form.get('card_expiry')
        card_cvv = request.form.get('card_cvv')
        payment_input = f"Card ending in {card_number[-4:] if card_number else 'XXXX'}"
    elif payment_method == 'netbanking':
        payment_input = request.form.get('bank_name')
    
    # Mock payment processing
    transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"
    
    # Simulate 90% success rate for online payments
    import random
    payment_success = random.random() < 0.9
    
    if payment_success:
        payment_data = {
            'payment_method': payment_method.upper(),
            'payment_input': payment_input,
            'payment_status': 'Success',
            'transaction_id': transaction_id,
            'paid_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'confirmed'
        }
    else:
        # Payment failed - cancel appointment to free slot
        payment_data = {
            'payment_method': payment_method.upper(),
            'payment_input': payment_input,
            'payment_status': 'Failed',
            'transaction_id': transaction_id,
            'status': 'cancelled'
        }
    
    # Update appointment
    data_handler.update_appointment(appointment_id, payment_data)
    
    if payment_data['payment_status'] == 'Failed':
        return redirect(url_for('payment_failed', appointment_id=appointment_id))
    else:
        return redirect(url_for('payment_success', appointment_id=appointment_id))

@app.route('/payment/success/<appointment_id>')
def payment_success(appointment_id):
    """Payment success page"""
    if 'user_id' not in session:
        flash('Please login to continue.', 'warning')
        return redirect(url_for('login'))
    
    appointment = data_handler.get_appointment_by_id(appointment_id)
    
    if not appointment or appointment['user_id'] != session['user_id']:
        flash('Appointment not found!', 'danger')
        return redirect(url_for('doctors_list'))
    
    return render_template('payment_success.html', appointment=appointment)

@app.route('/payment/failed/<appointment_id>')
def payment_failed(appointment_id):
    """Payment failed page"""
    if 'user_id' not in session:
        flash('Please login to continue.', 'warning')
        return redirect(url_for('login'))
    
    appointment = data_handler.get_appointment_by_id(appointment_id)
    
    if not appointment or appointment['user_id'] != session['user_id']:
        flash('Appointment not found!', 'danger')
        return redirect(url_for('doctors_list'))
    
    doctor = data_handler.get_doctor_by_id(appointment['doctor_id'])
    
    return render_template('payment_failed.html', appointment=appointment, doctor=doctor)

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


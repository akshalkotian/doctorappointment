import json
import os
from datetime import datetime
import threading
import fcntl

class DataHandler:
    """Handler for JSON file operations with slot locking"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, 'users.json')
        self.doctors_file = os.path.join(data_dir, 'doctors.json')
        self.appointments_file = os.path.join(data_dir, 'appointments.json')
        self.cities_file = os.path.join(data_dir, 'cities.json')
        self.hospitals_file = os.path.join(data_dir, 'hospitals.json')
        
        # Thread lock for atomic operations
        self.lock = threading.Lock()
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def read_json(self, filename):
        """Read data from JSON file"""
        if not os.path.exists(filename):
            return []
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    
    def write_json(self, filename, data):
        """Write data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    
    # User operations
    def get_users(self):
        """Get all users"""
        return self.read_json(self.users_file)
    
    def get_user_by_email(self, email):
        """Get user by email"""
        users = self.get_users()
        for user in users:
            if user['email'] == email:
                return user
        return None
    
    def add_user(self, user_data):
        """Add a new user"""
        users = self.get_users()
        users.append(user_data)
        self.write_json(self.users_file, users)
    
    # Doctor operations
    def get_doctors(self):
        """Get all doctors"""
        return self.read_json(self.doctors_file)
    
    def get_doctor_by_id(self, doctor_id):
        """Get doctor by ID"""
        doctors = self.get_doctors()
        for doctor in doctors:
            if doctor['id'] == doctor_id:
                return doctor
        return None
    
    def search_doctors(self, query):
        """Search doctors by name or specialization"""
        doctors = self.get_doctors()
        if not query:
            return doctors
        
        query = query.lower()
        filtered = []
        for doctor in doctors:
            if (query in doctor['name'].lower() or 
                query in doctor['specialization'].lower()):
                filtered.append(doctor)
        return filtered
    
    def get_doctors_by_hospital(self, hospital_id):
        """Get all doctors for a specific hospital"""
        doctors = self.get_doctors()
        return [d for d in doctors if d.get('hospital_id') == hospital_id]
    
    # City operations
    def get_cities(self):
        """Get all cities"""
        return self.read_json(self.cities_file)
    
    def get_city_by_id(self, city_id):
        """Get city by ID"""
        cities = self.get_cities()
        for city in cities:
            if city['id'] == city_id:
                return city
        return None
    
    # Hospital operations
    def get_hospitals(self):
        """Get all hospitals"""
        return self.read_json(self.hospitals_file)
    
    def get_hospital_by_id(self, hospital_id):
        """Get hospital by ID"""
        hospitals = self.get_hospitals()
        for hospital in hospitals:
            if hospital['id'] == hospital_id:
                return hospital
        return None
    
    def get_hospitals_by_city(self, city_id):
        """Get all hospitals in a specific city"""
        hospitals = self.get_hospitals()
        return [h for h in hospitals if h['city_id'] == city_id]
    
    # Appointment operations
    def get_appointments(self):
        """Get all appointments"""
        return self.read_json(self.appointments_file)
    
    def get_appointments_by_user(self, user_email):
        """Get appointments for a specific user"""
        appointments = self.get_appointments()
        user_appointments = []
        for appt in appointments:
            if appt['user_email'] == user_email:
                user_appointments.append(appt)
        return user_appointments
    
    def get_appointments_by_doctor(self, doctor_id):
        """Get appointments for a specific doctor"""
        appointments = self.get_appointments()
        doctor_appointments = []
        for appt in appointments:
            if appt['doctor_id'] == doctor_id:
                doctor_appointments.append(appt)
        return doctor_appointments
    
    def is_slot_booked(self, doctor_id, date, time):
        """Check if a time slot is already booked (excluding cancelled and no_show)"""
        appointments = self.get_appointments_by_doctor(doctor_id)
        for appt in appointments:
            if (appt['date'] == date and appt['time'] == time and 
                appt['status'] in ['confirmed', 'pending_payment']):
                return True
        return False
    
    def add_appointment(self, appointment_data):
        """Add a new appointment (use atomic_book_slot for thread-safe booking)"""
        appointments = self.get_appointments()
        appointments.append(appointment_data)
        self.write_json(self.appointments_file, appointments)
        return True
    
    def atomic_book_slot(self, doctor_id, date, time, appointment_data):
        """
        Atomically book a slot - check and reserve in one operation
        Returns (success: bool, message: str, appointment_id: str or None)
        """
        with self.lock:
            # Re-check availability within lock
            if self.is_slot_booked(doctor_id, date, time):
                return False, "This time slot was just booked by another user. Please select another slot.", None
            
            # Check if slot is cancelled (cancelled slots show as available)
            appointments = self.get_appointments()
            for appt in appointments:
                if (appt['doctor_id'] == doctor_id and 
                    appt['date'] == date and 
                    appt['time'] == time and 
                    appt['status'] in ['confirmed', 'pending_payment']):
                    return False, "This time slot is already booked. Please select another slot.", None
            
            # Slot is available, book it
            appointments.append(appointment_data)
            self.write_json(self.appointments_file, appointments)
            return True, "Slot booked successfully", appointment_data['id']
    
    def get_appointment_by_id(self, appointment_id):
        """Get appointment by ID"""
        appointments = self.get_appointments()
        for appt in appointments:
            if appt['id'] == appointment_id:
                return appt
        return None
    
    def update_appointment(self, appointment_id, update_data):
        """Update an appointment with new data"""
        with self.lock:
            appointments = self.get_appointments()
            for i, appt in enumerate(appointments):
                if appt['id'] == appointment_id:
                    appointments[i].update(update_data)
                    self.write_json(self.appointments_file, appointments)
                    return True
            return False
    
    def cancel_appointment(self, appointment_id):
        """Cancel an appointment"""
        return self.update_appointment(appointment_id, {
            'status': 'cancelled',
            'cancelled_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def mark_no_show(self, appointment_id):
        """Mark appointment as no-show"""
        return self.update_appointment(appointment_id, {
            'status': 'no_show',
            'no_show_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def process_refund(self, appointment_id):
        """Process refund for an appointment"""
        return self.update_appointment(appointment_id, {
            'payment_status': 'Refunded',
            'refunded_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def mark_payment_paid(self, appointment_id):
        """Mark a pending payment as paid (for Pay-at-Clinic)"""
        return self.update_appointment(appointment_id, {
            'payment_status': 'Success',
            'paid_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        users = self.get_users()
        for user in users:
            if user['id'] == user_id:
                return user
        return None
    
    def update_user(self, user_id, update_data):
        """Update user information"""
        with self.lock:
            users = self.get_users()
            for i, user in enumerate(users):
                if user['id'] == user_id:
                    users[i].update(update_data)
                    self.write_json(self.users_file, users)
                    return True
            return False


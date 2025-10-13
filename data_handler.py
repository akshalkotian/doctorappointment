import json
import os
from datetime import datetime

class DataHandler:
    """Handler for JSON file operations"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, 'users.json')
        self.doctors_file = os.path.join(data_dir, 'doctors.json')
        self.appointments_file = os.path.join(data_dir, 'appointments.json')
        
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
        """Check if a time slot is already booked"""
        appointments = self.get_appointments_by_doctor(doctor_id)
        for appt in appointments:
            if appt['date'] == date and appt['time'] == time:
                return True
        return False
    
    def add_appointment(self, appointment_data):
        """Add a new appointment"""
        appointments = self.get_appointments()
        appointments.append(appointment_data)
        self.write_json(self.appointments_file, appointments)
        return True
    
    def get_appointment_by_id(self, appointment_id):
        """Get appointment by ID"""
        appointments = self.get_appointments()
        for appt in appointments:
            if appt['id'] == appointment_id:
                return appt
        return None


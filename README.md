# Doctor Appointment Booking Website

A complete web-based doctor appointment booking system built with Python Flask and JSON storage. This application allows users to register, login, search for doctors, view doctor profiles, and book appointments with an intuitive interface.

## Features

### User Management
- **User Registration**: New users can create accounts with email, password, phone number, and name
- **User Login/Logout**: Secure authentication with session handling
- **Session Management**: User sessions are maintained across the application

### Doctor Management
- **Doctor Listing**: Browse all available doctors with their specializations
- **Doctor Search**: Search doctors by name or specialization
- **Doctor Profiles**: View detailed information about each doctor including:
  - Name, photo, and specialization
  - Qualifications and experience
  - Contact information (email, phone)
  - Location/clinic details
  - About section

### Appointment Booking
- **Available Slots**: View available time slots for the next 30 days
- **Time Slot Selection**: Interactive time slot picker
- **Double-Booking Prevention**: Booked slots are automatically disabled
- **Appointment Confirmation**: Confirmation page after successful booking
- **My Appointments**: View all your booked appointments

### User Interface
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Bootstrap 5**: Modern and clean UI with Bootstrap framework
- **Font Awesome Icons**: Professional icons throughout the interface
- **Interactive Elements**: Smooth animations and transitions
- **Flash Messages**: User feedback for all actions

## Technology Stack

- **Backend**: Python Flask 3.0.0
- **Frontend**: HTML5, CSS3, JavaScript
- **Templating**: Jinja2
- **Styling**: Bootstrap 5.3.0, Custom CSS
- **Icons**: Font Awesome 6.4.0
- **Data Storage**: JSON files (users.json, doctors.json, appointments.json)
- **Security**: Werkzeug password hashing

## Project Structure

```
doctorappointment/
│
├── app.py                      # Main Flask application
├── data_handler.py             # JSON data operations handler
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── data/                       # JSON storage directory
│   ├── users.json             # User accounts
│   ├── doctors.json           # Doctor profiles
│   └── appointments.json      # Appointment records
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html              # Base template
│   ├── home.html              # Home page
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── doctors_list.html      # Doctor listing page
│   ├── doctor_detail.html     # Doctor profile page
│   ├── book_appointment.html  # Appointment booking page
│   ├── appointment_confirmation.html  # Confirmation page
│   └── my_appointments.html   # User's appointments page
│
└── static/                     # Static files
    ├── css/
    │   └── style.css          # Custom CSS styles
    └── js/
        └── script.js          # Custom JavaScript
```

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- VS Code (recommended) or any text editor

### Step 1: Clone or Download the Project
```bash
cd /path/to/doctorappointment
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install Flask==3.0.0 Werkzeug==3.0.1
```

### Step 3: Run the Application
```bash
python app.py
```

The application will start on `http://127.0.0.1:5000/`

### Step 4: Access the Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

## Usage Guide

### For New Users

1. **Register an Account**
   - Click "Register" in the navigation bar
   - Fill in your name, email, phone, and password
   - Submit the form to create your account

2. **Login**
   - Click "Login" in the navigation bar
   - Enter your email and password
   - You'll be redirected to the doctors list

3. **Search for a Doctor**
   - Browse all doctors or use the search bar
   - Search by doctor name or specialization (e.g., "Cardiologist", "Sarah")

4. **View Doctor Profile**
   - Click "View Profile" on any doctor card
   - See detailed information about the doctor

5. **Book an Appointment**
   - Click "Book Appointment" on a doctor card or profile
   - Select a date from the dropdown
   - Choose an available time slot
   - Enter the reason for your visit
   - Confirm your appointment

6. **View Your Appointments**
   - Click "My Appointments" in the navigation bar
   - See all your booked appointments with details

7. **Logout**
   - Click on your name in the navigation bar
   - Select "Logout" from the dropdown

## Sample Doctors

The application comes pre-loaded with 8 sample doctors:

1. **Dr. Sarah Johnson** - Cardiologist (15 years experience)
2. **Dr. Michael Chen** - Orthopedic Surgeon (12 years experience)
3. **Dr. Emily Rodriguez** - Dermatologist (10 years experience)
4. **Dr. James Williams** - Pediatrician (18 years experience)
5. **Dr. Priya Patel** - Neurologist (14 years experience)
6. **Dr. Robert Brown** - General Physician (20 years experience)
7. **Dr. Lisa Anderson** - Gynecologist (16 years experience)
8. **Dr. David Lee** - Psychiatrist (11 years experience)

## Available Time Slots

Appointments can be booked in the following time slots:
- 09:00 AM
- 10:00 AM
- 11:00 AM
- 12:00 PM
- 02:00 PM
- 03:00 PM
- 04:00 PM
- 05:00 PM

## Key Features Implementation

### Session Management
- Flask session is used to store user login state
- Users must be logged in to access doctor listings and booking features
- Sessions persist until logout

### Double-Booking Prevention
- The system checks for existing appointments before allowing new bookings
- Booked time slots are visually marked and disabled
- Real-time slot availability checking

### Data Persistence
- All data is stored in JSON files
- User passwords are securely hashed using Werkzeug
- Appointments are marked with unique IDs and timestamps

### Responsive Design
- Mobile-first approach
- Bootstrap grid system for layouts
- Custom CSS for enhanced visuals
- Smooth animations and transitions

## Security Features

- **Password Hashing**: All passwords are hashed using Werkzeug's security functions
- **Session Management**: Secure session handling with Flask sessions
- **Authentication Required**: Protected routes require user login
- **Input Validation**: Form validation on both client and server side

## Customization

### Changing the Secret Key
For production use, change the secret key in `app.py`:
```python
app.secret_key = 'your-secure-secret-key-here'
```

### Adding More Doctors
Edit `data/doctors.json` and add new doctor objects following the existing format.

### Modifying Time Slots
Edit the `TIME_SLOTS` list in `app.py`:
```python
TIME_SLOTS = [
    "09:00 AM", "10:00 AM", "11:00 AM", # ... add more
]
```

### Customizing Styles
Edit `static/css/style.css` to change colors, fonts, and layouts.

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, change it in `app.py`:
```python
app.run(debug=True, port=5001)  # Use a different port
```

### JSON Files Not Found
Make sure the `data/` directory exists. The application creates it automatically on first run.

### Static Files Not Loading
Ensure the `static/` directory structure is correct with `css/` and `js/` subdirectories.

## Development Mode

The application runs in debug mode by default:
```python
app.run(debug=True, port=5000)
```

Debug mode features:
- Auto-reload on code changes
- Detailed error messages
- Interactive debugger

**Note**: Disable debug mode in production!

## Future Enhancements

Potential features to add:
- Email notifications for appointments
- SMS reminders
- Doctor availability calendar
- Appointment rescheduling
- Appointment cancellation
- Admin panel for managing doctors
- Patient medical history
- Prescription management
- Payment integration
- Review and rating system

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Opera

## License

This project is created for educational purposes. Feel free to use and modify as needed.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Ensure all dependencies are installed correctly

## Credits

- **Framework**: Flask
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **Backend**: Python 3

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Author**: Healthcare Plus Development Team

Enjoy using the Doctor Appointment Booking System! 🏥

# Doctor Appointment Booking System

A comprehensive web-based doctor appointment booking system built with Python Flask and JSON storage. This application features patient and admin portals, slot locking, payment processing, and complete appointment management.

## 🚀 New Features (v2.0)

### 1. **Atomic Slot Locking**
- Thread-safe booking mechanism prevents double-booking
- Server-side re-check before confirming appointments
- Automatic slot release on payment failure
- Real-time slot availability checking

### 2. **Role-Based Authentication**
- **Patient Role**: Book appointments, view history, manage profile
- **Admin Role**: Full dashboard access, appointment management, analytics
- Separate login portals for patients and admins
- Session-based role management

### 3. **Admin Portal**
Complete administrative interface with:
- **Dashboard**: Statistics, filters, and appointment overview
  - Filter by doctor, date, and payment status
  - Booking counts per doctor
  - Payment status tracking
  - Real-time statistics (total bookings, confirmed, pending payments)
- **Timetable View**: Daily slot management
  - Visual representation of all slots (Booked/Available)
  - Doctor-wise and date-wise filtering
  - Quick actions on booked slots
- **Admin Actions**:
  - Cancel appointments
  - Mark appointments as no-show
  - Process refunds
  - Mark Pay-at-Clinic payments as paid

### 4. **Payment System (Mock)**
Multiple payment methods supported:
- **UPI**: PhonePe, GPay, Paytm
- **Card**: Credit/Debit cards
- **Net Banking**: All major banks
- **Wallet**: Paytm, PhonePe Wallet
- **Pay-at-Clinic**: Cash payment at clinic (pending status)

Payment features:
- Transaction ID generation
- Payment status tracking (Success/Failed/Pending/Refunded)
- Mock payment processing (90% success rate)
- Payment confirmation pages
- Admin can mark Pay-at-Clinic as paid

### 5. **Enhanced Frontend**
- **Status Badges**: Available, Filling Fast, Almost Full, Full
- **Payment Pages**: Modern payment selection interface
- **Success/Failure Pages**: Animated confirmation pages
- **Admin Navigation**: Separate navigation for admin users
- **Improved Error Messages**: Clear feedback for slot conflicts

## Features

### User Management
- **Patient Registration**: Create accounts with email, password, phone, and name
- **Admin Registration**: Secure admin account creation with admin code
- **Separate Login Portals**: Patient and admin login pages
- **Role-Based Access Control**: Protected routes based on user role
- **Session Management**: Secure session handling

### Doctor Management
- **Doctor Listing**: Browse all available doctors
- **Search Functionality**: Search by name or specialization
- **Detailed Profiles**: Complete doctor information
- **Symptom Checker**: Find doctors based on symptoms

### Appointment Booking
- **Atomic Slot Booking**: Thread-safe booking prevents conflicts
- **30-Day Availability**: Book appointments for the next 30 days
- **Real-Time Slot Status**: Visual indicators for slot availability
- **Status Badges**: Quick view of date availability
- **Payment Integration**: Multiple payment options
- **Appointment Confirmation**: Detailed confirmation with transaction ID
- **My Appointments**: View all booked appointments with payment status

### Admin Features
- **Comprehensive Dashboard**
  - Total bookings, confirmed, cancelled statistics
  - Payment status overview
  - Doctor-wise booking counts
  - Advanced filtering (doctor, date, payment status)
- **Timetable Management**
  - Daily slot view per doctor
  - Visual slot status indicators
  - Booking details in slots
- **Appointment Actions**
  - Cancel bookings
  - Mark no-show
  - Process refunds
  - Mark payments as paid
- **Booking History**: Complete audit trail with timestamps

## Technology Stack

- **Backend**: Python Flask 3.0.0
- **Frontend**: HTML5, CSS3, JavaScript
- **Templating**: Jinja2
- **Styling**: Bootstrap 5.3.0, Custom CSS
- **Icons**: Font Awesome 6.4.0
- **Data Storage**: JSON files with thread-safe operations
- **Security**: Werkzeug password hashing, role-based access control
- **Threading**: Python threading module for atomic operations

## Project Structure

```
doctorappointment/
│
├── app.py                      # Main Flask application with all routes
├── data_handler.py             # JSON operations with thread-safe locking
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── data/                       # JSON storage directory
│   ├── users.json             # User accounts (patients & admins)
│   ├── doctors.json           # Doctor profiles
│   └── appointments.json      # Appointments with payment info
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html              # Base template with role-based nav
│   ├── home.html              # Landing page
│   ├── login.html             # Patient login
│   ├── register.html          # Patient registration
│   ├── admin_login.html       # Admin login portal
│   ├── admin_register.html    # Admin registration
│   ├── admin_dashboard.html   # Admin dashboard
│   ├── admin_timetable.html   # Admin timetable view
│   ├── doctors_list.html      # Doctor listing
│   ├── doctor_detail.html     # Doctor profile
│   ├── find_doctor.html       # Symptom-based doctor finder
│   ├── book_appointment.html  # Booking with status badges
│   ├── payment.html           # Payment method selection
│   ├── payment_success.html   # Payment success page
│   ├── payment_failed.html    # Payment failure page
│   ├── appointment_confirmation.html  # Confirmation
│   └── my_appointments.html   # User appointments
│
└── static/                     # Static files
    ├── css/
    │   └── style.css          # Custom CSS
    └── js/
        └── script.js          # Custom JavaScript
```

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Navigate to Project Directory
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

## Routes & Endpoints

### Public Routes
- `/` - Home page
- `/register` - Patient registration
- `/login` - Patient login
- `/admin/register` - Admin registration (requires admin code: **ADMIN2024**)
- `/admin/login` - Admin login

### Patient Routes (Authentication Required)
- `/doctors` - Browse all doctors
- `/doctor/<doctor_id>` - View doctor profile
- `/find-doctor` - Symptom-based doctor search
- `/book/<doctor_id>` - Book appointment
- `/payment/<appointment_id>` - Payment page
- `/payment/process/<appointment_id>` - Process payment (POST)
- `/payment/success/<appointment_id>` - Payment success
- `/payment/failed/<appointment_id>` - Payment failure
- `/appointment/confirmation/<appointment_id>` - Appointment details
- `/my-appointments` - View all appointments
- `/logout` - Logout

### Admin Routes (Admin Authentication Required)
- `/admin/dashboard` - Admin dashboard with filters
- `/admin/timetable` - Daily timetable view
- `/admin/action/cancel/<appointment_id>` - Cancel appointment (POST)
- `/admin/action/no-show/<appointment_id>` - Mark no-show (POST)
- `/admin/action/refund/<appointment_id>` - Process refund (POST)
- `/admin/action/mark-paid/<appointment_id>` - Mark as paid (POST)

## Usage Guide

### For Patients

1. **Register an Account**
   - Click "Get Started" or "Patient Login"
   - Fill in your details and register
   - Role is automatically set to "patient"

2. **Login**
   - Use your email and password
   - Redirected to doctors list

3. **Book an Appointment**
   - Browse or search for doctors
   - Click "Book Appointment"
   - Select date (with availability badges)
   - Choose available time slot
   - Enter reason for visit
   - Redirected to payment page

4. **Make Payment**
   - Choose payment method:
     - UPI, Card, Net Banking, Wallet (instant)
     - Pay-at-Clinic (pending payment)
   - Complete payment process
   - View success/failure page

5. **View Appointments**
   - Check "My Appointments"
   - See all bookings with payment status

### For Admins

1. **Register as Admin**
   - Go to "Admin" in navigation
   - Click "Register here"
   - Use admin code: **ADMIN2024**
   - Complete registration

2. **Admin Login**
   - Click "Admin" in navigation
   - Login with admin credentials
   - Redirected to admin dashboard

3. **Dashboard Usage**
   - View statistics (bookings, payments)
   - Apply filters (doctor, date, payment status)
   - See all appointments with details
   - Perform actions:
     - Cancel appointments
     - Mark no-show
     - Process refunds
     - Mark Pay-at-Clinic as paid

4. **Timetable View**
   - Select doctor and date
   - View all 8 slots with status
   - See booking details in each slot
   - Quick actions on booked slots

## Data Schema

### users.json
```json
{
  "id": "uuid",
  "name": "string",
  "email": "string",
  "password": "hashed_string",
  "phone": "string",
  "role": "patient|admin",
  "created_at": "timestamp"
}
```

### appointments.json
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "user_email": "string",
  "user_name": "string",
  "doctor_id": "string",
  "doctor_name": "string",
  "date": "YYYY-MM-DD",
  "time": "HH:MM AM/PM",
  "reason": "string",
  "status": "pending_payment|confirmed|cancelled|no_show",
  "booked_at": "timestamp",
  "payment_status": "Success|Failed|Pending|Refunded",
  "payment_method": "UPI|Card|Netbanking|Wallet|Pay-at-Clinic",
  "transaction_id": "string",
  "paid_at": "timestamp",
  "cancelled_at": "timestamp",
  "no_show_at": "timestamp",
  "refunded_at": "timestamp"
}
```

## Key Implementation Details

### Slot Locking Mechanism
- Uses Python threading.Lock() for atomic operations
- `atomic_book_slot()` method performs check-and-book in one operation
- Prevents race conditions when multiple users book simultaneously
- Automatically releases slot if payment fails

### Payment Processing Flow
1. User selects slot → Appointment created with `pending_payment` status
2. Redirected to payment page
3. User selects payment method
4. Payment processed (90% success rate for demo)
5. If success: Status → `confirmed`, Payment → `Success`
6. If failed: Status → `cancelled`, Slot released
7. If Pay-at-Clinic: Status → `confirmed`, Payment → `Pending`

### Status Badge Logic
- **Available**: < 50% slots booked
- **Filling Fast**: 50-74% slots booked
- **Almost Full**: 75-99% slots booked
- **Full**: 100% slots booked

### Admin Security
- Admin code required for registration (configurable in app.py)
- Role-based route protection using decorator
- Separate session handling for admin users

## Configuration

### Admin Code
Change in `app.py` line 107:
```python
if admin_code != 'YOUR_NEW_ADMIN_CODE':
```

### Secret Key
Change in `app.py` line 8:
```python
app.secret_key = 'your-secure-secret-key-here'
```

### Time Slots
Modify in `app.py` lines 14-17:
```python
TIME_SLOTS = [
    "09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
    "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"
]
```

### Payment Success Rate
Adjust in `app.py` line 368:
```python
payment_success = random.random() < 0.9  # 90% success rate
```

## Sample Doctors

The application comes with 8 pre-loaded doctors:

1. **Dr. Rajesh Kumar Sharma** - Cardiologist (15 years)
2. **Dr. Amit Singh Rathore** - Orthopedic Surgeon (12 years)
3. **Dr. Meera Kulkarni** - Dermatologist (10 years)
4. **Dr. Suresh Reddy** - Pediatrician (18 years)
5. **Dr. Priya Menon** - Neurologist (14 years)
6. **Dr. Vikram Singh** - General Physician (20 years)
7. **Dr. Anjali Deshmukh** - Gynecologist (16 years)
8. **Dr. Arun Kapoor** - Psychiatrist (11 years)

## Security Features

- **Password Hashing**: Werkzeug secure password hashing
- **Role-Based Access Control**: Separate patient/admin access
- **Session Management**: Secure Flask sessions
- **Atomic Operations**: Thread-safe booking
- **Input Validation**: Server and client-side validation
- **Admin Code Protection**: Required for admin registration

## Troubleshooting

### Port Already in Use
```python
app.run(debug=True, port=5001)  # Change port
```

### Slot Locking Issues
Ensure only one instance of the application is running.

### Payment Always Failing
Check line 368 in `app.py` - adjust success rate.

### Admin Code Not Working
Verify admin code in `app.py` line 107.

## Future Enhancements

- Database integration (PostgreSQL/MySQL)
- Email notifications
- SMS reminders
- Real payment gateway integration
- Appointment rescheduling
- Doctor schedule management
- Patient medical records
- Prescription management
- Review and rating system
- Multi-language support
- Calendar view
- Export reports (PDF/Excel)

## Development Notes

### Debug Mode
Enabled by default:
```python
app.run(debug=True, port=5000)
```

**Disable in production!**

### Adding New Admins
1. Navigate to `/admin/register`
2. Enter admin code: **ADMIN2024**
3. Complete registration

### Testing Payments
- All methods except Pay-at-Clinic have 90% success rate
- Pay-at-Clinic always succeeds with pending payment
- Failed payments automatically cancel appointment

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Opera

## License

This project is created for educational purposes.

## Credits

- **Framework**: Flask
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **Backend**: Python 3

---

**Version**: 2.0.0  
**Last Updated**: November 2025  
**Author**: Healthcare Plus Development Team

## Changelog

### v2.0.0 (November 2025)
- ✨ Added atomic slot locking mechanism
- ✨ Implemented role-based authentication (patient/admin)
- ✨ Created comprehensive admin portal
- ✨ Added payment processing system (mock)
- ✨ Implemented admin dashboard with filters
- ✨ Added timetable view for admins
- ✨ Added admin actions (cancel, no-show, refund)
- ✨ Created payment success/failure pages
- ✨ Added status badges (Available/Filling Fast/Almost Full)
- ✨ Updated navigation with admin entry
- ✨ Enhanced error messages for slot conflicts
- 🔒 Improved security with role-based access
- 🎨 Modern UI updates across all pages

### v1.0.0 (October 2025)
- Initial release
- Basic patient registration and login
- Doctor listing and search
- Appointment booking
- Symptom-based doctor finder

---

Enjoy using the Doctor Appointment Booking System! 🏥💊

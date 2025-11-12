# 🏗️ HealthCarePlus - System Architecture

## 🎯 High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                             │
│                         (Frontend - HTML/CSS/JS)                       │
├────────────────────────────────────────────────────────────────────────┤
│  • Home Page             • Patient Dashboard    • Doctor Profiles      │
│  • Login/Register        • Find Doctor          • Booking Pages        │
│  • Admin Dashboard       • Payment Pages        • Appointment History  │
└───────────────────────┬────────────────────────────────────────────────┘
                        │
                        │ HTTP Requests (GET/POST)
                        │
┌───────────────────────▼────────────────────────────────────────────────┐
│                        APPLICATION LAYER                               │
│                        (Flask - app.py)                                │
├────────────────────────────────────────────────────────────────────────┤
│  Routes & Controllers:                                                 │
│  • Authentication (@login_required, @admin_required)                   │
│  • Business Logic (booking, payment, cancellation)                     │
│  • Data Validation                                                     │
│  • Session Management                                                  │
│  • API Endpoints (/api/hospitals/:city_id)                             │
└───────────────────────┬────────────────────────────────────────────────┘
                        │
                        │ Function Calls
                        │
┌───────────────────────▼────────────────────────────────────────────────┐
│                       DATA ACCESS LAYER                                │
│                    (data_handler.py - DataHandler class)               │
├────────────────────────────────────────────────────────────────────────┤
│  Operations:                                                           │
│  • CRUD operations for all entities                                    │
│  • Thread-safe atomic booking (threading.Lock)                         │
│  • Data enrichment (joins)                                             │
│  • Search & filter logic                                               │
└───────────────────────┬────────────────────────────────────────────────┘
                        │
                        │ File I/O (json.load/json.dump)
                        │
┌───────────────────────▼────────────────────────────────────────────────┐
│                        STORAGE LAYER                                   │
│                     (JSON Files - data/)                               │
├────────────────────────────────────────────────────────────────────────┤
│  • users.json          • cities.json         • hospitals.json          │
│  • doctors.json        • appointments.json                             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🌊 Complete User Booking Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    END-TO-END BOOKING FLOW                              │
└─────────────────────────────────────────────────────────────────────────┘

START
  │
  ▼
┌─────────────────────┐
│ User visits website │
│   GET /             │
└──────────┬──────────┘
           │
    ┌──────┴───────┐
    │              │
    ▼              ▼
[Not Logged In] [Logged In]
    │              │
    ▼              │
┌──────────┐       │
│Register/ │       │
│Login     │       │
└────┬─────┘       │
     │             │
     └─────┬───────┘
           │
           ▼
┌─────────────────────────────┐
│  PATIENT DASHBOARD          │
│  or HOME PAGE               │
└──────────┬──────────────────┘
           │
    ┌──────┴───────┬─────────────────┐
    │              │                 │
    ▼              ▼                 ▼
[By Location] [By Symptoms]  [Browse All]
    │              │                 │
    ▼              │                 │
Select City        │                 │
    │              │                 │
    ▼              │                 │
Select Hospital    │                 │
    │              │                 │
    └──────┬───────┴─────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  VIEW DOCTORS LIST          │
│  - Filter by gender         │
│  - Filter by experience     │
│  - Search by name/spec      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  SELECT DOCTOR              │
│  Click on doctor card       │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  DOCTOR PROFILE PAGE        │
│  - View details             │
│  - See qualifications       │
│  - Check fees               │
└──────────┬──────────────────┘
           │
           ▼ Click "Book Appointment"
┌─────────────────────────────┐
│  📅 BOOKING PAGE            │
│                             │
│  Step 1: Select Date        │
│    - Calendar grid UI       │
│    - Shows availability     │
│                             │
│  Step 2: Select Time        │
│    - Time slot cards        │
│    - Shows booked/available │
│                             │
│  Step 3: Enter Reason       │
│    - Symptoms/concerns      │
└──────────┬──────────────────┘
           │
           ▼ Submit Form
┌─────────────────────────────┐
│  ⚠️ ATOMIC SLOT CHECK       │
│  (Thread Lock Active)       │
│                             │
│  1. Check if still available│
│  2. If yes → Reserve slot   │
│  3. If no → Show error      │
└──────────┬──────────────────┘
           │
    ┌──────┴────────┐
    │               │
    ▼               ▼
[Available]    [Already Booked]
    │               │
    │               └──→ Show error, select new slot
    │
    ▼
┌─────────────────────────────┐
│  💳 PAYMENT PAGE            │
│                             │
│  Select Method:             │
│  ○ UPI → Enter UPI ID       │
│  ○ Card → Card details      │
│  ○ NetBanking → Bank select │
│  ○ Pay-at-Clinic            │
└──────────┬──────────────────┘
           │
           ▼ Submit Payment
┌─────────────────────────────┐
│  PROCESS PAYMENT            │
│  (Simulate: 80% success)    │
└──────────┬──────────────────┘
           │
    ┌──────┴─────────┐
    │                │
    ▼                ▼
[Success]        [Failed]
    │                │
    │                └──→ Retry payment option
    │
    ▼
┌─────────────────────────────┐
│  ✅ CONFIRMATION PAGE       │
│  - Appointment ID           │
│  - Doctor details           │
│  - Date/Time                │
│  - Payment receipt          │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  MY APPOINTMENTS            │
│  - View all bookings        │
│  - Reschedule               │
│  - Cancel (refund)          │
└─────────────────────────────┘

END
```

---

## 🔐 Authentication & Authorization Flow

```
┌────────────────────────────────────────────────────────────┐
│                  AUTHENTICATION FLOW                        │
└────────────────────────────────────────────────────────────┘

User Login Request
  │
  ▼
┌────────────────────┐
│ POST /login        │
│ - email            │
│ - password         │
└────────┬───────────┘
         │
         ▼
┌────────────────────────────┐
│ 1. Read users.json         │
│ 2. Find user by email      │
└────────┬───────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
[Found]   [Not Found]
    │         │
    │         └──→ Error: Invalid credentials
    │
    ▼
┌────────────────────────────┐
│ 3. Verify password         │
│    check_password_hash()   │
└────────┬───────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
[Match]   [No Match]
    │         │
    │         └──→ Error: Invalid credentials
    │
    ▼
┌────────────────────────────┐
│ 4. Create Session          │
│    session['user_id']      │
│    session['user_email']   │
│    session['user_name']    │
│    session['user_role']    │
└────────┬───────────────────┘
         │
         ▼
    ┌────┴──────┐
    │           │
    ▼           ▼
[Patient]   [Admin]
    │           │
    └───→ Dashboard Redirect


Protected Route Access:
┌────────────────┐
│ User requests  │
│ protected page │
└────────┬───────┘
         │
         ▼
┌──────────────────────┐
│ @login_required      │
│ Check session exists?│
└────────┬─────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
[Yes]      [No]
    │         │
    │         └──→ Redirect to /login
    │
    ▼
┌──────────────────────┐
│ @admin_required      │
│ Check role == admin? │
└────────┬─────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
[Yes]      [No]
    │         │
    │         └──→ Return 403 Forbidden
    │
    ▼
Allow Access
```

---

## 🎛️ Admin Operations Flow

```
┌────────────────────────────────────────────────────────────┐
│                    ADMIN WORKFLOW                           │
└────────────────────────────────────────────────────────────┘

Admin Login
  │
  ▼
┌─────────────────────┐
│ Admin Dashboard     │
│ /admin/dashboard    │
└──────────┬──────────┘
           │
    ┌──────┴───────────┬─────────────┐
    │                  │             │
    ▼                  ▼             ▼
[View Stats]    [Filter/Search]  [Manage Appointments]
    │                  │             │
    │                  │             ├──→ Cancel Appointment
    │                  │             │    └─→ Update status, refund
    │                  │             │
    │                  │             ├──→ Mark No Show
    │                  │             │    └─→ Update status
    │                  │             │
    │                  │             ├──→ Process Refund
    │                  │             │    └─→ Update payment_status
    │                  │             │
    │                  │             └──→ Mark Paid (Pay-at-Clinic)
    │                  │                  └─→ Update payment_status
    │                  │
    │                  ├──→ Filter by Doctor
    │                  ├──→ Filter by Date
    │                  └──→ Filter by Payment Status
    │
    └──→ View Statistics:
         - Total Doctors
         - Total Bookings
         - Payment Status
         - Hospital Analytics
```

---

## 🔄 Data Update Operations

### **Appointment Lifecycle:**

```
CREATE (Book Appointment)
  │
  ├─→ atomic_book_slot()
  │   └─→ WRITE appointments.json
  │
  ▼
READ (View Appointments)
  │
  ├─→ get_appointments_by_user()
  ├─→ get_appointments_by_doctor()
  └─→ get_appointment_by_id()
  │
  ▼
UPDATE (Modify Appointment)
  │
  ├─→ update_appointment()        [Thread-safe with lock]
  ├─→ cancel_appointment()        [Set status + timestamp]
  ├─→ mark_no_show()              [Set status + timestamp]
  ├─→ process_refund()            [Update payment_status]
  └─→ mark_payment_paid()         [Update payment_status]
      └─→ UPDATE appointments.json
  
Note: No DELETE operation - appointments are never deleted,
      only status is updated for audit trail.
```

---

## 🔍 Search & Filter Architecture

### **Doctor Search:**
```
User Input: "heart pain"
     │
     ▼
┌─────────────────────────────┐
│  AI Symptom Analyzer        │
│  - Keyword matching         │
│  - Symptom mapping          │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Recommended Specializations│
│  Example: ["Cardiologist"]  │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Filter doctors.json        │
│  WHERE specialization IN    │
│  recommended_specs          │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Enrich with Hospital & City│
│  - Join hospitals.json      │
│  - Join cities.json         │
└──────────┬──────────────────┘
           │
           ▼
Display Recommended Doctors
```

### **Location-based Search:**
```
User clicks: Bangalore
     │
     ▼
┌─────────────────────────────┐
│  Fetch Hospitals            │
│  GET /api/hospitals/city1   │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Read hospitals.json        │
│  WHERE city_id = "city1"    │
└──────────┬──────────────────┘
           │
           ▼
Display Hospital Cards with Images
     │
     ▼
User clicks Hospital
     │
     ▼
┌─────────────────────────────┐
│  Fetch Doctors              │
│  /hospital/:id/doctors      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Read doctors.json          │
│  WHERE hospital_id = :id    │
└──────────┬──────────────────┘
           │
           ▼
Display Doctor List
```

---

## 🧮 Slot Availability Algorithm

```
┌────────────────────────────────────────────────────────────────┐
│              SLOT AVAILABILITY CHECK                           │
└────────────────────────────────────────────────────────────────┘

Input: doctor_id, selected_date

1. Generate All Possible Slots
   ┌─────────────────────────┐
   │ time_slots = [          │
   │   "09:00 AM",           │
   │   "10:00 AM",           │
   │   "11:00 AM",           │
   │   "02:00 PM",           │
   │   "03:00 PM",           │
   │   "04:00 PM",           │
   │   "05:00 PM"            │
   │ ]                       │
   └──────────┬──────────────┘
              │
              ▼
2. Get Booked Slots
   ┌─────────────────────────┐
   │ Read appointments.json  │
   │ WHERE:                  │
   │   doctor_id = input     │
   │   date = input          │
   │   status IN [           │
   │     'confirmed',        │
   │     'pending_payment'   │
   │   ]                     │
   └──────────┬──────────────┘
              │
              ▼
3. Check Past Slots
   ┌─────────────────────────┐
   │ current_time = now()    │
   │ IF selected_date = today│
   │   Mark past times       │
   └──────────┬──────────────┘
              │
              ▼
4. Calculate Availability
   ┌─────────────────────────┐
   │ FOR each slot:          │
   │   IF booked → Disabled  │
   │   IF past → Disabled    │
   │   ELSE → Available      │
   └──────────┬──────────────┘
              │
              ▼
5. Display to User
   ┌─────────────────────────┐
   │ Available slots (green) │
   │ Booked slots (red)      │
   │ Past slots (gray)       │
   └─────────────────────────┘
```

---

## 💾 Data Persistence Strategy

### **File Operations:**

```
READ Operation:
┌──────────────────┐
│ read_json(file)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────────┐
│ open(file, 'r')      │
│ json.load(f)         │
└────────┬─────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
[Exists]  [Missing]
    │         │
    │         └──→ Return []
    │
    └──→ Return parsed data


WRITE Operation:
┌──────────────────────┐
│ write_json(file, data)
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ open(file, 'w')      │
│ json.dump(data, f,   │
│    indent=4)         │
└──────────────────────┘


ATOMIC WRITE (with Lock):
┌──────────────────────┐
│ with self.lock:      │
│   1. Read data       │
│   2. Modify data     │
│   3. Write data      │
└──────────────────────┘
```

---

## 🎨 Frontend-Backend Integration

### **Page Load Flow:**

```
User navigates to /doctors_list
         │
         ▼
┌─────────────────────────────┐
│ Flask Route Handler         │
│ @app.route('/doctors_list') │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Business Logic:             │
│ 1. Get search query         │
│ 2. Call data_handler        │
│    .search_doctors(query)   │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Data Layer:                 │
│ 1. Read doctors.json        │
│ 2. Filter by query          │
│ 3. Read hospitals.json      │
│ 4. Join hospital data       │
│ 5. Read cities.json         │
│ 6. Join city data           │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Return enriched data to     │
│ render_template()           │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Jinja2 Template Engine      │
│ - doctors_list.html         │
│ - Loop through doctors      │
│ - Render HTML               │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Send HTML to Browser        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Client-Side JavaScript      │
│ - Instant search filtering  │
│ - Gender filter             │
│ - Experience filter         │
│ - No server calls needed    │
└─────────────────────────────┘
```

---

## 🔄 Real-Time Features

### **Dynamic Hospital Loading:**

```
User Flow:
1. User clicks city icon (e.g., "Bangalore")
                │
                ▼
2. JavaScript AJAX call
   fetch('/api/hospitals/city1')
                │
                ▼
3. Flask API endpoint
   @app.route('/api/hospitals/<city_id>')
   ├─→ Read hospitals.json
   └─→ Return JSON array
                │
                ▼
4. JavaScript receives data
   ├─→ Create HTML hospital cards
   ├─→ Insert into DOM
   └─→ Add click handlers
                │
                ▼
5. Display hospital cards with images
```

### **Instant Client-Side Filtering:**

```
Browse All Doctors Page:
┌─────────────────────────────┐
│ All 127 doctors loaded once │
└──────────┬──────────────────┘
           │
           ▼
User types in search / selects filter
           │
           ▼
┌─────────────────────────────┐
│ JavaScript filters DOM      │
│ - No server request         │
│ - Show/hide cards instantly │
│ - Update count in real-time │
└─────────────────────────────┘
```

---

## 🧪 Data Validation Rules

### **User Registration:**
- Email: Must be unique, valid format
- Password: Minimum length, hashed before storage
- Phone: Validated format

### **Appointment Booking:**
- Date: Must be future date
- Time: Must be available slot
- Doctor: Must exist in doctors.json
- User: Must be logged in

### **Payment:**
- Amount: Must match doctor's fees
- Method: Must be one of [upi, card, netbanking, Pay-at-Clinic]
- Validation: Based on payment method

---

## 📦 File Structure

```
doctorappointment/
│
├── app.py                    ← Main Flask application
│   ├── Routes (50+ endpoints)
│   ├── Authentication decorators
│   ├── Business logic
│   └── Session management
│
├── data_handler.py           ← Database abstraction layer
│   ├── DataHandler class
│   ├── CRUD operations
│   ├── Thread-safe operations
│   └── Search & filter methods
│
├── data/                     ← JSON database
│   ├── users.json           ← User accounts (dynamic)
│   ├── cities.json          ← 6 cities (static)
│   ├── hospitals.json       ← 15 hospitals (static)
│   ├── doctors.json         ← 127 doctors (static)
│   └── appointments.json    ← Bookings (dynamic)
│
├── templates/                ← Jinja2 HTML templates
│   ├── base.html            ← Base layout
│   ├── home.html            ← Landing page
│   ├── patient_dashboard.html
│   ├── find_doctor.html     ← Symptom checker
│   ├── doctors_list.html    ← Browse all
│   ├── doctor_detail.html   ← Doctor profile
│   ├── book_appointment.html← Booking form
│   ├── payment.html         ← Payment page
│   ├── my_appointments.html ← User bookings
│   ├── admin_dashboard.html ← Admin panel
│   └── ... (20+ templates)
│
└── static/
    ├── css/
    │   └── style.css        ← Global styles
    └── images/
        └── doctors/         ← Fallback images
```

---

## ⚡ Performance Optimizations

1. **Lazy Loading:** Images load only when visible
2. **Client-Side Filtering:** No server calls for filters
3. **Data Caching:** Lookup dictionaries for joins
4. **Minimal Animations:** Fast transitions (0.15s-0.2s)
5. **Denormalized Data:** Appointment has doctor_name, hospital_name (no joins needed)

---

## 🔮 Scalability Considerations

### **Current Capacity:**
- ✅ Up to 1,000 concurrent users
- ✅ 10,000+ appointments
- ✅ Thread-safe booking prevents conflicts

### **Migration to SQL (Future):**
```sql
-- PostgreSQL / MySQL Schema

CREATE TABLE cities (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    state VARCHAR(100)
);

CREATE TABLE hospitals (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    city_id VARCHAR(50) REFERENCES cities(id),
    address TEXT,
    phone VARCHAR(20),
    specialties JSONB
);

CREATE TABLE doctors (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    specialization VARCHAR(100),
    hospital_id VARCHAR(50) REFERENCES hospitals(id),
    fees DECIMAL(10,2),
    image_url TEXT,
    -- ... other fields
);

CREATE TABLE users (
    id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20),
    -- ... other fields
);

CREATE TABLE appointments (
    id UUID PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(id),
    doctor_id VARCHAR(50) REFERENCES doctors(id),
    hospital_id VARCHAR(50) REFERENCES hospitals(id),
    date DATE NOT NULL,
    time TIME NOT NULL,
    status VARCHAR(50),
    payment_status VARCHAR(50),
    -- ... other fields
    UNIQUE(doctor_id, date, time) -- Prevents double booking at DB level
);

CREATE INDEX idx_appointments_user ON appointments(user_id);
CREATE INDEX idx_appointments_doctor ON appointments(doctor_id);
CREATE INDEX idx_appointments_date ON appointments(date);
```

---

## 🎯 Summary

**Architecture Type:** MVC (Model-View-Controller) with JSON storage

**Components:**
- **Model:** DataHandler (data_handler.py) + JSON files
- **View:** Jinja2 Templates (templates/)
- **Controller:** Flask Routes (app.py)

**Key Features:**
- ✅ Relational data model (5 entities)
- ✅ Thread-safe concurrent booking
- ✅ Real-time filtering (client-side)
- ✅ Role-based access control
- ✅ Atomic operations with locks
- ✅ Cross-platform compatible
- ✅ RESTful API design

**Data Flow:** Linear and predictable
**Scalability:** Ready for SQL migration
**Security:** Hashed passwords, session-based auth

---

*Generated for HealthCarePlus Doctor Appointment System*


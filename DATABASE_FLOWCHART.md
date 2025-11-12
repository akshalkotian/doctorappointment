# 🏥 HealthCarePlus - Database & System Flowchart

## 📊 Database Architecture Overview

This system uses **JSON-based file storage** with 5 main data entities.

---

## 🗄️ Database Schema

### 1. **Users (users.json)**
```
┌─────────────────────┐
│      USERS          │
├─────────────────────┤
│ id (PK)             │ → Unique user identifier
│ name                │ → Full name
│ email (UNIQUE)      │ → Email (login credential)
│ password (hashed)   │ → Hashed password
│ phone               │ → Phone number
│ role                │ → 'patient' or 'admin'
│ created_at          │ → Registration timestamp
└─────────────────────┘
```

### 2. **Cities (cities.json)**
```
┌─────────────────────┐
│      CITIES         │
├─────────────────────┤
│ id (PK)             │ → Unique city identifier
│ name                │ → City name (e.g., "Bangalore")
│ state               │ → State name (e.g., "Karnataka")
└─────────────────────┘
```

### 3. **Hospitals (hospitals.json)**
```
┌─────────────────────┐
│    HOSPITALS        │
├─────────────────────┤
│ id (PK)             │ → Unique hospital identifier
│ name                │ → Hospital name
│ city_id (FK)        │ → References CITIES.id
│ address             │ → Full address
│ phone               │ → Contact number
│ specialties []      │ → Array of specializations
└─────────────────────┘
           │
           ├─── BELONGS TO ───→ CITIES
```

### 4. **Doctors (doctors.json)**
```
┌─────────────────────┐
│     DOCTORS         │
├─────────────────────┤
│ id (PK)             │ → Unique doctor identifier
│ name                │ → Doctor name (with Dr. prefix)
│ specialization      │ → Medical specialty
│ department          │ → Department name
│ qualification       │ → Degrees (MBBS, MD, etc.)
│ experience          │ → Years of experience
│ fees                │ → Consultation fee (₹)
│ hospital_id (FK)    │ → References HOSPITALS.id
│ email               │ → Contact email
│ phone               │ → Contact number
│ image (URL)         │ → Profile image URL
│ about               │ → Description/bio
└─────────────────────┘
           │
           ├─── WORKS AT ───→ HOSPITALS
```

### 5. **Appointments (appointments.json)**
```
┌─────────────────────────────┐
│       APPOINTMENTS          │
├─────────────────────────────┤
│ id (PK)                     │ → Unique appointment ID (UUID)
│ user_email (FK)             │ → References USERS.email
│ user_name                   │ → Patient name (denormalized)
│ doctor_id (FK)              │ → References DOCTORS.id
│ doctor_name                 │ → Doctor name (denormalized)
│ hospital_id (FK)            │ → References HOSPITALS.id
│ hospital_name               │ → Hospital name (denormalized)
│ city_id (FK)                │ → References CITIES.id
│ city_name                   │ → City name (denormalized)
│ date                        │ → Appointment date (YYYY-MM-DD)
│ time                        │ → Appointment time (HH:MM AM/PM)
│ reason                      │ → Reason for visit
│ status                      │ → 'confirmed', 'cancelled', 'no_show', 'pending_payment'
│ payment_status              │ → 'Success', 'Pending', 'Failed', 'Refunded'
│ payment_method              │ → 'upi', 'card', 'netbanking', 'Pay-at-Clinic'
│ booked_at                   │ → Booking timestamp
│ cancelled_at (optional)     │ → Cancellation timestamp
│ no_show_at (optional)       │ → No-show timestamp
│ refunded_at (optional)      │ → Refund timestamp
└─────────────────────────────┘
           │
           ├─── BOOKED BY ───→ USERS
           ├─── FOR DOCTOR ──→ DOCTORS
           ├─── AT HOSPITAL ─→ HOSPITALS
           └─── IN CITY ─────→ CITIES
```

---

## 🔄 Entity Relationships

```
┌──────────┐
│  CITIES  │
└────┬─────┘
     │ 1
     │ has many
     │ n
┌────▼─────────┐
│  HOSPITALS   │
└────┬─────────┘
     │ 1
     │ employs many
     │ n
┌────▼─────────┐
│   DOCTORS    │
└────┬─────────┘
     │ 1
     │ has many
     │ n
┌────▼──────────────┐         ┌──────────┐
│   APPOINTMENTS    │◄────────┤  USERS   │
└───────────────────┘  books  └──────────┘
         many                      1
```

**Key Relationships:**
- 1 City → Many Hospitals
- 1 Hospital → Many Doctors
- 1 Doctor → Many Appointments
- 1 User → Many Appointments

---

## 🔀 System Flow Diagram

### **User Journey Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER WORKFLOW                             │
└─────────────────────────────────────────────────────────────────┘

1. REGISTRATION/LOGIN
   ┌──────────┐
   │  START   │
   └────┬─────┘
        │
   ┌────▼──────────┐
   │ Register/Login│
   │  (users.json) │
   └────┬──────────┘
        │
        ├─── Patient ──→ Patient Dashboard
        └─── Admin ───→ Admin Dashboard


2. PATIENT BOOKING FLOW
   ┌────────────────┐
   │ Patient Login  │
   └────┬───────────┘
        │
   ┌────▼────────────────────┐
   │ Home / Patient Dashboard│
   └────┬────────────────────┘
        │
        ├───→ Option A: Browse by Location
        │     ┌────▼──────────┐
        │     │ Select City   │ (cities.json)
        │     └────┬──────────┘
        │          │
        │     ┌────▼──────────┐
        │     │Select Hospital│ (hospitals.json)
        │     └────┬──────────┘
        │          │
        │          └───────────┐
        │                      │
        ├───→ Option B: Search by Symptoms
        │     ┌────▼──────────┐
        │     │ Find My Doctor│
        │     │  (AI Match)   │
        │     └────┬──────────┘
        │          │
        │          └───────────┐
        │                      │
        └───→ Option C: Browse All
              ┌────▼──────────┐
              │  Browse All   │
              │   Doctors     │
              └────┬──────────┘
                   │
   ┌───────────────┴──────────────┐
   │                              │
   ▼                              ▼
┌─────────────┐           ┌──────────────┐
│View Doctors │           │ Apply Filters│
│(doctors.json)           │ (gender, exp)│
└────┬────────┘           └──────┬───────┘
     │                           │
     └──────────┬────────────────┘
                │
   ┌────────────▼──────────────┐
   │   Select Doctor Profile   │
   └────────────┬──────────────┘
                │
   ┌────────────▼──────────────┐
   │   📅 Book Appointment      │
   │   - Select Date (Calendar) │
   │   - Select Time Slot       │
   │   - Enter Reason           │
   └────────────┬──────────────┘
                │
   ┌────────────▼──────────────┐
   │   💳 Payment Page          │
   │   - Select Method (UPI/    │
   │     Card/NetBanking)       │
   │   - Enter Details          │
   └────────────┬──────────────┘
                │
   ┌────────────▼──────────────┐
   │  Process Payment           │
   │  (Random Success/Fail)     │
   └────────────┬──────────────┘
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
   ┌─────────┐     ┌──────────┐
   │ SUCCESS │     │  FAILED  │
   └────┬────┘     └────┬─────┘
        │               │
        │               └──→ Retry Payment
        │
   ┌────▼──────────────────────┐
   │ Appointment Confirmed     │
   │ (appointments.json)        │
   └────┬──────────────────────┘
        │
   ┌────▼──────────────────────┐
   │  View/Manage Appointment   │
   │  - View Details            │
   │  - Reschedule              │
   │  - Cancel (Get Refund)     │
   └───────────────────────────┘


3. ADMIN FLOW
   ┌────────────────┐
   │  Admin Login   │
   └────┬───────────┘
        │
   ┌────▼──────────────────┐
   │  Admin Dashboard      │
   │  - View All Bookings  │
   │  - Filter by:         │
   │    * Doctor           │
   │    * Date             │
   │    * Payment Status   │
   └────┬──────────────────┘
        │
        ├───→ View Statistics
        │     - Total Doctors
        │     - Total Bookings
        │     - Pending Payments
        │     - Hospital Stats
        │
        └───→ Manage Appointments
              - Cancel Appointment
              - Mark No Show
              - Process Refund
              - Mark Paid (Pay-at-Clinic)
```

---

## 🔐 Data Access Patterns

### **Read Operations:**
```
GET /                        → Read: cities, hospitals
GET /patient/dashboard       → Read: cities, appointments (user-specific)
GET /find_doctor             → Read: cities, doctors, hospitals
GET /doctors_list            → Read: doctors, hospitals, cities
GET /hospital/:id/doctors    → Read: doctors (by hospital)
GET /doctor/:id              → Read: doctor, hospital, city
GET /book_appointment/:id    → Read: doctor, booked_slots
GET /my_appointments         → Read: appointments (user-specific)
GET /admin/dashboard         → Read: appointments, doctors, hospitals, cities
```

### **Write Operations:**
```
POST /register               → Write: users.json
POST /book_appointment       → Write: appointments.json (atomic with lock)
POST /cancel_appointment     → Update: appointments.json (status + cancelled_at)
POST /process_payment        → Update: appointments.json (payment_status)
POST /admin/cancel           → Update: appointments.json (cancel)
POST /admin/mark_no_show     → Update: appointments.json (no_show)
POST /admin/refund           → Update: appointments.json (refund)
POST /admin/mark_paid        → Update: appointments.json (mark paid)
```

---

## 🔒 Concurrency Control

### **Thread-Safe Operations:**

```python
class DataHandler:
    def __init__(self):
        self.lock = threading.Lock()  # Thread lock for atomic operations
    
    def atomic_book_slot(self, doctor_id, date, time, appointment_data):
        """
        Prevents double-booking with thread lock
        """
        with self.lock:
            # 1. Check if slot is available
            # 2. If available, book immediately
            # 3. Return success/failure
```

**Protected Operations:**
- ✅ `atomic_book_slot()` - Prevents race conditions
- ✅ `update_appointment()` - Thread-safe updates
- ✅ `cancel_appointment()` - Thread-safe cancellation

---

## 📈 Data Flow: Booking Appointment

```
┌──────────────────────────────────────────────────────────────────┐
│                  APPOINTMENT BOOKING FLOW                         │
└──────────────────────────────────────────────────────────────────┘

Step 1: User Selection
┌────────────────┐
│ User chooses   │
│ City → Hospital│──→ Filters doctors.json by hospital_id
│ → Doctor       │
└────┬───────────┘
     │
     ▼
┌────────────────────────────────┐
│ Display Doctor Profile         │
│ - Read from doctors.json       │
│ - Lookup hospital (join)       │
│ - Lookup city (join)           │
└────┬───────────────────────────┘
     │
     ▼
Step 2: Slot Selection
┌────────────────────────────────┐
│ Check Available Slots          │
│ - Read appointments.json       │
│ - Filter by doctor_id          │
│ - Check booked slots           │
│ - Generate available slots     │
└────┬───────────────────────────┘
     │
     ▼
┌────────────────────────────────┐
│ User Selects Date & Time       │
└────┬───────────────────────────┘
     │
     ▼
Step 3: Confirmation
┌────────────────────────────────┐
│ Submit Booking Form            │
│ - Validate inputs              │
│ - Check slot still available   │
└────┬───────────────────────────┘
     │
     ▼
┌────────────────────────────────┐
│ ⚠️  CRITICAL: Atomic Check     │
│                                │
│ WITH LOCK:                     │
│  1. Re-check slot availability │
│  2. If available → Book        │
│  3. If taken → Show error      │
│                                │
│ WRITE to appointments.json     │
└────┬───────────────────────────┘
     │
     ▼
Step 4: Payment
┌────────────────────────────────┐
│ Payment Page                   │
│ - Select method (UPI/Card/NB)  │
│ - Enter payment details        │
└────┬───────────────────────────┘
     │
     ▼
┌────────────────────────────────┐
│ Process Payment                │
│ - Simulate payment (80% success│
│ - UPDATE appointments.json     │
│   * payment_status → Success   │
│   * status → confirmed         │
└────┬───────────────────────────┘
     │
     ├──→ Success: Confirmation page
     └──→ Failed: Retry option
```

---

## 🔍 Filter Operations (Admin Dashboard)

```
┌─────────────────────────────────────────────────┐
│          ADMIN DASHBOARD FILTERS                │
└─────────────────────────────────────────────────┘

INPUT: Filter Parameters
├─ doctor_id (optional)
├─ date (optional)
└─ payment_status (optional)

PROCESS:
1. Read ALL appointments.json
2. Enrich with doctor/hospital names
   ┌─────────────────────────────┐
   │ FOR each appointment:       │
   │  - Lookup doctor_name       │
   │    from doctors_dict[id]    │
   │  - Lookup hospital_name     │
   │    from hospitals_dict[id]  │
   └─────────────────────────────┘

3. Apply Filters (Sequential)
   ┌─────────────────────────────┐
   │ IF doctor_filter:           │
   │   SKIP if doctor_id != filter
   │                             │
   │ IF date_filter:             │
   │   SKIP if date != filter    │
   │                             │
   │ IF payment_status_filter:   │
   │   SKIP if status != filter  │
   └─────────────────────────────┘

4. Add Time Status
   ┌─────────────────────────────┐
   │ Calculate time_status:      │
   │  - upcoming (future)        │
   │  - completed (past)         │
   │  - missed (past no-show)    │
   │  - cancelled                │
   └─────────────────────────────┘

5. Sort by date (recent first)

OUTPUT: Filtered & Enriched Appointments
```

---

## 📊 Database Relationships Diagram

```
                    ┌─────────────────┐
                    │     CITIES      │
                    │  (6 cities)     │
                    └────────┬────────┘
                             │
                             │ 1:N (city_id)
                             │
                    ┌────────▼────────┐
                    │   HOSPITALS     │
                    │  (15 hospitals) │
                    └────────┬────────┘
                             │
                             │ 1:N (hospital_id)
                             │
                    ┌────────▼────────┐
                    │    DOCTORS      │
                    │  (127 doctors)  │
                    └────────┬────────┘
                             │
                             │ 1:N (doctor_id)
                             │
         ┌───────────────────┴───────────────────┐
         │                                       │
┌────────▼────────┐                   ┌─────────▼────────┐
│  APPOINTMENTS   │                   │     USERS        │
│  (N records)    │◄──────────────────┤  (N patients)    │
└─────────────────┘   1:N (user_email)└──────────────────┘
```

---

## 🎯 Key Operations & Their Data Access

### **1. Book Appointment (Atomic Operation)**
```
┌─────────────────────────────────────────┐
│ atomic_book_slot(doctor_id, date, time) │
└─────────────────────────────────────────┘
         │
    ┌────▼────┐
    │  LOCK   │ ← threading.Lock()
    └────┬────┘
         │
    ┌────▼──────────────────────────────┐
    │ 1. Read appointments.json         │
    │ 2. Check if slot is booked        │
    │    (doctor_id + date + time)      │
    │ 3. If available:                  │
    │    - Append new appointment       │
    │    - Write to appointments.json   │
    │    - Return success               │
    │ 4. If booked:                     │
    │    - Return error                 │
    └───────────────────────────────────┘
         │
    ┌────▼────┐
    │ UNLOCK  │
    └─────────┘
```

### **2. Search Doctors**
```
Input: search_query (name/specialization)
  │
  ├─→ Read doctors.json
  │
  ├─→ Filter:
  │   WHERE name CONTAINS query
  │   OR specialization CONTAINS query
  │
  ├─→ Join with hospitals.json (hospital_id)
  │
  └─→ Join with cities.json (city_id)
      
Output: Enriched doctor list with hospital & city info
```

### **3. Get Hospitals by City**
```
Input: city_id
  │
  ├─→ Read hospitals.json
  │
  └─→ Filter: WHERE city_id = input
      
Output: List of hospitals in that city
API: GET /api/hospitals/{city_id}
```

---

## 📁 File Storage Structure

```
doctorappointment/
├── data/
│   ├── users.json          ← User accounts
│   ├── cities.json         ← City master data (6 cities)
│   ├── hospitals.json      ← Hospital master data (15 hospitals)
│   ├── doctors.json        ← Doctor profiles (127 doctors)
│   └── appointments.json   ← All bookings (dynamic)
│
├── data_handler.py         ← All database operations
└── app.py                  ← Routes & business logic
```

---

## 🚀 API Endpoints & Data Operations

### **Public Routes:**
| Route | Method | Reads | Writes | Description |
|-------|--------|-------|--------|-------------|
| `/` | GET | cities, hospitals | - | Home page |
| `/register` | GET/POST | users | users.json | User registration |
| `/login` | GET/POST | users | - | User login |

### **Patient Routes:**
| Route | Method | Reads | Writes | Description |
|-------|--------|-------|--------|-------------|
| `/patient/dashboard` | GET | cities, appointments | - | Patient dashboard |
| `/find_doctor` | GET/POST | cities, doctors, hospitals | - | Symptom-based search |
| `/doctors_list` | GET | doctors, hospitals, cities | - | Browse all doctors |
| `/doctor/:id` | GET | doctor, hospital, city | - | Doctor profile |
| `/book_appointment/:id` | GET/POST | doctor, appointments | appointments.json | Book appointment |
| `/payment/:id` | GET/POST | appointment, doctor | appointments.json | Payment processing |
| `/my_appointments` | GET | appointments | - | User's bookings |
| `/cancel/:id` | POST | appointment | appointments.json | Cancel appointment |

### **Admin Routes:**
| Route | Method | Reads | Writes | Description |
|-------|--------|-------|--------|-------------|
| `/admin/dashboard` | GET | appointments, doctors, hospitals, cities | - | Admin overview with filters |
| `/admin/timetable` | GET | appointments, doctors | - | Timetable view |
| `/admin/cancel/:id` | POST | appointment | appointments.json | Admin cancel |
| `/admin/refund/:id` | POST | appointment | appointments.json | Process refund |
| `/admin/mark_paid/:id` | POST | appointment | appointments.json | Mark as paid |
| `/admin/no_show/:id` | POST | appointment | appointments.json | Mark no-show |

### **API Routes:**
| Route | Method | Reads | Description |
|-------|--------|-------|-------------|
| `/api/hospitals/:city_id` | GET | hospitals | Get hospitals by city (JSON) |

---

## 🎨 Frontend-Backend Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  FRONTEND ↔ BACKEND FLOW                    │
└─────────────────────────────────────────────────────────────┘

SCENARIO: User Books Appointment

1. User clicks "Book Appointment" on doctor profile
   Frontend: /doctor/doc1
   Backend:  Reads doctors.json → Returns doctor details
   
2. User sees booking form
   Frontend: /book_appointment/doc1
   Backend:  
     - Reads doctors.json
     - Reads appointments.json (check booked slots)
     - Calculates available slots
     - Returns booking page with available dates/times
   
3. User selects date & time
   Frontend: JavaScript validates selection
   Backend:  No call yet (client-side only)
   
4. User submits form
   Frontend: POST /book_appointment/doc1
   Backend:  
     - Validates inputs
     - Calls atomic_book_slot() with LOCK
     - IF successful:
       * Writes to appointments.json
       * Redirects to payment page
     - IF failed:
       * Returns error (slot taken)
   
5. User completes payment
   Frontend: POST /process_payment
   Backend:  
     - Simulates payment (80% success)
     - Updates appointments.json:
       * payment_status: "Success"
       * status: "confirmed"
     - Redirects to success/fail page
```

---

## 📋 Sample Data Records

### **Sample City:**
```json
{
    "id": "city1",
    "name": "Bangalore",
    "state": "Karnataka"
}
```

### **Sample Hospital:**
```json
{
    "id": "hosp1",
    "name": "Apollo Hospital",
    "city_id": "city1",
    "address": "154/11, Bannerghatta Road, Bangalore",
    "phone": "+91-80-2630-2630",
    "specialties": ["Cardiology", "Neurology", "Orthopedics"]
}
```

### **Sample Doctor:**
```json
{
    "id": "doc1",
    "name": "Dr. Rajesh Kumar",
    "specialization": "Cardiologist",
    "qualification": "MBBS, MD, DM (Cardiology)",
    "experience": "15 years",
    "fees": 800,
    "hospital_id": "hosp1",
    "image": "https://images.unsplash.com/photo-...",
    "about": "Expert in interventional cardiology"
}
```

### **Sample Appointment:**
```json
{
    "id": "a1107850-72ca-43a9-b837-1234567890ab",
    "user_email": "patient@example.com",
    "user_name": "John Doe",
    "doctor_id": "doc1",
    "doctor_name": "Dr. Rajesh Kumar",
    "hospital_id": "hosp1",
    "hospital_name": "Apollo Hospital",
    "date": "2025-11-25",
    "time": "10:00 AM",
    "reason": "Chest pain checkup",
    "status": "confirmed",
    "payment_status": "Success",
    "payment_method": "upi",
    "booked_at": "2025-11-12 14:30:00"
}
```

---

## 🔄 Status Flow Diagrams

### **Appointment Status Flow:**
```
┌──────────────┐
│ pending_     │ ← Initial state (before payment)
│ payment      │
└──────┬───────┘
       │
       ├──→ Payment Success
       │    ┌────▼──────┐
       │    │ confirmed │ ← Active appointment
       │    └────┬──────┘
       │         │
       │         ├──→ User cancels
       │         │    ┌────▼──────┐
       │         │    │ cancelled │ ← Refund processed
       │         │    └───────────┘
       │         │
       │         └──→ User doesn't show
       │              ┌────▼──────┐
       │              │ no_show   │ ← Marked by admin
       │              └───────────┘
       │
       └──→ Payment Failed
            ┌────▼──────┐
            │ Failed    │ ← Can retry payment
            └───────────┘
```

### **Payment Status Flow:**
```
┌─────────┐     Payment       ┌─────────┐
│ Pending │────Processing────→│ Success │
└────┬────┘                   └────┬────┘
     │                             │
     │                             └──→ Can be Refunded
     │                                  ┌────▼────┐
     │                                  │Refunded │
     │                                  └─────────┘
     └──→ Payment Failed
          ┌────▼────┐
          │ Failed  │
          └─────────┘
```

---

## 🛠️ Core Database Functions

### **DataHandler Class Methods:**

#### **User Operations:**
- `get_users()` → Read all users
- `get_user_by_email(email)` → Find user by email
- `add_user(user_data)` → Create new user

#### **Doctor Operations:**
- `get_doctors()` → Read all doctors
- `get_doctor_by_id(id)` → Find doctor by ID
- `search_doctors(query)` → Search by name/specialization
- `get_doctors_by_hospital(hospital_id)` → Doctors in specific hospital

#### **City Operations:**
- `get_cities()` → Read all cities
- `get_city_by_id(id)` → Find city by ID

#### **Hospital Operations:**
- `get_hospitals()` → Read all hospitals
- `get_hospital_by_id(id)` → Find hospital by ID
- `get_hospitals_by_city(city_id)` → Hospitals in specific city

#### **Appointment Operations:**
- `get_appointments()` → Read all appointments
- `get_appointments_by_user(email)` → User's appointments
- `get_appointments_by_doctor(doctor_id)` → Doctor's appointments
- `is_slot_booked(doctor_id, date, time)` → Check availability
- `atomic_book_slot(...)` → **Thread-safe booking** ⚡
- `get_appointment_by_id(id)` → Find appointment by ID
- `update_appointment(id, data)` → Update appointment
- `cancel_appointment(id)` → Cancel with timestamp
- `mark_no_show(id)` → Mark no-show
- `process_refund(id)` → Process refund
- `mark_payment_paid(id)` → Mark as paid

---

## 🔐 Security & Data Integrity

### **Password Security:**
```
User Registration/Login:
├─ Password hashing with werkzeug.security
├─ generate_password_hash() → Store hashed password
└─ check_password_hash() → Verify login
```

### **Session Management:**
```
Flask Session (server-side):
├─ user_id
├─ user_email
├─ user_name
└─ user_role (patient/admin)
```

### **Access Control:**
```
@login_required decorator:
  - Checks if session['user_id'] exists
  - Redirects to login if not authenticated

@admin_required decorator:
  - Checks if session['user_role'] == 'admin'
  - Returns 403 if not admin
```

---

## 📈 Statistics & Analytics

### **Admin Dashboard Stats:**
```
┌───────────────────────────────────┐
│       STATISTICS CALCULATED       │
├───────────────────────────────────┤
│ • Total Doctors                   │ ← len(doctors.json)
│ • Total Bookings                  │ ← len(appointments.json)
│ • Pending Payments                │ ← count where payment_status = "Pending"
│ • Successful Payments             │ ← count where payment_status = "Success"
│ • Confirmed Bookings              │ ← count where status = "confirmed"
│ • Cancelled Bookings              │ ← count where status = "cancelled"
│ • Doctors per Hospital            │ ← group by hospital_id
│ • Bookings per Hospital           │ ← group by hospital_id from appointments
│ • Bookings per Doctor             │ ← group by doctor_id
└───────────────────────────────────┘
```

---

## 🎨 Frontend Components Using Database

### **Dynamic Components:**
1. **City Selection** → Reads: `cities.json`
2. **Hospital Cards** → Reads: `hospitals.json` (filtered by city)
3. **Doctor Grid** → Reads: `doctors.json` (with joins)
4. **Appointment Calendar** → Reads: `appointments.json` (booked slots)
5. **My Appointments** → Reads: `appointments.json` (user-specific)
6. **Admin Dashboard** → Reads: ALL data files (with filters)

---

## 🔧 Cross-Platform Compatibility

### **OS Compatibility:**
✅ **Windows, Mac, Linux** compatible:
- Uses `os.path.join()` for paths (handles `/` and `\`)
- Uses `threading.Lock()` (works on all OS)
- Uses `os.makedirs()` (cross-platform)
- **Removed** `fcntl` (Unix-only) ← Fixed for Windows!

---

## 📊 Data Volumes

| Entity | Count | Notes |
|--------|-------|-------|
| Cities | 6 | Bangalore, Mumbai, Chennai, Hyderabad, Delhi, Udupi |
| Hospitals | 15 | Distributed across cities |
| Doctors | 127 | Assigned to hospitals |
| Users | Dynamic | Grows with registrations |
| Appointments | Dynamic | Grows with bookings |

---

## 🔮 Future Scalability

**Current:** JSON file-based storage
- ✅ Simple, no DB setup required
- ✅ Version control friendly
- ✅ Easy backup/restore
- ⚠️ Limited to low-medium traffic

**Migration Path to SQL Database:**
```
JSON Files                   SQL Database
─────────────────           ────────────────
users.json         →        users table
cities.json        →        cities table
hospitals.json     →        hospitals table
doctors.json       →        doctors table
appointments.json  →        appointments table

threading.Lock()   →        Database transactions
                            (ACID compliance)
```

---

## 📝 Summary

This is a **relational data model** implemented with JSON files:
- 5 main entities with clear relationships
- Thread-safe booking with locks
- Enriched data through joins
- Proper filtering and search
- Cross-platform compatible
- Ready for migration to SQL database

**Total Data Flow:** Users → Cities → Hospitals → Doctors → Appointments ✨


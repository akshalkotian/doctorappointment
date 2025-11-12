# 📚 HealthCarePlus - Quick Reference Guide

## 🗂️ Database Files Overview

| File | Records | Purpose | Relationships |
|------|---------|---------|---------------|
| **users.json** | Dynamic | Patient & Admin accounts | → Appointments (1:N) |
| **cities.json** | 6 | City master data | → Hospitals (1:N) |
| **hospitals.json** | 15 | Hospital information | → Cities (N:1), Doctors (1:N) |
| **doctors.json** | 127 | Doctor profiles | → Hospitals (N:1), Appointments (1:N) |
| **appointments.json** | Dynamic | Booking records | → Users, Doctors, Hospitals (N:1) |

---

## 🔑 Primary Keys & Foreign Keys

```
CITIES
  ├── id [PK]
  └── → hospitals.city_id [FK]

HOSPITALS
  ├── id [PK]
  ├── city_id [FK] → cities.id
  └── → doctors.hospital_id [FK]

DOCTORS
  ├── id [PK]
  ├── hospital_id [FK] → hospitals.id
  └── → appointments.doctor_id [FK]

USERS
  ├── id [PK]
  ├── email [UNIQUE]
  └── → appointments.user_email [FK]

APPOINTMENTS
  ├── id [PK] (UUID)
  ├── user_email [FK] → users.email
  ├── doctor_id [FK] → doctors.id
  ├── hospital_id [FK] → hospitals.id
  └── city_id [FK] → cities.id
```

---

## 🎯 Main User Flows (Quick)

### **Patient Flow:**
1. Register/Login → 2. Select City/Hospital → 3. Choose Doctor → 4. Book Slot → 5. Pay → 6. Confirmed

### **Admin Flow:**
1. Admin Login → 2. View Dashboard → 3. Filter Appointments → 4. Manage (Cancel/Refund/Mark Paid)

---

## 📊 Data Counts

- **Cities:** 6 (Bangalore, Mumbai, Chennai, Hyderabad, Delhi, Udupi)
- **Hospitals:** 15 (3 per major city, 5 in Udupi)
- **Doctors:** 127 (distributed across hospitals)
- **Time Slots:** 7 per day (09:00 AM - 05:00 PM)
- **Available Dates:** 14 days from today

---

## 🔐 User Roles

| Role | Access Level | Can Do |
|------|--------------|--------|
| **Patient** | User-level | Book, Cancel, View own appointments |
| **Admin** | Full access | View all, Cancel any, Refund, Mark paid/no-show |
| **Guest** | Public pages | View home, Register, Login |

---

## 💳 Payment Methods

1. **UPI** → Enter UPI ID
2. **Card** → Card number, Expiry, CVV
3. **Net Banking** → Select bank
4. **Pay-at-Clinic** → Pay later (admin marks paid)

---

## 🎨 UI Features by Page

### **Home Page:**
- ✅ City icon selection (6 cities)
- ✅ Hospital cards with images
- ✅ Popular specializations
- ✅ How it works section

### **Find Doctor Page:**
- ✅ Symptom-based AI search
- ✅ Quick symptom selection
- ✅ City/hospital filters
- ✅ Enhanced "How it works" UI

### **Browse All Page:**
- ✅ Instant search (real-time)
- ✅ Gender filter (Male/Female)
- ✅ Experience filter (0-5, 6-10, 11-15, 16-20, 20+)
- ✅ Lazy loading images
- ✅ Fast animations (0.15s)

### **Booking Page:**
- ✅ Calendar-style date selection
- ✅ Modern time slot cards
- ✅ Availability badges
- ✅ Step-by-step UI

### **Payment Page:**
- ✅ Separate sections for each method
- ✅ UPI → Only UPI fields
- ✅ Card → Only card fields
- ✅ NetBanking → Only bank dropdown

### **Admin Dashboard:**
- ✅ Statistics cards
- ✅ Filter by doctor/date/payment
- ✅ Clean table view (no images)
- ✅ Action buttons (cancel, refund, mark paid)

---

## 🚀 Key Functions Reference

### **DataHandler Methods:**

```python
# User
get_user_by_email(email)
add_user(user_data)

# Doctor
get_doctors()
get_doctor_by_id(id)
search_doctors(query)
get_doctors_by_hospital(hospital_id)

# Hospital
get_hospitals()
get_hospital_by_id(id)
get_hospitals_by_city(city_id)

# City
get_cities()
get_city_by_id(id)

# Appointment
get_appointments()
get_appointments_by_user(email)
get_appointments_by_doctor(doctor_id)
is_slot_booked(doctor_id, date, time)
atomic_book_slot(doctor_id, date, time, data)  ← THREAD-SAFE
update_appointment(id, data)
cancel_appointment(id)
mark_no_show(id)
process_refund(id)
mark_payment_paid(id)
```

---

## 🔄 Status Values

### **Appointment Status:**
- `pending_payment` → Before payment
- `confirmed` → Active appointment
- `cancelled` → User cancelled
- `no_show` → Patient didn't show up

### **Payment Status:**
- `Pending` → Awaiting payment
- `Success` → Paid successfully
- `Failed` → Payment failed
- `Refunded` → Money returned

### **Time Status (Calculated):**
- `upcoming` → Future appointment
- `completed` → Past appointment
- `missed` → Past + no_show
- `cancelled` → Cancelled appointment

---

## 🎨 Color Coding

| Status | Color | Badge |
|--------|-------|-------|
| Available | Green | `bg-success` |
| Filling Fast | Yellow | `bg-warning` |
| Booked | Red | `bg-danger` |
| Past/Full | Gray | `bg-secondary` |
| Confirmed | Blue | `bg-primary` |
| Refunded | Cyan | `bg-info` |

---

## 🔧 Configuration

### **Time Slots (Default):**
```python
time_slots = [
    "09:00 AM", "10:00 AM", "11:00 AM",
    "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"
]
```

### **Available Dates:**
- Next 14 days from today
- Calculated dynamically on each page load

### **Payment Simulation:**
- 80% success rate
- Random success/failure for testing

---

## 🔍 How to Debug

### **Check Appointments:**
```bash
python3 -c "import json; print(json.dumps(json.load(open('data/appointments.json')), indent=2))"
```

### **Count Doctors:**
```bash
python3 -c "import json; print(len(json.load(open('data/doctors.json'))))"
```

### **Verify Filter Logic:**
```bash
python3 -c "
import json
appts = json.load(open('data/appointments.json'))
doctor_id = 'doc1'
filtered = [a for a in appts if a.get('doctor_id') == doctor_id]
print(f'Doctor {doctor_id} has {len(filtered)} appointment(s)')
"
```

---

## 🎯 Quick Navigation Map

```
/ (Home)
├── /register → Register new user
├── /login → Patient login
├── /admin_login → Admin login
│
├── /patient/dashboard → Patient home
│   ├── /find_doctor → Symptom search
│   ├── /doctors_list → Browse all
│   ├── /hospital/:id/doctors → Doctors by hospital
│   ├── /doctor/:id → Doctor profile
│   ├── /book_appointment/:id → Book slot
│   ├── /payment/:id → Pay for booking
│   └── /my_appointments → View my bookings
│
└── /admin/dashboard → Admin panel
    ├── Apply filters (doctor/date/payment)
    └── Manage appointments (cancel/refund/mark)
```

---

## 🌐 AJAX/API Endpoints

| Endpoint | Returns | Used By |
|----------|---------|---------|
| `/api/hospitals/<city_id>` | JSON array of hospitals | City selection on home, patient dashboard |

---

## 💡 Pro Tips

1. **Thread Safety:** All booking operations use `atomic_book_slot()` with lock
2. **Data Enrichment:** Appointments are enriched with names at query time
3. **Denormalization:** Names are stored in appointments for fast display
4. **Client-Side Filtering:** Browse all page filters 127 doctors instantly
5. **No Database Setup:** Just run `python3 app.py` - JSON files are auto-created

---

## 🐛 Common Issues & Solutions

**Issue:** Filters not working
**Solution:** Check data enrichment in admin_dashboard() - names must be populated

**Issue:** Double booking
**Solution:** Use atomic_book_slot() - never use add_appointment() directly

**Issue:** Images not loading
**Solution:** All images are now URLs from Unsplash - no local files needed

**Issue:** Windows compatibility error
**Solution:** Removed fcntl import - now uses threading.Lock() (cross-platform)

---

*Quick Reference for HealthCarePlus - Doctor Appointment System*


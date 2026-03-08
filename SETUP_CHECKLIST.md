# EMSI ClassFlow Backend - Setup Checklist

Complete this checklist to get your backend running.

---

## ✅ Pre-Installation Checklist

- [ ] Python 3.8+ installed (`python --version`)
- [ ] pip installed (`pip --version`)
- [ ] PostgreSQL 12+ installed and running
- [ ] Git installed (optional, for version control)
- [ ] Text editor or IDE available (VS Code, PyCharm, etc.)

---

## 📥 Installation Checklist

### Step 1: Create Virtual Environment
- [ ] Navigate to project folder: `cd EmsiClassFlowBackEnd`
- [ ] Create venv: `python -m venv venv`
- [ ] Activate venv: `venv\Scripts\activate` (Windows)
  - Or: `source venv/bin/activate` (Mac/Linux)
- [ ] Verify activation: `(venv)` should appear in terminal

### Step 2: Install Dependencies
- [ ] Run: `pip install -r requirements.txt`
- [ ] Wait for completion (1-2 minutes)
- [ ] Verify: `pip list` should show installed packages

### Step 3: Setup PostgreSQL
- [ ] Open terminal/command prompt
- [ ] Login to PostgreSQL: `psql -U postgres`
- [ ] Create database: `CREATE DATABASE emsi_classflow;`
- [ ] Exit psql: `\q`
- [ ] Verify: Database created successfully

### Step 4: Configure Database Connection
- [ ] Open `app/database.py`
- [ ] Find line 6: `DATABASE_URL = "postgresql://..."`
- [ ] Update with your credentials:
  ```python
  DATABASE_URL = "postgresql://postgres:your_password@localhost:5432/emsi_classflow"
  ```
- [ ] Replace `your_password` with actual PostgreSQL password
- [ ] Save the file

---

## 🚀 Running the Backend

### Step 5: Start the Server
- [ ] Ensure virtual environment is activated: `(venv)` shows
- [ ] Navigate to project root
- [ ] Run: `uvicorn app.main:app --reload`
- [ ] Wait for message: "Uvicorn running on http://127.0.0.1:8000"

### Step 6: Verify It Works
- [ ] Open browser
- [ ] Visit: http://localhost:8000/health
- [ ] You should see: `{"status": "healthy", ...}`
- [ ] Visit: http://localhost:8000/docs
- [ ] Interactive API documentation should load

---

## 🧪 Testing Checklist

### API Documentation
- [ ] Visit http://localhost:8000/docs
- [ ] See Swagger UI interface
- [ ] See all 32+ endpoints listed
- [ ] Expand at least one endpoint

### Test a Room Creation
- [ ] In Swagger UI, find POST /rooms
- [ ] Click "Try it out"
- [ ] Enter test data:
  ```json
  {
    "name": "A101",
    "capacity": 30,
    "floor": 1,
    "type": "classroom"
  }
  ```
- [ ] Click "Execute"
- [ ] See response code 201
- [ ] See room created with ID

### Test Room Listing
- [ ] In Swagger UI, find GET /rooms
- [ ] Click "Try it out"
- [ ] Click "Execute"
- [ ] See response code 200
- [ ] See the room you created listed

### Test a Reservation
- [ ] Create a second room first
- [ ] Find POST /reservations
- [ ] Click "Try it out"
- [ ] Enter test data:
  ```json
  {
    "room_id": 1,
    "user_id": 123,
    "date": "2024-03-20",
    "start_time": "09:00:00",
    "end_time": "11:00:00",
    "purpose": "Team meeting"
  }
  ```
- [ ] Click "Execute"
- [ ] See status pending
- [ ] See response code 201

### Test Conflict Detection
- [ ] Try creating another reservation for same room/time:
  ```json
  {
    "room_id": 1,
    "user_id": 456,
    "date": "2024-03-20",
    "start_time": "10:00:00",
    "end_time": "12:00:00",
    "purpose": "Another meeting"
  }
  ```
- [ ] Should get 409 Conflict error
- [ ] Message: "Room is not available for the requested time slot"
- [ ] **✅ Conflict detection working!**

---

## 📖 Documentation Checklist

- [ ] Read START_HERE.md (2 minutes)
- [ ] Read QUICKSTART.md (5 minutes)
- [ ] Read README.md for full reference
- [ ] Bookmark API_EXAMPLES.md for endpoint details
- [ ] Review TECHNICAL_REFERENCE.md for architecture
- [ ] Skim DEPLOYMENT.md for future reference

---

## 🔍 Code Exploration Checklist

- [ ] Open `app/main.py` - See FastAPI setup
- [ ] Open `app/routers/rooms.py` - See endpoint examples
- [ ] Open `app/models/room.py` - See database model
- [ ] Open `app/schemas/room_schema.py` - See validation
- [ ] Open `app/routers/reservations.py` - See smart logic

---

## 🎯 Core Features Checklist

### Rooms
- [ ] Create a room
- [ ] List rooms
- [ ] Get specific room
- [ ] Delete room

### Reservations
- [ ] Create reservation (should be pending)
- [ ] List reservations
- [ ] Get reservation details
- [ ] Try double-booking (should fail with 409)
- [ ] Update reservation
- [ ] Approve reservation
- [ ] Reject reservation

### Exams
- [ ] Create exam
- [ ] Get student's exams
- [ ] List all exams

### Incidents
- [ ] Report incident
- [ ] List incidents
- [ ] Update incident
- [ ] Resolve incident

### Documents
- [ ] Request document
- [ ] Get student's requests
- [ ] Approve request
- [ ] Reject request

---

## ✨ Optional Enhancements Checklist

### When You're Comfortable:
- [ ] Read code comments in detail
- [ ] Customize error messages
- [ ] Modify database field lengths
- [ ] Add new endpoints following existing patterns
- [ ] Add request logging

### For Production:
- [ ] Read DEPLOYMENT.md completely
- [ ] Choose cloud platform (Render/Railway/AWS)
- [ ] Set up production database
- [ ] Configure environment variables
- [ ] Enable HTTPS
- [ ] Add authentication
- [ ] Set up monitoring
- [ ] Create automated tests

---

## 🐛 Troubleshooting Checklist

### If venv activation fails:
- [ ] Check Python is installed: `python --version`
- [ ] Try different activation: `venv\Scripts\activate.bat`
- [ ] Create new venv: `rm -r venv` then `python -m venv venv`

### If pip install fails:
- [ ] Upgrade pip: `python -m pip install --upgrade pip`
- [ ] Check internet connection
- [ ] Try: `pip install --upgrade -r requirements.txt`

### If PostgreSQL fails:
- [ ] Check PostgreSQL is running
- [ ] Verify connection: `psql -U postgres -c "SELECT 1"`
- [ ] Check password is correct
- [ ] Verify database exists: `psql -l`

### If server won't start:
- [ ] Check port 8000 is not in use
- [ ] Check DATABASE_URL is correct
- [ ] Check virtual environment is activated
- [ ] Check all imports work: `python -c "from app.main import app"`

### If endpoints return errors:
- [ ] Check database is running
- [ ] Check DATABASE_URL in app/database.py
- [ ] Check all models are imported in main.py
- [ ] Check recent error logs in terminal

---

## 📋 Final Verification

- [ ] Terminal shows "Uvicorn running on http://127.0.0.1:8000"
- [ ] http://localhost:8000/docs loads without errors
- [ ] http://localhost:8000/health returns healthy status
- [ ] Can create a room
- [ ] Can create a reservation
- [ ] Can view both in API docs
- [ ] Conflict detection works (209 when booking same time)
- [ ] All 32+ endpoints are visible in API docs

---

## ✅ Congratulations!

When all items are checked, your backend is:

✅ Installed
✅ Configured
✅ Running
✅ Tested
✅ Ready to develop

---

## 🚀 Next Steps

1. **Explore the API**: Use http://localhost:8000/docs
2. **Test endpoints**: Try examples from API_EXAMPLES.md
3. **Read the code**: Understand how it works
4. **Add features**: Follow existing patterns
5. **Deploy**: When ready, see DEPLOYMENT.md

---

## 📞 Still Need Help?

- **Setup issues**: Check QUICKSTART.md
- **API questions**: Check API_EXAMPLES.md
- **Technical details**: Check TECHNICAL_REFERENCE.md
- **Deployment help**: Check DEPLOYMENT.md
- **Navigation**: Check INDEX.md

---

**Status: Ready to Go! 🎉**

Your EMSI ClassFlow Backend is installed, running, and ready for development.

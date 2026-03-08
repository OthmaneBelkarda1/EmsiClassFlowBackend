# EMSI ClassFlow Backend - Technical Reference

## Database Schema

### Entity Relationship Diagram (ERD)

```
┌─────────────────┐
│     ROOMS       │
├─────────────────┤
│ id (PK)         │
│ name (UNIQUE)   │◄─┐
│ capacity        │  │
│ floor           │  │ FK
│ type (ENUM)     │  │
└─────────────────┘  │
                     │
     ┌───────────────┴─────────────┐
     │                             │
┌────┴──────────────┐   ┌─────────┴────────┐
│  RESERVATIONS     │   │      EXAMS       │
├─────────────────┤   ├──────────────────┤
│ id (PK)         │   │ id (PK)          │
│ room_id (FK)    │   │ room_id (FK)     │
│ user_id         │   │ subject          │
│ date            │   │ date             │
│ start_time      │   │ time             │
│ end_time        │   │ student_id       │
│ purpose         │   │ table_number     │
│ status (ENUM)   │   └──────────────────┘
│ created_at      │
└─────────────────┘
     
     ┌────────────────────┐   ┌─────────────────────┐
     │    INCIDENTS       │   │ DOCUMENT_REQUESTS   │
     ├────────────────────┤   ├─────────────────────┤
     │ id (PK)            │   │ id (PK)             │
     │ room_id (FK)     ◄─┼─ │ student_id          │
     │ reporter_id        │   │ document_type       │
     │ description        │   │ status (ENUM)       │
     │ equipment          │   │ created_at          │
     │ status (ENUM)      │   └─────────────────────┘
     │ created_at         │
     └────────────────────┘
```

---

## Table Specifications

### ROOMS Table
```sql
CREATE TABLE rooms (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    floor INTEGER NOT NULL CHECK (floor >= 0),
    type ENUM('classroom', 'lab', 'amphitheater') NOT NULL,
    INDEX idx_name (name)
);
```

**Constraints**:
- `name` must be unique (no two rooms with same identifier)
- `capacity` must be greater than 0
- `floor` must be non-negative integer
- `type` must be one of: classroom, lab, amphitheater

---

### RESERVATIONS Table
```sql
CREATE TABLE reservations (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    room_id INTEGER NOT NULL REFERENCES rooms(id),
    user_id INTEGER NOT NULL,
    date VARCHAR(10) NOT NULL,
    start_time VARCHAR(8) NOT NULL,
    end_time VARCHAR(8) NOT NULL,
    purpose VARCHAR(255) NOT NULL,
    status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_room_id (room_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);
```

**Constraints**:
- `room_id` must reference existing room
- `end_time` must be after `start_time`
- `status` default is 'pending'
- Time format: HH:MM:SS (24-hour)
- Date format: YYYY-MM-DD

---

### EXAMS Table
```sql
CREATE TABLE exams (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    subject VARCHAR(100) NOT NULL,
    room_id INTEGER NOT NULL REFERENCES rooms(id),
    date VARCHAR(10) NOT NULL,
    time VARCHAR(8) NOT NULL,
    student_id INTEGER NOT NULL,
    table_number INTEGER NOT NULL CHECK (table_number > 0),
    INDEX idx_subject (subject),
    INDEX idx_room_id (room_id),
    INDEX idx_student_id (student_id)
);
```

**Constraints**:
- `room_id` must reference existing room
- `table_number` must be positive integer
- Multiple exams can be scheduled in same room at different times

---

### INCIDENTS Table
```sql
CREATE TABLE incidents (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    room_id INTEGER NOT NULL REFERENCES rooms(id),
    reporter_id INTEGER NOT NULL,
    description VARCHAR(500) NOT NULL,
    equipment VARCHAR(100) NOT NULL,
    status ENUM('reported', 'analyzed', 'resolved') NOT NULL DEFAULT 'reported',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_room_id (room_id),
    INDEX idx_status (status)
);
```

**Constraints**:
- `room_id` must reference existing room
- `status` default is 'reported'
- Status workflow: reported → analyzed → resolved

---

### DOCUMENT_REQUESTS Table
```sql
CREATE TABLE document_requests (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    student_id INTEGER NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_id (student_id),
    INDEX idx_status (status)
);
```

**Constraints**:
- `status` default is 'pending'
- One student can have multiple requests
- Multiple requests for same document type allowed

---

## Business Logic Rules

### Reservation Rules
1. ✅ **Auto-Pending**: All new reservations are created with "pending" status
2. ✅ **Conflict Detection**: System prevents overlapping reservations for same room
   - Check if ANY time slot overlaps with existing pending/approved reservations
   - Return 409 Conflict error if overlap detected
3. ✅ **Time Validation**: End time must be after start time
4. ✅ **Update Restrictions**: Only pending reservations can be updated or deleted
5. ✅ **Status Flow**: pending → approved/rejected (one-way)
6. ✅ **Approval Workflow**: Only admin can approve/reject

### Room Availability Algorithm
```
For new reservation (room_id, date, start_time, end_time):
  1. Find all reservations for same room on same date
  2. Filter to only PENDING and APPROVED status
  3. Check for time overlap:
     - If any: (new_start < existing_end) AND (new_end > existing_start)
     - Then: REJECT with "Room is not available"
  4. Else: ACCEPT the reservation
```

### Incident Rules
1. ✅ **Auto-Reported**: All new incidents created with "reported" status
2. ✅ **Status Workflow**: reported → analyzed → resolved (one-way)
3. ✅ **Resolution**: Incident can be marked as resolved by admin
4. ✅ **AI Processing**: Incidents are stored for later AI analysis

### Document Request Rules
1. ✅ **Auto-Pending**: All new requests created with "pending" status
2. ✅ **Update Restrictions**: Only pending requests can be updated
3. ✅ **Delete Restrictions**: Only pending requests can be deleted
4. ✅ **Approval**: Admin can approve or reject
5. ✅ **Status Flow**: pending → approved/rejected (one-way)

### Room Deletion Rules
1. ✅ **Active Reservations Check**: Cannot delete room with pending/approved reservations
2. ✅ **Cascade**: Deleting room does NOT cascade delete reservations (explicit check prevents this)

---

## API Response Codes

### Success Responses
- **200 OK**: Successful GET, PUT request
- **201 Created**: Successful POST request
- **204 No Content**: Successful DELETE request

### Client Error Responses
- **400 Bad Request**:
  - Invalid input data
  - Attempting to update non-pending reservation
  - Attempting to approve non-pending request
  - Invalid status code
  
- **404 Not Found**:
  - Resource doesn't exist
  - Foreign key reference missing (e.g., room doesn't exist)
  
- **409 Conflict**:
  - Room not available for time slot
  - Cannot delete room with active reservations
  - Incident already resolved
  - Status transition not allowed

### Server Error Responses
- **500 Internal Server Error**: Unhandled exceptions

---

## Validation Rules

### Date/Time Validation
- **Date Format**: `YYYY-MM-DD` (ISO 8601)
- **Time Format**: `HH:MM:SS` (24-hour)
- **End Time**: Must be strictly after start time
- **Date Range**: No past date restrictions (can set future exams/reservations)

### String Validation
- **Room Name**: 1-100 characters, must be unique
- **Purpose**: 1-255 characters
- **Description**: 1-500 characters
- **Equipment**: 1-100 characters
- **Document Type**: 1-100 characters
- **Subject**: 1-100 characters

### Numeric Validation
- **Capacity**: Must be > 0
- **Floor**: Must be >= 0
- **User ID**: Must be > 0
- **Student ID**: Must be > 0
- **Reporter ID**: Must be > 0
- **Table Number**: Must be > 0

### Enum Validation
**Room Type**:
- `classroom`
- `lab`
- `amphitheater`

**Reservation Status**:
- `pending`
- `approved`
- `rejected`

**Incident Status**:
- `reported`
- `analyzed`
- `resolved`

**Document Status**:
- `pending`
- `approved`
- `rejected`

---

## Performance Considerations

### Index Strategy
1. Primary keys on all tables
2. Foreign keys indexed for joins
3. `status` fields indexed for filtering
4. Search fields indexed (name, subject, etc.)
5. `user_id`, `student_id`, `room_id` indexed

### Query Optimization
1. Room availability check uses indexed queries
2. Filter queries on status use indexes
3. Connection pooling enabled
4. `pool_pre_ping=True` to test connections

### Potential Bottlenecks
- High-frequency availability checks (mitigate with caching if needed)
- Large result sets (add pagination if needed)
- Multiple joins (use select_in_load for relationships if needed)

---

## Authentication & Security (To Be Implemented)

This backend does NOT include authentication. Implementation notes for future developer:

1. **JWT Tokens**:
   - Add `/auth/login` endpoint
   - Validate tokens in dependency injector
   - Add `user_id` extraction from token

2. **Role-Based Access**:
   - Admin role for approval endpoints
   - Student role for own requests
   - Add role check in routers

3. **SQL Injection**: Already protected by SQLAlchemy ORM

4. **CORS**: Currently allows all origins - restrict in production

5. **Rate Limiting**: Consider adding rate limiting middleware

6. **HTTPS**: Use in production deployment

---

## Deployment Checklist

- [ ] Change `echo=False` database logging
- [ ] Update CORS origins
- [ ] Move DATABASE_URL to environment variable
- [ ] Set `reload=False` in production
- [ ] Enable HTTPS
- [ ] Add authentication
- [ ] Add rate limiting
- [ ] Set up database backups
- [ ] Add monitoring/logging
- [ ] Create database migrations with Alembic
- [ ] Add API key management
- [ ] Set up CI/CD pipeline

---

## File Dependencies

```
main.py
├── database.py (DB config)
├── models/
│   ├── room.py
│   ├── reservation.py
│   ├── exam.py
│   ├── incident.py
│   └── document_request.py
├── schemas/
│   └── All schema files
└── routers/
    ├── rooms.py
    ├── reservations.py
    ├── admin.py
    ├── exams.py
    ├── incidents.py
    └── documents.py
```

Each router is independent and can be modified without affecting others (loose coupling).

---

## Code Principles Applied

1. **DRY (Don't Repeat Yourself)**:
   - Shared availability check function
   - Reusable database get_db() dependency

2. **SOLID Principles**:
   - Single Responsibility: Each router handles one domain
   - Open/Closed: Easy to add new routers
   - Liskov Substitution: Standard Pydantic bases
   - Interface Segregation: Specific schemas per endpoint
   - Dependency Inversion: Database dependency injection

3. **Clean Code**:
   - Clear naming conventions
   - Comprehensive docstrings
   - Type hints throughout
   - Proper error messages

4. **RESTful Design**:
   - Standard HTTP methods
   - Proper status codes
   - Resource-based URLs
   - JSON request/response

---

## Testing Strategy (To Be Implemented)

```python
# Example test structure
def test_create_room():
    # Arrange
    room_data = {...}
    
    # Act
    response = client.post("/rooms", json=room_data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["name"] == "A101"

def test_reservation_conflict():
    # Test that overlapping reservations are rejected
    
def test_admin_approval():
    # Test that only admin can approve
```

---

## PostgreSQL Setup Commands

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE emsi_classflow;

# Connect to database
\c emsi_classflow

# View tables
\dt

# Drop database (if needed)
DROP DATABASE emsi_classflow;
```

---

## Useful SQL Queries

```sql
-- Find all pending reservations for a room
SELECT * FROM reservations 
WHERE room_id = 1 AND status = 'pending';

-- Find all exams for a student
SELECT * FROM exams WHERE student_id = 456;

-- Find unresolved incidents
SELECT * FROM incidents WHERE status != 'resolved';

-- Count rooms by type
SELECT type, COUNT(*) FROM rooms GROUP BY type;

-- Find double-booked rooms
SELECT r1.room_id, COUNT(*) FROM reservations r1
GROUP BY r1.room_id, r1.date
HAVING COUNT(*) > 1;
```

---

## Environment Variables Reference

```env
# Required
DATABASE_URL=postgresql://user:password@localhost:5432/emsi_classflow

# Optional
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

This technical reference covers all aspects of the EMSI ClassFlow backend architecture, database design, and business logic.

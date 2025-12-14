# Pot Your Progress

A habit tracking application where users can create habits (represented as plants) and track their progress by "watering" them. Plants flourish when habits are maintained and wilt when neglected.

## Features

- User authentication (signup, login, password reset with OTP)
- Create, read, update, and delete habits
- Track habit completions (daily or weekly)
- Visual plant states (flourishing/wilting) based on habit completion
- Email reminders for habit tracking (displayed as popup notifications on the website)
- Completion history tracking

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: React with Vite
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Session-based with bcrypt password hashing
- **Email Service**: Resend
- **Scheduler**: APScheduler for automated tasks

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn
- Supabase account and project
- Resend account and API key (for email functionality)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd pot-your-progress-1
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
pip install flask flask-cors bcrypt supabase requests apscheduler resend
```

Or use pip to install from a requirements file if you prefer:
```bash
pip install -r requirements.txt
```

#### Configure Database

1. Create a Supabase project at https://supabase.com
2. Get your Supabase URL and API key
3. Update `backend/db.py` with your credentials:

```python
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-key"
```

#### Configure Email Service (Resend)

1. Sign up at https://resend.com
2. Get your Resend API key
3. Update `backend/email_service.py` with your API key:

```python
RESEND_API_KEY = "your-resend-api-key"
```

#### Database Schema

Create the following tables in your Supabase database:

**Users Table:**
```sql
CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  full_name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Habits Table:**
```sql
CREATE TABLE habits (
  habit_id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
  habit_name VARCHAR(255) NOT NULL,
  frequency VARCHAR(20) CHECK (frequency IN ('daily', 'weekly')) DEFAULT 'daily',
  plant_state VARCHAR(20) CHECK (plant_state IN ('flourishing', 'wilting')) DEFAULT 'flourishing',
  last_watered TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Habit Completions Table (Optional - for detailed tracking):**
```sql
CREATE TABLE habit_completions (
  completion_id SERIAL PRIMARY KEY,
  habit_id INTEGER REFERENCES habits(habit_id) ON DELETE CASCADE,
  user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
  completion_date DATE NOT NULL,
  completed_at TIMESTAMP DEFAULT NOW(),
  period_key VARCHAR(20) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### Run Backend Server

```bash
cd backend
python app.py
```

The backend server will run on `http://localhost:5000`

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Run Development Server

```bash
npm run dev
```

The frontend will run on `http://localhost:5173` (or 5174 if 5173 is in use)

### 4. Environment Configuration

Make sure your frontend API configuration matches your backend URL. Check `frontend/src/api.js`:

```javascript
const API = axios.create({
  baseURL: "http://localhost:5000",
  withCredentials: true,
});
```

## Project Structure

```
pot-your-progress-1/
├── backend/
│   ├── auth/
│   │   └── routes.py          # Authentication routes
│   ├── habits/
│   │   └── routes.py          # Habit management routes
│   ├── app.py                 # Flask application entry point
│   ├── db.py                  # Supabase database connection
│   ├── email_service.py       # Email service configuration
│   └── scheduler.py           # Background scheduler for plant states
├── frontend/
│   ├── src/
│   │   ├── pages/             # React components
│   │   ├── CSS/               # Stylesheets
│   │   ├── api.js             # API client configuration
│   │   └── App.jsx            # Main application component
│   └── package.json           # Frontend dependencies
└── README.md                  # This file
```

## API Documentation

See [API_Documentation.md](./API_Documentation.md) for detailed API endpoint documentation.

## Usage

1. **Sign Up**: Create a new account with email and password
2. **Login**: Authenticate with your credentials
3. **Create Habits**: Add new habits (plants) with a name and frequency (daily/weekly)
4. **Track Progress**: Click the water droplet to mark a habit as completed
5. **Monitor Plants**: Plants flourish when habits are maintained regularly and wilt when neglected
6. **Manage Habits**: Edit or delete habits as needed
7. **Set Reminders**: Configure reminders for your habits (displayed as popup notifications when plants are wilting)

## Dependencies

### Backend Dependencies
- `flask` - Web framework
- `flask-cors` - Cross-origin resource sharing support
- `bcrypt` - Password hashing
- `supabase` - Database client
- `requests` - HTTP library
- `apscheduler` - Task scheduler
- `resend` - Email service

### Frontend Dependencies
- `react` - UI library
- `react-dom` - React DOM renderer
- `react-router-dom` - Routing
- `axios` - HTTP client
- `vite` - Build tool and dev server

## Troubleshooting

### Backend Issues
- Ensure Python 3.8+ is installed
- Verify Supabase credentials are correct
- Check that all Python packages are installed
- Ensure port 5000 is not in use

### Frontend Issues
- Ensure Node.js 16+ is installed
- Delete `node_modules` and run `npm install` again if dependency issues occur
- Check that the backend server is running before starting frontend

### Database Issues
- Verify Supabase project is active
- Check table schema matches the provided SQL
- Ensure proper RLS (Row Level Security) policies if using Supabase authentication

### Email Issues
- Verify Resend API key is correct
- During testing, Resend may only allow emails to your registered email address
- Check Resend dashboard for email delivery status

## Email Service Limitations & Workaround

**Important Note**: Free versions of third-party email services (like Resend) do not allow sending scheduled emails without purchasing a domain. Additionally, during testing phases, these services typically only allow sending emails to the account owner's registered email address.

### Current Implementation

Due to these limitations, the application uses a hybrid approach:

1. **OTP Codes**: When users request a password reset, the system:
   - Attempts to send the OTP via Resend API (keeps the API integration active)
   - **Displays the OTP code in a popup on the website** (similar to error messages) if email sending fails or is restricted
   - This ensures users can always reset their passwords regardless of email service limitations

2. **Habit Reminders**: When the scheduler detects wilting plants:
   - Attempts to send reminder emails via Resend API (keeps the API integration active)
   - **Stores reminders in memory and displays them as popup notifications** on the website
   - Reminders appear automatically when users are logged into the dashboard
   - The scheduler runs on schedule (daily), and reminders are shown in popup format (similar to OTP popups)

3. **Test Reminder Email**: When clicking "Add Reminder" in the UI:
   - Still attempts to send a test email via Resend API
   - This allows testing the email integration when using a verified email address

### Why This Approach?

- **No Domain Purchase Required**: Works with free tier email services
- **Always Functional**: Users can always receive OTPs and reminders, even if email sending fails
- **API Integration Maintained**: The Resend API calls remain in place, so the system will automatically use email delivery once a domain is purchased and verified
- **Better User Experience**: Popup notifications are immediate and don't require checking email inboxes

### Future Enhancement

Once a domain is purchased and verified with Resend (or another email service), the system will automatically send emails instead of showing popups, as the API integration is already in place.

## Development & Testing Notes

### Time Travel Feature (Unlinked)

During initial development, a time travel feature was implemented for demo and testing purposes. This feature allowed fast-forwarding time by 20 hours to simulate habit wilting behavior without waiting for the actual time to pass.

**Status**: The time travel CLI tool (`backend/time_travel_cli.py`) exists in the codebase but is **not linked or integrated** into the main application. It was used during development and demos to quickly test the plant wilting functionality, but it is not accessible through the user interface and is not part of the production application.

**Note**: If you need to test wilting behavior during development, you can manually run the time travel CLI script from the command line, but this feature is not available to end users and is not connected to any frontend components or API endpoints.



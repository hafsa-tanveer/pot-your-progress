# Backend Unit Tests

This folder contains all unit tests for the backend application.

## Prerequisites

**Important**: Before running tests, make sure you have installed all backend dependencies:

```bash
cd backend
pip install flask flask-cors bcrypt supabase requests apscheduler resend
```

**You do NOT need to run `app.py` before running tests.** Unit tests are isolated and use mocks, so they don't require:
- The Flask server to be running
- A live database connection
- API keys
- External services

## Test Files

- `test_auth.py` - Tests for authentication routes (signup, login, logout, password reset)
- `test_habits.py` - Tests for habits routes and helper functions
- `test_email_service.py` - Tests for email service functions
- `test_scheduler.py` - Tests for scheduler functions
- `test_reminder_storage.py` - Tests for reminder storage functions
- `test_db.py` - Tests for database connection
- `test_app.py` - Tests for Flask app configuration

## How to Run Tests

### Run All Tests

From the `backend` directory:

```bash
python -m pytest tests/
```

Or using unittest:

```bash
python -m unittest discover tests -p "test_*.py" -v
```

Or using the test runner:

```bash
python tests/run_tests.py
```

### Run a Specific Test File

```bash
python -m unittest tests.test_auth -v
python -m unittest tests.test_habits -v
python -m unittest tests.test_email_service -v
# etc.
```

Or using the test runner:

```bash
python tests/run_tests.py auth
python tests/run_tests.py habits
python tests/run_tests.py email_service
# etc.
```

### Run a Specific Test Class or Method

```bash
python -m unittest tests.test_auth.TestAuthRoutes -v
python -m unittest tests.test_auth.TestAuthRoutes.test_signup_success -v
```

## Test Structure

All tests use `unittest.mock` to mock external dependencies like:
- Database connections (Supabase)
- Email services (Resend API)
- External API calls
- Scheduler startup (to prevent it from running during tests)

This means tests can run without requiring:
- A live database connection
- API keys
- External services
- The Flask server to be running

## Common Issues

### ModuleNotFoundError (e.g., "No module named 'flask'")

**Solution**: Install the backend dependencies first:
```bash
cd backend
pip install flask flask-cors bcrypt supabase requests apscheduler resend
```

### Scheduler Starting During Tests

If you see scheduler-related errors, the tests should automatically mock the scheduler startup. If issues persist, make sure you're not importing `app.py` directly in your tests - instead, import the blueprints and modules you need to test.

## Notes

- Tests are isolated and don't affect each other
- Each test file includes path manipulation to import backend modules correctly
- All tests follow the unittest.TestCase pattern
- Tests do NOT require `app.py` to be running

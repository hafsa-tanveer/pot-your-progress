import datetime

# Mock Constants
NUMBER = "NUMBER"
TIMESTAMP = "TIMESTAMP"
CURSOR = "CURSOR"

class DatabaseError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.args = (type('obj', (object,), {'code': code}),) if code else (message,)

# The "Database" (In-Memory List)
MOCK_HABITS = []
NEXT_ID = 1

class MockVar:
    def __init__(self, type_): self.value = None
    def getvalue(self): return self.value
    def setvalue(self, val): self.value = val

class MockCursor:
    def var(self, type_): return MockVar(type_)

    def callproc(self, name, args):
        global NEXT_ID
        
        if name == "create_habit":
            user_id, habit_name, schedule, out_var = args
            habit_id = NEXT_ID
            NEXT_ID += 1
            MOCK_HABITS.append({
                "id": habit_id,
                "user_id": user_id,
                "habit_name": habit_name,
                "schedule": schedule,
                "state": "flourishing",
                "last_watered": None
            })
            out_var.setvalue([habit_id])

        elif name == "track_habit": # Used for "Edit/Update" in this context
            # We treat 'tracking' as updating the habit for now
            plant_id, user_id, out_var = args
            habit = next((h for h in MOCK_HABITS if h["id"] == plant_id), None)
            if habit:
                now = datetime.datetime.now()
                habit["last_watered"] = now
                out_var.setvalue([now])
            else:
                raise DatabaseError("Habit not found", 20002)

        elif name == "delete_habit":
            plant_id, user_id = args
            initial_len = len(MOCK_HABITS)
            MOCK_HABITS[:] = [h for h in MOCK_HABITS if h["id"] != plant_id]
            if len(MOCK_HABITS) == initial_len:
                 raise DatabaseError("Habit not found", 20002)

        # Support for renaming if your edit popup sends it
        elif name == "update_habit_details":
            plant_id, user_id, new_name = args
            habit = next((h for h in MOCK_HABITS if h["id"] == plant_id), None)
            if habit:
                habit["habit_name"] = new_name

    def callfunc(self, name, return_type, args):
        if name == "get_user_habits":
            user_id = args[0]
            # Return list format: (id, name, schedule, state, last_watered)
            results = []
            for h in MOCK_HABITS:
                if h["user_id"] == user_id:
                    results.append([
                        h["id"], h["habit_name"], h["schedule"], h["state"], h["last_watered"]
                    ])
            return results
        return []

    def close(self): pass

class MockConnection:
    def cursor(self): return MockCursor()
    def commit(self): pass
    def close(self): pass

def get_db_connection(): return MockConnection()
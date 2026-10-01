import os
os.environ["DATABASE_URL"] = "sqlite:///./test_crime.db"
os.environ["SCHEDULER_ENABLED"] = "false"
os.environ["ADMIN_API_KEY"] = "test-key"

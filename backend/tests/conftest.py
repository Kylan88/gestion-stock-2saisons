import os

# Tests must never use the developer or production database.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

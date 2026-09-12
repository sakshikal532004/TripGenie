from sqlalchemy import text

from backend.database.database import engine


try:
    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT version();")
        )

        version = result.fetchone()

        print("PostgreSQL connection successful!")
        print(version[0])

except Exception as e:

    print("Database connection failed!")
    print(e)
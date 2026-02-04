"""
Database initialization script
Run this script to create the database tables and default users
"""
import pymysql
from app.core.config import settings


def init_database():
    """Initialize database with tables and default data"""
    try:
        # Connect to MySQL server
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            charset='utf8mb4'
        )
        cursor = connection.cursor()

        # Read and execute SQL script
        with open('database/init.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # Execute SQL script
        for statement in sql_script.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)

        connection.commit()
        print("Database initialized successfully!")
        print("\nDefault users created:")
        print("- Admin: username=admin, password=admin123")
        print("- User1: username=user1, password=user123")
        print("- User2: username=user2, password=user123")

    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    init_database()

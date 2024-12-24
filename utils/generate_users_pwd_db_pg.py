import pandas as pd
import bcrypt
from src.db_management.db_configurations import users_passwords_db_connection, advisors_passwords_db_connection, users_passwords_db_cursor, advisors_passwords_db_cursor


# Users passwords table creation function
def create_users_passwords_tables(table_name):
    try:
        users_passwords_db_cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            user_id VARCHAR(10) PRIMARY KEY,
            password VARCHAR(200) NOT NULL
        );
        """)
        users_passwords_db_connection.commit()
    except Exception as e:
        print(f"Error creating {table_name} table: {e}")


# Advisors passwords table creation function
def create_advisors_passwords_tables(table_name):
    try:
        advisors_passwords_db_cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                advisor_id VARCHAR(10) PRIMARY KEY,
                password VARCHAR(200) NOT NULL
            );
        """)
        advisors_passwords_db_connection.commit()
    except Exception as e:
        print(f"Error creating {table_name} table: {e}")


# Hash password function 
def hash_password(password):
    """Hash a single password using bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# Insert password into database function
def insert_password(row, table_name, db_connection_function, identifier):
    try:
        connection = db_connection_function
        cursor = connection.cursor()
        user_id, hashed_password = row
        insert_query = f"""
            INSERT INTO {table_name} ({identifier}, password)
            VALUES (%s, %s)
            ON CONFLICT ({identifier}) DO NOTHING
        """
        cursor.execute(insert_query, (user_id, hashed_password))
        connection.commit()
    except Exception as e:
        print(f"Insertion error for {user_id} : {e}")
    finally:
        cursor.close()
        connection.close()


# Insert hashed passwords function
def populate_passwords(csv_file, table_name, identifier, db_connection_function):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file, sep=";", header=0)
        
        # Get a single connection for the entire operation
        connection = db_connection_function
        cursor = connection.cursor()
        
        try:
            for index, row in df.iterrows():
                try:
                    # Hash the password
                    hashed_password = hash_password(row['password'])
                    
                    # Insert into database
                    insert_query = f"""
                        INSERT INTO {table_name} ({identifier}, password)
                        VALUES (%s, %s)
                        ON CONFLICT ({identifier}) DO NOTHING
                    """
                    cursor.execute(insert_query, (row[identifier], hashed_password))
                    connection.commit()  # Commit after each successful insert
                    
                except Exception as e:
                    print(f"Error processing row {row[identifier]}: {e}")
                    connection.rollback()  # Rollback on error
                    continue  # Continue with next row
            
            print(f"Password population completed successfully for {table_name}")
            
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Error populating table {table_name}: {e}")
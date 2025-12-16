import pandas as pd
import bcrypt
from src.db_management.db_configurations import users_passwords_db_connection, advisors_passwords_db_connection, users_passwords_db_cursor, advisors_passwords_db_cursor


def create_users_passwords_tables(table_name):
    """
    Creates the users passwords table if it does not exist.

    Args:
    table_name (str): Name of the table to create.
    """
    
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


def create_advisors_passwords_tables(table_name):
    """
    Creates the advisors passwords table if it does not exist.

    Args:
    table_name (str): Name of the table to create.
    """
    
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


def hash_password(password):
    """
    Hashes a plaintext password using bcrypt.

    Args:
    password (str): Plaintext password.

    Returns:
    str: Securely hashed password.
    """
    
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def insert_password(row, table_name, db_connection_function, identifier):
    """
    Inserts a hashed password into the database.

    Args:
    row (tuple): Identifier and hashed password.
    table_name (str): Target database table.
    db_connection_function (psycopg2.connection): Database connection.
    identifier (str): Column name used as identifier.
    """
    
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


def populate_passwords(csv_file, table_name, identifier, db_connection_function):
    """
    Populates a passwords table from a CSV file.
    
    Passwords are hashed before insertion and duplicates are ignored.
    
    Args:
    csv_file (str): Path to the CSV file.
    table_name (str): Target database table.
    identifier (str): Identifier column name.
    db_connection_function (psycopg2.connection): Database connection.
    """
    
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
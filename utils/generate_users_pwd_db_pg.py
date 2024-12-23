import pandas as pd
import bcrypt
import concurrent.futures

# Hash password function 
def hash_password(row):
    identifier, password = row
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    return identifier, hashed_password

# Insert password into database function
def insert_password(row, table_name, db_connection_function, identifier):
    try:
        connection = db_connection_function()
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
        df = pd.read_csv(csv_file, sep=";", names=[identifier, "password"])
        rows = df.itertuples(index=False, name=None)
        
        # Step 1: Hashing Passwords
        with concurrent.futures.ProcessPoolExecutor() as executor:
            hashed_passwords = list(executor.map(hash_password, rows))
        # Step 2: Insert into the database
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for row in hashed_passwords:
                executor.submit(insert_password, row, table_name, db_connection_function, identifier)

        print(f"Successful settlement for {table_name}")
    except Exception as e:
        print(f"Error populating table {table_name} : {e}")

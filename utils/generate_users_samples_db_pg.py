from src.db_management.db_configurations import users_db_connection, users_db_cursor


def create_users_table_and_index(table_name):
    """
    Creates the users table and associated indexes if they do not exist.
    
    Args:
    table_name (str): Name of the users table.
    """
    
    try:
        users_db_cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                user_id VARCHAR(10) PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                location_street VARCHAR(100),
                location_postcode VARCHAR(10),
                location_city VARCHAR(50),
                email VARCHAR(100) UNIQUE
            );
            DROP INDEX IF EXISTS idx_user_id;
            CREATE INDEX idx_user_id ON {table_name}(user_id);
        """)
        users_db_connection.commit()
    except Exception as e:
        print(f"Error creating {table_name} table: {e}")


def create_advisors_table_and_index(table_name):
    """
    Creates the advisors table and associated indexes if they do not exist.
    
    Args:
    table_name (str): Name of the advisors table.
    """
    
    try:
        users_db_cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                advisor_id VARCHAR(10) PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                role VARCHAR(20),
                email VARCHAR(100) UNIQUE
            );
            DROP INDEX IF EXISTS idx_advisor_id;
            CREATE INDEX idx_advisor_id ON {table_name}(advisor_id);
        """)
        users_db_connection.commit()
    except Exception as e:
        print(f"Error creating {table_name} table: {e}")


def create_users_advisors_table_and_index(table_name):
    """
    Creates the users-advisors mapping table and indexes.
    
    Args:
    table_name (str): Name of the mapping table.
    """
    
    try:
        users_db_cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                user_id VARCHAR(10) NOT NULL,
                advisor_id VARCHAR(10) NOT NULL,
                PRIMARY KEY (user_id, advisor_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (advisor_id) REFERENCES advisors(advisor_id)
            );
            DROP INDEX IF EXISTS idx_user_advisor;
            CREATE INDEX idx_user_advisor ON {table_name}(user_id, advisor_id);
        """)
        users_db_connection.commit()
    except Exception as e:
        print(f"Error creating {table_name} table: {e}")


def populate_table_users(table_name, data):
    """
    Populates the users table from a DataFrame.
    
    Args:
    table_name (str): Target users table.
    data (pandas.DataFrame): Users data.
    """
    
    for index, row in data.iterrows():
        try:
            users_db_cursor.execute(f"""
                INSERT INTO {table_name} (user_id, first_name, last_name, location_street, location_postcode, location_city, email) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING;
            """, 
            (row["user_id"], row["first_name"], row["last_name"], 
            row["location_street"], row["location_postcode"], 
            row["location_city"], row["email"]))
    
        except Exception as e:
            print(f"Error inserting user {row['user_id']}: {e}")
            continue
    
    users_db_connection.commit()
    print(f"{len(data)} users processed.")


def populate_table_adivsors(table_name, data):
    """
    Populates the advisors table from a DataFrame.
    
    Args:
    table_name (str): Target advisors table.
    data (pandas.DataFrame): Advisors data.
    """
    
    for index, row in data.iterrows():
        try:
            users_db_cursor.execute(f"""
                INSERT INTO {table_name} (advisor_id, first_name, last_name, role, email) 
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (advisor_id) DO NOTHING;
            """, 
            (row["advisor_id"], row["first_name"], row["last_name"], 
            row["role"], row["email"]))
    
        except Exception as e:
            print(f"Error inserting advisor {row['advisor_id']}: {e}")
            continue
    
    users_db_connection.commit()
    print(f"{len(data)} advisors processed.")


def populate_table_users_advisors(table_name, data):
    """
    Populates the users-advisors relationship table.
    
    Args:
    table_name (str): Target mapping table.
    data (pandas.DataFrame): Relationship data.
    """
    
    for index, row in data.iterrows():
        try:
            users_db_cursor.execute(f"""
                INSERT INTO {table_name} (user_id, advisor_id) 
                VALUES (%s, %s)
                ON CONFLICT (user_id, advisor_id) DO NOTHING;
            """, 
            (row["user_id"], row["advisor_id"]))
    
        except Exception as e:
            print(f"Error inserting user-advisor relation {row['user_id']}-{row['advisor_id']}: {e}")
            continue
    
    users_db_connection.commit()
    print(f"{len(data)} user-advisor relations processed.")
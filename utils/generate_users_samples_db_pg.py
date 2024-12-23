from src.db_management.db_configurations import users_db_connection, users_db_cursor

# User table creation and index function
def create_users_table_and_index(table_name):
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
        CREATE INDEX idx_user_id ON {table_name}(user_id);
    """)

# Advisor table creation and index function
def create_advisors_table_and_index(table_name):
    users_db_cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            advisor_id VARCHAR(10) PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            role VARCHAR(20),
            email VARCHAR(100) UNIQUE
        );
        CREATE INDEX idx_advisor_id ON {table_name}(advisor_id);
    """)

# Users_Advisors table creation and index function
def create_users_advisors_table_and_index(table_name):
    users_db_cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            user_id VARCHAR(10) NOT NULL,
            advisor_id VARCHAR(10) NOT NULL,
            PRIMARY KEY (user_id, advisor_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (advisor_id) REFERENCES advisors(advisor_id)
        );
        CREATE INDEX idx_user_advisor ON {table_name}(user_id, advisor_id);
    """)

# Populate the users table function
def populate_table_users(table_name, data):
    for index, row in data.iterrows():
        user_id = row["user_id"]
        first_name = row["first_name"]
        last_name = row["last_name"]
        location_street = row["location_street"]
        location_postcode = row["location_postcode"]
        location_city = row["location_city"]
        email = row["email"]
        users_db_cursor.execute(f"""
            INSERT INTO {table_name} (user_id, first_name, last_name, location_street, location_postcode, location_city, email) VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (user_id, first_name, last_name, location_street, location_postcode, location_city, email))
        
    users_db_connection.commit()
    print(f"{len(user_id)} users successfully imported.")

# Populate the advisors table function
def populate_table_adivsors(table_name, data):
    for index, row in data.iterrows():
        advisor_id = row["advisor_id"]
        first_name = row["first_name"]
        last_name = row["last_name"]
        role = row["role"]
        email = row["email"]
        users_db_cursor.execute(f"""
            INSERT INTO {table_name} (advisor_id, first_name, last_name, role, email) VALUES (%s, %s, %s, %s, %s);
        """, (advisor_id, first_name, last_name, role, email))
        
    users_db_connection.commit()
    print(f"{len(advisor_id)} advisors successfully imported.")


# Populate the users_advisors table function
def populate_table_users_advisors(table_name, data):
    for index, row in data.iterrows():
        user_id = row["user_id"]
        advisor_id = row["advisor_id"]
        users_db_cursor.execute(f"""
            INSERT INTO {table_name} (user_id, advisor_id) VALUES (%s, %s);
        """, (user_id, advisor_id))
        
    users_db_connection.commit()
    print(f"{len(user_id)} users-advisors relations successfully imported.")

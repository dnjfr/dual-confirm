from src.db_management.db_configurations import audit_db_connection, audit_db_cursor


def create_passwords_generation_audit_table(table_name):
    """
    Creates the passwords generation audit table if it does not exist.
    
    Args:
    table_name (str): Name of the audit table to create.
    """
    
    try:
        audit_db_cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(10)NOT NULL,
                user_pwd VARCHAR(60) NOT NULL,
                advisor_id VARCHAR(10)NOT NULL,
                advisor_pwd  VARCHAR(60) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            DROP INDEX IF EXISTS idx_{table_name}_user_id;
            DROP INDEX IF EXISTS idx_{table_name}_advisor_id;
            CREATE INDEX idx_{table_name}_user_id ON {table_name}(user_id);
            CREATE INDEX idx_{table_name}_advisor_id ON {table_name}(advisor_id);
        """)
        audit_db_connection.commit()
    except Exception as e:
        print(f"Error creating {table_name} table: {e}")


def create_sessions_users_audit_table(table_name):
    """
    Creates the users sessions audit table if it does not exist.
    
    Args:
    table_name (str): Name of the sessions audit table.
    """
    
    try:
        audit_db_cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255),
                advisor_id VARCHAR(255),
                role VARCHAR(50),
                login_timestamp TIMESTAMP,
                logout_timestamp TIMESTAMP,
                session_duration INTERVAL,
                ip_address VARCHAR(45),
                user_agent TEXT,
                status VARCHAR(50) 
            );
            DROP INDEX IF EXISTS idx_{table_name}_user_id;
            DROP INDEX IF EXISTS idx_{table_name}_advisor_id;
            CREATE INDEX idx_{table_name}_user_id ON {table_name}(user_id);
            CREATE INDEX idx_{table_name}_advisor_id ON {table_name}(advisor_id);
        """)
        audit_db_connection.commit()
    except Exception as e:
        print(f"Error creating {table_name} table: {e}")
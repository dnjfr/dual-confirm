from src.db_management.db_configurations import audit_db_connection, audit_db_cursor

def create_passwords_generation_audit_table(table_name):
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
            DROP INDEX IF EXISTS idx_passwords_audit_user_id;
            DROP INDEX IF EXISTS idx_passwords_audit_advisor_id;
            CREATE INDEX idx_passwords_audit_user_id ON passwords_audit(user_id);
            CREATE INDEX idx_passwords_audit_advisor_id ON passwords_audit(advisor_id);
        """)
        audit_db_connection.commit()
    except Exception as e:
        print(f"Error creating {table_name} table: {e}")
        

def create_sessions_users_audit_table(table_name):
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
            DROP INDEX IF EXISTS idx_sessions_users_audit_user_id;
            DROP INDEX IF EXISTS idx_sessions_users_audit_advisor_id;
            CREATE INDEX idx_sessions_users_audit_user_id ON session_audit(user_id);
            CREATE INDEX idx_sessions_users_audit_advisor_id ON session_audit(advisor_id);
        """)
        audit_db_connection.commit()
    except Exception as e:
        print(f"Error creating {table_name} table: {e}")
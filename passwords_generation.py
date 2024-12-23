import bcrypt
import random
import psycopg2
from datetime import datetime
from src.db_management.db_configurations import get_audit_db_connection, passwords_generation_audit_tablename, redis_words, redis_passwords, redis_users_sessions, redis_set, redis_get 


delay_regeneration = 30 # TTL - Time period between password expiration and renewal"-


# Check connection status function
def is_connected(user_id=None, advisor_id=None):
    """
    Checks if a user or advisor is logged in.
    """
    if user_id:
        connection_key = f"connection_status:client:{user_id}"
    elif advisor_id:
        connection_key = f"connection_status:advisor:{advisor_id}"
    else:
        return False

    return redis_get(redis_users_sessions, connection_key) == "connected"

# check if a client is selected by the advisor function
def is_selected(advisor_id, user_id):
    """
    Checks if a customer is selected by an advisor.
    """
    selection_key = f"selection_status:{advisor_id}:{user_id}"
    
    # If user_id is "Empty", delete all existing selection keys
    if user_id == "Empty":
        pattern = f"selection_status:*:*"
        existing_selection_keys = redis_users_sessions.keys(pattern)
        for key in existing_selection_keys:
            redis_users_sessions.delete(key)
        return False
    
    return redis_get(redis_users_sessions, selection_key) == "selected"

# Check if the user is active on his dashboard function
def is_active(user_id=None, advisor_id=None):
    """
    Checks if a user or advisor is active.
    """
    if user_id:
        active_key = f"active_status:client:{user_id}"
    elif advisor_id:
        active_key = f"active_status:advisor:{advisor_id}"
    else:
        return False

    return redis_get(redis_users_sessions, active_key) == "active"

# On-demand generation with memoization function
def generate_password_on_demand(user_id, advisor_id, timer=delay_regeneration):
    """
    Generate passwords on demand with memoization to avoid duplicates
    """
    try:
        # Creating a unique lock key
        lock_key = f"lock:password:{user_id}:{advisor_id}"
        
        # Creating the lock with a timeout
        lock = redis_passwords.lock(lock_key, timeout=10)
        
        # Attempt to acquire the lock without blocking
        if lock.acquire(blocking=False):
            try:
                # First check if the passwords already exist and are valid
                existing_passwords = get_password_and_timer(user_id, advisor_id)

                # If existing passwords are still valid, they are reused.
                if (existing_passwords['user_pwd'] and 
                    existing_passwords['user_ttl'] > 0 and 
                    existing_passwords['advisor_pwd'] and 
                    existing_passwords['advisor_ttl'] > 0):
                    return existing_passwords

                # Only if passwords have expired, we regenerate
                user_pwd = generate_password()
                advisor_pwd = generate_password()
                while user_pwd == advisor_pwd:
                    advisor_pwd = generate_password()
                
                # Temporary storage in Redis
                redis_set(redis_passwords, f"password:user:{user_id}:advisor:{advisor_id}", user_pwd, ex=timer)
                redis_set(redis_passwords, f"password:advisor:{advisor_id}:user:{user_id}", advisor_pwd, ex=timer)
                
                # Auditing in PostgreSQL
                audit_passwords(user_id, user_pwd, advisor_id, advisor_pwd)
                
                # Password Hashing (on request, comment out lines above)
                # hashed_user_pwd = hash_password(user_pwd)
                # hashed_advisor_pwd = hash_password(advisor_pwd)
                # redis_set(redis_passwords, f"password:user:{user_id}:advisor:{advisor_id}", hashed_user_pwd, ex=timer)
                # redis_set(redis_passwords, f"password:advisor:{advisor_id}:user:{user_id}", hashed_advisor_pwd, ex=timer)
                # audit_passwords(user_id, hashed_user_pwd, advisor_id, hashed_advisor_pwd)
                
                print(f"Passwords generated on demand for {user_id} - {advisor_id}.")
                        
                return {
                    "user_pwd": user_pwd,
                    "advisor_pwd": advisor_pwd,
                    "user_ttl": timer,
                    "advisor_ttl": timer
                }
                
            except Exception as e:
                print(f"Error while generating: {e}")
                return None
            
            finally:
                # Libére le verrou
                lock.release()

        else:
            print(f"[INFO] Regeneration in progress for {user_id} - {advisor_id}. Waiting...")
            # Recover existing passwords
            return get_password_and_timer(user_id, advisor_id)

    except Exception as e:
        print(f"Error acquiring lock: {e}")
    return None


# Retrieve passwords and TTL from Redis function
def get_password_and_timer(user_id, advisor_id):
    user_key = f"password:user:{user_id}:advisor:{advisor_id}"
    advisor_key = f"password:advisor:{advisor_id}:user:{user_id}"
    
    user_pwd = redis_get(redis_passwords, user_key)
    advisor_pwd = redis_get(redis_passwords, advisor_key)
    
    user_ttl = int(redis_passwords.ttl(user_key) or 0)
    advisor_ttl = int(redis_passwords.ttl(advisor_key) or 0)
    
    # If passwords have expired or do not exist, return None
    if user_ttl <= 0 or advisor_ttl <= 0 or not user_pwd or not advisor_pwd:
        return {
            "user_pwd": None,
            "user_ttl": 0,
            "advisor_pwd": None,
            "advisor_ttl": 0
        }

    return {
        "user_pwd": user_pwd,
        "user_ttl": user_ttl,
        "advisor_pwd": advisor_pwd,
        "advisor_ttl": advisor_ttl,
    }


# Retrieve a word from Redis function
def get_random_word():
    # Retrieves keys synchronously
    keys = list(redis_words.keys("word:*"))
    
    if not keys:
        return None
    
    random_key = random.choice(keys)
    
    # Retrieves and decodes the word if it is bytes
    word = redis_get(redis_words, random_key)
    
    return word


# Generate random password function
def generate_password():
    selected_word = get_random_word()
    return f"{selected_word}"


# Hash a password function
def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# Audit passwords in PostgreSQL function
def audit_passwords(user_id, hashed_user_pwd, advisor_id, hashed_advisor_pwd):
    try:
        audit_db_connection = get_audit_db_connection()
        audit_db_cursor = audit_db_connection.cursor()
        query = f"""
            INSERT INTO {passwords_generation_audit_tablename} (user_id, user_pwd, advisor_id, advisor_pwd, timestamp)
            VALUES (%s, %s, %s, %s, %s);
        """
        audit_db_cursor.execute(query, (user_id, hashed_user_pwd, advisor_id, hashed_advisor_pwd, datetime.now()))
        audit_db_connection.commit()
        audit_db_cursor.close()
        audit_db_connection.close()
    except psycopg2.Error as e:
        print(f"Error inserting into audit table for {user_id} et {advisor_id} : {e}")
    except Exception as e:
        print(f"Unexpected error while auditing passwords for {user_id} et {advisor_id} : {e}")


# Monitor Redis events and regenerate expired passwords function
def listen_for_expired_keys():
    try:
        redis_passwords.config_set('notify-keyspace-events', 'Ex')
        
        pubsub = redis_passwords.pubsub()
        pubsub.psubscribe("__keyevent@0__:expired")

        print("Redis event listening enabled.")
        for message in pubsub.listen():
            if message["type"] == "pmessage":
                key = message["data"].decode("utf-8")
                if key.startswith("password:user:"):
                    parts = key.split(":")
                    user_id = parts[2]
                    advisor_id = parts[4]
                    
                    # Explicit verification of customer selection
                    selection_key = f"selection_status:{advisor_id}:{user_id}"
                    is_client_selected = redis_get(redis_users_sessions, selection_key) == "selected"
                    
                    # Check if the advisor is connected
                    advisor_connection_key = f"connection_status:advisor:{advisor_id}"
                    is_advisor_connected = redis_get(redis_users_sessions, advisor_connection_key) == "connected"
                    
                    # Check if clients and advisors are active
                    client_active_key = f"active_status:client:{user_id}"
                    is_client_active = redis_get(redis_users_sessions, client_active_key) == "active"
                    
                    advisor_active_key = f"active_status:advisor:{advisor_id}"
                    is_advisor_active = redis_get(redis_users_sessions, advisor_active_key) == "active"
                    
                    # Conditions for regenerating passwords
                    if (is_connected(user_id=user_id) and is_client_active) or (is_advisor_connected and is_client_selected and is_advisor_active):
                        print(f"Regeneration triggered for {user_id} - {advisor_id} (logged in or selected customer).")
                        try:
                            generate_password_on_demand(user_id, advisor_id)
                        except Exception as regeneration_error:
                            print(f"Error while regenerating for {user_id} - {advisor_id}: {regeneration_error}")
                    else:
                        # If the customer is no longer selected, remove their status
                        redis_users_sessions.delete(selection_key)
                        print(f"No regeneration: {user_id} not selected or {advisor_id} disconnected.")
                
    except Exception as e:
        print(f"Error listening to Redis events: {e}")

# Exécution
if __name__ == "__main__":
    
    listen_for_expired_keys()
import os
import redis
import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)


#####################################################################
#                                                                   #
#                               REDIS                               # #                                                                   #
#####################################################################

# Get a connection to the Redis database of common words used to generate random passwords function
def get_redis_words_connection():
    """
    Establishes and returns a connection to the Redis common words database
    """
    try:
        redis_words = redis.StrictRedis( 
            host=os.getenv("GLOBAL_HOST_NETWORK") or "localhost",
            port=int(os.getenv("REDIS_DB_WORDS_PORT") or 6379),
            username=os.getenv("REDIS_DB_WORDS_USER"),
            password=os.getenv("REDIS_DB_WORDS_PASSWORD"),
            db=0)
        
        # Vérifie la connexion
        redis_words.ping()
        return redis_words
    except Exception as e:
        print(f"Error connecting to Redis Words: {e}")
        raise
    
        
redis_words = get_redis_words_connection()



# Get a connection to the Redis database of randomly generated passwords function
def get_redis_passwords_connection():
    """
    Establishes and returns a connection to the Redis password database
    """
    try:
        redis_passwords = redis.StrictRedis(
            host=os.getenv("GLOBAL_HOST_NETWORK") or "localhost",
            port=int(os.getenv("REDIS_DB_PASSWORDS_PORT") or 6389),
            username=os.getenv("REDIS_DB_PASSWORDS_USER"),
            password=os.getenv("REDIS_DB_PASSWORDS_PASSWORD"),
            db=0)
        
        # Vérifie la connexion
        redis_passwords.ping()
        return redis_passwords
    except Exception as e:
        print(f"Error connecting to Redis Passwords: {e}")
        raise


redis_passwords = get_redis_passwords_connection()



# Get a connection to the Redis database of current user sessions function
def get_redis_users_sessions_connection():
    """
    Establishes and returns a connection to the Redis database of current user sessions
    """
    try:
        redis_users_sessions = redis.StrictRedis( 
            host=os.getenv("GLOBAL_HOST_NETWORK") or "localhost",
            port=int(os.getenv("REDIS_DB_USERS_SESSIONS_PORT") or 6399),
            username=os.getenv("REDIS_DB_USERS_SESSIONS_USER"),
            password=os.getenv("REDIS_DB_USERS_SESSIONS_PASSWORD"),
            db=0)
        
        # Vérifie la connexion
        redis_users_sessions.ping()
        return redis_users_sessions
    except Exception as e:
        print(f"Error connecting to Redis Redis Users Sessions: {e}")
        raise


redis_users_sessions = get_redis_users_sessions_connection()



# Utility for storing in Redis
def redis_set(redis_db,key, value, ex=None):
    redis_db.set(key, value.encode("utf-8"), ex=ex)

# Utility to read from Redis
def redis_get(redis_db, key):
    value = redis_db.get(key)
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value



#####################################################################
#                                                                   #
#                             POSTGRES                              # #                                                                   #
#####################################################################

# Get a connection to the users database function 
def get_users_db_connection():
    """
    Establishes and returns a connection to the users database
    """
    try:
        connection = psycopg2.connect(
            host=os.getenv("GLOBAL_HOST_NETWORK"),
            port=os.getenv("POSTGRES_DB_USERS_PORT"),
            database=os.getenv("POSTGRES_DB_NAME_USERS"),
            user=os.getenv("POSTGRES_DB_USERS_USER"),
            password=os.getenv("POSTGRES_DB_USERS_PASSWORD")
        )
        return connection
    except Exception as e:
        print(f"Error connecting to users database: {e}")
        raise


users_db_connection = get_users_db_connection()
users_db_cursor = users_db_connection.cursor()
users_tablename = os.getenv("POSTGRES_DB_USERS_TABLENAME_USERS")
advisors_tablename = os.getenv("POSTGRES_DB_USERS_TABLENAME_ADVISORS")
users_advisors_tablename = os.getenv("POSTGRES_DB_USERS_TABLENAME_USERS_ADVISORS")



# Get a connection to the customer password database function
def get_users_passwords_db_connection():
    """
    Establishes and returns a connection to the client password database
    """
    try:
        connection = psycopg2.connect(
            host=os.getenv("GLOBAL_HOST_NETWORK"),
            port=os.getenv("POSTGRES_DB_USERS_PORT"),
            database=os.getenv("POSTGRES_DB_NAME_USERS_PASSWORDS"),
            user=os.getenv("POSTGRES_DB_USERS_USER"),
            password=os.getenv("POSTGRES_DB_USERS_PASSWORD")
        )
        return connection
    except Exception as e:
        print(f"Error connecting to user password database: {e}")
        raise


users_passwords_db_connection = get_users_passwords_db_connection()
users_passwords_db_cursor = users_passwords_db_connection.cursor()
users_passwords_tablename = os.getenv("POSTGRES_DB_USERS_PASSWORD_TABLENAME_USERS_PASSWORD")



# Get a connection to the password advisors database function
def get_advisors_passwords_db_connection():
    """
    Establishes and returns a connection to the password advisor database
    """
    try:
        connection = psycopg2.connect(
            host=os.getenv("GLOBAL_HOST_NETWORK"),
            port=os.getenv("POSTGRES_DB_USERS_PORT"),
            database=os.getenv("POSTGRES_DB_NAME_ADVISORS_PASSWORDS"),
            user=os.getenv("POSTGRES_DB_USERS_USER"),
            password=os.getenv("POSTGRES_DB_USERS_PASSWORD")
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the password advisor database: {e}")
        raise


advisors_passwords_db_connection = get_advisors_passwords_db_connection()
advisors_passwords_db_cursor = advisors_passwords_db_connection.cursor()
advisors_passwords_tablename = os.getenv("POSTGRES_DB_ADVISORS_PASSWORD_TABLENAME_ADVISORS_PASSWORD")



# Get a connection to the audit database function
def get_audit_db_connection():
    """
    Establishes and returns a connection to the audit database
    """
    try:
        connection = psycopg2.connect(
            host=os.getenv("GLOBAL_HOST_NETWORK"),
            port=os.getenv("POSTGRES_DB_AUDIT_PORT"),
            database=os.getenv("POSTGRES_DB_NAME_AUDIT"),
            user=os.getenv("POSTGRES_DB_AUDIT_USER"),
            password=os.getenv("POSTGRES_DB_AUDIT_PASSWORD")
        )
        return connection
    except Exception as e:
        print(f"Audit database connection error: {e}")
        raise


audit_db_connection = get_audit_db_connection()
audit_db_cursor = audit_db_connection.cursor()
session_audit_tablename = os.getenv("POSTGRES_DB_AUDIT_TABLENAME_SESSIONS_AUDIT")
passwords_generation_audit_tablename = os.getenv("POSTGRES_DB_AUDIT_TABLENAME_PASSWORDS_GENERATION_AUDIT")
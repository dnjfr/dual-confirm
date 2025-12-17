import os
import redis
import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)


#####################################################################
#                                                                   #
#                               REDIS                               # #                                                                   #
#####################################################################


def get_redis_connection_with_tls(host, port, username, password, db=0):
    """
    Establishes a secure Redis connection using TLS authentication.
    
    Args:
    host (str): Redis host.
    port (int): Redis port.
    username (str): Redis ACL username.
    password (str): Redis ACL password.
    db (int): Redis database index.
    
    Returns:
    redis.Redis: Authenticated Redis connection.
    
    Raises:
    Exception: If the connection or TLS handshake fails.
    """
    
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        # Configuration TLS
        ssl_cert_reqs = 'required'  # Or 'none' if no need to verify the certificate
        ssl_ca_certs = os.path.join(base_dir, 'ssl_certificates', 'ca.pem')
        ssl_certfile = os.path.join(base_dir, 'ssl_certificates', 'cert.pem')
        ssl_keyfile = os.path.join(base_dir, 'ssl_certificates', 'key.pem')
        
        redis_connection = redis.StrictRedis(
            host=host,
            port=port,
            username=username,
            password=password,
            db=db,
            ssl=True,
            ssl_cert_reqs=ssl_cert_reqs,
            ssl_ca_certs=ssl_ca_certs,
            ssl_certfile=ssl_certfile,
            ssl_keyfile=ssl_keyfile,
            ssl_check_hostname=False
        )
        
        # Check the connection
        redis_connection.ping()
        return redis_connection
    except Exception as e:
        print(f"Redis connection error with TLS: {e}")
        raise


def get_redis_words_connection():
    """
    Creates a Redis connection dedicated to the common words database.
    
    Returns:
    redis.Redis: Redis connection for common words storage.
    """
    
    try:
        redis_words = get_redis_connection_with_tls(
            host=os.getenv("GLOBAL_HOST_NETWORK") or "localhost",
            port=int(os.getenv("REDIS_DB_WORDS_PORT") or 6379),
            username=os.getenv("REDIS_DB_WORDS_USER"),
            password=os.getenv("REDIS_DB_WORDS_PASSWORD"),
            db=0)
        
        # # Check the connection
        # redis_words.ping()
        return redis_words
    except Exception as e:
        print(f"Error connecting to Redis Words: {e}")
        raise

redis_words = get_redis_words_connection()


def get_redis_passkeys_pairs_connection():
    """
    Creates a Redis connection dedicated to generated passkeys pairs storage.
    
    Returns:
    redis.Redis: Redis connection for passkeys database.
    """
    
    try:
        redis_passkeys_pairs = get_redis_connection_with_tls(
            host=os.getenv("GLOBAL_HOST_NETWORK") or "localhost",
            port=int(os.getenv("REDIS_DB_PASSKEYS_PORT") or 6389),
            username=os.getenv("REDIS_DB_PASSKEYS_USER"),
            password=os.getenv("REDIS_DB_PASSKEYS_PASSWORD"),
            db=0)
        
        return redis_passkeys_pairs
    except Exception as e:
        print(f"Error connecting to Redis Passkeys: {e}")
        raise

redis_passkeys_pairs = get_redis_passkeys_pairs_connection()


def get_redis_users_sessions_connection():
    """
    Creates a Redis connection dedicated to active user sessions.
    
    Returns:
    redis.Redis: Redis connection for user sessions.
    """
    
    try:
        redis_users_sessions = get_redis_connection_with_tls( 
            host=os.getenv("GLOBAL_HOST_NETWORK") or "localhost",
            port=int(os.getenv("REDIS_DB_USERS_SESSIONS_PORT") or 6399),
            username=os.getenv("REDIS_DB_USERS_SESSIONS_USER"),
            password=os.getenv("REDIS_DB_USERS_SESSIONS_PASSWORD"),
            db=0)
        
        return redis_users_sessions
    except Exception as e:
        print(f"Error connecting to Redis Redis Users Sessions: {e}")
        raise

redis_users_sessions = get_redis_users_sessions_connection()


def redis_set(redis_db,key, value, ex=None):
    """
    Stores a UTF-8 encoded value in Redis.
    
    Args:
    redis_db (redis.Redis): Redis connection.
    key (str): Redis key.
    value (str): Value to store.
    ex (int, optional): Expiration time in seconds.
    """
    
    redis_db.set(key, value.encode("utf-8"), ex=ex)


def redis_get(redis_db, key):
    """
    Retrieves and decodes a value from Redis.
    
    Args:
    redis_db (redis.Redis): Redis connection.
    key (str): Redis key.
    
    Returns:
    str or None: Decoded value if present, otherwise None.
    """
    
    value = redis_db.get(key)
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value



#####################################################################
#                                                                   #
#                             POSTGRES                              # #                                                                   #
#####################################################################


def get_users_db_connection():
    """
    Establishes a connection to the users database.
    
    Returns:
    psycopg2.connection: Users database connection.
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


def get_users_passwords_db_connection():
    """
    Establishes a connection to the users passwords database.
    
    Returns:
    psycopg2.connection: Users passwords database connection.
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


def get_advisors_passwords_db_connection():
    """
    Establishes a connection to the advisors passwords database.
    
    Returns:
    psycopg2.connection: Advisors passwords database connection.
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


def get_audit_db_connection():
    """
    Establishes a connection to the audit database.
    
    Returns:
    psycopg2.connection: Audit database connection.
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
users_sessions_audit_tablename = os.getenv("POSTGRES_DB_AUDIT_TABLENAME_USERS_SESSIONS_AUDIT")
passkeys_pairs_generation_audit_tablename = os.getenv("POSTGRES_DB_AUDIT_TABLENAME_PASSKEYS_PAIRS_GENERATION_AUDIT")
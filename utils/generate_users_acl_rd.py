import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Set directory paths for each Redis instance
paths = {
    "redis-words": "databases/redis/redis-conf/redis-words-conf/users.acl",
    "redis-passwords": "databases/redis/redis-conf/redis-passwords-conf/users.acl",
    "redis-users-sessions": "databases/redis/redis-conf/redis-users-sessions-conf/users.acl",
}

# User configurations for each instance
configs = {
    "redis-words": {
        "username": os.getenv("REDIS_DB_WORDS_USER"),
        "password": os.getenv("REDIS_DB_WORDS_PASSWORD"),
    },
    "redis-passwords": {
        "username": os.getenv("REDIS_DB_PASSWORDS_USER"),
        "password": os.getenv("REDIS_DB_PASSWORDS_PASSWORD"),
    },
        "redis-users-sessions": {
        "username": os.getenv("REDIS_DB_USERS_SESSIONS_USER"),
        "password": os.getenv("REDIS_DB_USERS_SESSIONS_PASSWORD"),
    }
}

def generate_users_acl():
# Generate and write `users.acl` files for each instance
    for instance, path in paths.items():
        user = configs[instance]

        if user["username"] and user["password"]:
            if user["username"] == os.getenv("REDIS_DB_PASSWORDS_USER"):
                # Add ability to monitor expired keys in Redis
                acl_content = f'user {user["username"]} on >{user["password"]} ~* +@all +@pubsub &__keyevent@0__:expired'
            else:
                acl_content = f'user {user["username"]} on >{user["password"]} ~* +@all'
                
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, "w") as acl_file:
                acl_file.write(acl_content)
            print(f"File '{path}' generated successfully.")

        else:
            print(f"Missing configuration for instance '{instance}'.")

generate_users_acl()
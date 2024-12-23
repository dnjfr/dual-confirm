

# DualConfirm - Dynamic password authentication system

A secure authentication system for critical institutions that generates synchronized, time-based dynamic passwords for both clients and advisors to verify each other's identity during phone calls.

## 🌎 Select language
<p align="center">
[![en](https://img.shields.io/badge/English-red.svg)](README.md)
[![fr](https://img.shields.io/badge/French-fr-green.svg)](README.fr.md)
</p>

* [Purpose](https://github.com/dnjfr/dual-confirm#-purpose)
* [Key Features](https://github.com/dnjfr/dual-confirm#-key-features)
* [Example Usage](https://github.com/dnjfr/dual-confirm#-example-usage)
* [Architecture](https://github.com/dnjfr/dual-confirm#-architecture)
* [Getting Started](https://github.com/dnjfr/dual-confirm#-getting-started)
* [Security Considerations](https://github.com/dnjfr/dual-security-considerations)
* [Contributing](https://github.com/dnjfr/dual-confirm#-contributing)
* [License](https://github.com/dnjfr/dual-confirm#-license)

## 📔 Purpose 
Following recent cyber attacks worldwide, particularly in France, large amounts of personal data, including IBAN numbers, have been stolen.

Scammers are exploiting these data breaches by posing as advisors, especially bank representatives, to gain their victims' trust and access their accounts.
In the face of these threats, securing communications between clients and their advisors has become crucial.

This project proposes a simple solution: allowing clients and advisors to mutually verify their identity through their application before any sensitive exchange.

The goal is to put both the advisor and the client at the center of the authentication process.


## 🔑 Key Features

- **Dynamic password generation**
  - Real-time generation of unique passwords for each client-advisor pair
  - Passwords change every 60 seconds while users are active
  - Uses common dictionary words (min 6 - max 9 letters) for better memorability
  - Scalable system capable of handling thousands of simultaneous password pairs

- **Dual authentication flow**
  - Each client has their own unique password
  - Each advisor sees distinct passwords for each of their clients
  - Mutual verification process during phone calls
  - Real-time synchronization between client and advisor interfaces

- **Security architecture**
  - Separate Redis instances for common words, password pairs, and user sessions
  - Segregated PostgreSQL databases for user management and audit logging
  - Complete session management with automatic timeouts
  - HTTPS support with SSL/TLS encryption
  - JWT-based authentication

- **Advanced session management**
  - Automatic session timeout after 180 seconds of inactivity
  - Real-time connection status monitoring
  - Graceful disconnection handling
  - WebSocket-based real-time updates

## 📞 Example Usage
```
Client: "Hello, this is Mr. Smth."
Advisor: "Hello Mr. Smth, this is Mr. Williams from Fictional Company. Could you confirm your client password shown on your interface?"
Client: "My password is 'weather'. Could you confirm your advisor password?"
Advisor: "My password is 'diamond'."
```
## 🏗️ Architecture

### Global scheme



### Redis databases
1. **Common words database (Instance 1)**
   - Stores dictionary words for password generation
   - Key format: `word:wd_xxxxx`

2. **Password pairs database (Instance 2)**
   - Stores temporary generated passwords
   - Key formats:
     - Client: `password:user:<user_id>:advisor:<advisor_id>`
     - Advisor: `password:advisor:<advisor_id>:user:<user_id>`

3. **User sessions database (Instance 3)**
   - Manages active sessions and connection states
   - Key formats:
     - Connection status: `connection_status:<role>:<id>`
     - Activity status: `active_status:<role>:<id>`
     - JWT tokens: `otp:<id>`

### PostgreSQL databases

1. **Users database**
   - Tables:
     - `users`: Client information
     - `advisors`: Advisor information
     - `users_advisors`: Client-advisor relationships
     - `users_passwords`: Hashed client passwords
     - `advisors_passwords`: Hashed advisor passwords

2. **Audit database**
   - Tables:
     - `passwords_audit`: Password generation history
     - `session_audit`: Session tracking and security events

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js and npm
- OpenSSL (optional, for local HTTPS setup)

### Installation
<details>
<summary>Follow the guide ⬇️</summary>
<br>

**1.** Clone the repository:
```bash
git clone <repository-url>
```

**2.** Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3.** Install dependencies:
```bash
pip install -r requirements.txt
npm init
```

**4.** Update `package.json`:
```json
{
  "type": "module"
}
```

**5.** Create `.env` file with the following variables:

<details>
<summary>List of environnements variables used ⬇️</summary>
<br>

  ```
    GLOBAL_HOST_NETWORK=host.docker.internal

    PGADMIN_DEFAULT_EMAIL=pgadmin@pgadmin.com
    PGADMIN_DEFAULT_PASSWORD=pgadmin

    POSTGRES_DB_NAME_USERS=DC_PG_USERS_ADVISORS
    POSTGRES_DB_USERS_PORT=5433
    POSTGRES_DB_USERS_USER=<your_identifier_for_users_base>
    POSTGRES_DB_USERS_PASSWORD=<your_password_for_users_base>
    POSTGRES_DB_USERS_TABLENAME_USERS=users
    POSTGRES_DB_USERS_TABLENAME_ADVISORS=advisors
    POSTGRES_DB_USERS_TABLENAME_USERS_ADVISORS=users_advisors

    POSTGRES_DB_NAME_USERS_PASSWORDS=DC_PG_USERS_PASSWORDS
    POSTGRES_DB_USERS_PASSWORD_TABLENAME_USERS_PASSWORD=users_passwords
    POSTGRES_DB_NAME_ADVISORS_PASSWORDS=DC_PG_ADVISORS_PASSWORDS
    POSTGRES_DB_ADVISORS_PASSWORD_TABLENAME_ADVISORS_PASSWORD=advisors_passwords

    POSTGRES_DB_NAME_AUDIT=DC_PG_AUDIT
    POSTGRES_DB_AUDIT_PORT=5431
    POSTGRES_DB_AUDIT_USER=<your_identifier_for_audit_base>
    POSTGRES_DB_AUDIT_PASSWORD=<your_password_for_audit_base>
    POSTGRES_DB_AUDIT_TABLENAME_PASSWORDS_GENERATION_AUDIT=passwords_generation_audit
    POSTGRES_DB_AUDIT_TABLENAME_SESSIONS_AUDIT=session_audit

    REDIS_DB_WORDS_PORT=6379
    REDIS_DB_WORDS_USER=<your_password_for_common_words_base>
    REDIS_DB_WORDS_PASSWORD=<your_password_for_common_words_base>

    REDIS_DB_PASSWORDS_PORT=6389
    REDIS_DB_PASSWORDS_USER=<your_identifier_for_generated_passwords_base>
    REDIS_DB_PASSWORDS_PASSWORD=<your_password_for_generated_passwords_base>

    REDIS_DB_USERS_SESSIONS_PORT=6399
    REDIS_DB_USERS_SESSIONS_USER=<your_identifier_for_session_user_base>
    REDIS_DB_USERS_SESSIONS_PASSWORD=<your_password_for_session_user_base>

    FLASK_SECRET=<your_Flask_secret_key>
    JWT_SECRET=<your_JWT_secret_key>

    SAMPLES_LANGUAGE=<en_or_fr>
  ```

</details>

<br>


**6.** Generate Redis ACL files:
```bash
python utils/generate_users_acl.py
```

**7.** Start the Docker containers:
```bash
docker compose up -d
```

**8.** Set up databases:
<details>
  <summary>PostgreSQL Setup ⬇️</summary>
  <br>

  **8.1.** Access pgAdmin at http://localhost:5050/

  **8.2.** Configure users database server:
  - Host: 172.25.0.5
  - Port: 5432
  - Database: DC_PG_USERS
  - Username: `<your_identifier_for_users_base>`
  - Password: `<your_password_for_users_base>`

  **8.3.** Configure audit database server:
  - Host: 172.25.0.6
  - Port: 5432
  - Database: DC_PG_AUDIT
  - Username: `<your_identifier_for_audit_base>`
  - Password: `<your_password_for_audit_base>`
</details>

<details>
  <summary>Redis Setup ⬇️</summary>
  <br>

**8.4.** Access RedisInsight at http://localhost:5540/

  **8.5.** Configure common words database instance:
  - Host: 172.25.0.2
  - Port: 6379
  - Database: DC_RD_WORDS
  - Username: `<your_identifier_for_common_words_base>`
  - Password: `<your_password_for_common_words_base>`

  **8.6.** Configure passwords database instance:
  - Host: 172.25.0.3
  - Port: 6389
  - Database: DC_RD_PASSWORDS
  - Username: `<your_identifier_for_generated_passwords_base>`
  - Password: `<your_password_for_generated_passwords_base>`

  **8.7.** Configure sessions database instance:
  - Host: 172.25.0.4
  - Port: 6399
  - Database: DC_RD_SESSIONS_USERS
  - Username: `<your_identifier_for_session_user_base>`
  - Password: `<your_password_for_session_user_base>`


</details>

**9.** Run database setup script:
```bash
python setup_db_creation_population.py
```

**10.** Generate SSL certificates for HTTPS:
```bash
python utils/setup_ssl.py
```

**11.** Start the application:
```bash
# Terminal 1: Start password generation service
python passwords_generation.py

# Terminal 2: Start main application
python app.py
```
</details>

## 🔒 Security Considerations

- Passwords are automatically rotated every 30 seconds
- All database instances are isolated and run on separate Docker containers
- Passwords are hashed using bcrypt
- Session management includes automatic timeouts and activity monitoring
- SSL/TLS encryption for all communications
- Complete audit logging of all authentication attempts and password generations

### Security Notes - For development only

- Default test passwords:
    ```
    Clients: "mypassword"
    Advisors: "mypassword2"
    ```
- Production deployments should use proper password management
- HTTPS certificates are self-signed for development

## 🤝 Contributing

This is a learning project and contributions are welcome. Please feel free to submit pull requests or open issues.

## 📝 License

[Choose an appropriate license and add it here]
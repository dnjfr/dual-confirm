

# DualConfirm - Dynamic password authentication system
<p align="center">
<a href="README.md"><img src="https://img.shields.io/badge/English-green.svg" /></a>
<a href="README.fr.md"><img src="https://img.shields.io/badge/French-fr-blue.svg" /></a>
</p>

<p align="center">
<img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" />
<img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" />
<img src="https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E" />
<img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
<img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" />
<img src="https://img.shields.io/badge/redis-%23DD0031.svg?&style=for-the-badge&logo=redis&logoColor=white" />
</p>


A secure authentication system for critical institutions that generates synchronized, time-based dynamic passwords for both clients and advisors to verify each other's identity during phone calls.

## 👩‍💻 Table of Contents

* [Purpose](#-purpose)
* [Key Features](#-key-features)
* [Example Usage](#-example-usage)
* [Architecture](#%EF%B8%8F-architecture)
* [Getting Started](#-getting-started)
* [Security Notes - For development only](#-security-notes---for-development-only)
* [Contributing](#-contributing)

## 📔 Purpose 
Following recent cyber attacks worldwide, particularly in France, large amounts of personal data, including IBAN numbers, have been stolen.

Scammers are exploiting these data breaches by posing as advisors, especially bank representatives, to gain their victims' trust and access their accounts.
In the face of these threats, securing communications between clients and their advisors has become crucial.

This project proposes a simple solution: allowing clients and advisors to mutually verify their identity through their application before any sensitive exchange.

The goal is to put both the advisor and the client at the center of the authentication process.


## 🔑 Key Features

- **Dynamic password generation**
  - Real-time generation of unique passwords for each client-advisor pair
  - Passwords change every 30 seconds while users are active
  - Uses common dictionary words (min 6 - max 9 letters) for better memorability
  - Scalable system capable of handling thousands of simultaneous password pairs

- **Dual authentication flow**
  - Each client has their own unique password
  - Each advisor sees distinct passwords for each of their clients
  - Mutual verification process during phone calls
  - Real-time synchronization between client and advisor interfaces

- **Security Architecture & Considerations**
  - Infrastructure Isolation
    - Separate Redis instances for common words, password pairs, and user sessions
    - Segregated PostgreSQL databases for user management and audit logging
    - All database instances run on isolated Docker containers
  - Authentication & Session Management
    - JWT-based authentication
    - Automatic password rotation every 30 seconds
    - Complete session management with automatic timeouts
    - Comprehensive audit logging of all authentication attempts and password generations
  - Encryption & Data Protection
    - HTTPS support with SSL/TLS encryption for all communications
    - Password hashing using bcrypt

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

<p align="center">
<img width="1000" src="/git-img/global-scheme.png"/>
</p>

### Redis databases
1. **Common words database (Instance 1)**
   - Stores dictionary words for password generation
   - Key format: `word:word_id`

2. **Password pairs database (Instance 2)**
   - Stores temporary generated passwords
   - Key formats:
     - Client: `password:user:<user_id>:advisor:<advisor_id>`
     - Advisor: `password:advisor:<advisor_id>:user:<user_id>`

3. **Users sessions database (Instance 3)**
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
     - `users_sessions_audit`: Session tracking and security events

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- OpenSSL (optional, for local HTTPS setup)

### Installation
<details>
<summary>Follow the guide ⬇️</summary>
<br>

**1.** Clone the repository:
```bash
git clone https://github.com/dnjfr/dual-confirm
cd dual-confirm
```

**2.** Create and activate virtual environment:
```bash
python -m venv .venv 
source .venv/bin/activate  # On Windows: .venv/Scripts/activate
```

**3.** Install dependencies:
```bash
pip install -r requirements.txt
```

**4.** Create `.env` file with the following variables:

<details>
<summary>List of environnements variables used ⬇️</summary>
<br>

  ```
    GLOBAL_HOST_NETWORK=host.docker.internal

    PGADMIN_DEFAULT_EMAIL=<your_email_for_pgadmin>
    PGADMIN_DEFAULT_PASSWORD=<your_password_for_pgadmin>

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
    POSTGRES_DB_AUDIT_TABLENAME_USERS_SESSIONS_AUDIT=users_sessions_audit

    REDIS_DB_WORDS_PORT=6379
    REDIS_DB_WORDS_USER=<your_password_for_common_words_base>
    REDIS_DB_WORDS_PASSWORD=<your_password_for_common_words_base>

    REDIS_DB_PASSWORDS_PORT=6389
    REDIS_DB_PASSWORDS_USER=<your_identifier_for_generated_passwords_base>
    REDIS_DB_PASSWORDS_PASSWORD=<your_password_for_generated_passwords_base>

    REDIS_DB_USERS_SESSIONS_PORT=6399
    REDIS_DB_USERS_SESSIONS_USER=<your_identifier_for_users_sessions_base>
    REDIS_DB_USERS_SESSIONS_PASSWORD=<your_password_for_users_sessions_base>

    FLASK_SECRET=<your_Flask_secret_key>
    JWT_SECRET=<your_JWT_secret_key>

    SAMPLES_LANGUAGE=<en_or_fr>
  ```

</details>

<br>

**5.** Generate Redis ACL files:
```bash
python utils/generate_users_acl_rd.py
```

**6.** Start the Docker containers:
```bash
docker compose up -d
```

**7.** Set up databases:
<details>
  <summary>PostgreSQL Setup ⬇️</summary>
  <br>

  **7.1.** Access pgAdmin at <a href="http://localhost:5050/" target="_blank">http://localhost:5050/</a> (please wait a few seconds while the service starts) and enter your email/password (PGADMIN_DEFAULT_EMAIL and PGADMIN_DEFAULT_PASSWORD variables created in `.env`) 

  **7.2.** To configure a server, click on "Add new server"

  **7.3.** Configure users database server:
  - Server name: postgres-users
  - Host: 172.25.0.5
  - Port: 5432
  - Username: `<your_identifier_for_users_base>`
  - Password: `<your_password_for_users_base>`

  **7.4.** Configure audit database server:
  - Server name: postgres-audit
  - Host: 172.25.0.6
  - Port: 5432
  - Username: `<your_identifier_for_audit_base>`
  - Password: `<your_password_for_audit_base>`

  **7.5.** Create 3 databases in server postgres-users : 
  - All users base : DC_PG_USERS_ADVISORS
  - Users passwords base : DC_PG_USERS_PASSWORDS
  - Avisors passwords base : DC_PG_ADVISORS_PASSWORDS

  **7.6.** Create the database in server postgres-audit :  
  - Passwords pair and users sessions audit base : DC_PG_AUDIT
</details>

<details>
  <summary>Redis Setup ⬇️</summary>
  <br>

  **7.7.** Access RedisInsight at <a href="http://localhost:5540/" target="_blank">http://localhost:5540/</a> and click on "Add Redis database"

  **7.8.** Configure common words database instance:
  - Host: 172.25.0.2
  - Port: 6379
  - Database Alias: DC_RD_WORDS
  - Username: `<your_identifier_for_common_words_base>`
  - Password: `<your_password_for_common_words_base>`

  **7.9.** Configure passwords database instance:
  - Host: 172.25.0.3
  - Port: 6379
  - Database Alias: DC_RD_PASSWORDS
  - Username: `<your_identifier_for_generated_passwords_base>`
  - Password: `<your_password_for_generated_passwords_base>`

  **7.10.** Configure sessions database instance:
  - Host: 172.25.0.4
  - Port: 6379
  - Database Alias: DC_RD_USERS_SESSIONS
  - Username: `<your_identifier_for_users_sessions_base>`
  - Password: `<your_password_for_users_sessions_base>`
</details>

**8.** Run database setup script (the process can take a while, have a ☕):
```bash
python setup_db_creation_population.py
```

**9.** Generate SSL certificates for HTTPS (optional):

<details>
<summary>Windows users ⬇️</summary>
<br>
If your operating system is Windows and OpenSSL is not installed on your machine, the simplest solution is to download and install the version compatible with your system via FireDaemon: https://kb.firedaemon.com/support/solutions/articles/4000121705
</details>

```bash
python utils/setup_ssl.py
```

Then modify `app.py` file depending on whether or not SSL is used.

**10.** Open two terminals (make sure both terminals have `.venv` activated) and start the application:
```bash
# Terminal 1: Start password generation service
python passwords_generation.py

# Terminal 2: Start main application
python app.py
```
</details>

## 🔒 Security Notes - For development only

- Default test passwords used for the project :
  - Clients: `mypassword`
  - Advisors: `mypassword2`
- Production deployments should use proper password management
- HTTPS certificates are self-signed for development

## 🤝 Contributing

This is a learning project and contributions are welcome. Please feel free to submit pull requests or open issues.
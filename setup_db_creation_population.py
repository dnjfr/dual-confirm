import time
import pandas as pd
import os
from dotenv import load_dotenv
from src.db_management.db_configurations import users_passwords_db_connection, advisors_passwords_db_connection, users_tablename, advisors_tablename, users_advisors_tablename, users_passwords_tablename, advisors_passwords_tablename
from utils.generate_commonwords_db_rd import populate_common_words_db
from utils.generate_users_samples_db_pg import create_advisors_table_and_index, create_users_advisors_table_and_index, create_users_table_and_index, populate_table_adivsors, populate_table_users, populate_table_users_advisors
from utils.generate_users_pwd_db_pg import create_users_passwords_tables, create_advisors_passwords_tables, populate_passwords

load_dotenv(override=True)

samples_language = os.getenv("SAMPLES_LANGUAGE")


# Redis common words database population

commonwords_csv_file = f"samples-datas/words/{samples_language}/words.csv"

populate_common_words_db(commonwords_csv_file)

# Creating tables and importing user test data
users_csv_file = pd.read_csv(f"samples-datas/users-data/{samples_language}/users.csv", sep=';')
advisors_csv_file = pd.read_csv(f"samples-datas/users-data/{samples_language}/advisors.csv", sep=';')
users_advisors_csv_file = pd.read_csv(f"samples-datas/users-data/{samples_language}/users-advisors.csv", sep=';')

create_users_table_and_index(users_tablename)
create_advisors_table_and_index(advisors_tablename)
create_users_advisors_table_and_index(users_advisors_tablename)

populate_table_users(users_tablename, users_csv_file)
populate_table_adivsors(advisors_tablename, advisors_csv_file)
populate_table_users_advisors(users_advisors_tablename, users_advisors_csv_file)

# Creating tables and importing data and generating hashed passwords for test users

users_passwords_csv_file = "samples-datas/users-passwords/users_passwords.csv"
advisors_passwords_csv_file = "samples-datas/users-passwords/advisors_passwords.csv"

create_users_passwords_tables(users_passwords_tablename)
create_advisors_passwords_tables(advisors_passwords_tablename)

populate_passwords(users_passwords_csv_file, users_passwords_tablename, 'user_id', users_passwords_db_connection)

populate_passwords(advisors_passwords_csv_file, advisors_passwords_tablename, 'advisor_id', advisors_passwords_db_connection)
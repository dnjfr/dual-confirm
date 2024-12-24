import pandas as pd
from src.db_management.db_configurations import redis_words

# Common words database population function
def populate_common_words_db(csv_file):
    df = pd.read_csv(csv_file, sep=";", header=0)

    for index, row in df.iterrows():
        word_id = row["word_id"]
        word = row["word"]
        redis_words.set(f"word:{word_id}", word)

    print(f"{len(df)} common words imported into Redis.")

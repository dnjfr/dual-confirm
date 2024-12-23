import pandas as pd
from src.db_management.db_configurations import redis_words


def populate_common_words_db(csv_file):
# Charge le fichier CSV
    df = pd.read_csv(csv_file, sep=";", header=None, names=["word_id", "word"], skiprows=1)

    # Importe les mots dans Redis
    for index, row in df.iterrows():
        word_id = row["word_id"]
        word = row["word"]
        redis_words.set(f"word:{word_id}", word)

    print(f"{len(df)}common words imported into Redis.")

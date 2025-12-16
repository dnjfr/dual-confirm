import pandas as pd
from src.db_management.db_configurations import redis_words


def populate_common_words_db(csv_file):
    """
    Populates the Redis common words database from a CSV file.
    
    Args:
    csv_file (str): Path to the CSV file containing common words.
    """
    
    df = pd.read_csv(csv_file, sep=";", header=0)
    
    for index, row in df.iterrows():
        word_id = row["word_id"]
        word = row["word"]
        redis_words.set(f"word:{word_id}", word)
        
    print(f"{len(df)} common words imported into Redis.")

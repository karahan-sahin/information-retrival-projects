import re
import string
import json
import math
from collections import defaultdict
import scrapper


def import_collection() -> dict:
    """
    Import json file containing data collection.
    Runs the scrapper script, if cannot find the data.

    -i: None
    -o: collection -> dict
    """
    try: # Opens json file and loads as a dictionary
        with open("books.json", "r", encoding="utf-8") as f_in:
            data = f_in.read()
            collection = json.loads(data, encoding="utf-8")

    # If data is not parsed and collected
    except FileNotFoundError:
        print("Dataset is Not Found!")
        # Runs the scrapper script
        scrapper.main()
        # Recursivity for returning content
        collection = import_collection()

        return collection

    return collection


def count_vectorize_description(collection):
    """
    Iterates over book descriptions and returns a dictionary containing \\
    each book and counts of unique tokens and a dictionary containing\\
    vocabulary with their collection frequency

    -i: collection dict
    -o: dictionary -> word -> string
                      frequency
        count dictionaries -> title
                              document frequency
    """

    # Unique words and their collection frequency
    dictionary = defaultdict(int)

    # Unique word counts
    count_dictionaries = defaultdict(dict)

    # Iterate over books and their info contents
    for book, info in collection.items():
        # Count dictionary for each document
        count_dictionary = defaultdict(int)
        # Get Description of book, and lower the content
        description = info["Description"].lower()

        # split punctuations and other special characters
        punctuations = string.punctuation + "‘’—–“”…•·„"

        # Split string with all non-word and non-digit character
        tokens = re.split(pattern=r'\n|[{}]+|\s+'.format(punctuations),
                          string=description)

        # This is for count vector
        # Add one to document frequency for each unique token seen
        for word in tokens:
            count_dictionary[word] += 1

        # Add one for each unique token for collection frequency
        for word in count_dictionary.keys():
            dictionary[word] += 1

        # Append count dictionaries for given book
        count_dictionaries[book] = count_dictionary

    return dictionary, count_dictionaries


def tf_idf_description(dictionary, count_dictionaries) -> dict:
    """
    Using count dictionaries of books and vocabulary with collection frequencies\\
    Calculates tf-idf scores of description content, then returns a dictionary with titles and their tf-idf \\
    weighted vector dictionaries

    -i: dictionary with vocabulary collection freq
        dictionary with books and their count dictionaries
    -o: dict --> title
                 tf-idf weighted vector dictionaries

    """

    tf_idf_dictionary = defaultdict(dict)

    # Iterate over each book and description vector of given book
    for book, counts in count_dictionaries.items():
        
        # Tf-idf dictionary for description of each book
        count_dictionary = defaultdict(int)

        for word, freq in counts.items():
            # Document frequency of term
            term_frequency = freq
            # Inverted document frequency of term
            # total number of vocabulary divided by collection frequency of term
            inverted_doc_freq = math.log10(
                len(collection.keys())/dictionary[word])
            
            # For each word, append its weighted score to the dictionary
            count_dictionary[word] = term_frequency * inverted_doc_freq

        # For each book, append its tf-idf dictionary
        tf_idf_dictionary[book] = count_dictionary

    return tf_idf_dictionary


def description_dump(tf_idf_dictionary):
    """
    Dumps dictionary content in a json file
    """
    with open("tf_idf_dictionary.json", "w", encoding="utf-8") as f_out:
        json.dump(tf_idf_dictionary, f_out)


def count_vectorize_genres(collection):
    """
    Iterates over book genres-votes and returns a dictionary containing \\
    each book with votes count of genres as term weight, and a dictionary \\
    unique genres with their document frequency for their collection weight


    -i: collection dict
    -o: dictionary -> word -> string
                      frequency
        count dictionaries -> title
                              document frequency
    """

    # Genre dict and collection frequency
    genre_dictionary = defaultdict(int)
    # Collection of count dictionaries of genre and their weights for each book
    count_dictionaries = defaultdict(dict)
    # Iterating over book and their information
    for book, info in collection.items():

        count_dictionary = defaultdict(int)

        # Dictionary item
        genres = info["Genres"]

        # Create count(vote) dictionary for genre
        for genre, vote in genres.items():
            count_dictionary[genre] = vote

        # Append a count dictionary for document genres
        count_dictionaries[book] = count_dictionary

        # vocabulary of genre with collection frequency
        for genre in genres.keys():
            genre_dictionary[genre] += 1

    return genre_dictionary, count_dictionaries


def tf_idf_genres(dictionary, count_dictionaries) -> dict:
    """
    Using count dictionaries of books and vocabulary with collection frequencies\\
    Calculates tf-idf scores of genre content, then returns a dictionary with titles and their tf-idf \\
    weighted vector dictionaries

    -i: dictionary with vocabulary collection freq
        dictionary with books and their count dictionaries
    -o: dict --> title
                 tf-idf weighted vector dictionaries

    """

    tf_idf_dictionary = defaultdict(dict)

    # Iterate over each book and genre vector of given book
    for book, counts in count_dictionaries.items():

        # Dictionary for genres of each book
        count_dictionary = defaultdict(int)

        # Calculated total amount of vote
        total_vote = 0
        for vote in counts.values():
            total_vote += vote

        # Iterate over each genre and its vote of given book
        for genre, vote in counts.items():

            # total_vote / vote gives the weight of the genre for given book
            # log operation easier calculation over float64 class items
            genre_frequency = math.log10(total_vote**vote)
            # idf score as log(N/genre collection frequency)
            inverted_doc_freq = math.log10(
                len(dictionary.keys())/dictionary[genre])

            # For each genre, append its weighted score to the dictionary
            count_dictionary[genre] = abs(genre_frequency * inverted_doc_freq)

        # For each book, append its tf-idf dictionary
        tf_idf_dictionary[book] = count_dictionary

    return tf_idf_dictionary


def genre_dumps(tf_idf_dictionary):
    """
    Dumps dictionary content in a json file
    """
    with open("genre_dictionary.json", "w", encoding="utf-8") as f_out:
        json.dump(tf_idf_dictionary, f_out)


# These function run when tf-idf script imported,
# while query processing we are using these variables
collection = import_collection()
_dictionary, _ = count_vectorize_description(collection)
_genre_dictionary, _ = count_vectorize_genres(collection)


def main():
    print("Processing dataset...")
    # Extracting dataset
    collection = import_collection()
    # Description processing
    _dictionary, _count_dictionaries = count_vectorize_description(collection)
    tf_idf_dictionary = tf_idf_description(_dictionary, _count_dictionaries)
    description_dump(tf_idf_dictionary)
    # Genre processing
    _genre_dictionary, _count_dictionaries = count_vectorize_genres(collection)
    tf_idf_dictionary = tf_idf_genres(_genre_dictionary, _count_dictionaries)
    genre_dumps(tf_idf_dictionary)

# Run if called
if __name__ == "__main__":
    main()

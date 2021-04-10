import json
import os
import sys
from collections import defaultdict
import scrapper
import tf_idf

def import_dictionaries():
    """
    Imports dictionaries, if datas cannot be found, runs the corresponding script

    -i: None
    -o: collection
        tf_idf_dictionary --> tf-idf weighted vector dictionaries of book descriptions
        genre_dictionary --> tf-idf weighted vector dictionaries of book genres
    """

    collection = tf_idf.import_collection()

    try: #Opens json files and imports as dictionaries
        with open("tf_idf_dictionary.json","r",encoding="utf-8") as f_in:
            data = f_in.read()
            tf_idf_dictionary = json.loads(data,encoding="utf-8")
        
        with open("genre_dictionary.json","r",encoding="utf-8") as f_in:
            data = f_in.read()
            genre_dictionary = json.loads(data,encoding="utf-8")

    # If doesn't exits, runs main function the scripts
    except FileNotFoundError:
        print("Tf-Idf Vectors Not Found!")
        tf_idf.main()
        # Recursivity for returning data, after json files are created
        collection, tf_idf_dictionary, genre_dictionary = import_dictionaries()

        return collection, tf_idf_dictionary, genre_dictionary

        
    return collection, tf_idf_dictionary, genre_dictionary

# Reads the path of .txt for urls of query books
url_path = sys.argv[1]

def query_processing(path):

    """
    Extracts the information for processing query(s) and vectorizes the content

    -i: path to .txt file containing URLs
    -o: dict -> query book collection in appropriate format
        dict -> description tf-idf vector dictionary
        dict -> weighted genre vector dictionary 
    """
    
    urls = [] 

    # If path is a single url
    if path.startswith("https"):
        urls.append(path)
    
    # If path is a path to .txt file
    else:
        # Read and list URL
        with open(f"{path}","r") as f_in:
            urls = f_in.readlines()
            urls = [url.strip('\n') for url in urls]
    
    # Containin information in given format
    book_infos = defaultdict(dict)

    # Iterate over queries
    for query in urls:

        # For security
        if query.startswith("https"):

            # Parse given url
            book_info = scrapper.html_parser(query)

            # Use book name as the key to book_info dict
            book_name = book_info["Title"]

            info = dict()

            # Append rest of the information 
            for section in book_info.keys():
                if section != "Title":
                    info[section] = book_info[section]
            
            book_infos[book_name] = info


    # TD-IDF Vectorizing of Query Book Descriptions
    _, count_vec_d = tf_idf.count_vectorize_description(book_infos)
    # Tf-idf vectorize using tf-idf-dictionary from tf-idf script
    query_tf_idf_description = tf_idf.tf_idf_description(tf_idf._dictionary, count_vec_d)

    # Vectorizing of Query Book Genres with Weighting Scheme
    _, count_vec_d = tf_idf.count_vectorize_genres(book_infos)
    # Tf-idf vectorize using genre-dictionary from tf-idf script
    query_tf_idf_genre = tf_idf.tf_idf_genres(tf_idf._genre_dictionary,count_vec_d)

    return book_infos, query_tf_idf_description, query_tf_idf_genre

book_infos, query_tf_idf_description, query_tf_idf_genre = query_processing(url_path)

# Iterate over query(s)
for query in book_infos.keys():

    def cosine_similarity_calculator(query,a = 0.35) -> dict:
        """
        For given query, calculates the combinatory cosine similarity with each documents'\\
        tf-idf vectors of descriptions and weighted genre vectors with a given parameter for\\
        weights of these two vectors in scoring. \\
        Returns a dictionary with sorted by decreasing score value
        
        -i: Title of query book
        -o: sorted by scores dictionary
        """

        # Import dictionaries
        __ , tf_idf_dictionary, genre_dictionary = import_dictionaries()

        # Store the book titles for iteration
        book_list = list(tf_idf_dictionary.keys())

        # Extract the query description and genre vectors
        query_description_vec = query_tf_idf_description[query]
        query_genre_vec = query_tf_idf_genre[query]

        # Description vector length normalization of the query
        total = 0
        for freq in query_description_vec.values(): # Add squared length each dimension
            total += freq**2
        
        # Binary vectorizing query norm for description vector's deminator
        query_description_norm = total**0.5

        # Genre vector length normalization of the query
        total = 0
        for freq in query_genre_vec.values(): # Add squared length each dimension
            total += freq**2

        # Binary vectorizing query norm for genre vector's deminator
        query_genre_norm = total**0.5

        scores = dict()

        # Iterate over every other document for
        for book in book_list:

            # Skip if the query is in dataset
            if book == query:
                continue

            ## COSINE SIMILARITY FOR TEXTS

            # Extract tf-idf vector of given book document
            document_description_vec = tf_idf_dictionary[book]

            # Description vector length normalization of the document
            total = 0
            for w in document_description_vec.values(): # Add squared length each dimension
                total += w**2

            # Binary vectorizing document norm for description vector's deminator
            document_description_norm = total**0.5
            
            # Find tokens of two compared description vectors and intersect them for
            # operating on non-zero dimensions of each vector
            query_description_tokens = set(query_description_vec.keys())
            document_description_tokens = set(document_description_vec.keys())
            matching_tokens = document_description_tokens.intersection(query_description_tokens)

            ## Dot product of two description vectors
            # Multiply each non-zero dimensions of each vector and add to numerator of the dot product
            sums = 0
            for token in list(matching_tokens):
                sums += query_description_vec[token] * document_description_vec[token]

            # Score is the division of dot product of two vectors and multiplication of their norms
            desc_score = sums / (query_description_norm * document_description_norm)

            ## COSINE SIMILARITY FOR GENRES 
             
            # Extract weighted genre vector of given book document
            document_genre_vec = genre_dictionary[book]

            # Genre vector length normalization of the document
            total = 0
            for g in document_genre_vec.values():
                total += g**2

            # Binary vectorizing document norm for genre vector's deminator
            document_genre_norm = total**0.5

            # Find tokens of two compared genre vectors and intersect them for
            # operating on non-zero dimensions of each vector
            query_genre_tokens = set(query_genre_vec.keys())
            document_genre_tokens = set(document_genre_vec.keys())
            matching_tokens = query_genre_tokens.intersection(document_genre_tokens)

            ## Dot product of two genre vectors
            # Multiply each non-zero dimensions of each vector and add to numerator of the dot product
            sums = 0
            for token in matching_tokens :
                sums += query_genre_vec[token] * document_genre_vec[token]

            # Score is the division of dot product of two vectors and multiplication of their norms
            try:
                genre_score = sums / (query_genre_norm * document_genre_norm)
            except ZeroDivisionError: # Problematic case non-matching genres
                genre_score = 0

            # Combine scores from two different vector similarities with given parameter
            score = a*desc_score + (1-a)*genre_score

            # Append score of book to query
            scores[book] = score

        # Sort the dictionary by decreasing scores
        sorted_by_scores = dict(sorted(scores.items(), key=lambda item: item[1],reverse=True))

        return sorted_by_scores

    sorted_by_scores = cosine_similarity_calculator(query)

    def retrieve_top_k(sorted_by_scores, retrieved_document=18) -> list:
        """
        Retrieve given number of documents with their relevancy scores 

        -i: dict:sorted by decreasing scores, 
            int:top_K

        -o: list:tuples(book,relevancy) 
        """

        retrieved_list = []
        # Import collection
        collection, _ , _ = import_dictionaries()
        # Find the ground Recommended books for the query
        recommended = collection[query]["Recommended"]

        # 
        for book in sorted_by_scores.keys():
            # Loop until the desired number of docs retrieved
            if retrieved_document == 0:
                break
            # If the retrieved document is in recommended list rel:1
            if book in recommended or book == query:
                retrieved_list.append((book, 1))
            # Otherwise rel:0
            else:
                retrieved_list.append((book, 0))

            # Decrement retrieved doc number
            retrieved_document -= 1

        return retrieved_list

    retrieved_list = retrieve_top_k(sorted_by_scores)

    def evaluate_system(retrieved_list, P_18m = True, AP_Nm = True):
        """
        Calculates the Precision@18 and Average Precision score from given retrieved items

        -i: retrieved docs sorted by decreasing score
            measure P_18 -> Bool
            measure AP@N -> Bool
        -o: P_18 score
            AP@N score
        """

        relevant = 0
        recall = 1
        AP_N = 0

        # only look at the relevancy of retrieved docs
        for __, relevance in retrieved_list:
            
            # If relevant at point
            if relevance == 1:
                # For total relevancy
                relevant += 1
                # Add the relevancy of that point to AP@N measure
                AP_N += relevant/recall
            # Increment recall at the end
            recall += 1
        
        P_18 = relevant/recall

        AP_N = AP_N/len(retrieved_list)
        
        # Return condition for given metrics
        if P_18m and AP_Nm:
            return P_18, AP_N

        elif not P_18m:
            return 0, AP_N
            
        elif not AP_Nm:
            return P_18, 0 

    P_18, AP_N = evaluate_system(retrieved_list)

    # Print Title of the book
    print(query)
    # Print Description of the book
    print(book_infos[query]["Description"])
    # Print retrieved recommendations 
    for i, (book, rel) in enumerate(retrieved_list):
        print(f"{i+1}. {book}")
    # Print scores
    print(f"P_18: {P_18}     AP@N: {AP_N}\n")
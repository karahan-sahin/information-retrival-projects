import pickle
import json
import HelperClass

# Read query
query = input("Enter input: ")

# Load inverted index
_inverted_index = open("inverted_index.json", "r")
inverted_index = json.loads(_inverted_index.read())

# Load Trie
_dictionary = open("trie.pickle","rb")
dictionary = pickle.loads(_dictionary.read())

ids = []

# Prefix search
if query.endswith("*"):
    # Remove wildcard 
    query = query[:-1]

    # Get all possible words
    word_list = dictionary.PrefixSearch(query)
    
    # Occurances of all possible words
    total = []

    # Add each occurance to the total
    for word in word_list:

        for ID in inverted_index[word]:

            if ID not in total:
                total.append(ID)

    total.sort()

    print(word_list)
    new = total
    print(total)
    

# Word search 
elif dictionary.search(query):
    new = inverted_index[query]
    print(inverted_index[query])
    

else:
    print("Word is not in the dictionary")

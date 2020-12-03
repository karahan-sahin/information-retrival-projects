import os
import sys
import json
import pickle
import tokenizer
from HelperClass import Trie

# Get directory as argument
path = sys.argv[1]

# Get the files end with .smg
documents = [os.path.join(path,files) for files in os.listdir(path) if files.endswith(".sgm")]

# Create inverted index
file = "inverted_index.json"
f = open(file, "w", encoding="latin-1")

# Get inverted index for each word
inverted_index = {}

# Trie
_dictionary = Trie()

for d in documents:

    document = tokenizer.tokenize(d)

    for ID, content in document.items():

        for tags, in_content in content.items():

            for token in in_content:

                # Try to append the dictionary_items.IDlist
                try:
                    if inverted_index[token][len(inverted_index[token])-1] != ID: 
                        inverted_index[token].append(ID)

                # If key is not found append inverted_index
                except KeyError:
                    inverted_index[token] = [ID]
                    _dictionary.insert(token)

  
# Write on inverted index in JSON Format
x = json.dumps(inverted_index, indent= 1, ensure_ascii=False)
f.write(x)
f.close()

# Pickle trie and write on pickle file
trie_pickle = open("trie.pickle","wb")
pickle.dump(_dictionary, trie_pickle)
trie_pickle.close()
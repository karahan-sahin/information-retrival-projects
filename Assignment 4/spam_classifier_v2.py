import re
import math
from collections import defaultdict

import utilities

import sys
data_path = sys.argv[1]

# Import Training Data
training_data = utilities.import_training_data(data_path)
# Create the Mutual Information table to be used in Feature Selection
MI_dict = defaultdict(lambda: {"n_11": 0,"n_10": 0,"n_01": 0,"n_00": 0})

# Create only the Mega Documents
spam_dict,_ = utilities.parse_spam_docs(training_data["spam"],
                                        MI_dict=MI_dict,
                                        features=True)

legitimate_dict,_ = utilities.parse_legitimate_docs(training_data["legitimate"],
                                                    MI_dict=MI_dict,
                                                    features=True)


def MI_Feature_Selection(top_k):
    """
    This function uses Mutual Information Algorithm based Feature Selection
    which uses all the unique tokens in all "both" classes and hierarchicly order
    them based on their informativeness to select the top k informative features "tokens"
    for a better feature representation of both classes. The function returns the list of top k
    features.
    
    n_[word,class]
    word  -> 1 = docs contain word
             0 = docs doesn't contain word
    class -> 1 = spam
             0 = legitimate
                contains     class    
        n_11 --> word         spam         
        n_10 -->  !        legitimate
        n_01 --> word         spam
        n_10 -->  !        legitimate

    -i: k desired number of features for each class
    -o: feature list
    """
    
    # Create the dictionary tokens with match Mutual Information scores
    MI_scores = defaultdict(int)
    # Number of all documents
    all_docs = len(training_data["spam"] + training_data["legitimate"])

    # Iterate over all tokens and their MI tables
    for token, matrix in MI_dict.items():
        # Number of documents that are classified as spam which does not contain the given token
        matrix["n_01"] = len(training_data["spam"]) - matrix["n_11"] 
        # Number of documents that are classified as legitimate which does not contain the given token
        matrix["n_00"] = len(training_data["legitimate"]) - matrix["n_10"] 
        
        # Calculate MI score
        score = 0
        # Iterate over the table
        for w in range(2):
            for c in range(2):
                try:
                    # Probability of document is at the given condition on the table
                    given_p = (matrix[f'n_{w}{c}']/all_docs)
                    # Probability of document obtaining all the conditions indiviually
                    numerator = (all_docs*matrix[f'n_{w}{c}'])
                    denom = (matrix[f'n_{w}1'] + matrix[f'n_{w}0']) * (matrix[f'n_1{c}'] + matrix[f'n_0{c}'])
                    score += given_p * math.log2(numerator/denom)
                # Handling possible 0 value at the denom
                except (ZeroDivisionError, ValueError): continue

        # If the score is 0, then it is not relevant
        if score == 0: continue
        # If it has positive value at it to the list
        else: MI_scores[token] = score

    # Sorting the scores
    sorted_scores = dict(sorted(MI_scores.items(), key=lambda item: item[1], reverse= True))

    # Selecting top k features
    # Create an empty feature list
    features_list = []
    # Selecting top k spam and legitimate class features
    k_spam = top_k
    k_leg = top_k
    # Iterate over all top scored features
    for word in sorted_scores.keys():
        # If both classes have k number of features
        if k_spam <= 0 and k_leg <= 0: 
            break
        # If the word is in spam class features and there is more to select
        elif word in list(spam_dict.keys()) and k_spam > 0:
            # Append to the feature list
            features_list.append(word)
            # Decrease the number of remaining
            k_spam -= 1
        
        # If the word is in legitimate class features and there is more to select
        elif word in list(legitimate_dict.keys()) and k_leg > 0:
            # Append to the feature list
            features_list.append(word)
            # Decrease the number of remaining
            k_leg -= 1
    
    return features_list

# Fetch the feature list
features_list = MI_Feature_Selection(100)

# Calculate the overall number of tokens 
def token_size(features_list):
    """
    For given feature list, the function calculates the overall number of tokens in mega documents of 
    both classes. Returns individual token size of number of both classes

    -i: feature list: list
    -o: spam mega document token_size: int
        legitimate mega document token_size: int
    """
    # Calculate the number of overall tokens at the spam class mega document after feature selection
    spam_token_size = 0
    # Iterate over count dict of spam mega document
    for word, freq in spam_dict.items():
        # Add to the token size if it is in the feature list
        if word in features_list:
            spam_token_size += freq

    # Calculate the number of overall tokens at the legitimate class mega document after feature selection
    legitimate_token_size = 0
    # Iterate over count dict of legitimate mega document
    for word, freq in legitimate_dict.items():
        # Add to the token size if it is in the feature list
        if word in features_list:
            legitimate_token_size += freq

    return spam_token_size, legitimate_token_size

# Get the number of overall tokens at the both classes' mega document after feature selection
spam_token_size, legitimate_token_size = token_size(features_list)

def Spam_Classifier(test_doc, alpha=1):
    """
    Spam Classifier that Naivie Bayes Algorithm which is trained over 480 e-mails
    either classified as spam or legitimate. The function takes a test document path
    and returns a tuple with document path and classification tag "spam: 1; legitimate: 0"

    In this version, the algorithm uses vocabulary obtained by Mutual Information based feature selection

    -i: test document path: str
    -o: (document path: str, classification tag: int)

    """

    # All unique tokens selected via Feature Selection in the training data 
    vocabulary_size = len(features_list)

    # Prior Probabilities of Classes
    prior_spam = len(training_data["spam"])/len(training_data["spam"] + training_data["legitimate"])
    prior_legitimate = len(training_data["legitimate"])/len(training_data["spam"] + training_data["legitimate"])
   
    # Open the test document
    with open(test_doc, "r", encoding="utf-8") as f_in:
        # Read the test document
        data = f_in.read()

    # Count dictionary for the test document
    count_dict = defaultdict(int)

    # Split data into tokens 
    tokens = re.split(r'\s|\\n',data)

    # Append the dictionary with token and its term frequency
    for token in tokens:
        # If it is one of the top k feature
        if token in features_list:
            count_dict[token] += 1
    
    # Spam 
    sum_prob = 0
    # Iterate over unique token
    for word, freq in count_dict.items():
        # Add the log probability of each token is in class spam   
        sum_prob += math.log10((spam_dict[word]+alpha)/
                                (spam_token_size+(alpha*vocabulary_size))) * freq
    
    # Then add the log of prior probability of document to be in class spam
    spam_prob = math.log10(prior_spam) + sum_prob  

    # Legitimate probability
    sum_prob = 0
    # Iterate over unique token
    for word, freq in count_dict.items():
        # Add the log probability of each token is in class legitimate   
        sum_prob += math.log10((legitimate_dict[word]+alpha)/
                                (legitimate_token_size+(alpha*vocabulary_size))) * freq
    
    # Then add the log of prior probability of document to be in class legitimate
    legitimate_prob = math.log10(prior_legitimate) + sum_prob
    
    # If it has higher probability in class spam
    if spam_prob > legitimate_prob:
        # Classify as spam
        return (test_doc, 1)
    # If not, it is 
    else:
        # Classify as legitimate
        return (test_doc, 0)

# Import test data
test_data = utilities.import_test_data(data_path)
# Run classifier on test data
classifier_results = utilities.run_classifier("v2",test_data)
# Calculate evaluation metrics
macro_precision, recall, f_measure = utilities.evaluation(test_data, classifier_results)

def main():
    # Print the evaluation metrics
    print(f"""Spam Classifier with MI Feature Selection:
        Macro Precision: {macro_precision}
        Recall: {recall}
        F-measure: {f_measure}
        """)
if __name__ == "__main__":
    main()
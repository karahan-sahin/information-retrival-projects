import sys

import re
import math
from collections import defaultdict

import utilities

# Get dataset path
data_path = sys.argv[1]

# Import training data
training_data = utilities.import_training_data(data_path)

# Create the Mega Documents and Get the Token Sizes of each class
spam_megadoc, spam_token_size  = utilities.parse_spam_docs(training_data["spam"])
legitimate_megadoc, legitimate_token_size = utilities.parse_legitimate_docs(training_data["legitimate"])


def Spam_Classifier(test_doc, alpha=1):
    """
    Spam Classifier that Naivie Bayes Algorithm which is trained over 480 e-mails
    either classified as spam or legitimate. The function takes a test document path
    and returns a tuple with document path and classification tag "spam: 1; legitimate: 0"

    In this version, the algorithm uses all the avaible vocabulary without any feature selection

    -i: test document path: str
    -o: (document path: str, classification tag: int)

    """
    # All unique tokens in the training data
    vocabulary_size = len(set(list(spam_megadoc.keys())+list(legitimate_megadoc.keys())))
    
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

    # Append term frequency for each token
    for token in tokens:
        count_dict[token] += 1
    
    # Spam probability
    sum_prob = 0
    # Iterate over unique token
    for word, freq in count_dict.items():
        # Add the log probability of each token is in class spam   
        sum_prob += math.log10((spam_megadoc[word]+alpha)/
                                (spam_token_size+(alpha*vocabulary_size))) * freq
    
    # Then add the log of prior probability of document to be in class spam
    spam_prob = math.log10(prior_spam) + sum_prob  

    # Legitimate probability
    sum_prob = 0
    # Iterate over unique token
    for word, freq in count_dict.items():
        # Add the log probability of each token is in class legitimate   
        sum_prob += math.log10((legitimate_megadoc[word]+alpha)/
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
classifier_results = utilities.run_classifier("v1",test_data)
# Calculate evaluation metrics
macro_precision, recall, f_measure = utilities.evaluation(test_data, classifier_results)

def main():
    # Print scores
    print(f"""Spam Classifier without Feature Selection:
        Macro Precision: {macro_precision}
        Recall: {recall}
        F-measure: {f_measure}
        """)
if __name__ == "__main__":
    main()
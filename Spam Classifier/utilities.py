import os
import re
from collections import defaultdict

# Training data
def import_training_data(directory):
    """
    Imports training data in the format\n
    keys -> "spam" "legitimate"\n
    values -> [spam document paths], [legitimate document paths]

    -i: dataset file path
    -o: dictionary contaning training data item paths
    """
    # Create the dictionary
    training_data = defaultdict(list)
    # conjoin spam text names with its current folder directory
    training_data["spam"] = [os.path.join(f"{directory}\\training\\spam",f) 
                            for f in os.listdir(f"{directory}\\training\\spam")
                            if f.endswith("txt")]
    # conjoin legitimate text names with its current folder directory
    training_data["legitimate"] = [os.path.join(f"{directory}\\training\\legitimate",f) 
                            for f in os.listdir(f"{directory}\\training\\legitimate")
                            if f.endswith("txt")]

    return training_data

# Test data
def import_test_data(directory):
    """
    Imports test data in the format\n
    keys -> "spam" "legitimate"\n
    values -> [spam document paths], [legitimate document paths]

    -i: dataset file path
    -o: dictionary contaning test data item paths
    """
    # Create the dictionary
    test_data = defaultdict(list)
    # conjoin spam text names with its current folder directory
    test_data["spam"] = [os.path.join(f"{directory}\\test\\spam",f)
                            for f in os.listdir(f"{directory}\\test\\spam")
                            if f.endswith("txt")]

    # conjoin legitimate text names with its current folder directory
    test_data["legitimate"] = [os.path.join(f"{directory}\\test\\legitimate",f)
                            for f in os.listdir(f"{directory}\\test\\legitimate")
                            if f.endswith("txt")]

    return test_data


# Spam Mega Doc
def parse_spam_docs(spam_docs,MI_dict = defaultdict(),features = False):
    """
    Parsing spam docs at the training data returns an count dictionary vector
    of spam mega document to used in NB algorithm.
    If want to use Mutual Information based Feature Selection, must give a separate
    MI dictionary in the format:

        MI_dict = defaultdict(lambda: {"n_11": 0, "n_10": 0, "n_01": 0, "n_00": 0})
    
    for probability table and giving features argument True value. Then the function
    adds the n_11 score of each token.

    -i: spam documents file list
        MI dictionary (optional)
        feature (optional) (default: False)
    -o: count dictionary vector
        total token size
    
    """
    # Create an empty count dictionary for mega document
    spam_megadoc = defaultdict(int)
    # Iterate over spam documents
    for spam in spam_docs:
        # Open the document
        with open(spam, "r", encoding="utf-8") as f_in:
            # Read the document as a string
            data = f_in.read()
            # Split the document into tokens
            tokens = re.split(r'\s|\\n',data)
            # For each token append its frequency in mega document
            for token in tokens:
                spam_megadoc[token] += 1

            # If MI feature selection applied
            if features:
                # For each unique word appends its spam document frequency
                for token in list(set(tokens)):
                    # Append if doc contains word --> doc_freq of word in class spam
                    MI_dict[token]["n_11"] += 1

    # Calculate the total number of individual tokens in the spam megadocument
    spam_token_size = 0
    for freq in spam_megadoc.values():
        spam_token_size += freq

    return spam_megadoc, spam_token_size

# Legitimate Mega Doc
def parse_legitimate_docs(legitimate_docs,MI_dict = defaultdict(),features = False):
    """
    Parsing legitimate docs at the training data returns an count dictionary vector
    of legitimate mega document to used in NB algorithm.
    If want to use Mutual Information based Feature Selection, must give a separate
    MI dictionary in the format:

        MI_dict = defaultdict(lambda: {"n_11": 0, "n_10": 0, "n_01": 0, "n_00": 0})
    
    for probability table and giving features argument True value. Then the function
    adds the n_10 score of each token.

    -i: legitimate documents file list: list
        MI dictionary (optional): defaultdict()
        feature (optional) (default: False): boolean
    -o: count dictionary vector: defaultdict() 
        total token size: int
    
    """
    # Create an empty count dictionary for mega document
    legitimate_megadoc = defaultdict(int)
    # Iterate over Legitimate documents
    for spam in legitimate_docs:
        # Open the document
        with open(spam, "r", encoding="utf-8") as f_in:
            # Read the document as a string
            data = f_in.read()
            # Split the document into tokens
            tokens = re.split(r'\s|\\n',data)
            # For each token append its frequency in mega document
            for token in tokens:
                legitimate_megadoc[token] += 1

            # If MI feature selection applied
            if features:  
                # For each unique word appends its Legitimate document frequency
                for token in list(set(tokens)):
                    # Append if doc contains word --> doc_freq of word in class legitimate
                    MI_dict[token]["n_10"] += 1


    # Calculate the total number of individual tokens in the Legitimate mega document
    legitimate_token_size = 0
    for freq in legitimate_megadoc.values():
        legitimate_token_size += freq


    return legitimate_megadoc, legitimate_token_size

def evaluation(test_data, classifier_results):
    """
    Evaluating the classifier results on the test dataset
    Returns the macro precision, recall, and f-measure scores

    -i: test data: defaultdict(lambda: {"spam": [paths], "legitimate": [paths]})
        classifier output: list

    -o: macro precision score: float
        recall score: float
        f-measure score: float

    """

    #True Positive Spam
    tp_spam = 0
    #False Positive Legitimate
    fp_leg = 0
    
    #True Positive Legitimate
    tp_leg = 0
    #False Positive Spam
    fp_spam = 0

    # Iterate over classified docs
    for result in classifier_results:
        # If the classified document is in spam docs
        if result[0] in test_data["spam"]:
            # Check if it is classified correctly
            if result[1] == 1:
                # It is a True positive
                tp_spam += 1
            # If it is classified as legitimate document
            # although it is a spam document
            else:
                # It is a False Positive
                fp_leg += 1
        
        # If the classified document is in spam docs
        elif result[0] in test_data["legitimate"]:
            # Check if it is classified correctly
            if result[1] == 0:
                # It is a True positive
                tp_leg += 1
            # If it is classified as legitimate document
            # although it is a spam document
            else:
                # It is a False Positive
                fp_spam += 1


    # If the classifier doesn't classify any document as spam
    try:
        spam_precision = float(tp_spam / (tp_spam + fp_spam))
    except ZeroDivisionError:
        spam_precision = 0
   
    # If the classifier doesn't classify any document as legitimate
    try:
        legitimate_precision = float(tp_leg / (tp_leg + fp_leg))
    except ZeroDivisionError:
        legitimate_precision = 0

    # Recall fraction of documents classified correctly out of all the documents that are classified
    recall = float((tp_spam + tp_leg) / (len(test_data["spam"] + test_data["legitimate"])))
    # Average of scores of precisions for each class 
    macro_precision = (spam_precision + legitimate_precision) / 2
    # Calculate the F-measure score
    f_measure = (2*macro_precision*(recall)) / (macro_precision + (recall))

    return macro_precision, recall, f_measure


def run_classifier(version: str,test_data, a=1):
    """
    Runs the classifiers on the test set

    -i: version of the classifier "v1" or "v2"
    -o: results from classifier document
    """
    # Empty list of results
    classifier_results = []
    # If the version is without feature selection
    if version == "v1":
        # Import the classifier if the condition is met 
        # in order to remove circularity issue
        from spam_classifier_v1 import Spam_Classifier as v1

        # Run on Spam docs
        for tspam in test_data["spam"]:
            result = v1(tspam, alpha=a)
            classifier_results.append(result)

        # Run on Legitimate docs
        for tspam in test_data["legitimate"]:
            result = v1(tspam, alpha=a)
            classifier_results.append(result)
    
    # If the version is with feature selection
    if version == "v2":
        # Import the classifier if the condition is met 
        # in order to remove circularity issue
        from spam_classifier_v2 import Spam_Classifier as v2

        # Run on Spam Docs
        for tspam in test_data["spam"]:
            result = v2(tspam,alpha=a)
            classifier_results.append(result)

        # Run on Legitimate Docs 
        for tspam in test_data["legitimate"]:
            result = v2(tspam, alpha=a)
            classifier_results.append(result)

    return classifier_results
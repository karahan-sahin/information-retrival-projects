import sys

import random

import spam_classifier_v1
import spam_classifier_v2

from utilities import import_test_data, evaluation

# Fetch the path
data_path = sys.argv[1]

# Import the classifier results 
model1_results = spam_classifier_v1.classifier_results
model2_results = spam_classifier_v2.classifier_results
# Import the test results
test_data = import_test_data(data_path)
# Prior test statics of the difference between F-measures of 2 classifier versions
test_stats = abs(spam_classifier_v1.f_measure - spam_classifier_v2.f_measure)

# Number of times that the randomization test will occur
r = 1000
# Number of times the null hypothesis(two systems are the same) is more likely
counter = 0
for _ in range(r):
    # Generate 240 random indices that the results of two models is going to be interchanged
    random_indices = sorted(random.sample(range(480), 240))

    # Append the random indiced items between each system
    a_results = [model2_results[i] if i in random_indices else model1_results[i] for i in range(480)]
    b_results = [model1_results[i] if i in random_indices else model2_results[i] for i in range(480)]

    # Calculate the f-measures of the two shuffled systems
    _,_,a_score = evaluation(test_data,a_results)
    _,_,b_score = evaluation(test_data,b_results)

    # Calculate Pseudo Statistics of the difference between 
    pseudo_stats = abs(a_score - b_score)
    # If the null hypothesis is more prominent
    if pseudo_stats >= test_stats:
        counter += 1

# Calculate the p-value of randomization test 
p_value = (counter+1) / (r+1)
print(f"p-value of Randomization Test: {p_value}")
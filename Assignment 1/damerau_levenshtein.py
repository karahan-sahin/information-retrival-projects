import numpy as np
import pandas as pd


string_1 = input("String 1: ")
string_2 = input("String 2: ")

# Not to change the string before the first string
max_dist = len(string_1) + len(string_2)

# Matrix with All 0's for edit table
table = np.zeros((len(string_1)+2, len(string_2)+2),dtype=int)


# Fill max_dist and Default costs 
for i in range(0,len(string_1)+2):
    table[i,0] = max_dist
    table[i,1] = i-1

for j in range(len(string_2)+2):
    table[0,j] = max_dist
    if j != 0:
        table[1,j] = j-1


# Table values starts at table[2,2]
for i in range(2,len(string_1)+2):

    for j in range(2,len(string_2)+2):
        #Default --> Replace
        rc = 1

        # If they are the same character
        if string_1[i-2] == string_2[j-2]:
            rc = 0
            
        # Minimum of operations
        table[i,j] = min(table[i-1,j]+1,    # deletion
                         table[i,j-1]+1,    # insertion
                         table[i-1,j-1]+rc  # replacement/copy
                         )
        
        # Transposition condition 
        if string_1[i-2] == string_2[j-3] and string_1[i-3] == string_2[j-2]:
            
            table[i,j] = min(table[i,j], table[i-2,j-2] + rc)




# The last cell
damerau_levenshtein_distance = table[len(string_1)+1, len(string_2)+1]


# LEVENSHTEIN EDIT TABLE

# Row names
indexes = ["",""]
for i in string_1:
    indexes.append(i)

# Column names
column = ["", ""]
for j in string_2:
    column.append(j)



damerau_levenshtein_matrix = pd.DataFrame(data=table, index=indexes, columns=column, dtype=int)

# Operations = [cost, operation, input, output]
operation_column = []

# Backtrace start last cell table[]
i = len(string_1)+1
j = len(string_2)+1

# Backtrace loop
while True:
    
    current_cell = table[i,j]

    #Transposition
    if current_cell == table[i-2,j-2] + 1 and string_1[i-2] == string_2[j-3] and string_1[i-3] == string_2[j-2]:

        # Go to Last Copy cell
        i -= 2
        j -= 2

        operation_column.append([1, "transpose", string_1[i]+string_1[i-1], string_1[i-1]+string_1[i]])

        continue

    
    # Deletion
    elif current_cell == table[i-1,j]+1:
        
        # Go to Above
        i -= 1

        operation_column.append([1, "delete", string_1[i-1], "*"])

        continue

    # Insertion
    elif current_cell == table[i,j-1]+1:

        # Go to Left
        j -= 1

        operation_column.append([1, "insert", "*", string_2[j-1]])        

        continue

    # Replace
    elif current_cell == table[i-1,j-1]+1:

        # Go to Upper Left
        i -= 1
        j -= 1

        operation_column.append([1, "replace", string_1[i-1], string_2[j-1]])

        continue
    
    # Copy
    elif current_cell == table[i-1,j-1]:

        # Go to Upper Left
        i -= 1
        j -= 1

        operation_column.append([0, "copy", string_1[i-1], string_2[j-1]])

        continue

    
    else:
        break


# Operations from the beginning of the word
operation_column.reverse()

# Operations data frame
operation_df = pd.DataFrame(data=operation_column, index=None, columns=["cost","operation","input","output"])


print("Damerau-Levenshtein edit distance: {}".format(damerau_levenshtein_distance))
print("\n")
print(damerau_levenshtein_matrix)
print("\n")
print(operation_df)


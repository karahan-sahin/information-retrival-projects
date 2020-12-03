import numpy as np
import pandas as pd


string_1 = input("String 1:")
string_2 = input("String 2:")

# Matrix with All 0's for edit table
table = np.zeros((len(string_1)+1, len(string_2)+1),dtype=int)

# Fill the deletion - col 0
for i in range(len(string_1)+1):
    table[i,0] = i

# Fill the insertion - row 0
for j in range(len(string_2)+1):
    table[0,j] = j

for i in range(1,len(string_1)+1):
    for j in range(1,len(string_2)+1):
        # Default replace
        rc = 1 # cost of either replace or copy
        # If copy, no cost
        if string_1[i-1] == string_2[j-1]:
            rc = 0
        table[i,j] = min(table[i-1,j]+1,    # deletion
                         table[i,j-1]+1,    # insertion
                         table[i-1,j-1]+rc  # substitution
                         )


# The last cell
levenshtein_distance = table[len(string_1), len(string_2)]

# LEVENSHTEIN EDIT TABLE

# Row names
indexes = [" "]
for i in string_1:
    indexes.append(i)

# Column names
column = [""]
for j in string_2:
    column.append(j)


levenshtein_matrix = pd.DataFrame(data=table, index=indexes, columns=column, dtype=int)

# Operations = [cost, operation, input, output] 
operation_column = []

# Beginning of backtrace table[i,j]
i = len(string_1)
j = len(string_2)

# Backtrace loop
while True:
    
    current_cell = table[i,j]
    
    # Deletion
    if current_cell == table[i-1,j]+1:
        
        # Above
        i -= 1

        operation_column.append([1, "delete", string_1[i], "*"])

        continue

    # Insertion
    elif current_cell == table[i,j-1]+1:

        # Left
        j -= 1

        operation_column.append([1, "insert", "*", string_2[j]])
        
        continue

    # Replace
    elif current_cell == table[i-1,j-1]+1:

        # Upper Left
        i -= 1
        j -= 1

        operation_column.append([1, "replace", string_1[i], string_2[j]])

        continue
    
    # Copy
    elif current_cell == table[i-1,j-1]:

        # Upper Left
        i -= 1
        j -= 1

        operation_column.append([0, "copy", string_1[i], string_2[j]])

        continue

    else:
        break

# Operations from the beginning of the word
operation_column.reverse()

operation_df = pd.DataFrame(data=operation_column, index=None, columns=["cost","operation","input","output"])


print("Levenshtein edit distance: {}".format(levenshtein_distance))
print("\n")
print(levenshtein_matrix)
print("\n")
print(operation_df)
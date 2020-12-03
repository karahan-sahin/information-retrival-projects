# Assignment 2



Python version

````python
pyhton --version
Python 3.7.9
````



The program runs two main scripts


1. First run `prep.py` with the directory of folder includes Reuters files

`````python
python prep.py <input-directory>
`````

After the run, `inverted_index.json` and `trie.pickle` are created

​		2. Run `query.py` and give your input as two forms

- $word$
- $prefix_{1}*$

````python
python query.py
"Enter query: "
````

The program will print 

- the inverted index of word 
- the inverted index of words start with the prefix
- If the word is not found in the dictionary, prints an error message
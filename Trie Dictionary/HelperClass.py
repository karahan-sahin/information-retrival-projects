class Trie_Node:
    def __init__(self):
        self.children = {}
        self.isend = False


class Trie:

    def __init__(self):
        self.root = Trie_Node()

    def insert(self, word: str):
        current_node = self.root

        for letter in word:
            if letter not in current_node.children:
                current_node.children[letter] = Trie_Node()
            current_node = current_node.children[letter]
        current_node.isend = True

    def search(self, word: str):
        current_node = self.root

        for letter in word:
            if letter not in current_node.children:
                return False
            current_node = current_node.children[letter]

        if current_node.isend == True:
            return True
        else:
            return False

    def startWith(self, prefix: str):
        # -i: prefix: str
        # -o: the current node of the prefix

        current_node = self.root

        for letter in prefix:
            if letter not in current_node.children:
                return False

            current_node = current_node.children[letter]

        return current_node

    def PrefixSearch(self, prefix: str):
        # -i: prefix: str
        # -o: word_list: list

        word_list = []

        current_node = self.startWith(prefix= prefix)

        # Traverse the tree and Finds a word, appends the word list
        def findEach(node, word):
            if node.isend:
                word_list.append(word)

            for a, n in node.children.items():
                findEach(n, word + a)

        findEach(current_node, prefix)

        return word_list

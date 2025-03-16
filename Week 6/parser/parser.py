import nltk
nltk.download('punkt_tab')
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | S Conj S | NP VP SubConj S
NP -> Det N | N | NP PP | Det Adj N | Det AP N
AP -> Adj | Adj AP
VP -> V | V NP | VP PP | Adv VP | V NP Adv | VP Conj VP | V Adv | VP Adv
PP -> P NP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """

    # Convert Sentences to a list of its words
    words = nltk.word_tokenize(sentence)

    # Lowercase
    words = [word.lower() for word in words]

    # Filter Words
    filtered_words = [word for word in words if any(c.isalpha() for c in word)]

    return filtered_words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """

    np_chunks = []

    # Take the subtee with NP label
    for subtree in tree.subtrees(lambda x: x.label() == "NP"):
        
        # Ensure no more smaller NP inside
        if not any(child.label() == "NP" for child in subtree.subtrees(lambda x: x != subtree)):

            # Valid np chunk
            np_chunks.append(subtree)

    return np_chunks


if __name__ == "__main__":
    main()

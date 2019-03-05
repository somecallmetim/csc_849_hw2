import PositionalInvertedIndexConstr
from nltk.stem import PorterStemmer

#create inverted index to use throughout program
invertedIndex = PositionalInvertedIndexConstr.createPositionalInvertedIndex()

# set up file pointers to create/overwrite files for inverted index and search results
indexFile = open("Inverted_Index.txt", "w+")
resultFile = open("Results_File.txt", "w+")

# set up var for stemming
stemmer = PorterStemmer()

print(type(invertedIndex))

# write inverted index into file with easy to read format
for term in invertedIndex:
    # this var gives us access to object that stores things like postings lists & term doc freq for given term
    termData = invertedIndex[term]
    # posting list for the current term
    postingList = termData.getPostingList()

    # prints/writes term name and df_t
    print(term + " : " +  str(termData.getDocumentFrequency()))
    indexFile.write((term + " : " +  str(termData.getDocumentFrequency())) + "\r")

    # for loop gets each docId associated with term and prints out term positions & frequencies
    for docId in postingList:
        # prints/writes docId & freq of term in that specific doc
        print("\t" + docId + ", " + str(postingList[docId].getTermDocumentFrequency()) + " :", end =" ")
        indexFile.write("\t" + docId + ", " + str(postingList[docId].getTermDocumentFrequency()) + " : ")
        # prints out a list of each numerical position of the term in the doc
        for wordPosition in postingList[docId].getTermPositionList():
            print(" " + str(wordPosition) + ",", end ="")
            indexFile.write(" " + str(wordPosition) + ",")
        print("\r")
        indexFile.write("\r")
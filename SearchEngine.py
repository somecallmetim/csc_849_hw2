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
for item in invertedIndex:

    termData = invertedIndex[item]
    postingList = termData.getPostingList()
    print(item + " : " +  str(termData.getDocumentFrequency()))
    indexFile.write((item + " : " +  str(termData.getDocumentFrequency())) + "\r")

    for docId in postingList:
        print("\t" + docId + " :", end =" ")
        indexFile.write("\t" + docId + " : ")
        for wordPosition in postingList:
            print(" " + wordPosition + ",", end ="")
            indexFile.write(" " + wordPosition + ",")
        print("\r")
        indexFile.write("\r")


    # indexFile.write("\r\t" + str(invertedIndex[item].getFrequency()))
    # indexFile.write("\r\t" + str(invertedIndex[item].getPostingList()) + "\r\r")
import PositionalInvertedIndexConstr
import math
from nltk.stem import PorterStemmer

class ComplexSearchTerm:
    def __init__(self, name, docId):
        self.__name = name
        self.__df_t= 0
        # posting list will contain docId and tf inside the doc associated with docId
        self.__postingList = {}

        self.addPosting(docId)

    def addPosting(self, docId):
        if docId not in self.__postingList:
            self.__postingList[docId] = 1
            self.__df_t += 1
        else:
            self.__postingList[docId] += 1

    def getDf_f(self):
        return self.__df_t

    def get_tf(self, docId):
        if docId in self.__postingList:
            return self.__postingList[docId]
        else:
            return -1

def findComplexQueries(queryString, complexQueryList):
    startOfComplexQuery = queryString.find("(")
    if startOfComplexQuery != -1:
        numOfWordsBetween = queryString[startOfComplexQuery - 1]
        endOfComplexQuery = queryString.find(")")

        complexQuery = queryString[startOfComplexQuery - 1:endOfComplexQuery + 1]

        queryString = queryString.replace(complexQuery, "")
        complexQueryList.append(complexQuery)

        return findComplexQueries(queryString, complexQueryList)

    else:
        return queryString

def parseSearchQuery(queryString):
    searchTerms = []
    complexSearchTerms = []

    # print(" - " + queryString + " - ")

    queryString = findComplexQueries(queryString, complexSearchTerms)

    # for searchTerm in complexSearchTerms:
    #     print("=== " + searchTerm + " ===")

    # print("*** " + queryString + " ***")

    for term in queryString.split():
        # print(term)
        searchTerms.append(term)

    return [searchTerms, complexSearchTerms]

def simpleSearch(queryList, documentList):
    
    for term in queryList:
        # makes the term all lower case
        term = str(term).lower()
        # stems the now lower case and punctuation free word
        term = stemmer.stem(term)

        if term in invertedIndex:
            tempPostingLIst = invertedIndex[term].getPostingList()
            for key in tempPostingLIst:
                if key not in documentList:
                    documentList.append(key)

def complexSearch(queryList, complexSearchTermData, documentList):
    index = 0
    for term in queryList:
        allowableSeparation = int(term[0])
        cleanedUpTerm = term[2:len(term)-1]
        queryList[index] = cleanedUpTerm

        tempQueryList = list(queryList[0].split(" "))

        # initiate complext search if both query terms exist in positional inverted index
        if tempQueryList[0] in invertedIndex and tempQueryList[1] in invertedIndex:

            # get posting lists for both terms
            firstTermPostingList = invertedIndex[tempQueryList[0]].getPostingList()
            secondTermPostingList = invertedIndex[tempQueryList[1]].getPostingList()

            # iterate through each docId associated with the first term
            for docId in firstTermPostingList:
                # check to see if the current document being looked at exists in the second terms document list
                if docId in secondTermPostingList:

                    # get position list for both terms
                    firstTermPositionList = firstTermPostingList[docId].getTermPositionList()
                    secondTermPositionList = secondTermPostingList[docId].getTermPositionList()

                    # get length of second term's posting to list to avoid boundary errors
                    lengthOfSecondTermList = len(secondTermPostingList)
                    # get iterator for second term's position list
                    pointerForSecondTermList = 0

                    # check each document to see if it's a match based on search terms and allowed separation
                    for position in firstTermPositionList:

                        # make sure we haven't overshot the boundary of the second term position list AND
                            # skip over positions in the second list until position 2 > position 1
                            # Note: if the second position isn't bigger than the first position, by default it won't
                            #       math our search query
                        while(pointerForSecondTermList <= lengthOfSecondTermList and
                              position > secondTermPositionList[pointerForSecondTermList]):
                            # increment pointerForSecondTermList
                            pointerForSecondTermList += 1

                        # check if position 2 is close enough to position 1 to register as a search hit
                        if (position - secondTermPositionList[pointerForSecondTermList]) <= allowableSeparation:
                            if docId not in documentList:
                                documentList.append(docId)
                            if cleanedUpTerm not in complexSearchTermData:
                                complexSearchTermData[cleanedUpTerm] = ComplexSearchTerm(cleanedUpTerm, docId)
                            else:
                                complexSearchTermData[cleanedUpTerm].addPosting(docId)

        index += 1

#create inverted index to use throughout program
invertedIndex = PositionalInvertedIndexConstr.createPositionalInvertedIndex()

# set up file pointers to create/overwrite files for inverted index and search results
indexFile = open("Inverted_Index.txt", "w+")
resultFile = open("Results_File.txt", "w+")

# set up var for stemming
stemmer = PorterStemmer()


# write inverted index into file with easy to read format
for term in invertedIndex:
    # this var gives us access to object that stores things like postings lists & term doc freq for given term
    termData = invertedIndex[term]
    # posting list for the current term
    postingList = termData.getPostingList()

    # prints/writes term name and df_t
    # print(term + " : " +  str(termData.getDocumentFrequency()))
    indexFile.write((term + " : " +  str(termData.getDocumentFrequency())) + "\r")

    # for loop gets each docId associated with term and prints out term positions & frequencies
    for docId in postingList:
        # prints/writes docId & freq of term in that specific doc
        # print("\t" + docId + ", " + str(postingList[docId].getTermDocumentFrequency()) + " :", end =" ")
        indexFile.write("\t" + docId + ", " + str(postingList[docId].getTermDocumentFrequency()) + " : ")
        # prints out a list of each numerical position of the term in the doc
        for wordPosition in postingList[docId].getTermPositionList():
            # print(" " + str(wordPosition) + ",", end ="")
            indexFile.write(" " + str(wordPosition) + ",")
        # print("\r")
        indexFile.write("\r")

# set up search terms for this toy example
searchTerms = [
    # "nexus like love happy",
    # "asus repair",
    "0(touch screen) fix repair",
    "1(great tablet) 2(tablet fast)",
    # "tablet"
]



for queryString in searchTerms:

    docList = []
    docListAndScore = {}
    docListByScore = []
    totalNumberOfDocuments = 10.0

    # get simple and complex search terms
    tempSearchTermResults = parseSearchQuery(queryString)
    simpleSearchTerms = tempSearchTermResults[0]
    complexSearchTerms = tempSearchTermResults[1]
    allSearchTerms = simpleSearchTerms + complexSearchTerms

    # get doc list for simple search terms
    simpleSearch(simpleSearchTerms, docList)

    # will help track df_t & idf for complex search terms
    complexSearchTermData = {}

    complexSearch(complexSearchTerms, complexSearchTermData, docList)

    # get doc list for complex search terms
    # calculate idf
        # idf for each term -> log(N/df_t)
            # get document frequency for each term (df_t) from TermInPositionalInvertedIndex in PositionalInvertedIndexConstr.py
            # need total number of documents
    # calculate tf-idf score for each doc
        # tf -> 1 + log(tf)
        # tf-idf -> (1 + log(tf)) * log(N/df_t)

    resultFile.write(queryString + "\r")
    print(queryString)
    for docId in docList:
        docScore = 0
        for term in allSearchTerms:
            # makes the term all lower case
            term = str(term).lower()
            # stems the now lower case and punctuation free word
            term = stemmer.stem(term)
            tempPostingList = invertedIndex[term].getPostingList()

            if docId in tempPostingList:
                tf = tempPostingList[docId].getTermDocumentFrequency()
                df_t = invertedIndex[term].getDocumentFrequency()

                idf = math.log(totalNumberOfDocuments/df_t,10)

                tf_idf = (1 + math.log(tf, 10)) * idf

                docScore += tf_idf

        docListAndScore[docId] = docScore

        resultFile.write("\tdocument " + str(docId) + " score : " + str(docScore) + "\r")
        print("\tdocument " + str(docId) + " score : " + str(docListAndScore[docId]))


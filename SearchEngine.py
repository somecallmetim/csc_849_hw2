import PositionalInvertedIndexConstr
import math
import operator
from nltk.stem import PorterStemmer


# class temporarily tracks df_t & tf for complex search terms
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

    def getDf_t(self):
        return self.__df_t

    def get_tf(self, docId):
        if docId in self.__postingList:
            return self.__postingList[docId]
        else:
            return -1

    def getPostingList(self):
        return self.__postingList


# detects and parses the complex portions of a query string
def findComplexQueries(queryString, complexQueryList):
    # complex queries are of the form n(term1 term2) where 'n' is the max number of words allowed between the terms
        # this first bit finds the position of the first '('
    startOfComplexQuery = queryString.find("(")
    # find() returns -1 if it can't find the requested token
    if startOfComplexQuery != -1:
        endOfComplexQuery = queryString.find(")")

        # gives us the portion of the query string that follows the 'n(term1 term2)' format
        complexQuery = queryString[startOfComplexQuery - 1:endOfComplexQuery + 1]

        # replaces 'n(term1 term2)' in the original query with an empty string
        queryString = queryString.replace(complexQuery, "")
        # adds the 'n(term1 term2)' string the the complex query list
        complexQueryList.append(complexQuery)

        # calls this function recursively until all complex strings are found, added to the appropriate list, & removed
            # from the query string
        return findComplexQueries(queryString, complexQueryList)

    else:
        # returns original query string minus all complex terms in the form of 'n(term1 term2)'
        return queryString


# parses the query string to pull out of the the simple and complex search terms
def parseSearchQuery(queryString):
    # list that stores simple search terms
    searchTerms = []
    # list that stores complex search terms in the form of 'n(term1 term2)'
    complexSearchTerms = []
    # finds and removes all complex search terms in the form of 'n(term1 term2)'
        # (see findComplexQueries() for description)
    queryString = findComplexQueries(queryString, complexSearchTerms)

    # split all simple search terms into individual strings and add tham to searchTerms list
    for term in queryString.split():
        searchTerms.append(term)

    # return lists for both simple and complex search terms
    return [searchTerms, complexSearchTerms]


# finds all docs that contain at least one simple search terms and put's their doc id's into a list
def simpleSearch(queryList, documentList):

    # looks for each simple search term in our positional inverted index
    for term in queryList:
        # makes the term all lower case
        term = str(term).lower()
        # stems the now lower case and punctuation free word
        term = stemmer.stem(term)

        # if the term exists in our positional inverted index, attempts to add its posting list to our document list
        if term in invertedIndex:
            # create a temporary posting list from the current search term
            tempPostingLIst = invertedIndex[term].getPostingList()
            # iterate through each doc id in our temporary posting list
            for key in tempPostingLIst:
                # make sure the doc id isn't already in our document list
                if key not in documentList:
                    # adds the doc id to our doc list if it wasn't already there
                    documentList.append(key)

# finds all docs that contain hits to our complex search terms
def complexSearch(queryList, complexSearchTermData, documentList):
    # we keep track of the index to allow us to manipulate the query list that was passed in so we only have
        # to do our stemming and other string clean up work in just one place. This is by no means the cleanest
        # way to do this, but I ran out of time to go back and come up with a cleaner implementation
    index = 0
    # parse and do search for every complex term in our query list
    for term in queryList:
        # you have to add a 1 to "allowable separation" to prevent off by one errors
            # ie 0 allowable separation only yields results when the two terms are identical ie 0(test test)
            # when it should yield results for 0(term1 term2) when they are directly next to one another
        allowableSeparation = int(term[0]) + 1
        # terms come in the form 'n(term1 term2)'. This strips off the extraneous data & punctuation to leave
            # only 'term1 term2'
        cleanedUpTerm = term[2:len(term)-1]
        # replaces n(term1 term2) in our original query list with 'term1 term2'
        queryList[index] = cleanedUpTerm

        # splits our query string into individual terms so we can stem and otherwise parse
        tempQueryList = list(queryList[index].split(" "))

        tempString = ""

        # this for loop does our stemming & then also adds the updated terms back into our original query list
        for term in tempQueryList:
            # have to stem and lower case the terms here so they match the positional inverted index
            # makes the term all lower case
            term = str(term).lower()
            # stems the now lower case and punctuation free word
            term = stemmer.stem(term)

            # if tempString is empty, puts the term in
            if tempString == "":
                tempString = term
            # if there is at least one term already in tempString, adds a space and the current term to the string
            else:
                tempString = tempString + " " + term

        # adds the stemmed lower case terms back into our original query list
        queryList[index] = tempString

        # initiate complex search if both query terms exist in positional inverted index
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
                    lengthOfSecondTermList = len(secondTermPositionList)
                    # get iterator for second term's position list
                    pointerForSecondTermList = 0

                    # check each document to see if it's a match based on search terms and allowed separation
                    for positionOfFirstTerm in firstTermPositionList:
                        # make sure we haven't overshot the boundary of the second term position list AND
                            # skip over positions in the second list until position 2 > position 1
                            # Note: if the second position isn't bigger than the first position, by default it won't
                            #       math our search query
                        while(positionOfFirstTerm > secondTermPositionList[pointerForSecondTermList]):

                            # increment pointerForSecondTermList
                            pointerForSecondTermList += 1

                            # make sure we don't overshoot our boundary
                            if(pointerForSecondTermList >= lengthOfSecondTermList):
                                # point our pointer at the last item in our secondTermPositionList
                                pointerForSecondTermList = lengthOfSecondTermList - 1
                                break

                        # check if position 2 is close enough to position 1 to register as a search hit
                            # Note: both checks here are necessary as the pointer defaults to pointing at the last
                            #       index in the second position list & that value may be smaller than the position of
                            #       the first term. This is not the cleanest way to do this, but I ran out of time
                            #       to clean it up
                        if (positionOfFirstTerm < secondTermPositionList[pointerForSecondTermList] and secondTermPositionList[pointerForSecondTermList] - positionOfFirstTerm <= allowableSeparation):
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

    # writes term name and df_t
    indexFile.write((term + " : " +  str(termData.getDocumentFrequency())) + "\r")

    # for loop gets each docId associated with term and prints out term positions & frequencies
    for docId in postingList:
        # writes docId & freq of term in that specific doc
        indexFile.write("\t" + docId + ", " + str(postingList[docId].getTermDocumentFrequency()) + " : ")
        # writes out a list of each numerical position of the term in the doc
        for wordPosition in postingList[docId].getTermPositionList():
            indexFile.write(" " + str(wordPosition) + ",")
        indexFile.write("\r")

# set up search terms for this toy example
searchTerms = [
    "nexus like love happy",
    "asus repair",
    "0(touch screen) fix repair",
    "1(great tablet) 2(tablet fast)",
    "tablet"
]


# run search for each query string in the above list of search strings
for queryString in searchTerms:
    # keeps track of documents that have search hits
    docList = []
    # lets us track of document scores
    docListAndScore = {}
    # in this toy example there are exactly 10 "documents." We need this number in future calculations
    totalNumberOfDocuments = 10.0

    # get simple and complex search terms
    tempSearchTermResults = parseSearchQuery(queryString)
    simpleSearchTerms = tempSearchTermResults[0]
    complexSearchTerms = tempSearchTermResults[1]

    # get doc list for simple search terms
    simpleSearch(simpleSearchTerms, docList)

    # will help track df_t & idf for complex search terms
    complexSearchTermData = {}

    # get doc list for complex search terms
    complexSearch(complexSearchTerms, complexSearchTermData, docList)

    # combine doc lists for simple and complex search terms
    allSearchTerms = simpleSearchTerms + complexSearchTerms

    # write/print original query string to console and Results_File.txt
    resultFile.write(queryString + "\r")
    print(queryString)

    # here doclist gives us every document that has at least one of the search terms in it, whether simple or complex
        # however, none of the documents have been scored. This is where we do that work
    for docId in docList:
        # every document's score starts off at zero
        docScore = 0
        # this loop will add up the document's score for every term in the original query
        for term in allSearchTerms:
            # simple & complex terms are handled very differently. This block handles scoring of simple terms
            if term not in complexSearchTerms:

                # have to stem and lower case the terms here so they match the positional inverted index
                # makes the term all lower case
                term = str(term).lower()
                # stems the now lower case and punctuation free word
                term = stemmer.stem(term)

                # simple terms have their associated posting lists stored in the postional inverted index.
                    # beyond that, term frequency, tf, and document frequency, df_t, are also stored there
                tempPostingList = invertedIndex[term].getPostingList()

                # if this individual term is in the given document, we increase the document's score accordingly
                    # this block is all about calculating tf-idf for simple search terms
                if docId in tempPostingList:
                    tf = tempPostingList[docId].getTermDocumentFrequency()
                    df_t = invertedIndex[term].getDocumentFrequency()

                    idf = math.log(totalNumberOfDocuments / df_t, 10)

                    tf_idf = (1 + math.log(tf, 10)) * idf

                    docScore += tf_idf

            # This block handles scoring of complex search terms using tf-idf
            else:
                tempPostingList = complexSearchTermData[term].getPostingList()
                if docId in tempPostingList:
                    tf = complexSearchTermData[term].get_tf(docId)
                    df_t = complexSearchTermData[term].getDf_t()

                    idf = math.log(totalNumberOfDocuments / df_t, 10)

                    tf_idf = (1 + math.log(tf, 10)) * idf

                    docScore += tf_idf

        # sets score for the current document
        docListAndScore[docId] = docScore

    # turns the dict we used for document id's & scores into a list of tuples and then sorts them by their score
        # largest to smallest
    sortedDocListAndScore = sorted(docListAndScore.items(), key=operator.itemgetter(1), reverse=True)

    # writes/prints results to console & Results_File.txt
    for item in sortedDocListAndScore:
        resultFile.write("\tdocument " + item[0] + " score : " + str(item[1]) + "\r")
        print("\tdocument " + item[0] + " score : " + str(item[1]))


    print("-------------------------\r\r")


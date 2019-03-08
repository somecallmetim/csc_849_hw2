from nltk.stem import PorterStemmer
import string

# class to track term frequency & position for a given document
class TermPositionListForGivenDoc:
    # constructor
    def __init__(self, docId, numericalPosition):
        #fields
        self.__docId = docId
        self.__termFrequency = 0
        self.__positionList = []

        self.addPosition(numericalPosition)

    def addPosition(self, numericalPosition):
        self.__positionList.append(numericalPosition)
        self.__termFrequency += 1

    def getTermPositionList(self):
        return self.__positionList

    def getTermDocumentFrequency(self):
        return self.__termFrequency

# class to help track data for each term in our document list vocabulary
class TermInPositionalInvertedIndex:
    # constructor
    def __init__(self, name, docId, numericalPosition):
        # fields
        self.__name = name
        self.__documentFrequency = 0
        # posting list is of the format { docId : TermPositionListForGivenDoc } where value is object listed above
        self.__postingList = {}

        #start with the first docId the term is associated with in its postingList
        self.addPosting(docId, numericalPosition)

    # add new occurance of term and increment frequency in which it appears
    def addPosting(self, docId, numericalPosition):
        # only add the docId if it's not already in the postingList
        if docId not in self.__postingList:
            self.__postingList[docId] = TermPositionListForGivenDoc(docId, numericalPosition)
            self.__documentFrequency += 1
        else:
            self.__postingList[docId].addPosition(numericalPosition)

    def getPostingList(self):
        return self.__postingList

    def getDocumentFrequency(self):
        return self.__documentFrequency
    
    def getTermPositionList(self, docId):
        if docId not in self.__postingList:
            return 0
        else:
            return self.__postingList[docId]

    def getName(self):
        return self.__name

# from https://www.dotnetperls.com/punctuation-python
def remove_punctuation(value):
    result = ""
    for c in value:
        # If char is not punctuation, add it to the result.
        if c not in string.punctuation:
            result += c
    return result

def createPositionalInvertedIndex():
    stemmer = PorterStemmer()
    # this is the document (or hypothetical set of documents) we're scanning from
    file = open("documents.txt", "r")

    numericalPosition = 0
    currentDocId = 0
    positionalInvertedIndex = {}

    # parse document line by line and add words to inverted index
    for line in file:
        # scane each line word for word
        for word in line.split():
            # individual documents in this toy example are delineated by tags ie <DOC 1> ~~~ </DOC 1>
                # this part of the if block detects document tags and sets the docId accordingly
            if "<" in word and "</" not in word:
                word = line.strip('<DOC ')
                word = word.split('>')
                # set currentDocId to the number indicated in the line
                currentDocId = word[0]
                # reset numericalPosition for the new document
                numericalPosition = 0
            elif ">" in word:
                pass
            # if the word/line isn't a document tag
            else:
                # makes the term all lower case
                key = str(word).lower()
                # attempts to remove all punctuation
                key = remove_punctuation(key)
                # if a word is all punctuation, ie ..., skips the word completely
                if key == "":
                    break
                # increment counter for word position in the document
                numericalPosition += 1
                # stems the now lower case and punctuation free word
                key = stemmer.stem(key)
                # if key isn't in the inverted index, it creates a new object and adds it to inverted index
                if key not in positionalInvertedIndex:
                    positionalInvertedIndex[key] = TermInPositionalInvertedIndex(key, currentDocId, numericalPosition)
                # if key is in positional inverted index, program attempts to add new posting
                else:
                    positionalInvertedIndex[key].addPosting(currentDocId, numericalPosition)

    return positionalInvertedIndex


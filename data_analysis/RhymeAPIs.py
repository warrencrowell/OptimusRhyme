from json import loads
from urllib import urlopen

def RhymeBrain(word,MaxResults=None):
    """
    QUERY LIMIT: 350 requests per hour

    Input: takes in a word as a string (only accepts words witho only letters)
    Output: returns a list of unicode dictionaries with the values:
        * word      : The rhyming word
        * score     : The RhymeRank score for the word.
                    : Scores of 300 and above are perfect rhymes.
                    : Scores between 0 and 300 are near rhymes without similar sounding consonents.
                    : Words with the same score are listed with the most matching sounds first. 
                      If you later sort by score again, it is best to preserve this ordering 
                      before showing the results to the user.
        * flags     : A list of letters giving more information about the word.
              a     : The word is offensive.
              b     : The word might be found in most dictionaries.
              c     : The pronunciation is known with confidence. It was not automatically generated.
        * syllables : An estimate of the number of syllables in the rhyming word.
        * freq      : A number that tells you how common the word is. The number is a 
                      logarithm of the frequency of usage in common texts. Currently, 
                      the highest possible value is 34.
    """
    RhymeBrainAPIurl = "http://rhymebrain.com/talk?function=getRhymes&word="
    if(MaxResults):
        query = RhymeBrainAPIurl + word + "&MaxResults="+MaxResults
    else:
        query = RhymeBrainAPIurl + word
    url = urlopen(query)
    listOfRhymeDicts = loads(url.read())
    return listOfRhymeDicts

def WordNik(word,MaxResults):
    """
    QUERY LIMIT: 15000 requests per hour

    Input: takes in a word as a string (only accepts words witho only letters)
    Output: returns a list of MaxResults words that rhyme with the query word
    """
    APIkey="a2a73e7b926c924fad7001ca3111acd55af2ffabf50eb4ae5"
    query="http://api.wordnik.com/v4/word.json/"+word+"/relatedWords?useCanonical=false&relationshipTypes=rhyme&limitPerRelationshipType="+str(MaxResults)+"&api_key="+APIkey
    url = urlopen(query)
    listOfRhymeDicts = loads(url.read())
    if len(listOfRhymeDicts)!=2 or (not listOfRhymeDicts[0].has_key('words')):
        return None
    return listOfRhymeDicts[0]['words']


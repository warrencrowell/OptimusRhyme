from json import loads
from re import compile, match
from urllib import urlopen

getRhymes(word):
    """
    Input: takes in a word as a string (only accepts words witho only letters)
    Output: returns a list of unicode dictionaries with the values:
        * u'flags'
        * u'freq'
        * u'score'
        * u'word'
        * u'syllables'
    """
    r.compile('^[a-zA-Z]$')
    if not r.match(word):
        print "Word is not only letters:\""+word+"\""
        return None
    RhymeBrainAPIurl = "http://rhymebrain.com/talk?function=getRhymes&word="
    url = urlopen(RhymeBrainAPIurl + word)
    listOfRhymeDicts = loads(url.read())
    return listOfRhymeDicts



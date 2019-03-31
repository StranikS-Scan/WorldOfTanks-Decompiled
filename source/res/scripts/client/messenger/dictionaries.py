# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/dictionaries.py
# Compiled at: 2011-05-10 17:24:02
from debug_utils import LOG_CURRENT_EXCEPTION
import re, sre_compile
import ResMgr
_defaultReplacementFunction = lambda word: '*' * len(word)

class ObsceneLanguageDictionary(object):
    __nonAlphaNumPattern = re.compile(u'[^a-zA-Z]', re.M | re.S | re.U | re.I)
    __equivalents = {}
    __badWordPatterns = []
    replace = staticmethod(_defaultReplacementFunction)

    @classmethod
    def load(cls, resourceId):
        """
        Load obscene dictionary for the specified language.
        @resourceId: the id of the resource to open.
        @return: ObsceneLanguageDictionary object.
        """
        object = ObsceneLanguageDictionary.__new__(cls)
        dSection = ResMgr.openSection(resourceId)
        if dSection is None:
            return object
        else:
            eqsSection = dSection['equivalents']
            if eqsSection is not None:
                for eqSection in eqsSection.values():
                    find = eqSection['find'].asWideString if eqSection.has_key('find') else None
                    replace = eqSection['replace'].asWideString if eqSection.has_key('replace') else None
                    if find and replace:
                        object.__equivalents[find] = replace

            nonAnSection = dSection['nonAlphanumericCharacter']
            if nonAnSection is not None:
                nonAnPattern = nonAnSection.asWideString
                try:
                    object.__nonAlphaNumPattern = re.compile(nonAnPattern, re.M | re.S | re.U | re.I)
                except sre_compile.error:
                    LOG_CURRENT_EXCEPTION()

            badWordsSection = dSection['badWords']
            if badWordsSection is not None:
                for badWordSet in badWordsSection.values():
                    try:
                        if badWordSet.has_key('include'):
                            include = re.compile(badWordSet['include'].asWideString, re.M | re.S | re.U | re.I)
                        else:
                            include = re.compile(badWordSet.asWideString, re.M | re.S | re.U | re.I)
                        exclude = None
                        if badWordSet.has_key('exclude'):
                            exclude = re.compile(badWordSet['exclude'].asWideString, re.M | re.S | re.U | re.I)
                        object.__badWordPatterns.append((include, exclude))
                    except sre_compile.error:
                        LOG_CURRENT_EXCEPTION()

            return object

    @staticmethod
    def overrideReplacementFunction(function):
        """
        Overrides replacement method.
        """
        ObsceneLanguageDictionary.replace = staticmethod(function)

    @staticmethod
    def resetReplacementFunction():
        """
        Resets to default replacement method.
        """
        ObsceneLanguageDictionary.replace = staticmethod(_defaultReplacementFunction)

    def searchAndReplace(self, text):
        """
        Search bad words and if find, than replace by replacement function.
        Search stages:
                1. splits string using space.
                2. for each word: removed non-alphanumeric character, 
                find and replace equivalents to required characters
                3. try finds bad words. If find, than replace, else do nothing.
        
        @param text: string to search for bad words (unicode).
        @return: parsed string (unicode).
        """
        words = text.split(' ')
        for idx, word in enumerate(words):
            parsing = self.__nonAlphaNumPattern.sub('', word.lower())
            for find, replace in self.__equivalents.iteritems():
                parsing = parsing.replace(find, replace)

            for include, exclude in self.__badWordPatterns:
                match = include.search(parsing)
                if match and (exclude is None or not exclude.search(parsing)):
                    words[idx] = self.replace(word)
                    break

        return ' '.join(words)

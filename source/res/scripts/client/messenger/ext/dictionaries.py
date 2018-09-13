# Embedded file name: scripts/client/messenger/ext/dictionaries.py
from debug_utils import *
import re, sre_compile
import ResMgr
_defaultReplacementFunction = lambda word: '*' * len(word)

class ObsceneLanguageDictionary(object):
    replace = staticmethod(_defaultReplacementFunction)

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
        return text


class BasicOLDictionary(ObsceneLanguageDictionary):
    __nonAlphaNumPattern = re.compile(u'[^a-zA-Z]', re.M | re.S | re.U | re.I)
    __equivalents = {}
    __badWordPatterns = []

    @classmethod
    def load(cls, resourceId):
        """
        Load obscene dictionary for the specified language.
        @resourceId: the id of the resource to open.
        @return: ObsceneLanguageDictionary object.
        """
        obj = BasicOLDictionary.__new__(cls)
        dSection = ResMgr.openSection(resourceId)
        if dSection is None:
            return obj
        else:
            eqsSection = dSection['equivalents']
            if eqsSection is not None:
                for eqSection in eqsSection.values():
                    find = eqSection['find'].asWideString if eqSection.has_key('find') else None
                    replace = eqSection['replace'].asWideString if eqSection.has_key('replace') else None
                    if find and replace:
                        obj.__equivalents[find] = replace

            nonAnSection = dSection['nonAlphanumericCharacter']
            if nonAnSection is not None:
                nonAnPattern = nonAnSection.asWideString
                try:
                    obj.__nonAlphaNumPattern = re.compile(nonAnPattern, re.M | re.S | re.U | re.I)
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
                        obj.__badWordPatterns.append((include, exclude))
                    except sre_compile.error:
                        LOG_CURRENT_EXCEPTION()

            return obj

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


class SpecialOLDictionary(ObsceneLanguageDictionary):
    __badWordPatterns = []

    @classmethod
    def load(cls, resourceId):
        """
        Load obscene dictionary for the specified language.
        @resourceId: the id of the resource to open.
        @return: ObsceneLanguageDictionary object.
        """
        obj = SpecialOLDictionary.__new__(cls)
        dSection = ResMgr.openSection(resourceId)
        if dSection is None:
            return obj
        else:
            badWordsSection = dSection['badWords']
            if badWordsSection is not None:
                for badWordSet in badWordsSection.values():
                    try:
                        badWordC = re.compile(badWordSet.asWideString, re.M | re.S | re.U | re.I)
                        obj.__badWordPatterns.append(badWordC)
                    except sre_compile.error:
                        LOG_CURRENT_EXCEPTION()

            return obj

    def searchAndReplace(self, text):
        try:
            for pat in self.__badWordPatterns:
                lowerText = text.lower()
                processed = []
                offset = 0
                for m in pat.finditer(lowerText):
                    start = m.start()
                    end = m.end()
                    processed.append(text[offset:start])
                    processed.append(self.replace(text[start:end]))
                    offset = end

                if offset:
                    processed.append(text[offset:])
                if len(processed):
                    text = ''.join(processed)

        except Exception:
            LOG_ERROR('There is exception in special bad words filter')
            LOG_CURRENT_EXCEPTION()

        return text


class DomainNameDictionary(object):
    __webPrefix = '^(http(s)?://)?(www\\.)?'
    __domainNamePatterns = []
    replace = staticmethod(_defaultReplacementFunction)

    @classmethod
    def load(cls, resourceId):
        """
        Load domain names dictionary for the specified language.
        @resourceId: the id of the resource to open.
        @return: DomainNameDictionary object.
        """
        obj = DomainNameDictionary.__new__(cls)
        dSection = ResMgr.openSection(resourceId)
        if dSection is None:
            return obj
        else:
            domainNameSection = dSection['domainNames']
            if domainNameSection is not None:
                for domainNameSet in domainNameSection.values():
                    try:
                        include = re.compile(obj.__webPrefix + domainNameSet.asWideString, re.M | re.S | re.U | re.I)
                        obj.__domainNamePatterns.append(include)
                    except sre_compile.error:
                        LOG_CURRENT_EXCEPTION()

            return obj

    @staticmethod
    def overrideReplacementFunction(function):
        """
        Overrides replacement method.
        """
        DomainNameDictionary.replace = staticmethod(function)

    @staticmethod
    def resetReplacementFunction():
        """
        Resets to default replacement method.
        """
        DomainNameDictionary.replace = staticmethod(_defaultReplacementFunction)

    def searchAndReplace(self, text):
        """
        Search domain names and if find, than replace by replacement function.
        Search stages:
                1. splits string using space.
                2. try finds domain names. If found, than replace, else do nothing.
        
        @param text: string to search for domain names (unicode).
        @return: parsed string (unicode).
        """
        words = text.split(' ')
        for idx, word in enumerate(words):
            for pattern in self.__domainNamePatterns:
                match = pattern.search(word)
                if match:
                    words[idx] = self.replace(word)
                    break

        return ' '.join(words)

# Embedded file name: scripts/client/messenger/gui/Scaleform/data/faq_data.py
from collections import namedtuple
import re
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.Scaleform.locale.FAQ import FAQ as I18N_FAQ
from gui.shared.events import OpenLinkEvent
from helpers import i18n
from messenger import g_settings
QUESTION_PATTERN = re.compile('^\\#faq:question_(\\d+)$')
ANSWER_FORMAT = '#faq:answer_{0:d}'
SUPPORTED_LINKS_EVENTS = (OpenLinkEvent.SUPPORT,)
FAQItem = namedtuple('FAQItem', ('number', 'question', 'answer'))

class FAQList(object):

    def __init__(self):
        super(FAQList, self).__init__()
        self.__extraFormats = {'contains_links': '_FAQList__formatLinksInAnswer'}
        self.__links = self.__buildLinks()
        self.__list = self.__buildList()
        self.__cursor = 0

    def clear(self):
        self.__links.clear()
        self.__extraFormats.clear()

    def getItem(self, index):
        result = FAQItem(index, '', '')
        if len(self.__list) > index:
            result = self.__list[index]
        return result

    def getIterator(self, offset = 0):
        for item in self.__list[offset:]:
            yield item

    def __buildLinks(self):
        links = {}
        htmlFormat = g_settings.htmlTemplates.format
        endTag = htmlFormat('closeLinkTagInFAQ')
        for link in SUPPORTED_LINKS_EVENTS:
            links[link] = {'openTag': htmlFormat('openLinkTagInFAQ', ctx={'eventType': link}),
             'closeTag': endTag}

        return links

    def __buildList(self):
        faq = []
        for questionKey in I18N_FAQ.QUESTION_ENUM:
            sreMatch = QUESTION_PATTERN.match(questionKey)
            if sreMatch is not None and len(sreMatch.groups()) > 0:
                number = int(sreMatch.groups()[0])
                answerKey = ANSWER_FORMAT.format(number)
                if answerKey in I18N_FAQ.ANSWER_ENUM:
                    answer = i18n.makeString(answerKey)
                else:
                    answer = self.__findAnswerWithSuffix(answerKey)
                if answer:
                    faq.append(FAQItem(number, i18n.makeString(questionKey), answer))
                else:
                    LOG_ERROR('Answer is not found', number)

        return sorted(faq, cmp=lambda item, other: cmp(item.number, other.number))

    def __formatLinksInAnswer(self, answer):
        try:
            answer = answer.format(**self.__links)
        except (ValueError, TypeError, KeyError):
            LOG_CURRENT_EXCEPTION()

        return answer

    def __findAnswerWithSuffix(self, answerKey):
        result = None
        for suffix, methodName in self.__extraFormats.iteritems():
            nextKey = '{0}/{1}'.format(answerKey, suffix)
            if nextKey in I18N_FAQ.ANSWER_ENUM:
                method = getattr(self, methodName, None)
                if method and callable(method):
                    result = method(i18n.makeString(nextKey))
                else:
                    LOG_ERROR('Method is not found', methodName)
                break

        return result

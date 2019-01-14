# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/data/faq_data.py
import logging
from collections import namedtuple
from gui.impl.gen import R
from gui.shared.events import OpenLinkEvent
from helpers import dependency
from messenger import g_settings
from skeletons.gui.impl import IGuiLoader
_logger = logging.getLogger(__name__)
QUESTION_FORMAT = 'question_{0:d}'
ANSWER_FORMAT = 'answer_{0:d}'
SUPPORTED_LINKS_EVENTS = (OpenLinkEvent.SUPPORT,)
FAQItem = namedtuple('FAQItem', ('number', 'question', 'answer'))

class FAQList(object):
    gui = dependency.descriptor(IGuiLoader)

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

    def getIterator(self, offset=0):
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
        result = []
        faq = R.strings.faq
        length = faq.length()
        translation = self.gui.resourceManager.getTranslatedText
        for number in xrange(1, length + 1):
            question = faq.dyn(QUESTION_FORMAT.format(number))
            if not question:
                continue
            questionText = translation(question())
            answer = faq.dyn(ANSWER_FORMAT.format(number))
            if not answer:
                _logger.error('Answer %d is not found', number)
                continue
            elif not answer.exists():
                answerText = self.__findAnswerWithSuffix(answer)
            else:
                answerText = translation(answer())
            result.append(FAQItem(number, questionText, answerText))

        return sorted(result, key=lambda item: item.number)

    def __formatLinksInAnswer(self, answer):
        try:
            answer = answer.format(**self.__links)
        except (ValueError, TypeError, KeyError):
            _logger.exception('Link can not be added to answer')

        return answer

    def __findAnswerWithSuffix(self, answer):
        result = R.invalid()
        for suffix, methodName in self.__extraFormats.iteritems():
            nextAnswer = answer.dyn(suffix)
            if nextAnswer:
                method = getattr(self, methodName, None)
                if method and callable(method):
                    result = method(self.gui.resourceManager.getTranslatedText(nextAnswer()))
                else:
                    _logger.error('Method %s is not found', methodName)
                break

        return result

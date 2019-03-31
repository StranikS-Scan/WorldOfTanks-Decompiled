# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scalefrom/FAQInterface.py
# Compiled at: 2012-02-28 19:07:07
import BigWorld
from debug_utils import LOG_ERROR
import gettext
from helpers import i18n
from messenger import g_settings
from messenger.gui.Scalefrom import FAQ_COMMANDS
import re
FAQ_BATCH_SIZE = 5

class FAQInterface(object):
    __questionPattern = re.compile('^question_(\\d+)$')
    __answerFormat = 'answer_{0:d}'

    def __init__(self):
        super(FAQInterface, self).__init__()
        self.__movieViewHandler = None
        self.__faqDictLoaded = False
        return

    def __buildFAQDict(self):
        if self.__faqDictLoaded:
            return
        else:
            self.__faqDict = {}
            path = i18n.convert(BigWorld.wg_resolveFileName('text')[:-5])
            translator = gettext.translation('faq', path, languages=['text'])
            for key in translator._catalog.iterkeys():
                if len(key) > 0:
                    sreMatch = self.__questionPattern.match(key)
                    if sreMatch is not None and len(sreMatch.groups()) > 0:
                        number = int(sreMatch.groups()[0])
                        answer = translator.gettext(self.__answerFormat.format(number))
                        if answer is not None and len(answer) > 0:
                            self.__faqDict[number] = (translator.gettext(key), answer)
                        else:
                            LOG_ERROR('Answer %s is not found' % number)

            self.__faqDictLoaded = True
            return

    def populateUI(self, movieViewHandler):
        self.__movieViewHandler = movieViewHandler
        self.__movieViewHandler.addExternalCallbacks({FAQ_COMMANDS.Get(): self.onGetFAQ})

    def dispossessUI(self):
        self.__movieViewHandler.removeExternalCallbacks(FAQ_COMMANDS.Get())
        self.__movieViewHandler = None
        return

    def onGetFAQ(self, *args):
        self.__buildFAQDict()
        faq = sorted(self.__faqDict.items(), cmp=lambda item, other: cmp(item[0], other[0]))
        template = g_settings.getHtmlTemplate('firstFAQItem')
        batch = []
        if len(faq) > 0:
            number, (question, answer) = faq[0]
            batch = [template % (number, question, answer)]
        template = g_settings.getHtmlTemplate('nextFAQItem')
        for number, (question, answer) in faq[1:]:
            if FAQ_BATCH_SIZE > len(batch):
                self.__movieViewHandler.call(FAQ_COMMANDS.Append(), [''.join(batch)])
                batch = []
            batch.append(template % (number, question, answer))

        if len(batch) > 0:
            self.__movieViewHandler.call(FAQ_COMMANDS.Append(), [''.join(batch)])

# Embedded file name: scripts/client/tutorial/gui/Scaleform/quests/pop_ups.py
from gui.Scaleform.daapi.view.lobby.AwardWindow import AwardWindow
from gui.server_events.awards import FormattedAward
from gui.server_events.bonuses import getTutorialBonusObj
from gui.shared import events, g_eventBus
from helpers import i18n

class TutorialQuestAwardWindow(AwardWindow):

    def __init__(self, content):
        ctx = {'award': _TutorialQuestAward(content)}
        super(TutorialQuestAwardWindow, self).__init__(ctx)


class _TutorialQuestAward(FormattedAward):

    def __init__(self, content):
        super(_TutorialQuestAward, self).__init__()
        self.__content = content

    def clear(self):
        super(_TutorialQuestAward, self).clear()
        self.__content = None
        return

    def getButtonStates(self):
        return (False, True, self.__content['showQuestsBtn'])

    def getWindowTitle(self):
        return i18n.makeString('#tutorial:tutorialQuest/awardWindow/title')

    def getBackgroundImage(self):
        return self.__content['bgImage']

    def getHeader(self):
        return i18n.makeString(self.__content['header'])

    def getDescription(self):
        return i18n.makeString(self.__content['description'])

    def getBodyButtonText(self):
        return i18n.makeString('#tutorial:tutorialQuest/awardWindow/nextQuest')

    def _getBonuses(self):
        bonuses = self.__content.get('bonuses', {})
        result = []
        for n, v in bonuses.iteritems():
            result.append(getTutorialBonusObj(n, v))

        return result

    def handleCloseButton(self):
        g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.SIMPLE_WINDOW_CLOSED, targetID=self.__content['chapterID']))

    def handleBodyButton(self):
        g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.SIMPLE_WINDOW_PROCESSED, targetID=self.__content['chapterID']))

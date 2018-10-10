# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/quests/queries.py
from helpers import i18n
from tutorial.control import ContentQuery
from tutorial.control.functional import FunctionalConditions
from tutorial.doc_loader import getQuestsDescriptor

class AwardWindowContentQuery(ContentQuery):

    def invoke(self, content, varID):
        descriptor = getQuestsDescriptor()
        chapterID = self.getVar(varID)
        chapter = descriptor.getChapter(chapterID)
        value = content['description']
        content['description'] = self.getVar(value, default=value)
        content['header'] = self.__getAwardHeader(content, chapter)
        content['bgImage'] = self.__getAwardIcon(content, chapter)
        content['bonuses'] = None
        bonus = chapter.getBonus()
        altBonusConditions = FunctionalConditions(bonus.getAltBonusValuesConditions())
        if altBonusConditions.allConditionsOk() and bonus.getAltValues():
            content['bonuses'] = bonus.getAltValues()
        else:
            content['bonuses'] = bonus.getValues()
        content['chapterID'] = chapterID
        progrCondition = chapter.getProgressCondition()
        if progrCondition.getID() == 'vehicleBattlesCount':
            content['vehicle'] = progrCondition.getValues().get('vehicle')
        content['showQuestsBtn'] = not descriptor.areAllBonusesReceived(self._bonuses.getCompleted())
        return

    def __getAwardHeader(self, content, chapter):
        value = content['header']
        return self.getVar(value, default=value) or i18n.makeString('#tutorial:tutorialQuest/awardWindow/header', qName=chapter.getTitle())

    def __getAwardIcon(self, content, chapter):
        value = content['bgImage']
        return self.getVar(value, default=value) or chapter.getImage()

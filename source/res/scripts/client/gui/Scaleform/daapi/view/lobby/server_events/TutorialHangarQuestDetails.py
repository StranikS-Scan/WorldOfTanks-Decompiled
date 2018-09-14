# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/TutorialHangarQuestDetails.py
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.daapi.view.meta.TutorialHangarQuestDetailsMeta import TutorialHangarQuestDetailsMeta
from gui.prb_control.dispatcher import g_prbLoader
from gui.server_events.bonuses import getTutorialBonusObj
from gui.server_events import formatters
from gui.shared import event_dispatcher
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters import text_styles
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.shared.events import OpenLinkEvent
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from helpers import i18n

class CONDITION_TYPE(object):
    CHAIN = 'chain'
    TUTORIAL = 'tutorial'
    VIDEO = 'video'


class TutorialHangarQuestDetails(TutorialHangarQuestDetailsMeta):

    def __init__(self):
        super(TutorialHangarQuestDetailsMeta, self).__init__()
        self.__questsDescriptor = None
        return

    def _dispose(self):
        self.__questsDescriptor = None
        super(TutorialHangarQuestDetails, self)._dispose()
        return

    def setQuestsDescriptor(self, descriptor):
        self.__questsDescriptor = descriptor

    def showTip(self, id, type):
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher and prbDispatcher.getFunctionalState().isNavigationDisabled():
            return SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error)
        if type == CONDITION_TYPE.CHAIN:
            event_dispatcher.runTutorialChain(id)
        elif type == CONDITION_TYPE.TUTORIAL:
            battle_selector_items.getItems().select(PREBATTLE_ACTION_NAME.BATTLE_TUTORIAL)
        elif type == CONDITION_TYPE.VIDEO:
            assert id in (OpenLinkEvent.REPAIRKITHELP_HELP, OpenLinkEvent.MEDKIT_HELP, OpenLinkEvent.FIRE_EXTINGUISHERHELP_HELP)
            self.fireEvent(OpenLinkEvent(id, title=i18n.makeString('#tutorial:tutorialQuest/video/%s' % id)))

    def requestQuestInfo(self, questID):
        if self.__questsDescriptor is None:
            return
        else:
            chapter = self.__questsDescriptor.getChapter(questID)
            image = chapter.getImage()
            description = chapter.getDescription()
            self.as_updateQuestInfoS({'image': image,
             'awards': self.__getBonuses(chapter),
             'title': text_styles.highTitle(chapter.getTitle()),
             'description': self.__getDescription(description, chapter)})
            return

    def __getBonuses(self, chapter, useIconFormat=False):
        if not chapter.isBonusReceived(g_itemsCache.items.stats.tutorialsCompleted):
            result = []
            iconResult = []
            output = []
            bonus = chapter.getBonus()
            if bonus is not None:
                for n, v in bonus.getValues().iteritems():
                    b = getTutorialBonusObj(n, v)
                    if b is not None:
                        if b.hasIconFormat() and useIconFormat:
                            iconResult.extend(b.getList())
                        else:
                            flist = b.formattedList()
                            if flist:
                                result.extend(flist)

            if len(result):
                output.append(formatters.packSimpleBonusesBlock(result))
            if len(iconResult):
                output.append(formatters.packIconAwardBonusBlock(iconResult))
            return formatters.todict(output)
        else:
            return formatters.todict([formatters.packTextBlock('#quests:beginnerQuests/details/noAward')])
            return

    def __getDescription(self, description, chapter):
        return {'descTitle': text_styles.middleTitle(QUESTS.BEGINNERQUESTS_DETAILS_DESCRIPTIONTITLE),
         'descText': text_styles.main(description),
         'conditionItems': self.__getTopConditions(chapter),
         'conditionsTitle': text_styles.middleTitle(QUESTS.BEGINNERQUESTS_DETAILS_CONDITIONSTITLE)}

    def __getTopConditions(self, chapter):
        blocks = []
        progrCondition = chapter.getProgressCondition()
        vehicle = None
        if progrCondition.getID() == 'vehicleBattlesCount':
            vehicleCD = progrCondition.getValues().get('vehicle')
            vehicle = g_itemsCache.items.getItemByCD(vehicleCD)
        for questCondition in chapter.getQuestConditions():
            chainType = questCondition['type']
            blocks.append({'type': chainType,
             'id': questCondition['id'],
             'btnText': questCondition['btnLabel'],
             'text': self.__getConditionText(questCondition['text'], vehicle)})

        return blocks

    def __getConditionText(self, questConditionText, vehicle):
        if vehicle is not None:
            questConditionText = i18n.makeString('#tutorial:%s' % questConditionText, vehName=vehicle.userName)
        return text_styles.main(questConditionText)

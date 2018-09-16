# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/tank_girls_popover.py
import operator
from gui.server_events.events_dispatcher import showTankwomanAward
from gui.shared.formatters import text_styles
from helpers.i18n import makeString as _ms
from gui.Scaleform.daapi.view.meta.TankgirlsPopoverMeta import TankgirlsPopoverMeta
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from helpers import dependency
from shared_utils import first
from skeletons.gui.server_events import IEventsCache

class TankgirlsPopover(TankgirlsPopoverMeta):
    __eventsCache = dependency.descriptor(IEventsCache)

    def onRecruitClick(self, eventID):
        self.__getMissionAward(eventID)
        self.destroy()

    def _populate(self):
        super(TankgirlsPopover, self)._populate()
        self.__eventsCache.onProgressUpdated += self.__onQuestsUpdated
        self.__update()

    def _dispose(self):
        self.__eventsCache.onProgressUpdated -= self.__onQuestsUpdated
        super(TankgirlsPopover, self)._dispose()

    def __update(self):
        tankwomenQuests = []
        for _, o in sorted(self.__eventsCache.getPersonalMissions().getAllOperations().iteritems(), key=operator.itemgetter(0)):
            if o.isUnlocked():
                operationName = _ms('#personal_missions:operations/title%d' % o.getID())
                for classifier in o.getIterationChain():
                    _, quests = o.getChainByClassifierAttr(classifier)
                    for _, q in sorted(quests.iteritems(), key=operator.itemgetter(0)):
                        bonus = q.getTankmanBonus()
                        needToGetTankman = q.needToGetAddReward() and not bonus.isMain or q.needToGetMainReward() and bonus.isMain
                        if needToGetTankman and bonus.tankman is not None:
                            tankwomenQuests.append({'id': str(q.getID()),
                             'operationLabel': text_styles.standard(operationName),
                             'missionLabel': text_styles.main(q.getShortUserName()),
                             'recruitBtnLabel': PERSONAL_MISSIONS.PERSONALMISSIONS_TANKGIRLSPOPOVER_RECRUITBTN})

        self.as_setListDataProviderS(tankwomenQuests)
        return

    def __getMissionAward(self, eventID):
        quest = self.__eventsCache.getPersonalMissions().getAllQuests()[int(eventID)]
        bonus = quest.getTankmanBonus()
        if quest.needToGetReward() and bonus.tankman is not None:
            showTankwomanAward(quest.getID(), first(bonus.tankman.getTankmenData()))
        return

    def __onQuestsUpdated(self, *args):
        self.__update()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/tank_girls_popover.py
import operator
from gui.shared.formatters import text_styles
from helpers.i18n import makeString as _ms
from gui import SystemMessages
from gui.Scaleform.daapi.view.meta.TankgirlsPopoverMeta import TankgirlsPopoverMeta
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.server_events import events_helpers
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from gui.shared.utils import decorators
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

class TankgirlsPopover(TankgirlsPopoverMeta):
    __eventsCache = dependency.descriptor(IEventsCache)

    def onRecruitClick(self, eventID):
        self._getMissionAward(eventID)
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
        for oID, o in sorted(events_helpers.getPersonalMissionsCache().getOperations().iteritems(), key=operator.itemgetter(0)):
            if o.isUnlocked():
                operationName = _ms('#personal_missions:operations/title%d' % o.getID())
                for vehicleType in VEHICLE_TYPES_ORDER:
                    _, quests = o.getChainByVehicleType(vehicleType)
                    for qID, q in sorted(quests.iteritems(), key=operator.itemgetter(0)):
                        tankman, isMainBonus = q.getTankmanBonus()
                        needToGetTankman = q.needToGetAddReward() and not isMainBonus or q.needToGetMainReward() and isMainBonus
                        if needToGetTankman and tankman is not None:
                            tankwomenQuests.append({'id': str(q.getID()),
                             'operationLabel': text_styles.standard(operationName),
                             'missionLabel': text_styles.main(q.getShortUserName()),
                             'recruitBtnLabel': PERSONAL_MISSIONS.PERSONALMISSIONS_TANKGIRLSPOPOVER_RECRUITBTN})

        self.as_setListDataProviderS(tankwomenQuests)
        return

    @decorators.process('updating')
    def _getMissionAward(self, eventID):
        quest = events_helpers.getPersonalMissionsCache().getQuests()[int(eventID)]
        if quest.needToGetReward():
            result = yield events_helpers.getPersonalMissionAward(quest)
            if result and result.userMsg:
                SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def __onQuestsUpdated(self, *args):
        self.__update()

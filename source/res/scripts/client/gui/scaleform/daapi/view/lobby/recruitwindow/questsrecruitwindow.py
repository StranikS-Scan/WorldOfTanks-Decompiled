# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/recruitWindow/QuestsRecruitWindow.py
import nations
from items import tankmen
from gui import SystemMessages
from gui.shared.utils import decorators
from gui.shared.gui_items import Tankman
from gui.server_events import g_eventsCache
from gui.shared.gui_items.processors.quests import PotapovQuestsGetTankwomanReward
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.QuestRecruitWindowMeta import QuestRecruitWindowMeta

class QuestsRecruitWindow(QuestRecruitWindowMeta):

    def __init__(self, ctx = None):
        super(QuestsRecruitWindow, self).__init__()
        self.__currentSelectedNationID = None
        raise len({'isPremium',
         'fnGroup',
         'lnGroup',
         'iGroupID',
         'questID'} - set(ctx.keys())) == 0 or AssertionError
        self.__questID = ctx['questID']
        self.__isPremium = ctx['isPremium']
        self.__fnGroup = ctx['fnGroup']
        self.__lnGroup = ctx['lnGroup']
        self.__iGroupID = ctx['iGroupID']
        self.__freeXpValue = ctx.get('freeXP', 0)
        return

    def onWindowClose(self):
        self.destroy()

    @decorators.process('updating')
    def onApply(self, data):
        potapovQuest = g_eventsCache.potapov.getQuests().get(self.__questID)
        result = yield PotapovQuestsGetTankwomanReward(potapovQuest, int(data.nation), int(data.vehicle), data.tankmanRole).request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self.destroy()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(QuestsRecruitWindow, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.RECRUIT_PARAMS:
            viewPy.onDataChange += self.__paramsChangeHandler
            viewPy.setNationsData(showEmptyRow=False)

    def _onUnregisterFlashComponent(self, viewPy, alias):
        super(QuestsRecruitWindow, self)._onUnregisterFlashComponent(viewPy, alias)
        viewPy.onDataChange -= self.__paramsChangeHandler

    def __paramsChangeHandler(self, selectedNationID, selectedVehClass, selectedVehicle, selectedTmanRole):
        selectedNationID = int(selectedNationID)
        nationName = nations.NAMES[selectedNationID]
        if self.__currentSelectedNationID != selectedNationID:
            firstNameID, lastNameID, iconID = g_eventsCache.potapov.getNextTankwomanIDs(selectedNationID, self.__isPremium, int(self.__fnGroup), int(self.__lnGroup), int(self.__iGroupID))
            rankID = Tankman.calculateRankID(tankmen.MAX_SKILL_LEVEL, self.__freeXpValue)
            self.as_setInitDataS({'name': Tankman.getFullUserName(selectedNationID, firstNameID, lastNameID),
             'nation': nationName,
             'rank': Tankman.getRankUserName(selectedNationID, rankID),
             'vehicle': '',
             'faceIcon': Tankman.getBigIconPath(selectedNationID, iconID),
             'rankIcon': Tankman.getRankBigIconPath(selectedNationID, rankID)})
        self.__currentSelectedNationID = selectedNationID

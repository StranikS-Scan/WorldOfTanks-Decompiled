# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCHangarHeader.py
from gui.Scaleform.daapi.view.lobby.hangar.hangar_header import HangarHeader
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import events, EVENT_BUS_SCOPE

class BCHangarHeader(HangarHeader):

    def showQuestsWindow(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_QUESTS_VIEW), scope=EVENT_BUS_SCOPE.LOBBY)

    def showPersonalQuests(self):
        self.showQuestsWindow()

    def showCommonQuests(self):
        self.showQuestsWindow()

    def _addQuestsToHeaderVO(self, headerVO, _):
        headerVO.update(self.__getFakeQuestData())

    def __getFakeQuestData(self):
        return {'commonQuestsLabel': '',
         'commonQuestsIcon': RES_ICONS.questsStateIconOutline('available'),
         'commonQuestsTooltip': '',
         'commonQuestsEnable': True}

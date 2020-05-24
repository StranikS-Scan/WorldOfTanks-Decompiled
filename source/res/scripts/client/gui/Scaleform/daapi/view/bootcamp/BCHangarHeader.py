# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCHangarHeader.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.hangar_header import HangarHeader
from gui.Scaleform.genConsts.HANGAR_HEADER_QUESTS import HANGAR_HEADER_QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import events, EVENT_BUS_SCOPE

class BCHangarHeader(HangarHeader):

    def showQuestsWindow(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_QUESTS_VIEW), scope=EVENT_BUS_SCOPE.LOBBY)

    def onQuestBtnClick(self, questType, questID):
        if questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_COMMON:
            self.showQuestsWindow()

    def _getCommonQuestsToHeaderVO(self, vehicle):
        return [self._wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_COMMON, '', [self._headerQuestFormaterVo(enable=True, icon=RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_AVAILABLE, label='', questType=HANGAR_HEADER_QUESTS.QUEST_TYPE_COMMON, flag=RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_BLUE)])]

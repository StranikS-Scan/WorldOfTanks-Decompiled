# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_boards_battle_overlay.py
from gui.Scaleform.daapi.view.meta.EventBoardsBattleOverlayMeta import EventBoardsBattleOverlayMeta
from gui.Scaleform.daapi.view.lobby.event_boards.event_summary import getSummaryInfoData

class EventBoardsBattleOverlay(EventBoardsBattleOverlayMeta):
    __opener = None

    def setOpener(self, view):
        self.__opener = view
        ctx = self.__opener.ctx
        eventData = self.__opener.eventData
        data = getSummaryInfoData(eventData, ctx.get('leaderboard'), ctx.get('excelItem'))
        self.as_setDataS(data.getHeader())
        self.as_setExperienceDataS(data.getExperienceBlock())
        self.as_setStatisticsDataS(data.getStatisticsBlock())
        if data.isTable():
            self.as_setTableHeaderDataS(data.getTableHeaderData())
            self.as_setTableDataS(data.getTableData())

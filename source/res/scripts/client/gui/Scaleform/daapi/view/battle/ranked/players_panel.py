# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/ranked/players_panel.py
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.battle.ranked.ranked_voip_helper import RankedVoipHelper, VoiceChatControlTextStyles
from gui.Scaleform.daapi.view.meta.RankedPlayersPanelMeta import RankedPlayersPanelMeta

class PlayersPanel(RankedPlayersPanelMeta):

    def __init__(self):
        super(PlayersPanel, self).__init__()
        self.__voipHelper = RankedVoipHelper(component=self, textStyle=VoiceChatControlTextStyles.PLAYERS_PANEL)

    def onVoiceChatControlClick(self):
        self.__voipHelper.onVoiceChatControlClick()

    def setPeriod(self, period):
        self.__voipHelper.enable(enable=self.__isVoipControlEnabled(period))

    def _populate(self):
        super(PlayersPanel, self)._populate()
        self.__voipHelper.populate()
        self.__voipHelper.enable(enable=self.__isVoipControlEnabled())

    def _dispose(self):
        self.__voipHelper.dispose()
        super(PlayersPanel, self)._dispose()

    @classmethod
    def __isVoipControlEnabled(cls, period=None):
        if period is None:
            period = cls.sessionProvider.shared.arenaPeriod.getPeriod()
        return period == ARENA_PERIOD.PREBATTLE

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/ranked/full_stats.py
from gui.Scaleform.daapi.view.battle.ranked.ranked_voip_helper import RankedVoipHelper, VoiceChatControlTextStyles
from gui.Scaleform.daapi.view.meta.RankedFullStatsMeta import RankedFullStatsMeta

class FullStatsComponent(RankedFullStatsMeta):

    def __init__(self):
        super(FullStatsComponent, self).__init__()
        self.__voipHelper = RankedVoipHelper(component=self, textStyle=VoiceChatControlTextStyles.FULL_STATS)

    def onVoiceChatControlClick(self):
        self.__voipHelper.onVoiceChatControlClick()

    def _populate(self):
        super(FullStatsComponent, self)._populate()
        self.__voipHelper.populate()
        self.__voipHelper.enable(enable=True)

    def _dispose(self):
        self.__voipHelper.dispose()
        super(FullStatsComponent, self)._dispose()

    @staticmethod
    def _buildTabs(builder):
        builder.addStatisticsTab()
        builder.addBoostersTab()
        return builder.getTabs()

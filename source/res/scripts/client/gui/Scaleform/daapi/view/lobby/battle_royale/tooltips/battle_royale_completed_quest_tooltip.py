# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/tooltips/battle_royale_completed_quest_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from gui.server_events import IEventsCache
from gui.Scaleform.daapi.view.lobby.battle_royale.tooltips.battle_royale_tooltip_quest_helper import getQuestTooltipBlock

class BattleRoyaleQuestsTooltip(BlocksTooltipData):
    __eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ()

    def __init__(self, context):
        super(BattleRoyaleQuestsTooltip, self).__init__(context, TOOLTIP_TYPE.EPIC_QUESTS)
        self._setContentMargin(top=0, left=0, bottom=0, right=0)
        self._setMargins(afterBlock=0)
        self._setWidth(322)

    def _packBlocks(self, *args, **kwargs):
        allQuests = self.__eventsCache.getAllQuests()
        quests = [ allQuests.get(qId) for qId in args[1] ]
        if quests:
            return [self._packHeader()] + [ getQuestTooltipBlock(q) for q in quests ]
        return super(BattleRoyaleQuestsTooltip, self)._packBlocks()

    def _packHeader(self):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.epic_battle.questsTooltip.epicBattle.steelhunter.header())), img=backport.image(R.images.gui.maps.icons.quests.epic_steelhunter_quests_infotip()), txtPadding=formatters.packPadding(top=18, bottom=-12), txtOffset=20)

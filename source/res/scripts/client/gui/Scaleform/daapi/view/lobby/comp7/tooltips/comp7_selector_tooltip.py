# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/comp7/tooltips/comp7_selector_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.battle_selector import SeasonalBattleSelectorTooltip
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, time_utils
from skeletons.gui.game_control import IComp7Controller
_R_COMP7_SELECTOR_TOOLTIP = R.strings.comp7.selectorTooltip
_TOOLTIP_MIN_WIDTH = 280

class Comp7SelectorTooltip(SeasonalBattleSelectorTooltip):
    _battleController = dependency.descriptor(IComp7Controller)
    _TOOLTIP_TYPE = TOOLTIP_TYPE.COMP7_SELECTOR_INFO
    _TOOLTIP_WIDTH = _TOOLTIP_MIN_WIDTH
    _R_BATTLE_SELECTOR_STR = R.strings.comp7.seasonalBattleSelector

    @staticmethod
    def _getTitle():
        return backport.text(_R_COMP7_SELECTOR_TOOLTIP.title())

    @staticmethod
    def _getDescription():
        return backport.text(_R_COMP7_SELECTOR_TOOLTIP.desc())


class Comp7SelectorUnavailableTooltip(BlocksTooltipData):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, context):
        super(Comp7SelectorUnavailableTooltip, self).__init__(context, TOOLTIP_TYPE.COMP7_SELECTOR_UNAVAILABLE_INFO)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *_, **__):
        items = super(Comp7SelectorUnavailableTooltip, self)._packBlocks()
        items.append(self._packHeaderBlock())
        items.append(self._packInfoBlock())
        return items

    @staticmethod
    def _packHeaderBlock():
        return formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(_R_COMP7_SELECTOR_TOOLTIP.title())), desc=text_styles.main(backport.text(_R_COMP7_SELECTOR_TOOLTIP.desc())))

    @classmethod
    def _packInfoBlock(cls):
        nextSeason = cls.__comp7Controller.getNextSeason()
        if cls.__comp7Controller.isFrozen():
            text = backport.text(_R_COMP7_SELECTOR_TOOLTIP.unavailable.frozen())
        elif nextSeason is not None:
            nextCycle = nextSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
            time = backport.getDateTimeFormat(time_utils.makeLocalServerTime(nextCycle.startDate))
            text = backport.text(_R_COMP7_SELECTOR_TOOLTIP.unavailable.nextSeason(), time=time)
        else:
            text = backport.text(_R_COMP7_SELECTOR_TOOLTIP.unavailable.finished())
        return formatters.packTextBlockData(text=text_styles.main(text))

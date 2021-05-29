# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/mapbox/tooltips/mapbox_selector_tooltip.py
from gui import makeHtmlString
from gui.impl.gen import R
from gui.impl import backport
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.Scaleform.daapi.view.lobby.formatters import tooltips
from gui.Scaleform.daapi.view.lobby.mapbox import mapbox_helpers
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from skeletons.gui.game_control import IMapboxController
from gui.shared.formatters import text_styles

class MapboxSelectorTooltip(BlocksTooltipData):
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    __BODY_TEMPLATE_PATH = 'html_templates:lobby/tooltips/battle_type_selector'
    __BODY_TEMPLATE_KEY = SELECTOR_BATTLE_TYPES.MAPBOX

    def __init__(self, context):
        super(MapboxSelectorTooltip, self).__init__(context, TOOLTIP_TYPE.MAPBOX_SELECTOR_INFO)
        self._setWidth(320)

    def _packBlocks(self, *args):
        items = []
        items.append(self.__packMainBlock())
        if self.__mapboxCtrl.isFrozen() or not self.__mapboxCtrl.isEnabled():
            items.append(self.__packFrozenBlock())
        else:
            actualSeason = self.__mapboxCtrl.getCurrentSeason() or self.__mapboxCtrl.getNextSeason()
            seasonIsStarted = self.__mapboxCtrl.getCurrentSeason() is not None
            timeStrGetter = mapbox_helpers.getTillTimeString if seasonIsStarted else backport.getDateTimeFormat
            items += tooltips.getScheduleBlock(self.__mapboxCtrl, SELECTOR_BATTLE_TYPES.MAPBOX, actualSeason, seasonIsStarted, timeStrGetter)
        return items

    def __packMainBlock(self):
        header = backport.text(R.strings.tooltips.battleTypes.mapbox.header())
        body = makeHtmlString(self.__BODY_TEMPLATE_PATH, self.__BODY_TEMPLATE_KEY, ctx={'range': toRomanRangeString(self.__mapboxCtrl.getModeSettings().levels)})
        return formatters.packTitleDescBlock(title=text_styles.middleTitle(header), desc=text_styles.main(body))

    def __packFrozenBlock(self):
        return formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.battleTypes.mapbox.frozen.body())))

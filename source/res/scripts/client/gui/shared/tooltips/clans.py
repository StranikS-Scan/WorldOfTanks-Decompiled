# Embedded file name: scripts/client/gui/shared/tooltips/clans.py
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortTransportationViewHelper import FortTransportationViewHelper
from helpers import int2roman
from helpers.i18n import makeString as _ms

class ClanProfileFortBuildingTooltipData(BlocksTooltipData, FortTransportationViewHelper):

    def __init__(self, context):
        super(ClanProfileFortBuildingTooltipData, self).__init__(context, TOOLTIP_TYPE.CLAN_PROFILE)
        self._setContentMargin(top=15, left=19, bottom=21, right=22)
        self._setMargins(afterBlock=14)
        self._setWidth(380)
        self._description = None
        self._title = None
        return

    def _packBlocks(self, uid, level):
        description = _ms(FORTIFICATIONS.buildingsprocess_longdescr(uid))
        self._description = _ms(CLANS.SECTION_FORT_BUILDING_TOOLTIP_BODY, level=text_styles.stats(int2roman(level)), description=description)
        self._title = _ms(FORTIFICATIONS.buildings_buildingname(uid))
        items = super(ClanProfileFortBuildingTooltipData, self)._packBlocks()
        items.append(formatters.packTitleDescBlock(text_styles.highTitle(self._title), desc=text_styles.main(self._description) if self._description else None))
        return items

    def isOnNextTransportingStep(self):
        return False

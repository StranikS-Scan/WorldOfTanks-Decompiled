# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/badges_tooltips.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
_TOOLTIP_MIN_WIDTH = 362

class BadgesSuffixItem(BlocksTooltipData):

    def __init__(self, context):
        super(BadgesSuffixItem, self).__init__(context, TOOLTIPS_CONSTANTS.BADGES_SUFFIX_ITEM)
        self._setContentMargin(top=15, left=20, bottom=10, right=15)
        self._setMargins(afterBlock=0)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args, **kwargs):
        self._badgeId = args[0]
        return [formatters.packBuildUpBlockData([self.packHeader(), self.packBody()], gap=-2)]

    def packHeader(self):
        title = text_styles.middleTitle(backport.text(R.strings.badge.dyn('badge_{}'.format(self._badgeId))()))
        icon = backport.image(R.images.gui.maps.icons.library.badges.c_24x24.dyn('badge_{}'.format(self._badgeId))())
        value = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.badges.strips.c_64x24.dyn('strip_{}'.format(self._badgeId))()), 64, 24)
        return formatters.packTitleDescParameterWithIconBlockData(title=title, icon=icon, value=value, iconPadding=formatters.packPadding(left=3), valuePadding=formatters.packPadding(left=-80, top=-2), valueAtRight=True)

    def packBody(self):
        return formatters.packTextBlockData(text_styles.main(backport.text(R.strings.badge.dyn('badge_{}_descr'.format(self._badgeId))())))

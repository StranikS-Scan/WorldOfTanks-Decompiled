# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/ingame_help/detailed_help_pages.py
from comp7_core.gui.ingame_help.detailed_help_pages import Comp7CorePagesBuilder
from comp7_common.comp7_constants import ARENA_GUI_TYPE
from comp7.gui.ingame_help import HelpPagePriority
from gui.impl.gen import R

class Comp7PagesBuilder(Comp7CorePagesBuilder):
    _SUITABLE_CTX_KEYS = ('isComp7',)
    _MODE_RES_ROOT_TEXTS = R.strings.ingame_help.detailsHelp.comp7
    _MODE_RES_ROOT_IMAGES = R.images.comp7.gui.maps.icons.battleHelp

    @classmethod
    def priority(cls):
        return HelpPagePriority.COMP7

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['isComp7'] = arenaVisitor.getArenaGuiType() in ARENA_GUI_TYPE.COMP7_RANGE

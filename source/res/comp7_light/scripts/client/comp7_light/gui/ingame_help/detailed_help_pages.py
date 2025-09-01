# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/ingame_help/detailed_help_pages.py
from gui.impl.gen import R
from comp7_core.gui.ingame_help.detailed_help_pages import Comp7CorePagesBuilder
from comp7_light_constants import ARENA_GUI_TYPE
from comp7_light.gui.ingame_help import HelpPagePriority

class Comp7LightPagesBuilder(Comp7CorePagesBuilder):
    _SUITABLE_CTX_KEYS = ('isComp7Light',)
    _MODE_RES_ROOT_TEXTS = R.strings.ingame_help.detailsHelp.comp7Light
    _MODE_RES_ROOT_IMAGES = R.images.comp7_light.gui.maps.icons.battleHelp

    @classmethod
    def priority(cls):
        return HelpPagePriority.COMP7_LIGHT

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['isComp7Light'] = arenaVisitor.getArenaGuiType() == ARENA_GUI_TYPE.COMP7_LIGHT

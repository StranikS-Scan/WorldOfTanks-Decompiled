# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/ingame_help/fun_random_pages.py
from constants import ARENA_GUI_TYPE
from fun_random.gui.ingame_help import HelpPagePriority
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasBattleSubMode
from fun_random.gui.Scaleform.daapi.view.battle.hint_panel.hint_panel_plugin import HelpHintContext
from gui.impl import backport
from gui.ingame_help.detailed_help_pages import addPage, DetailedHelpPagesBuilder
from gui.shared.formatters import text_styles

class FunRandomHelpPagesBuilder(DetailedHelpPagesBuilder, FunSubModesWatcher):
    _SUITABLE_CTX_KEYS = ('isFunRandom',)

    @classmethod
    def priority(cls):
        return HelpPagePriority.FUN_RANDOM

    @classmethod
    @hasBattleSubMode(defReturn=())
    def buildPages(cls, _):
        pages = []
        battleSubMode = cls.getBattleSubMode()
        iconsRoot = battleSubMode.getIconsResRoot()
        localsRoot = battleSubMode.getLocalsResRoot()
        commonTitle = backport.text(localsRoot.detailsHelpTitle())
        for pageID, pageRes in sorted(localsRoot.detailsHelp.items()):
            addPage(pages, commonTitle, backport.text(pageRes.title()), text_styles.mainBig(backport.text(pageRes.description())), [], [], backport.image(iconsRoot.battle_help.dyn(pageID)()), hintCtx=HelpHintContext.FUN_RANDOM)

        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['isFunRandom'] = arenaVisitor.getArenaGuiType() == ARENA_GUI_TYPE.FUN_RANDOM

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/ingame_help/detailed_help_pages.py
from comp7.gui.ingame_help import HelpPagePriority
from comp7_common.comp7_constants import ARENA_GUI_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.ingame_help.detailed_help_pages import DetailedHelpPagesBuilder, addPage
from gui.shared.formatters import text_styles

class Comp7PagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('isComp7',)
    HINT_CONTEXT = None

    @classmethod
    def priority(cls):
        return HelpPagePriority.COMP7

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        comp7Header = backport.text(R.strings.ingame_help.detailsHelp.comp7.mainTitle())
        for pageName in ('seasonModifiers', 'poi', 'roleSkills', 'rules'):
            addPage(datailedList=pages, headerTitle=comp7Header, title=backport.text(R.strings.ingame_help.detailsHelp.comp7.dyn(pageName).title()), descr=text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.comp7.dyn(pageName)())), vKeys=[], buttons=[], image=backport.image(R.images.comp7.gui.maps.icons.battleHelp.dyn(pageName)()))

        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['isComp7'] = arenaVisitor.getArenaGuiType() in ARENA_GUI_TYPE.COMP7_RANGE

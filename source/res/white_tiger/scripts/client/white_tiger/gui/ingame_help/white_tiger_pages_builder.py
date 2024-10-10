# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/ingame_help/white_tiger_pages_builder.py
from cgf_components import wt_helpers
from gui.impl import backport
from gui.impl.gen import R
from gui.ingame_help.detailed_help_pages import DetailedHelpPagesBuilder, HelpPagePriority, addPage
from white_tiger_common.wt_constants import ARENA_GUI_TYPE

class WhiteTigerHelpPagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('isWhiteTiger',)

    @classmethod
    def priority(cls):
        return HelpPagePriority.DEFAULT

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        header = backport.text(R.strings.white_tiger.detailsHelp.mainTitle())
        vehType = 'hunter'
        if ctx['isBoss']:
            vehType = 'boss'
        for pageNum in xrange(1, 6):
            pageName = 'page' + str(pageNum)
            addPage(datailedList=pages, headerTitle=header, title=backport.text(R.strings.white_tiger.detailsHelp.dyn(vehType).dyn(pageName).title()), descr=backport.text(R.strings.white_tiger.detailsHelp.dyn(vehType).dyn(pageName).description()), vKeys=[], buttons=[], image=backport.image(R.images.white_tiger.gui.maps.icons.battleHelp.dyn(vehType).dyn(pageName)()))

        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        isWhiteTiger = arenaVisitor.getArenaGuiType() == ARENA_GUI_TYPE.WHITE_TIGER
        ctx['isWhiteTiger'] = isWhiteTiger
        if isWhiteTiger:
            ctx['isBoss'] = wt_helpers.isBoss()

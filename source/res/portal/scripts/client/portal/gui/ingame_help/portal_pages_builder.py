# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/ingame_help/portal_pages_builder.py
from gui.impl import backport
from gui.impl.gen import R
from gui.ingame_help.detailed_help_pages import DetailedHelpPagesBuilder, HelpPagePriority, addPage
from portal_common.portal_constants import ARENA_GUI_TYPE

class PortalHelpPagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('isPortal',)

    @classmethod
    def priority(cls):
        return HelpPagePriority.COMP7

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        header = backport.text(R.strings.portal_event.detailsHelp.mainTitle())
        addPage(datailedList=pages, headerTitle=header, title=backport.text(R.strings.portal_event.detailsHelp.page1.title()), descr=backport.text(R.strings.portal_event.detailsHelp.page1.description()), image=backport.image(R.images.portal.gui.maps.icons.battleHelp.page1()), vKeys=[], buttons=[])
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        isPortal = arenaVisitor.getArenaGuiType() == ARENA_GUI_TYPE.PORTAL
        ctx['isPortal'] = isPortal

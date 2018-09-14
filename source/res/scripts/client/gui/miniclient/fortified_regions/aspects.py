# Embedded file name: scripts/client/gui/miniclient/fortified_regions/aspects.py
from gui.shared.formatters import text_styles
from helpers import aop
from helpers.i18n import makeString as _ms
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES

class OnViewPopulate(aop.Aspect):

    def atReturn(self, cd):
        cd.self.as_showMiniClientInfoS(text_styles.alert(_ms('#miniclient:fort_welcome_view/description')), _ms('#miniclient:personal_quests_welcome_view/continue_download'))


class OnFortifiedRegionsOpen(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        cd.self.as_loadViewS(FORTIFICATION_ALIASES.WELCOME_VIEW_LINKAGE, '')

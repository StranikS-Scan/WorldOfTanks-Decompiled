# Embedded file name: scripts/client/gui/miniclient/personal_quests/aspects.py
from gui.shared.formatters import text_styles
from helpers import aop
from helpers.i18n import makeString as _ms
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES

class OnViewPopulate(aop.Aspect):

    def atReturn(self, cd):
        cd.self.as_showMiniClientInfoS(text_styles.alert(_ms('#miniclient:personal_quests_welcome_view/description')), _ms('#miniclient:personal_quests_welcome_view/continue_download'))


class PersonalQuestsTabSelect(aop.Aspect):

    def atCall(self, cd):
        if cd.args[0] == QUESTS_ALIASES.TAB_PERSONAL_QUESTS:
            cd.avoid()
            cd.self._showWelcomeView()

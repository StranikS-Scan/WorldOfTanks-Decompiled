# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/abstract/RegularExtAchievement.py
from RegularAchievement import RegularAchievement
from helpers import i18n
from gui.shared.formatters import text_styles

class RegularExtAchievement(RegularAchievement):
    USER_DESCR_TEMPLATE = '%(title)s\n<font size="3">&nbsp;</font>\n%(standard)s\n%(ext)s'

    def getUserDescription(self):
        return RegularExtAchievement.USER_DESCR_TEMPLATE % {'title': text_styles.main(self._getTranslatedText('#achievements:%s_descr')),
         'standard': text_styles.main(self._getStandardDescription()),
         'ext': text_styles.main(self._getExtDescription())}

    def _getTranslatedText(self, translationRef):
        return text_styles.main(i18n.makeString(translationRef % self._getActualName()))

    def _getExtDescription(self):
        return self._getTranslatedText('#achievements:%s_ext_descr') % {'condition': text_styles.creditsSmall(self._getExtValues()) + self._getConditionText()}

    def _getStandardDescription(self):
        return self._getTranslatedText('#achievements:%s_standard_descr') % {'condition': text_styles.creditsSmall(self._getStandardValues()) + self._getConditionText()}

    def _getStandardValues(self):
        pass

    def _getExtValues(self):
        pass

    def _getConditionText(self):
        condTextKey = '#achievements:%s_condition_text' % self._getActualName()
        return text_styles.creditsSmall(i18n.makeString(condTextKey)) if i18n.doesTextExist(condTextKey) else ''

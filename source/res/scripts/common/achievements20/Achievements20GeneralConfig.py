# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/achievements20/Achievements20GeneralConfig.py
from typing import TYPE_CHECKING
from achievements20.settings import Achievements20GeneralConst
if TYPE_CHECKING:
    from typing import Optional

class Achievements20GeneralConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def isWTREnabled(self):
        return self._config.get(Achievements20GeneralConst.IS_WTR_ENABLED)

    def isLayoutEnabled(self):
        return self._config.get(Achievements20GeneralConst.IS_LAYOUT_ENABLED)

    def isSummaryEnabled(self):
        return self._config.get(Achievements20GeneralConst.IS_SUMMARY_ENABLED, True)

    def isLogSettingLayoutEnabled(self):
        return self._config.get(Achievements20GeneralConst.IS_LOG_SETTING_LAYOUT_ENABLED, False)

    def isLogRequestPlayerInfoEnabled(self):
        return self._config.get(Achievements20GeneralConst.IS_LOG_REQUEST_PLAYER_INFO_ENABLED, False)

    def getRequiredCountOfBattles(self):
        return self._config.get(Achievements20GeneralConst.REQUIRED_COUNT_OF_BATTLES)

    def _getLayout(self):
        return self._config.get(Achievements20GeneralConst.LAYOUT, {})

    def getLayoutLength(self):
        return self._getLayout().get(Achievements20GeneralConst.LAYOUT_LENGTH)

    def getStagesOfWTR(self):
        return self._config.get(Achievements20GeneralConst.WTR_STAGES, [])

    def getManualRules(self):
        return self._getLayout().get(Achievements20GeneralConst.MANUAL_RULES, [])

    def _getAutoGeneratingRules(self):
        return self._getLayout().get(Achievements20GeneralConst.AUTO_GENERATING_RULES, {})

    def getAutoGeneratingMainRules(self):
        return self._getAutoGeneratingRules().get(Achievements20GeneralConst.MAIN_SECTIONS, [])

    def getAutoGeneratingExtraRules(self):
        return self._getAutoGeneratingRules().get(Achievements20GeneralConst.EXTRA_SECTIONS, [])

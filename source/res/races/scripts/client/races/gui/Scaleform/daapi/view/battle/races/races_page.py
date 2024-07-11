# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/Scaleform/daapi/view/battle/races/races_page.py
import logging
from gui.Scaleform.daapi.view.battle.shared import SharedPage
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
_logger = logging.getLogger(__name__)
_RACES_COMPONENTS_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.RACES_HUD, BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, BATTLE_VIEW_ALIASES.PREBATTLE_TIMER)), (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)), (BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.RACES_HUD,))))

class RacesPage(SharedPage):

    def __init__(self):
        _logger.debug('RacesPage.__init__')
        super(RacesPage, self).__init__(components=_RACES_COMPONENTS_CONFIG, external=())

    def _onBattleLoadingStart(self):
        _logger.debug('RacesPage._onBattleLoadingStart')
        self._blToggling = set(self.as_getComponentsVisibilityS())
        self._blToggling.difference_update([BATTLE_VIEW_ALIASES.BATTLE_LOADING])
        self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.BATTLE_LOADING}, hidden=self._blToggling)

    def _addDefaultHitDirectionController(self, controllers):
        return controllers

    def _handleToggleFullStats(self, event):
        pass

    def _handleToggleFullStatsQuestProgress(self, event):
        pass

    def _handleToggleFullStatsPersonalReserves(self, event):
        pass

    def _handleGUIToggled(self, event):
        pass

    def _handleRadialMenuCmd(self, event):
        pass

    def _changeCtrlMode(self, ctrlMode):
        _logger.info('RacesPage._changeCtrlMode: %s', str(ctrlMode))

    def _canShowPostmortemTips(self):
        return False

    def _switchToPostmortem(self):
        pass

    def as_setPostmortemTipsVisibleS(self, value):
        pass

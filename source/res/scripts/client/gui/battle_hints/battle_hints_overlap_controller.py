# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_hints/battle_hints_overlap_controller.py
from enum import Enum
from logging import getLogger
import typing
from constants import ARENA_BONUS_TYPE
from helpers import dependency
from PlayerEvents import g_playerEvents
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_hints.battle_hints_overlap_controller import IBattleHintsOverlapController
from frameworks.wulf import WindowLayer
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.shared import SharedPage
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.battle_hints.queues import BattleHint
_logger = getLogger(__name__)

class HintScope(str, Enum):
    NEWBIE = 'newbie'
    STORY_MODE = 'story_mode'
    LOCAL_STORY = 'local_story'


NEWBIE_SETTINGS = {BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR,
 BATTLE_VIEW_ALIASES.PLAYERS_PANEL,
 BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
 BATTLE_VIEW_ALIASES.QUEST_PROGRESS_TOP_VIEW,
 BATTLE_VIEW_ALIASES.BATTLE_TIMER,
 BATTLE_VIEW_ALIASES.DEBUG_PANEL}
OVERLAP_SETTINGS = {ARENA_BONUS_TYPE.REGULAR: {HintScope.NEWBIE.value: NEWBIE_SETTINGS,
                            HintScope.LOCAL_STORY.value: NEWBIE_SETTINGS},
 ARENA_BONUS_TYPE.WINBACK: {HintScope.NEWBIE.value: NEWBIE_SETTINGS},
 ARENA_BONUS_TYPE.RANDOM_NP2: {HintScope.NEWBIE.value: NEWBIE_SETTINGS},
 ARENA_BONUS_TYPE.MAPBOX: {HintScope.LOCAL_STORY.value: NEWBIE_SETTINGS}}

def addSettings(arenaBonusType, hintScope, views):
    if arenaBonusType not in OVERLAP_SETTINGS:
        OVERLAP_SETTINGS[arenaBonusType] = {}
    if hintScope not in OVERLAP_SETTINGS[arenaBonusType]:
        OVERLAP_SETTINGS[arenaBonusType][hintScope] = views
    else:
        _logger.warning('Settings for arenaBattleType <%s> scope <%s> already exist. Skipping', arenaBonusType, hintScope)


class BattleHintsOverlapController(IBattleHintsOverlapController):
    _appLoader = dependency.descriptor(IAppLoader)
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleHintsOverlapController, self).__init__()
        self._hiddenViews = set()
        g_playerEvents.onShowBattleHint += self._onHintShown
        g_playerEvents.onEmptyBattleHintsQueue += self._onEmptyHintsQueue
        g_playerEvents.onAvatarBecomeNonPlayer += self._clear
        g_playerEvents.onAvatarBecomePlayer += self._clear
        _logger.debug('Initialized.')

    def fini(self):
        g_playerEvents.onShowBattleHint -= self._onHintShown
        g_playerEvents.onEmptyBattleHintsQueue -= self._onEmptyHintsQueue
        g_playerEvents.onAvatarBecomeNonPlayer -= self._clear
        g_playerEvents.onAvatarBecomePlayer -= self._clear
        self._hiddenViews = set()
        _logger.debug('Destroyed.')

    def _onHintShown(self, battleHint):
        scope = battleHint.model.props.scope
        page = self._getBattlePageView()
        scopeSettings = OVERLAP_SETTINGS.get(self._sessionProvider.arenaVisitor.getArenaBonusType(), {}).get(scope)
        if scopeSettings is None:
            return
        else:
            viewsToHide = scopeSettings.difference(self._hiddenViews)
            if page and viewsToHide:
                self._hiddenViews.update(viewsToHide)
                page.setComponentsVisibilityWithFade(hidden=viewsToHide)
                _logger.debug('onHintShown scope <%s>: hide panels <%s>', scope, viewsToHide)
            return

    def _onEmptyHintsQueue(self):
        page = self._getBattlePageView()
        if page and self._hiddenViews:
            page.setComponentsVisibilityWithFade(visible=self._hiddenViews)
            self._clear()

    def _clear(self):
        self._hiddenViews = set()

    def _getBattlePageView(self):
        app = self._appLoader.getDefBattleApp()
        if app and app.containerManager:
            return app.containerManager.getContainer(WindowLayer.VIEW).getView()
        else:
            _logger.warning('Battle page not found.')
            return None

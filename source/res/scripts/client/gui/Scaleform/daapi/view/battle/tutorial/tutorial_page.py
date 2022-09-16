# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/tutorial/tutorial_page.py
from gui.Scaleform.daapi.view.battle.classic.page import DynamicAliases
from gui.Scaleform.daapi.view.battle.shared import SharedPage
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager, plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings as _markers2d_settings
from gui.Scaleform.daapi.view.battle.shared.minimap import common
from gui.Scaleform.daapi.view.battle.shared.minimap import component
from gui.Scaleform.daapi.view.battle.shared.minimap import settings as _minimap_settings
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from gui.Scaleform.daapi.view.meta.BattleTutorialMeta import BattleTutorialMeta
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import minimap_utils
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from helpers import i18n

class TutorialComponent(BattleTutorialMeta):
    pass


class TutorialMinimapComponent(component.MinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(TutorialMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['tutorial'] = TutorialTargetPlugin
        return setup


class TutorialTargetPlugin(common.EntriesPlugin):

    def addTarget(self, markerID, position):
        matrix = minimap_utils.makePositionMatrix(position)
        model = self._addEntryEx(markerID, _minimap_settings.ENTRY_SYMBOL_NAME.TUTORIAL_TARGET, _minimap_settings.CONTAINER_NAME.ICONS, matrix=matrix, active=True)
        return model is not None

    def delTarget(self, markerID):
        return self._delEntryEx(markerID)


class TutorialStaticObjectsPlugin(plugins.MarkerPlugin):
    __slots__ = ('__weakref__', '__objects')

    def __init__(self, parentObj):
        super(TutorialStaticObjectsPlugin, self).__init__(parentObj)
        self.__objects = {}

    def addStaticObject(self, objectID, position):
        if objectID in self.__objects:
            return False
        markerID = self._createMarkerWithPosition(_markers2d_settings.MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER, position, active=True)
        self.__objects[objectID] = markerID
        return True

    def delStaticObject(self, objectID):
        markerID = self.__objects.pop(objectID, None)
        if markerID is not None:
            self._destroyMarker(markerID)
            return True
        else:
            return False

    def setupStaticObject(self, objectID, shape, minDistance, maxDistance, distance, color):
        if objectID in self.__objects:
            self._invokeMarker(self.__objects[objectID], 'init', shape, minDistance, maxDistance, distance, i18n.makeString(INGAME_GUI.MARKER_METERS), color)

    def setDistanceToObject(self, objectID, distance):
        if objectID in self.__objects:
            self._invokeMarker(self.__objects[objectID], 'setDistance', distance)


class TutorialMarkersManager(MarkersManager):

    def _setupPlugins(self, arenaVisitor):
        setup = super(TutorialMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['tutorial'] = TutorialStaticObjectsPlugin
        return setup


_TUTORIAL_COMPONENTS_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER, BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER)), (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,))), viewsConfig=((DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer),))
_TUTORIAL_EXTERNAL_COMPONENTS = (CrosshairPanelContainer, TutorialMarkersManager)

class TutorialPage(SharedPage):

    def __init__(self):
        super(TutorialPage, self).__init__(components=_TUTORIAL_COMPONENTS_CONFIG, external=_TUTORIAL_EXTERNAL_COMPONENTS)

    def _onBattleLoadingStart(self):
        self._blToggling = set(self.as_getComponentsVisibilityS())
        self._blToggling.difference_update([BATTLE_VIEW_ALIASES.BATTLE_LOADING])
        self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.BATTLE_LOADING}, hidden=self._blToggling)

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

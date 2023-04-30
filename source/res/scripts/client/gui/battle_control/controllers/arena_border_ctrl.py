# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/arena_border_ctrl.py
import BigWorld
import Math
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared import g_eventBus
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.doc_loaders import GuiColorsLoader
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core import settings_constants

class _SHOW_MODE(object):
    SHOW_BY_ALT_PRESS = 0
    SHOW_ALWAYS = 1
    HIDE = 2
    ALWAYS_HIDE = 3


class _DISPLAY_MODE(object):
    TYPE_WALL = 0
    TYPE_DOTTED = 1
    TYPE_HIDE = 2


class ArenaBorderController(IArenaLoadController):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__arenaVisitor = None
        self.__spaceID = None
        self.__showMode = _SHOW_MODE.HIDE
        self.__drawType = 0
        self.__color = Math.Vector4(0, 0, 0, 0)
        return

    def startControl(self, battleCtx, arenaVisitor):
        self.__arenaVisitor = arenaVisitor
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        g_eventBus.addListener(GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=EVENT_BUS_SCOPE.BATTLE)

    def stopControl(self):
        self.__arenaVisitor = None
        self.__spaceID = None
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        g_eventBus.removeListener(GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def spaceLoadCompleted(self):
        if BigWorld.player().spaceID <= 0:
            return
        arenaBoundingBox = self.__arenaVisitor.type.getBoundingBox()
        bounds = Math.Vector4(arenaBoundingBox[0][0], arenaBoundingBox[0][1], arenaBoundingBox[1][0], arenaBoundingBox[1][1])
        self.__spaceID = BigWorld.player().spaceID
        self._applySetting(self.settingsCore.getSetting(settings_constants.BATTLE_BORDER_MAP.MODE_SHOW_BORDER), self.settingsCore.getSetting(settings_constants.BATTLE_BORDER_MAP.TYPE_BORDER), self.__getCurrentColor(self.settingsCore.getSetting(settings_constants.GRAPHICS.COLOR_BLIND)))
        BigWorld.ArenaBorderHelper.setArenaBorderBounds(self.__spaceID, bounds)

    def getControllerID(self):
        return BATTLE_CTRL_ID.ARENA_BORDER

    def getDrawType(self):
        return self.__drawType

    def _applySetting(self, showMode, drawType, color):
        if not self.__spaceID:
            return
        self.__showMode = showMode
        self.__drawType = drawType
        self.__color = color
        BigWorld.ArenaBorderHelper.setArenaBorderVisible(self.__spaceID, self.__drawType != _DISPLAY_MODE.TYPE_HIDE)
        BigWorld.ArenaBorderHelper.setArenaBorderDrawType(self.__spaceID, self.__drawType)
        g_eventBus.handleEvent(GameEvent(GameEvent.ARENA_BORDER_TYPE_CHANGED, {'drawType': drawType}), scope=EVENT_BUS_SCOPE.BATTLE)
        distanceFaderMode = 0
        if self.__showMode == _SHOW_MODE.HIDE:
            distanceFaderMode = 1
        if self.__showMode == _SHOW_MODE.SHOW_BY_ALT_PRESS or self.__showMode == _SHOW_MODE.ALWAYS_HIDE:
            distanceFaderMode = 2
        BigWorld.ArenaBorderHelper.setArenaBorderDistanceFadeMode(self.__spaceID, distanceFaderMode)
        BigWorld.ArenaBorderHelper.setArenaBorderColor(self.__spaceID, color)
        BigWorld.ArenaBorderHelper.updatePolygonBordersColor(self.__spaceID, self.settingsCore.getSetting('isColorBlind'))

    def __handleShowExtendedInfo(self, event):
        if not self.__spaceID:
            return
        if self.__showMode != _SHOW_MODE.SHOW_BY_ALT_PRESS:
            return
        distanceFaderMode = 2
        if event.ctx['isDown']:
            distanceFaderMode = 0
        BigWorld.ArenaBorderHelper.setArenaBorderDistanceFadeMode(self.__spaceID, distanceFaderMode)

    def __onSettingsChanged(self, diff):
        if not self.__spaceID:
            return
        dirty = False
        showMode = self.__showMode
        drawType = self.__drawType
        color = self.__color
        if settings_constants.BATTLE_BORDER_MAP.TYPE_BORDER in diff:
            drawType = diff[settings_constants.BATTLE_BORDER_MAP.TYPE_BORDER]
            dirty = True
        if settings_constants.BATTLE_BORDER_MAP.MODE_SHOW_BORDER in diff:
            showMode = diff[settings_constants.BATTLE_BORDER_MAP.MODE_SHOW_BORDER]
            dirty = True
        if settings_constants.GRAPHICS.COLOR_BLIND in diff:
            color = self.__getCurrentColor(diff[settings_constants.GRAPHICS.COLOR_BLIND])
            dirty = True
        if dirty:
            self._applySetting(showMode, drawType, color)

    def __getCurrentColor(self, colorBlind):
        colors = GuiColorsLoader.load()
        scheme = colors.getSubScheme('areaBorder', 'color_blind' if colorBlind else 'default')
        color = scheme['rgba'] / 255
        return color


class BattleRoyaleBorderCtrl(ArenaBorderController):

    def _applySetting(self, showMode, _, color):
        super(BattleRoyaleBorderCtrl, self)._applySetting(_SHOW_MODE.SHOW_ALWAYS, _DISPLAY_MODE.TYPE_DOTTED, color)

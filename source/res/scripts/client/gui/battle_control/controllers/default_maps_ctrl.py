# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/default_maps_ctrl.py
import Event
from gui.battle_control import minimap_utils
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import IViewComponentsController
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class DefaultMapsController(IViewComponentsController):

    def __init__(self, setup):
        super(DefaultMapsController, self).__init__()
        self._plugins = {}
        self._miniMapUi = None
        self._eManager = Event.EventManager()
        return

    def getMinimapPositionById(self, cellId):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        if self._miniMapUi is not None:
            bottomLeft, upperRight = sessionProvider.arenaVisitor.type.getBoundingBox()
            return minimap_utils.getPositionByCellIndex(cellId, bottomLeft, upperRight, self._miniMapUi.getMinimapDimensions())
        else:
            return

    def getMinimapCellIdByPosition(self, position):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        bb = sessionProvider.arenaVisitor.type.getBoundingBox()
        return self._miniMapUi is not None and bb[0][0] <= position.x <= bb[1][0] and (minimap_utils.getCellIdFromPosition(position, bb, self._miniMapUi.getMinimapDimensions()) if bb[0][1] <= position.z <= bb[1][1] else None)

    def getMinimapCellNameById(self, cellId):
        return minimap_utils.getCellName(cellId, self._miniMapUi.getMinimapDimensions()) if self._miniMapUi is not None else ''

    def hasMinimapGrid(self):
        return self._miniMapUi.hasMinimapGrid() if self._miniMapUi is not None else False

    def setViewComponents(self, *components):
        self._miniMapUi = components[0]

    def getControllerID(self):
        return BATTLE_CTRL_ID.MAPS

    def clearViewComponents(self):
        self._miniMapUi = None
        return

    def startControl(self):
        pass

    def stopControl(self):
        self._eManager.clear()
        self._eManager = None
        return

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/fullmap.py
import GUI
from gui.Scaleform.daapi.view.battle.classic.minimap import GlobalSettingsPlugin
from gui.Scaleform.daapi.view.battle.pve_base.minimap import PveMinimapComponent
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import PersonalEntriesPlugin
from gui.Scaleform.genConsts.LAYER_NAMES import LAYER_NAMES
from gui.battle_control import minimap_utils
_FLASH_NAME = 'pveFullMap'
_MINIMAP_COMPONENT_PATH = '_level0.root.{}.main.{}.entriesContainer'.format(LAYER_NAMES.VIEWS, _FLASH_NAME)
_MINIMAP_SIZE = (352, 352)

class PveFullMapGlobalSettingsPlugin(GlobalSettingsPlugin):

    def _toogleVisible(self):
        pass


class PveFullMapPersonalEntriesPlugin(PersonalEntriesPlugin):
    __slots__ = ()

    def __init__(self, parentObj):
        super(PveFullMapPersonalEntriesPlugin, self).__init__(parentObj)
        bottomLeft, upperRight = self._parentObj.getBoundingBox()
        width = upperRight[0] - bottomLeft[0]
        self.setDefaultViewRangeCircleSize(width * minimap_utils.MINIMAP_SIZE[0] / _MINIMAP_SIZE[0])


class PveFullMapComponent(PveMinimapComponent):

    def setMinimapCenterEntry(self, entityID):
        pass

    def setVisibleRect(self, bl, tr):
        pass

    def setZoom(self, zoom):
        pass

    def _setupPlugins(self, arenaVisitor):
        setup = super(PveFullMapComponent, self)._setupPlugins(arenaVisitor)
        setup['settings'] = PveFullMapGlobalSettingsPlugin
        setup['personal'] = PveFullMapPersonalEntriesPlugin
        return setup

    def _getFlashName(self):
        return _FLASH_NAME

    def _createFlashComponent(self):
        return GUI.WGPveMinimapGUIComponentAS3(self.app.movie, _MINIMAP_COMPONENT_PATH)

    def _getMinimapSize(self):
        return _MINIMAP_SIZE

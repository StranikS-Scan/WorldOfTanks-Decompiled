# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/Scaleform/daapi/view/battle/markers_components.py
import BigWorld
from chat_commands_consts import INVALID_TARGET_ID
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import MinimapMarkerComponent
from helpers.CallbackDelayer import CallbackDelayer
from items import vehicles

class IlluminationFlareMinimapMarker(MinimapMarkerComponent):

    def __init__(self, config, matrixProduct, entity=None, targetID=INVALID_TARGET_ID, isVisible=True):
        super(IlluminationFlareMinimapMarker, self).__init__(config, matrixProduct, entity, targetID, isVisible)
        self._callbackDelayer = CallbackDelayer()
        self._launchTime = BigWorld.serverTime()

    @property
    def _equipment(self):
        return vehicles.g_cache.getEquipmentByName('poi_illumination_flare')

    def _createMarker(self, **kwargs):
        super(IlluminationFlareMinimapMarker, self)._createMarker(**kwargs)
        self._setRadius(self._equipment.startRadius)
        self._callbackDelayer.delayCallback(self._equipment.delay, self._updateRadius)

    def _deleteMarker(self):
        self._callbackDelayer.clearCallbacks()
        super(IlluminationFlareMinimapMarker, self)._deleteMarker()

    def _updateRadius(self):
        timeMul = min(1, (BigWorld.serverTime() - self._launchTime - self._equipment.delay) / self._equipment.duration)
        radiusDiff = self._equipment.startRadius - self._equipment.endRadius
        radius = self._equipment.startRadius - timeMul * radiusDiff
        self._setRadius(radius)
        self._callbackDelayer.delayCallback(0.1, self._updateRadius)

    def _setRadius(self, radius):
        gui = self._gui()
        if gui and self._isMarkerExists:
            gui.invoke(self.componentID, 'setRadius', radius)

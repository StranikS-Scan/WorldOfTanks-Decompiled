# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/lobby/vehicle_preview/vehicle_preview.py
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview
from gui.prb_control.entities.listener import IGlobalListener
from last_stand.gui.sounds import playSound
from last_stand.gui.sounds.sound_constants import LS_PREVIEW_ENTER, LS_PREVIEW_EXIT, HANGAR_SOUND_SETTINGS

class LSVehiclePreview(VehiclePreview, IGlobalListener):
    _COMMON_SOUND_SPACE = HANGAR_SOUND_SETTINGS

    def _populate(self):
        super(LSVehiclePreview, self)._populate()
        playSound(LS_PREVIEW_ENTER)
        self.startGlobalListening()

    def _dispose(self):
        self.stopGlobalListening()
        playSound(LS_PREVIEW_EXIT)
        super(LSVehiclePreview, self)._dispose()

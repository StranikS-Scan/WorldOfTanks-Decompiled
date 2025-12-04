# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/Scaleform/daapi/view/lobby/hangar/armory_yard_style_preview.py
from armory_yard.gui.Scaleform.daapi.view.lobby.hangar.sound_constants import ARMORY_YARD_VEHICLE_PREVIEW_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.vehicle_preview.style_preview import VehicleStylePreview
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardController

class ArmoryYardStylePreview(VehicleStylePreview, IGlobalListener):
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    _COMMON_SOUND_SPACE = ARMORY_YARD_VEHICLE_PREVIEW_SOUND_SPACE

    def __init__(self, ctx=None):
        super(ArmoryYardStylePreview, self).__init__(ctx)
        self.__ctx = ctx

    def onPrbEntitySwitching(self):
        self.__armoryYardCtrl.unloadScene(isReload=False)
        self.closeView()
        showHangar()

    def _populate(self):
        super(ArmoryYardStylePreview, self)._populate()
        self.__armoryYardCtrl.updateVisibilityHangarHeaderMenu()
        self.startGlobalListening()
        self.__armoryYardCtrl.onUpdated += self.__checkExit

    def _dispose(self):
        self.stopGlobalListening()
        super(ArmoryYardStylePreview, self)._dispose()
        self.__armoryYardCtrl.updateVisibilityHangarHeaderMenu(isVisible=True)
        if self.__armoryYardCtrl.isVehiclePreview:
            self.__armoryYardCtrl.unloadScene(isReload=True)
        self.__armoryYardCtrl.onUpdated -= self.__checkExit

    def __checkExit(self):
        if not self.__armoryYardCtrl.isActive():
            self.__armoryYardCtrl.unloadScene(isReload=True)
            self.closeView()
            showHangar()

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_STYLE_PROGRESSION_PY_ALIAS:
            viewPy.setCtx(self.__ctx)

    def closeView(self):
        self.destroy()

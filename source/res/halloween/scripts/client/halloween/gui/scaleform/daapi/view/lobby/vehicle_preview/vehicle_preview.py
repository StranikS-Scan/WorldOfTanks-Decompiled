# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/lobby/vehicle_preview/vehicle_preview.py
from __future__ import absolute_import
import BigWorld
from HeroTank import HeroTank
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from gui.prb_control.entities.listener import IGlobalListener
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.event_dispatcher import showVehPostProgressionView
from halloween.gui.scaleform.genConsts.HALLOWEEN_HANGAR_ALIASES import HALLOWEEN_HANGAR_ALIASES
from halloween.gui.shared.event_dispatcher import showHeroTankPreview, showHangar
from halloween.gui.sounds import playSound
from halloween.gui.sounds.sound_constants import HW_PREVIEW_ENTER, HW_PREVIEW_EXIT, HANGAR_SOUND_SETTINGS

class HWVehiclePreview(VehiclePreview, IGlobalListener):
    _COMMON_SOUND_SPACE = HANGAR_SOUND_SETTINGS

    def __init__(self, ctx=None):
        self.__ctx = ctx
        super(HWVehiclePreview, self).__init__(ctx)

    def setBottomPanel(self):
        if self.__ctx.get('isKingReward') or self.__ctx.get('isHeroTank'):
            self.as_setBottomPanelS(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_LINKAGE)

    def closeView(self):
        showHangar()

    def handleSelectedEntityUpdated(self, event):
        ctx = event.ctx
        entity = BigWorld.entities.get(ctx['entityId'], None)
        if ctx['state'] == CameraMovementStates.MOVING_TO_OBJECT:
            if isinstance(entity, HeroTank):
                descriptor = entity.typeDescriptor
                if descriptor:
                    vehicleCD = descriptor.type.compactDescr
                    showHeroTankPreview(vehicleCD, previewAlias=HALLOWEEN_HANGAR_ALIASES.HALLOWEEN_VEHICLE_PREVIEW, backOutfit=self.__ctx.get('outfit'), backBtnLabel=backport.text(R.strings.menu.cst_item_ctx_menu.preview()), isHiddenMenu=True, isKingReward=self.__ctx.get('isKingReward', False))
            elif entity.id == self._hangarSpace.space.vehicleEntityId:
                self._processBackClick({'entity': entity})
        return

    def _populate(self):
        super(HWVehiclePreview, self)._populate()
        playSound(HW_PREVIEW_ENTER)
        self.startGlobalListening()

    def _dispose(self):
        self.stopGlobalListening()
        playSound(HW_PREVIEW_EXIT)
        super(HWVehiclePreview, self)._dispose()

    def _processBackClick(self, ctx=None):
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.handleSelectedEntityUpdated)
        state = getLobbyStateMachine().getStateFromView(self)
        if state:
            state.goBack()

    def onGoToPostProgressionClick(self):
        self._resetPostProgressionBullet()
        showVehPostProgressionView(self._vehicleCD)

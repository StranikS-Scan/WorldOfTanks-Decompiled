# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/lobby/vehicle_preview/vehicle_preview.py
import BigWorld
from HeroTank import HeroTank
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from gui.prb_control.entities.listener import IGlobalListener
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.event_dispatcher import showVehPostProgressionView
from last_stand.gui.scaleform.genConsts.LAST_STAND_HANGAR_ALIASES import LAST_STAND_HANGAR_ALIASES
from last_stand.gui.shared.event_dispatcher import showHeroTankPreview, showHangar
from last_stand.gui.sounds import playSound
from last_stand.gui.sounds.sound_constants import LS_PREVIEW_ENTER, LS_PREVIEW_EXIT, HANGAR_SOUND_SETTINGS

class LSVehiclePreview(VehiclePreview, IGlobalListener):
    _COMMON_SOUND_SPACE = HANGAR_SOUND_SETTINGS

    def onGoToPostProgressionClick(self):
        self._resetPostProgressionBullet()
        showVehPostProgressionView(self._vehicleCD)

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
                    showHeroTankPreview(vehicleCD, previewAlias=LAST_STAND_HANGAR_ALIASES.LS_VEHICLE_PREVIEW, backOutfit=self.__ctx.get('outfit'), backBtnLabel=backport.text(R.strings.menu.cst_item_ctx_menu.preview()), isHiddenMenu=True)
            elif entity.id == self._hangarSpace.space.vehicleEntityId:
                self._processBackClick({'entity': entity})
        return

    def _populate(self):
        super(LSVehiclePreview, self)._populate()
        playSound(LS_PREVIEW_ENTER)
        self.startGlobalListening()

    def _dispose(self):
        self.stopGlobalListening()
        playSound(LS_PREVIEW_EXIT)
        super(LSVehiclePreview, self)._dispose()

    def _processBackClick(self, ctx=None):
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.handleSelectedEntityUpdated)
        super(LSVehiclePreview, self)._processBackClick(ctx)

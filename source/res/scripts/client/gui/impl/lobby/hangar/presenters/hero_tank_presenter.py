# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/hero_tank_presenter.py
from __future__ import absolute_import
import logging
import BigWorld
import Math
from GUI import WGMarkerPositionController
from HeroTank import HeroTank
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from gui.impl.gen.view_models.views.lobby.hangar.hero_tank_model import HeroTankModel
from gui.impl.pub.view_component import ViewComponent
from gui.shared import EVENT_BUS_SCOPE, event_dispatcher
from gui.shared.events import HangarVehicleEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
_logger = logging.getLogger(__name__)

class HeroTankPresenter(ViewComponent[HeroTankModel]):
    __itemsCache = dependency.descriptor(IItemsCache)
    __space = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(HeroTankPresenter, self).__init__(model=HeroTankModel)
        self.__markerCtrl = None
        self.__hasHeroTank = False
        return

    @property
    def viewModel(self):
        return super(HeroTankPresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(HeroTankPresenter, self)._onLoading(*args, **kwargs)
        self.__markerCtrl = WGMarkerPositionController()
        self.__fillHeroTank()

    def _finalize(self):
        if self.__markerCtrl is not None:
            self.__markerCtrl.clear()
            self.__markerCtrl = None
        super(HeroTankPresenter, self)._finalize()
        return

    def _getEvents(self):
        return ((self.__itemsCache.onSyncCompleted, self.__onCacheResync), (self.__space.onSpaceDestroy, self.__clearMarkers))

    def _getListeners(self):
        return ((CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated), (HangarVehicleEvent.ON_HERO_TANK_LOADED, self.__fillHeroTank, EVENT_BUS_SCOPE.LOBBY))

    def __clearMarkers(self, _):
        if self.__markerCtrl is not None:
            self.__markerCtrl.clear()
        self.__hasHeroTank = False
        return

    @staticmethod
    def __getCorrectedMarkerPosition(vehicle):
        guiNode = vehicle.model.node('HP_gui')
        translation = Math.Vector3(guiNode.localMatrix.translation)
        if hasattr(vehicle, 'markerHeightFactor'):
            translation.y *= vehicle.markerHeightFactor
        vehicleMatrix = vehicle.model.matrix
        worldPosition = vehicleMatrix.applyPoint(translation)
        return worldPosition

    def __fillHeroTank(self, *args):
        with self.getViewModel().transaction() as model:
            heroTankEntityList = [ entity for entity in BigWorld.entities.values() if isinstance(entity, HeroTank) ]
            if not heroTankEntityList:
                return
            if len(heroTankEntityList) > 1:
                _logger.error('Multiple HeroTanks found')
                return
            markerModel = model.heroTankMarker
            heroTankEntity = heroTankEntityList[0]
            descriptor = heroTankEntity.typeDescriptor
            if heroTankEntity.model is not None:
                markerPosition = self.__getCorrectedMarkerPosition(heroTankEntity)
                self.__markerCtrl.clear()
                self.__markerCtrl.add(markerModel.proxy, Math.Vector3(markerPosition))
                self.__hasHeroTank = True
            elif self.__hasHeroTank:
                self.__hasHeroTank = False
                model.setName('')
                model.setType('')
                self.__markerCtrl.remove(markerModel.proxy)
                return
            if descriptor is not None:
                model.setName(descriptor.type.userString)
                model.setType(descriptor.type.classTag)
        return

    def __handleSelectedEntityUpdated(self, event):
        ctx = event.ctx
        if ctx['state'] == CameraMovementStates.FROM_OBJECT:
            return
        else:
            entity = BigWorld.entities.get(ctx['entityId'], None)
            if isinstance(entity, HeroTank):
                descriptor = entity.typeDescriptor
                if descriptor:
                    vehicleCD = descriptor.type.compactDescr
                    event_dispatcher.showHeroTankPreview(vehicleCD, previousBackAlias=VIEW_ALIAS.LOBBY_HANGAR)
            return

    def __onCacheResync(self, reason, diff):
        if reason != CACHE_SYNC_REASON.CLIENT_UPDATE:
            return
        else:
            if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff:
                self.__fillHeroTank()
            return

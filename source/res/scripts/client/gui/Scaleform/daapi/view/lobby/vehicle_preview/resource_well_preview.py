# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/resource_well_preview.py
from gui.impl.gen.view_models.views.lobby.vehicle_preview.top_panel.top_panel_tabs_model import TabID
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.resource_well.sounds import RESOURCE_WELL_SOUND_SPACE, SOUNDS
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import dependency
from skeletons.gui.game_control import IResourceWellController
from skeletons.gui.shared.utils import IHangarSpace

class ResourceWellVehiclePreview(VehiclePreview):
    _COMMON_SOUND_SPACE = RESOURCE_WELL_SOUND_SPACE
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, ctx):
        self.__numberStyle = ctx.get('numberStyle')
        self.__isBackClicked = False
        super(ResourceWellVehiclePreview, self).__init__(ctx)

    def setBottomPanel(self):
        self.as_setBottomPanelS(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_WELL)

    def _populate(self):
        super(ResourceWellVehiclePreview, self)._populate()
        self.__resourceWell.startNumberRequesters()
        self.addListener(events.ResourceWellLoadingViewEvent.LOAD, self.__onViewOpened, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.ResourceWellLoadingViewEvent.DESTROY, self.__onViewClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__resourceWell.onEventUpdated += self.__onEventStateUpdated
        self.soundManager.setState(SOUNDS.STATE_PLACE, SOUNDS.STATE_PLACE_GARAGE)
        self.soundManager.playInstantSound(SOUNDS.PREVIEW_ENTER)

    def _dispose(self):
        if not self.__isBackClicked:
            self.__resourceWell.stopNumberRequesters()
        self.removeListener(events.ResourceWellLoadingViewEvent.LOAD, self.__onViewOpened, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.ResourceWellLoadingViewEvent.DESTROY, self.__onViewClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__resourceWell.onEventUpdated -= self.__onEventStateUpdated
        super(ResourceWellVehiclePreview, self)._dispose()

    def _processBackClick(self, ctx=None):
        self.__isBackClicked = True
        super(ResourceWellVehiclePreview, self)._processBackClick(ctx)

    def _destroy(self):
        if self.soundManager is not None:
            self.soundManager.playInstantSound(SOUNDS.PREVIEW_EXIT)
        super(ResourceWellVehiclePreview, self)._destroy()
        return

    def _getExitEvent(self):
        exitEvent = super(ResourceWellVehiclePreview, self)._getExitEvent()
        ctx = exitEvent.ctx
        ctx.update({'numberStyle': self.__numberStyle})
        topPanelData = ctx.get('topPanelData', {})
        if topPanelData:
            appearance = self.__hangarSpace.getVehicleEntityAppearance()
            if appearance is not None and appearance.outfit.style is not None:
                topPanelData.update({'currentTabID': TabID.PERSONAL_NUMBER_VEHICLE})
                ctx.update({'style': self.__numberStyle})
            else:
                topPanelData.update({'currentTabID': TabID.BASE_VEHICLE})
                ctx.update({'style': None})
        return exitEvent

    def __onViewOpened(self, *_):
        self.soundManager.playInstantSound(SOUNDS.PREVIEW_EXIT)

    def __onViewClosed(self, *_):
        self.soundManager.playInstantSound(SOUNDS.PREVIEW_ENTER)

    def __onEventStateUpdated(self):
        if not self.__resourceWell.isActive():
            self.closeView()

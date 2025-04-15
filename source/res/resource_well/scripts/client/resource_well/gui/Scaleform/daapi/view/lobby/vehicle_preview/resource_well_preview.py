# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/Scaleform/daapi/view/lobby/vehicle_preview/resource_well_preview.py
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.impl.gen.view_models.views.lobby.vehicle_preview.top_panel.top_panel_tabs_model import TabID
from gui.shared import EVENT_BUS_SCOPE
from helpers import dependency
from resource_well.gui.impl.lobby.feature.sounds import RESOURCE_WELL_PREVIEW_SOUND_SPACE, SOUNDS
from resource_well.gui.shared import events
from skeletons.gui.resource_well import IResourceWellController
from skeletons.gui.shared.utils import IHangarSpace

class ResourceWellVehiclePreview(VehiclePreview):
    _COMMON_SOUND_SPACE = RESOURCE_WELL_PREVIEW_SOUND_SPACE
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, ctx):
        self.__numberStyle = ctx.get('numberStyle')
        self.__rewardID = ctx.get('rewardID')
        self.__isBackClicked = False
        super(ResourceWellVehiclePreview, self).__init__(ctx)

    def setBottomPanel(self):
        self.as_setBottomPanelS(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_WELL)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(ResourceWellVehiclePreview, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_WELL_PY_ALIAS:
            viewPy.setRewardID(self.__rewardID)

    def _populate(self):
        super(ResourceWellVehiclePreview, self)._populate()
        self.__resourceWell.startNumberRequesters()
        self.addListener(events.ResourceWellLoadingViewEvent.LOAD, self.__onViewOpened, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.ResourceWellLoadingViewEvent.DESTROY, self.__onViewClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__resourceWell.onEventUpdated += self.__onEventStateUpdated
        self.__resourceWell.onSettingsChanged += self.__onEventStateUpdated

    def _dispose(self):
        if not self.__isBackClicked:
            self.__resourceWell.stopNumberRequesters()
        self.removeListener(events.ResourceWellLoadingViewEvent.LOAD, self.__onViewOpened, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.ResourceWellLoadingViewEvent.DESTROY, self.__onViewClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__resourceWell.onEventUpdated -= self.__onEventStateUpdated
        self.__resourceWell.onSettingsChanged -= self.__onEventStateUpdated
        super(ResourceWellVehiclePreview, self)._dispose()

    def _processBackClick(self, ctx=None):
        self.__isBackClicked = True
        super(ResourceWellVehiclePreview, self)._processBackClick(ctx)

    def _getExitEvent(self):
        exitEvent = super(ResourceWellVehiclePreview, self)._getExitEvent()
        ctx = exitEvent.ctx
        ctx.update({'numberStyle': self.__numberStyle,
         'rewardID': self.__rewardID})
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

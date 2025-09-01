# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/armor/armor_sub_presenter.py
from __future__ import absolute_import
import typing
import GUI
from PlayerEvents import g_playerEvents
from account_helpers.settings_core import settings_constants
from armor_inspector_common.schemas import armorInspectorConfigSchema
from frameworks.wulf import ViewStatus
from gui import g_mouseEventHandlers
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.app_loader import app_getter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_model import ArmorModel
from gui.impl.lobby.vehicle_hub.sub_presenters.armor.armor_tooltip import ArmorTooltipWindow
from cgf_components.armor_inspector_component import ArmorInspectorComponent
from gui.impl.lobby.vehicle_hub.sub_presenters.armor.utils import fillArmorData, getCursorPositionInPixels, getMaxArmor
from gui.impl.lobby.vehicle_hub.sub_presenters.sub_presenter_base import SubPresenterBase
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared.utils import IHangarSpace
from uilogging.vehicle_hub.loggers import ArmorTabLogger
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.application import AppEntry

class ArmorSubPresenter(SubPresenterBase):
    __slots__ = ('_prevAppBackgroundAlpha', '_prevOptimizationEnabled', '_level', '_normalArmorMax', '_spacedArmorMax', '_vehicleEntity', '_tooltip', '_isMouseOver', '_isInspectorStarted')
    _appLoader = dependency.descriptor(IAppLoader)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, model, parentView):
        super(ArmorSubPresenter, self).__init__(model, parentView)
        self._isMouseOver = False
        self._vehicleEntity = None
        self._tooltip = None
        self._level = 0
        self._normalArmorMax, self._spacedArmorMax = (0, 0)
        self._isInspectorStarted = False
        self._uiLogger = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @app_getter
    def app(self):
        pass

    def initialize(self, vhCtx, *args, **kwargs):
        super(ArmorSubPresenter, self).initialize(vhCtx, *args, **kwargs)
        self._vehicleEntity = self._hangarSpace.space.getVehicleEntity()
        self._level = self._vehicleEntity.typeDescriptor.level
        self._normalArmorMax, self._spacedArmorMax = getMaxArmor(self._vehicleEntity.typeDescriptor)
        g_mouseEventHandlers.add(self._handleMouseEvent)
        self._hangarSpace.lockVehicleSelectable(self)
        self._updateLinkButtonData()
        self._startUILogger()
        self._fillArmorData()
        self._startArmorInspector()

    def finalize(self):
        g_mouseEventHandlers.discard(self._handleMouseEvent)
        self._hangarSpace.unlockVehicleSelectable(self)
        self._destroyTooltip()
        if self._uiLogger is not None:
            self._uiLogger.logClose()
            self._uiLogger = None
        if self._hangarSpace.spaceInited:
            self._stopArmorInspector()
        self._vehicleEntity = None
        super(ArmorSubPresenter, self).finalize()
        return

    def clear(self):
        self.finalize()
        super(ArmorSubPresenter, self).clear()

    def _getEvents(self):
        return ((self.viewModel.onLinkButtonPressed, self._onLinkButtonClicked),
         (self.viewModel.onLegendClicked, self._onLegendClicked),
         (self.viewModel.onLegendTooltipOpened, self._onLegendTooltipOpened),
         (self.viewModel.onLegendTooltipClosed, self._onLegendTooltipClosed),
         (self._hangarSpace.onMouseEnter, self._onMouseEnter),
         (self._hangarSpace.onMouseExit, self._onMouseExit),
         (self._hangarSpace.onVehicleChangeStarted, self._onVehicleChangeStarted),
         (self._hangarSpace.onVehicleChanged, self._onVehicleChanged),
         (self._settingsCore.onSettingsChanged, self._onSettingsChanged),
         (g_playerEvents.onConfigModelUpdated, self._onConfigModelUpdateHandler))

    def _startArmorInspector(self):
        if not self._isInspectorStarted and self._hangarSpace.isModelLoaded:
            self._isInspectorStarted = True
            appearance = self._vehicleEntity.appearance
            if not appearance.findComponentByType(ArmorInspectorComponent):
                appearance.createComponent(ArmorInspectorComponent)

    def _stopArmorInspector(self):
        if self._isInspectorStarted:
            self._isInspectorStarted = False
            self._vehicleEntity.appearance.removeComponentByType(ArmorInspectorComponent)

    def _fillArmorData(self):
        fillArmorData(self.getViewModel(), self._level, self._normalArmorMax, self._spacedArmorMax, self._settingsCore.getSetting(settings_constants.GRAPHICS.COLOR_BLIND))

    def _updateLinkButtonData(self):
        configModel = armorInspectorConfigSchema.getModel()
        self.viewModel.setLinkButtonLabel(R.strings.armor_inspector.explanatory.linkButton() if configModel.linkButtonURL else R.invalid())

    def _startUILogger(self):
        cd = self._vehicleEntity.typeDescriptor.type.compactDescr
        self._uiLogger = ArmorTabLogger(cd)
        self._uiLogger.logOpen()

    def _onConfigModelUpdateHandler(self, gpKey):
        if armorInspectorConfigSchema.gpKey == gpKey:
            self._updateLinkButtonData()

    def _onLinkButtonClicked(self):
        url = armorInspectorConfigSchema.getModel().linkButtonURL
        if not url:
            return
        showBrowserOverlayView(url, alias=VIEW_ALIAS.BROWSER_OVERLAY)
        self._uiLogger.logVideoClick()

    def _onLegendClicked(self, event):
        self._uiLogger.legendStateChanged(event)

    def _onLegendTooltipOpened(self, _):
        self._uiLogger.tooltipOpened()

    def _onLegendTooltipClosed(self, event):
        self._uiLogger.legendTooltipClosed(event)

    def _handleMouseEvent(self, _):
        isOverActive3DScene = GUI.mcursor().inWindow and GUI.mcursor().inFocus and self._hangarSpace.isCursorOver3DScene
        if isOverActive3DScene:
            if self._tooltip:
                self._updateTooltip()
            elif self._isMouseOver:
                self._createTooltip()
        elif self._tooltip:
            self._destroyTooltip()

    def _onMouseEnter(self, entity):
        if not self._vehicleEntity == entity:
            return
        self._isMouseOver = True

    def _onMouseExit(self, entity):
        if not self._vehicleEntity == entity:
            return
        self._isMouseOver = False
        self._destroyTooltip()

    def _createTooltip(self):
        if self._tooltip is None and self._isInspectorStarted:
            self._tooltip = ArmorTooltipWindow(self._vehicleEntity)
            self._tooltip.onStatusChanged += self.__onTooltipStatusChanged
            self._updateTooltip()
            self._tooltip.load()
            self._uiLogger.tooltipOpened()
            GUI.switchArmorInspectorCursor(True)
        return

    def _updateTooltip(self):
        if self._tooltip:
            x, y = self._applyScaleToPosition(getCursorPositionInPixels())
            self._tooltip.move(x, y)
            self._tooltip.update()

    def _applyScaleToPosition(self, position):
        scale = self._settingsCore.interfaceScale.get()
        return (int(coord // scale) for coord in position) if scale != 1 else position

    def __onTooltipStatusChanged(self, status):
        if status == ViewStatus.DESTROYED:
            self._destroyTooltip()

    def _destroyTooltip(self):
        if self._tooltip is not None:
            self._tooltip.onStatusChanged -= self.__onTooltipStatusChanged
            self._tooltip.destroy()
            self._tooltip = None
            self._uiLogger.armorTooltipClosed()
            GUI.switchArmorInspectorCursor(False)
        return

    def _onVehicleChangeStarted(self):
        self._stopArmorInspector()

    def _onVehicleChanged(self):
        self._fillArmorData()
        self._startArmorInspector()

    def _onSettingsChanged(self, diff):
        if settings_constants.GRAPHICS.COLOR_BLIND in diff:
            self._fillArmorData()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/widgets/carousel_view.py
from __future__ import absolute_import
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from frameworks.wulf import WindowLayer
from notification import NotificationMVC
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.game_loading.resources.consts import Milestones
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.app_loader import sf_lobby
from gui.impl import backport
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from gui.shared.event_dispatcher import showVehicleHubOverview
from gui.shared.utils.functions import replaceHyphenToUnderscore
from halloween.gui.halloween_gui_constants import HALLOWEEN_CAROUSEL_VEHICLE_TOOLTIP
from halloween.gui.impl.gen.view_models.views.lobby.widgets.hangar_carousel_vehicle_view_model import CarouselTooltips, HangarCarouselVehicleViewModel, VehicleTypes
from halloween.gui.impl.gen.view_models.views.lobby.widgets.hangar_carousel_view_model import HangarCarouselViewModel
from halloween.gui.impl.lobby.hw_helpers import isDailyKeyQuestCompleted, getDailyKeyQuestDescription, getVehicleState
from halloween.gui.impl.lobby.tooltips.simple_format_tooltip import SimpleFormatTooltipView
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.uilogging.loggers import HWMetricsLogger
from halloween.uilogging.logging_constants import HWLogKeys
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace

class CarouselView(ViewComponent[HangarCarouselViewModel]):
    _POP_UP_PADDING_X = 5
    _POP_UP_PADDING_Y = 13
    _carouselSize = 0
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _itemsCache = dependency.descriptor(IItemsCache)
    _halloweenCtrl = dependency.descriptor(IHalloweenController)
    _halloweenArtefactsCtrl = dependency.descriptor(IHalloweenArtefactsController)

    def __init__(self):
        super(CarouselView, self).__init__(R.aliases.halloween.shared.Carousel(), HangarCarouselViewModel)
        self.__uiLogger = HWMetricsLogger(HWLogKeys.CAROUSEL)

    def _onLoaded(self, *args, **kwargs):
        super(CarouselView, self)._onLoaded(*args, **kwargs)
        if self._hangarSpace.spaceInited:
            self.__updateNotificationsLayout()
        else:
            g_playerEvents.onLoadingMilestoneReached += self.__onLoadingMilestoneReached

    def __onLoadingMilestoneReached(self, milestoneName):
        if milestoneName == Milestones.HANGAR_READY:
            g_playerEvents.onLoadingMilestoneReached -= self.__onLoadingMilestoneReached
            self.__updateNotificationsLayout()

    def __updateNotificationsLayout(self):
        notificationsModel = NotificationMVC.g_instance.getModel()
        if notificationsModel is not None:
            notificationsModel.onPopUpPaddingChanged(True, self._POP_UP_PADDING_X, self._carouselSize + self._POP_UP_PADDING_Y)
        return

    def _finalize(self):
        notificationsModel = NotificationMVC.g_instance.getModel()
        if notificationsModel is not None:
            notificationsModel.onPopUpPaddingChanged(False)
        super(CarouselView, self)._finalize()
        return

    def createToolTip(self, event):
        dialogsContainer = self.__app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
        if dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            return
        elif event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            specialArgs = []
            specialAlias = tooltipId
            if tooltipId == CarouselTooltips.HALLOWEENCAROUSELVEHICLE.value:
                intCD = event.getArgument('intCD', None)
                specialAlias = HALLOWEEN_CAROUSEL_VEHICLE_TOOLTIP
                if intCD is not None:
                    specialArgs = [int(intCD)]
            window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=specialAlias, specialArgs=specialArgs), self.getParentWindow())
            window.load()
            return window
        else:
            return super(CarouselView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.halloween.mono.lobby.tooltips.simple_format_tooltip():
            if event.getArgument('id', '') == CarouselTooltips.DAILYQUEST.value and g_currentVehicle.item:
                return SimpleFormatTooltipView(header=backport.text(R.strings.halloween_lobby.carousel.daily.header()), body=getDailyKeyQuestDescription(g_currentVehicle.intCD))
        return super(CarouselView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(CarouselView, self).getViewModel()

    @sf_lobby
    def __app(self):
        return None

    def _getVehicles(self):
        return [ self._itemsCache.items.getItemByCD(intCD) for intCD in self._halloweenCtrl.getModeSettings().vehicles ]

    def _onLoading(self, *args, **kwargs):
        super(CarouselView, self)._onLoading()
        self.__fillVehicles()

    def _subscribe(self):
        super(CarouselView, self)._subscribe()
        g_clientUpdateManager.addCallbacks({'cache.vehsLock': self.__onVehicleLockUpdated})
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        self._halloweenArtefactsCtrl.onArtefactSettingsUpdated += self.__onRentVehicleStatusUpdate
        self.viewModel.onChangeVehicle += self.__onTankChanged
        self.viewModel.onVehiclePreview += self.__onVehiclePreview
        self.viewModel.onChangeSize += self.__onResized

    def _unsubscribe(self):
        super(CarouselView, self)._unsubscribe()
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        g_playerEvents.onLoadingMilestoneReached -= self.__onLoadingMilestoneReached
        self._halloweenArtefactsCtrl.onArtefactSettingsUpdated -= self.__onRentVehicleStatusUpdate
        self.viewModel.onChangeVehicle -= self.__onTankChanged
        self.viewModel.onVehiclePreview -= self.__onVehiclePreview
        self.viewModel.onChangeSize -= self.__onResized

    def __onVehicleLockUpdated(self, *args):
        self.__fillVehicles()

    def __onRentVehicleStatusUpdate(self):
        self.__fillVehicles()

    def __fillVehicles(self):
        with self.viewModel.transaction() as vm:
            if g_currentVehicle.item:
                vm.setSelectedVehicle(g_currentVehicle.invID)
            vm.getVehicles().clear()
            for vehicle in self._getVehicles():
                model = HangarCarouselVehicleViewModel()
                model.setName(vehicle.userName)
                model.setIntCD(vehicle.intCD)
                model.setInvID(vehicle.invID)
                model.setIconName(replaceHyphenToUnderscore(vehicle.name.replace(':', '-')))
                model.setVehicleType(VehicleTypes(vehicle.type) if vehicle.type != '' else VehicleTypes.NONE)
                model.setVehicleState(getVehicleState(vehicle))
                model.setHasDaily(not isDailyKeyQuestCompleted(vehicle.intCD))
                vm.getVehicles().addViewModel(model)

            vm.getVehicles().invalidate()

    def __onCurrentVehicleChanged(self):
        if g_currentVehicle.item is None:
            return
        else:
            self.viewModel.setSelectedVehicle(g_currentVehicle.invID)
            return

    def __onTankChanged(self, args):
        if args is not None:
            self._halloweenCtrl.selectVehicle(int(args.get('invID')))
        return

    def __onVehiclePreview(self, args):
        intCD = args.get('intCD')
        if intCD is not None:
            self.__uiLogger.onClick(HWLogKeys.VEHICLE_PREVIEW_BUTTON)
            showVehicleHubOverview(int(intCD))
        return

    def __onResized(self, args):
        if args is not None:
            self._carouselSize = int(args.get('size'))
            self.__updateNotificationsLayout()
        return

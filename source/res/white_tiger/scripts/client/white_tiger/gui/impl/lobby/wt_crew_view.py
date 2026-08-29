# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_crew_view.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_crew_model import WtCrewModel
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.prebattle_vehicle import IPrebattleVehicle
from gui.doc_loaders.event_settings_loader import getVehicleCharacteristics
from gui.Scaleform.daapi.view.meta.WTHangarBaseWidgetMeta import WTHangarBaseWidgetMeta
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.wt_event.wt_event_helpers import getInfoPageURL
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from skeletons.gui.game_control import IWhiteTigerController
from gui.impl.gen.view_models.views.lobby.tooltips.tankman_tooltip_view_model import TankmanTooltipViewModel
from gui.impl.gen.view_models.views.lobby.tooltips.tankman_tooltip_view_icon_model import TankmanTooltipViewIconModel
from tooltips.wt_tankman_tooltip_adapters import WTTankmanInfoAdapter
from wt_settings import g_wt_config
_logger = logging.getLogger(__name__)

class WtTankmanTooltipView(ViewImpl):
    __slots__ = ('__tankmanInfo',)

    def __init__(self, tankmanInfo):
        settings = ViewSettings(R.views.lobby.tooltips.TankmanTooltipView())
        settings.model = TankmanTooltipViewModel()
        self.__tankmanInfo = tankmanInfo
        super(WtTankmanTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WtTankmanTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtTankmanTooltipView, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setTitle(self.__tankmanInfo.getFullUserName())
            model.setSubtitle(self.__tankmanInfo.getLabel())
            model.setMainIcon(self.__tankmanInfo.getTankmanIcon())
            model.setDescription(self.__tankmanInfo.getDescription())
            model.setIconsTitle(self.__tankmanInfo.getSkillsLabel())
            skillsModel = model.icons
            skillsModel.clearItems()
            for skill in self.__tankmanInfo.getSkills():
                skillModel = TankmanTooltipViewIconModel()
                skillModel.setIcon(skill)
                skillsModel.addViewModel(skillModel)

            skillsModel.invalidate()


class WTEventCrewWidget(WTHangarBaseWidgetMeta):

    def _makeInjectView(self):
        return WTEventCrewView()


class WTEventCrewView(ViewImpl, IGlobalListener):
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    __appLoader = dependency.descriptor(IAppLoader)
    __wtController = dependency.descriptor(IWhiteTigerController)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.CrewWidget(), flags=ViewFlags.VIEW, model=WtCrewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WTEventCrewView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            args = [int(event.getArgument('invID'))]
            if tooltipId == WtCrewModel.SKILL_TOOLTIP:
                tooltipMgr = self.__appLoader.getApp().getToolTipMgr()
                tooltipMgr.onCreateWulfTooltip(tooltipId, args, event.mouse.positionX, event.mouse.positionY)
                return TOOLTIPS_CONSTANTS.CREW_PERK_GF
        return super(WTEventCrewView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.TankmanTooltipView():
            vehicle = self.__prebattleVehicle.item
            if vehicle is None:
                return
            tankmanInfo = WTTankmanInfoAdapter(g_wt_config.getVehicleData(vehicle.intCD).crew)
            return WtTankmanTooltipView(tankmanInfo)
        else:
            return super(WTEventCrewView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(WTEventCrewView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__updateViewModel()

    def _finalize(self):
        self.__removeListeners()
        super(WTEventCrewView, self)._finalize()

    def __addListeners(self):
        self.__prebattleVehicle.onChanged += self.__updateViewModel
        self.viewModel.onAboutClicked += self.__onAboutClicked

    def __removeListeners(self):
        self.__prebattleVehicle.onChanged -= self.__updateViewModel
        self.viewModel.onAboutClicked -= self.__onAboutClicked

    def __updateViewModel(self):
        vehicle = self.__prebattleVehicle.item
        if vehicle is None:
            return
        else:
            info = getVehicleCharacteristics().get(vehicle.name)
            if info is None:
                _logger.error('There is not special characteristics of the event vehicle to get commander role')
                return
            tankmanInfo = g_wt_config.getVehicleData(vehicle.intCD).crew
            with self.viewModel.transaction() as model:
                model.setName(tankmanInfo.fullUserName)
                model.setTankmanID(info.role)
            return

    @staticmethod
    def __onAboutClicked():
        showBrowserOverlayView(getInfoPageURL(), VIEW_ALIAS.BROWSER_OVERLAY)

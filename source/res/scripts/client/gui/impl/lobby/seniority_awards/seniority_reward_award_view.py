# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_reward_award_view.py
import logging
import re
from collections import defaultdict
from frameworks.wulf import WindowFlags, ViewFlags
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.auxiliary.rewards_helper import getRewardRendererModelPresenter, getRewardTooltipContent
from gui.impl.backport import TooltipData, BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_screen_tooltips import BlueprintScreenTooltips
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_awards_vehicle_renderer_model import SeniorityAwardsVehicleRendererModel
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_reward_award_view_model import SeniorityRewardAwardViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.event_dispatcher import showSeniorityRewardWindow
from gui.shared.gui_items.Vehicle import getNationLessName, getIconResourceName
from gui.impl.auxiliary.rewards_helper import getSeniorityAwardsRewardsAndBonuses
_logger = logging.getLogger(__name__)
REG_EXP_QUEST_SUBTYPE = ':([Y, y]\\d*)|:([A,a,B,b][T,t])'
_UNVISIBLE_BONUSES = set(['slots'])
_SENIORITY_BONUSES_ORDER = (('customizations', 'style'),
 ('crewBooks', 'personalBook'),
 ('crewBooks', 'universalBook'),
 ('dossier', 'badge'),
 ('customizations', 'projectionDecal'),
 ('battleToken', ''),
 ('dossier', 'medal'),
 ('dossier', 'achievement'),
 ('customizations', 'emblem'),
 ('goodies', 'xp'),
 ('goodies', 'credits'),
 ('tokens', 'bonus_battle'))

def _getBonusOrder():
    bonusOrder = defaultdict(dict)
    for priority, (bonusType, bonusSubtype) in enumerate(_SENIORITY_BONUSES_ORDER):
        bonusOrder[bonusType].update({bonusSubtype: priority})

    return bonusOrder


def _keySortOrder(bonus, bonusOrder):
    bonusName = bonus.get('bonusName', '')
    if bonusName in bonusOrder:
        bonusSubtypes = bonusOrder.get(bonusName, {})
        for bonusSubtype, priority in bonusSubtypes.iteritems():
            if bonusSubtype in bonus.get('imgSource', ''):
                return priority

    return len(_SENIORITY_BONUSES_ORDER)


class SeniorityRewardAwardView(ViewImpl):
    __slots__ = ('__bonuses', '__vehicles', '__countBoxes', '__tooltipData', '__bonusOrder')

    def __init__(self, contentResId, *args, **kwargs):
        super(SeniorityRewardAwardView, self).__init__(contentResId, ViewFlags.VIEW, SeniorityRewardAwardViewModel, *args, **kwargs)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(SeniorityRewardAwardView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipData = self.__getBackportTooltipData(event)
        return getRewardTooltipContent(event, tooltipData)

    def _initialize(self, questID, data):
        super(SeniorityRewardAwardView, self)._initialize()
        self.viewModel.onCloseAction += self.__onWindowClose
        self.viewModel.onOpenBtnClick += self.__onOpenBtnClick
        questYearsType = None
        seniorityLvlSearch = re.search(REG_EXP_QUEST_SUBTYPE, questID)
        if seniorityLvlSearch is not None and len(seniorityLvlSearch.groups()) >= 2:
            questYearsType = seniorityLvlSearch.groups()[0] if seniorityLvlSearch.groups()[0] is not None else seniorityLvlSearch.groups()[1]
        bonuses, vehicles, countBoxes = getSeniorityAwardsRewardsAndBonuses(data, maxAwardCount=9)
        self.__bonusOrder = _getBonusOrder()
        self.__bonuses = sorted(bonuses, key=lambda b: _keySortOrder(b, self.__bonusOrder)) if bonuses is not None else []
        self.__vehicles = vehicles if vehicles is not None else []
        self.__countBoxes = countBoxes
        self.__tooltipData = {}
        self.__setRewards()
        self.__setBonuses()
        if questYearsType is not None:
            self.viewModel.setCategory(questYearsType.upper())
        return

    def _finalize(self):
        self.__bonusOrder = None
        self.__bonuses = None
        self.__vehicles = None
        self.viewModel.onCloseAction -= self.__onWindowClose
        self.viewModel.onOpenBtnClick -= self.__onOpenBtnClick
        super(SeniorityRewardAwardView, self)._finalize()
        return

    def __setRewards(self):
        with self.viewModel.transaction() as vm:
            vm.setBoxCount(self.__countBoxes)
            vehiclesList = vm.getVehicles()
            vehiclesList.clear()
            for vehicle in self.__vehicles:
                rendererModel = SeniorityAwardsVehicleRendererModel()
                rendererModel.setVehicleCD(str(vehicle.vehicleCD))
                rendererModel.setImgSource(self.__getVehImgResource(vehicle.name)())
                vehiclesList.addViewModel(rendererModel)

            vehiclesList.invalidate()

    def __setBonuses(self):
        with self.viewModel.transaction() as vm:
            bonusesList = vm.getBonuses()
            bonusesList.clear()
            for index, bonus in enumerate(self.__bonuses):
                if bonus.get('bonusName') in _UNVISIBLE_BONUSES:
                    continue
                modelPresenter = getRewardRendererModelPresenter(bonus)
                rendererModel = modelPresenter.getModel(bonus, index)
                bonusesList.addViewModel(rendererModel)
                self.__tooltipData[index] = TooltipData(tooltip=bonus.get('tooltip', None), isSpecial=bonus.get('isSpecial', False), specialAlias=bonus.get('specialAlias', ''), specialArgs=bonus.get('specialArgs', None))

            bonusesList.invalidate()
        return

    def __onOpenBtnClick(self):
        showSeniorityRewardWindow()

    def __onWindowClose(self, _=None):
        self.destroyWindow()

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        elif tooltipId in self.__tooltipData:
            return self.__tooltipData[tooltipId]
        vehicleCD = event.getArgument('vehicleCD')
        if vehicleCD is None:
            return
        elif tooltipId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT:
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_INFO, specialArgs=(int(vehicleCD), True))
        elif tooltipId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT_CONVERT_COUNT:
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_CONVERT_INFO, specialArgs=[vehicleCD])
        else:
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AWARD_VEHICLE, specialArgs=(vehicleCD,
             None,
             None,
             None,
             None,
             None,
             True)) if tooltipId == SeniorityAwardsVehicleRendererModel.TOOLTIP_VEHICLE_REWARD else None

    @staticmethod
    def __getVehImgResource(vehicleName):
        resourceName = getIconResourceName(getNationLessName(vehicleName))
        if resourceName in R.images.gui.maps.icons.seniorityAwards.vehicles.c_390x245.keys():
            return R.images.gui.maps.icons.seniorityAwards.vehicles.c_390x245.dyn(resourceName)
        else:
            _logger.error("Image %s doesn't exist", resourceName)
            return None


class SeniorityRewardAwardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, questID=None, data=None):
        seniorityAwardView = R.views.lobby.seniority_awards.seniority_reward_award.seniority_reward_award_view
        super(SeniorityRewardAwardWindow, self).__init__(content=SeniorityRewardAwardView(seniorityAwardView.SeniorityRewardAwardView(), questID=questID, data=data), wndFlags=WindowFlags.OVERLAY, decorator=None)
        return

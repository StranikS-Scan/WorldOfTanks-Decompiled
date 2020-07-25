# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/transfer_giveaway/transfer_giveaway_awards_view.py
import logging
import re
from frameworks.wulf import WindowFlags, ViewSettings
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.auxiliary.rewards_helper import DEF_MODEL_PRESENTERS
from gui.impl.auxiliary.rewards_helper import LootRewardDefModelPresenter
from gui.impl.auxiliary.rewards_helper import getRewardRendererModelPresenter, getRewardTooltipContent
from gui.impl.auxiliary.rewards_helper import getTransferGiveawayRewardsAndBonuses
from gui.impl.backport import TooltipData, BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_screen_tooltips import BlueprintScreenTooltips
from gui.impl.gen.view_models.views.lobby.transfer_giveaway.transfer_giveaway_awards_vehicle_renderer_model import TransferGiveawayAwardsVehicleRendererModel
from gui.impl.gen.view_models.views.lobby.transfer_giveaway.transfer_giveaway_awards_view_model import TransferGiveawayAwardsViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.bonuses import BlueprintsBonusSubtypes
from gui.shared.gui_items.Vehicle import getNationLessName, getIconResourceName
_logger = logging.getLogger(__name__)
_QUEST_CATEGORY_PATTERN = 'BETA|Y\\d+'
_AWARDS_COUNT_LIMIT = 9
_HIDDEN_BONUSES = {'slots'}
_BONUSES_ORDER = (('dossier', 'beta'),
 ('dossier', 'badge'),
 ('customizations', 'projectionDecal'),
 ('customizations', 'style'),
 ('dossier', 'achievement'),
 ('customizations', 'emblem'),
 ('crewBooks', 'personalBook'),
 ('crewBooks', 'universalBook'),
 ('goodies', 'booster_xp'),
 ('goodies', 'crew_xp'),
 ('battleToken', ''),
 ('tokens', 'bonus_battle'))

def _getBonusPriority(bonus):
    bonusName = bonus.bonusName
    imagePath = bonus.images['small']
    for index, (name, bonusSubtype) in enumerate(_BONUSES_ORDER):
        if name == bonusName and bonusSubtype in imagePath:
            return index

    return len(_BONUSES_ORDER)


class TransferGiveawayAwardsView(ViewImpl):
    __slots__ = ('__tooltipData',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.transfer_giveaway.transfer_giveaway_awards_view.TransferGiveawaydAwardsView())
        settings.model = TransferGiveawayAwardsViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__tooltipData = {}
        super(TransferGiveawayAwardsView, self).__init__(settings)

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
            return super(TransferGiveawayAwardsView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipData = self.__getBackportTooltipData(event)
        return getRewardTooltipContent(event, tooltipData)

    def _initialize(self, questID, data):
        super(TransferGiveawayAwardsView, self)._initialize()
        self.viewModel.onCloseAction += self.__onWindowClose
        category = self.__parseCategory(questID)
        bonuses, vehicles, _ = getTransferGiveawayRewardsAndBonuses(rewards=data, maxAwardCount=_AWARDS_COUNT_LIMIT, sortKey=_getBonusPriority, hiddenBonuses=_HIDDEN_BONUSES)
        self.__setVehicleRewards(vehicles)
        self.__setBonuses(bonuses)
        self.viewModel.setCategory(category)

    def _finalize(self):
        self.viewModel.onCloseAction -= self.__onWindowClose
        super(TransferGiveawayAwardsView, self)._finalize()

    @staticmethod
    def __parseCategory(questID):
        if questID:
            categoryData = re.findall(_QUEST_CATEGORY_PATTERN, questID)
            if categoryData:
                return '_'.join(categoryData).upper()

    def __setVehicleRewards(self, vehicles):
        with self.viewModel.transaction() as vm:
            vehiclesList = vm.getVehicles()
            vehiclesList.clear()
            if vehicles is not None:
                for vehicle in vehicles:
                    rendererModel = TransferGiveawayAwardsVehicleRendererModel()
                    rendererModel.setVehicleCD(str(vehicle.vehicleCD))
                    rendererModel.setImgSource(self.__getVehImgResource(vehicle.name)())
                    vehiclesList.addViewModel(rendererModel)

            vehiclesList.invalidate()
        return

    def __setBonuses(self, bonuses):
        with self.viewModel.transaction() as vm:
            bonusesList = vm.getBonuses()
            bonusesList.clear()
            for index, bonus in enumerate(bonuses):
                presenters = DEF_MODEL_PRESENTERS.copy()
                presenters[BlueprintsBonusSubtypes.UNIVERSAL_FRAGMENT] = LootRewardDefModelPresenter()
                modelPresenter = getRewardRendererModelPresenter(bonus, presenters=presenters)
                rendererModel = modelPresenter.getModel(bonus, index)
                bonusesList.addViewModel(rendererModel)
                self.__tooltipData[index] = TooltipData(tooltip=bonus.get('tooltip', None), isSpecial=bonus.get('isSpecial', False), specialAlias=bonus.get('specialAlias', ''), specialArgs=bonus.get('specialArgs', None))

            bonusesList.invalidate()
        return

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
             True)) if tooltipId == TransferGiveawayAwardsVehicleRendererModel.TOOLTIP_VEHICLE_REWARD else None

    @staticmethod
    def __getVehImgResource(vehicleName):
        resourceName = getIconResourceName(getNationLessName(vehicleName))
        if resourceName in R.images.gui.maps.icons.seniorityAwards.vehicles.c_390x245.keys():
            return R.images.gui.maps.icons.seniorityAwards.vehicles.c_390x245.dyn(resourceName)
        else:
            _logger.error("Image %s doesn't exist", resourceName)
            return None


class TransferGiveawayAwardsWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, questID, data):
        super(TransferGiveawayAwardsWindow, self).__init__(content=TransferGiveawayAwardsView(questID=questID, data=data), wndFlags=WindowFlags.OVERLAY, decorator=None)
        return

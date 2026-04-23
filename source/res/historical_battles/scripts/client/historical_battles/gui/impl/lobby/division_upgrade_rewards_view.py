# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/division_upgrade_rewards_view.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl
from gui.sounds.filters import switchHangarFilteredFilter
from helpers import dependency
from items import vehicles
from historical_battles.gui.impl.gen.view_models.views.lobby.division_upgrade_rewards_view_model import DivisionUpgradeRewardsViewModel, DivisionUpgradeAbilityModel
from historical_battles.gui.impl.lobby.tooltips.new_vehicles_available_tooltip import NewVehiclesAvailableTooltip
from historical_battles.gui.sounds.sound_constants import GENERAL_SOUND_SPACE
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
_logger = logging.getLogger(__name__)

class DivisionUpgradeRewardsView(ViewImpl):
    __gameEventController = dependency.descriptor(IGameEventController)
    __slots__ = ('__subdivisionId', '__previousLevel', '__currentLevel', '__closeCallback')
    _COMMON_SOUND_SPACE = GENERAL_SOUND_SPACE

    def __init__(self, layoutID, divisionData, closeCallback):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = DivisionUpgradeRewardsViewModel()
        super(DivisionUpgradeRewardsView, self).__init__(settings)
        self.__subdivisionId = divisionData.get('divisionID')
        self.__previousLevel = divisionData.get('prevLvl')
        self.__currentLevel = divisionData.get('currentLvl')
        self.__closeCallback = closeCallback

    @property
    def viewModel(self):
        return super(DivisionUpgradeRewardsView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.historical_battles.lobby.tooltips.NewVehiclesAvailableTooltip():
            divisionID = event.getArgument('divisionID')
            return NewVehiclesAvailableTooltip(divisionID)
        return super(DivisionUpgradeRewardsView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onConfirm, self.__onClose))

    def _onLoading(self, *args, **kwargs):
        super(DivisionUpgradeRewardsView, self)._onLoading(*args, **kwargs)
        switchHangarFilteredFilter(True)
        self.__updateModel()

    def _finalize(self):
        self.__executeCloseCallback()
        self.__subdivisionId = None
        self.__previousLevel = None
        self.__currentLevel = None
        switchHangarFilteredFilter(False)
        super(DivisionUpgradeRewardsView, self)._finalize()
        return

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            frontController = self.__gameEventController.frontController
            front = frontController.getFrontBySubdivisionId(self.__subdivisionId)
            subdivision = frontController.getSubdivisionById(self.__subdivisionId)
            if not subdivision:
                _logger.error('[DivisionUpgradeRewardsView] subdivision with id = %d not found', self.__subdivisionId)
                return
            model.setFrontName(front.getName())
            model.setSubDivisionIndex(self.__subdivisionId)
            model.setLevel(self.__currentLevel)
            model.setVehicleType(subdivision.getVehiclesType())
            model.setHasNewVehicles(True)
            abilities = subdivision.getAbilitiesData()
            if not abilities:
                _logger.error('[DivisionUpgradeRewardsView] abilities are empty')
                return
            self.__setAbilities(model, abilities[self.__previousLevel:self.__currentLevel])

    def __setAbilities(self, model, abilitiesData):
        abilities = model.getAbilities()
        abilities.clear()
        equipmentsCache = vehicles.g_cache.equipments()
        for abilityID in abilitiesData:
            abilityModel = DivisionUpgradeAbilityModel()
            ability = equipmentsCache[abilityID]
            abilityModel.setName(ability.name)
            abilityModel.setLabel(ability.userString)
            abilityModel.setIcon(ability.iconName)
            abilityModel.setCooldown(ability.cooldownSeconds)
            abilities.addViewModel(abilityModel)

        abilities.invalidate()

    def __onClose(self, *args):
        self.__executeCloseCallback()
        self.destroyWindow()

    def __executeCloseCallback(self):
        if self.__closeCallback is not None:
            callback = self.__closeCallback
            self.__closeCallback = None
            callback()
        return


class DivisionUpgradeRewardsViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, divisionData, closeCallback=None, parent=None):
        super(DivisionUpgradeRewardsViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=DivisionUpgradeRewardsView(R.views.historical_battles.lobby.DivisionUpgradeRewardsView(), divisionData, closeCallback), parent=parent)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/division_upgrade_rewards_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from historical_battles.gui.impl.gen.view_models.views.lobby.division_upgrade_rewards_view_model import DivisionUpgradeRewardsViewModel, DivisionUpgradeAbilityModel
from historical_battles.gui.impl.lobby.tooltips.new_vehicles_available_tooltip import NewVehiclesAvailableTooltip
from gui.impl.pub import ViewImpl, WindowImpl
from helpers import dependency
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from items import vehicles
import logging
_logger = logging.getLogger(__name__)

class DivisionUpgradeRewardsView(ViewImpl):
    __gameEventController = dependency.descriptor(IGameEventController)
    __slots__ = ('__subdivisionId', '__previousLevel', '__currentLevel')

    def __init__(self, layoutID, subdivisionId, prevLvl, currLvl):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = DivisionUpgradeRewardsViewModel()
        super(DivisionUpgradeRewardsView, self).__init__(settings)
        self.__subdivisionId = subdivisionId
        self.__previousLevel = prevLvl
        self.__currentLevel = currLvl

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
        self.__updateModel()

    def _finalize(self):
        self.__subdivisionId = None
        self.__previousLevel = None
        self.__currentLevel = None
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
        self.destroyWindow()


class DivisionUpgradeRewardsViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, subdivisionId, prevLvl, currLvl, parent=None):
        super(DivisionUpgradeRewardsViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=DivisionUpgradeRewardsView(R.views.historical_battles.lobby.DivisionUpgradeRewardsView(), subdivisionId, prevLvl, currLvl), parent=parent)

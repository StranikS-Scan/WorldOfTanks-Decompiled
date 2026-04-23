# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/division_panel.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl import backport
from gui.shared.utils import SelectorBattleTypesUtils
from helpers import dependency
from items import vehicles
from historical_battles.gui.impl.gen.view_models.views.lobby.division_panel_model import DivisionPanelModel
from historical_battles.gui.impl.gen.view_models.views.lobby.division_model import DivisionModel
from gui.impl.pub import ViewImpl
from historical_battles.gui.impl.lobby.tooltips.subdivision_tooltip import SubdivisionTooltip
from historical_battles.gui.impl.lobby.tooltips.ability_tooltip import AbilityTooltip
from historical_battles.gui.prb_control import prb_config
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.division_ability_model import DivisionAbilityModel
from historical_battles.gui.shared.event_dispatcher import showHBDivisionsView
_logger = logging.getLogger(__name__)

class DivisionPanel(InjectComponentAdaptor):

    def _makeInjectView(self):
        return DivisionPanelView(R.views.historical_battles.lobby.DivisionPanel())


class DivisionPanelView(ViewImpl):
    __gameEventCtrl = dependency.descriptor(IGameEventController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = DivisionPanelModel()
        super(DivisionPanelView, self).__init__(settings)
        self.__tooltipEnabled = True

    @property
    def viewModel(self):
        return super(DivisionPanelView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if not self.__tooltipEnabled:
            return None
        elif contentID == R.views.historical_battles.lobby.tooltips.SubdivisionTooltip():
            divisionID = event.getArgument('divisionID')
            return SubdivisionTooltip(divisionID)
        elif contentID == R.views.historical_battles.lobby.tooltips.AbilityTooltip():
            abilityID = event.getArgument('abilityID')
            return AbilityTooltip(abilityID)
        else:
            return super(DivisionPanelView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(DivisionPanelView, self)._onLoading()
        self.viewModel.onDivisionChanged += self.__onDivisionChanged
        self.viewModel.onNavigateToDivisionsClicked += self.__onNavigateToDivisionsClicked
        self.__gameEventCtrl.frontDataUpdated += self.__refillDivision
        self.__gameEventCtrl.onDisableDivisionsWidget += self.__onDisableDivisionsWidget
        self.__gameEventCtrl.onDivisionsExpChanged += self.__onDivisionsExpChanged
        self.__fillViewModel()

    def _onLoaded(self, *args, **kwargs):
        super(DivisionPanelView, self)._onLoaded(*args, **kwargs)
        SelectorBattleTypesUtils.setBattleTypeAsKnown(prb_config.PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES)

    def _finalize(self):
        self.viewModel.onDivisionChanged -= self.__onDivisionChanged
        self.viewModel.onNavigateToDivisionsClicked -= self.__onNavigateToDivisionsClicked
        self.__gameEventCtrl.frontDataUpdated -= self.__refillDivision
        self.__gameEventCtrl.onDisableDivisionsWidget -= self.__onDisableDivisionsWidget
        self.__gameEventCtrl.onDivisionsExpChanged -= self.__onDivisionsExpChanged
        super(DivisionPanelView, self)._finalize()

    def __fillViewModel(self):
        isDisabled = self.__gameEventCtrl.divisionsWidgetDisabled
        with self.viewModel.transaction() as tx:
            currentFront = self.__gameEventCtrl.frontController.getSelectedFront()
            tx.setFrontName(currentFront.getName())
            tx.setSelectedDivisionId(self.__gameEventCtrl.frontController.getSelectedSubdivision().getID())
            tx.setIsSwitchingDisabled(isDisabled)
            self.__fillDivisionPanel(tx)

    def __fillDivisionPanel(self, tx):
        divisions = tx.getDivisions()
        divisions.clear()
        for subdivId, subdiv in self.__gameEventCtrl.frontController.getAllSubdivisionsForSelectedFront().iteritems():
            model = DivisionModel()
            model.setId(subdivId)
            model.setVehicleType(subdiv.getVehiclesType())
            model.setLevel(subdiv.getProgressionLevel())
            self.__fillDivisionAbilities(subdiv, model)
            divisions.addViewModel(model)

        divisions.invalidate()

    def __fillDivisionAbilities(self, division, tx):
        abilities = tx.getAbilities()
        abilities.clear()
        equipmentsCache = vehicles.g_cache.equipments()
        for abilityId in division.getAbilitiesData():
            model = DivisionAbilityModel()
            eq = equipmentsCache[abilityId]
            res = R.images.historical_battles.gui.maps.icons.artefact.c_80x80.dyn(eq.iconName)
            if res.exists():
                model.setName(eq.name)
                model.setIcon(backport.image(res()))
                abilities.addViewModel(model)
            _logger.warning("[DivisionPanel] Can't find icon %s", eq.iconName)

        abilities.invalidate()

    def __onDivisionChanged(self, args):
        divisionID = int(args.get('id'))
        if self.viewModel.getSelectedDivisionId() == divisionID:
            return
        self.__gameEventCtrl.updateFrontData(divisionID=divisionID)

    def __onNavigateToDivisionsClicked(self):
        showHBDivisionsView()

    def __onDivisionsExpChanged(self, divisionIds):
        with self.viewModel.transaction() as tx:
            divisionsModels = tx.getDivisions()
            for divisionModel in divisionsModels:
                subdivId = divisionModel.getId()
                if subdivId in divisionIds:
                    self.__updateDivisionLevel(divisionModel, subdivId)

            divisionsModels.invalidate()

    def __updateDivisionLevel(self, model, subdivid):
        subdiv = self.__gameEventCtrl.frontController.getSubdivisionById(subdivid)
        model.setLevel(subdiv.getProgressionLevel())

    def __refillDivision(self, *_):
        self.__fillViewModel()

    def __onDisableDivisionsWidget(self, isDisabled):
        with self.viewModel.transaction() as tx:
            tx.setIsSwitchingDisabled(isDisabled)

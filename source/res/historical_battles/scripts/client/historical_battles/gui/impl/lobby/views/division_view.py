# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/views/division_view.py
from shared_utils import first
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl import backport
from gui.impl.gen import R
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.division_view_model import DivisionViewModel, DivisionModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.division_level_model import DivisionLevelModel, DivisionVehicleModel, DivisionAbilityModel
from helpers import dependency
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from items import vehicles
from historical_battles.gui.impl.lobby.division_confirm_upgrade_view import DivisionConfirmUpgradeViewWindow
from historical_battles.gui.impl.lobby.tooltips.hb_coin_tooltip import HbCoinTooltip
from historical_battles.gui.sounds.sound_hangar_controller import SoundHangarController
from gui.impl.pub.tooltip_window import ToolTipWindow
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
import logging
_logger = logging.getLogger(__name__)

class SubdivDataIndices(object):
    TANKSETS = 'tankSets'
    ABILITIES = 'abilities'
    LEVELS_EXP = 'levelsXp'


class DivisionView(SubModelPresenter):
    __gameEventController = dependency.descriptor(IGameEventController)

    @property
    def viewModel(self):
        return super(DivisionView, self).getViewModel()

    def getParentWindow(self):
        return self.parentView.getParentWindow()

    def initialize(self, *args, **kwargs):
        super(DivisionView, self).initialize(args, kwargs)
        self.__updateModel()
        SoundHangarController.onEnterDivisionView()

    def _getEvents(self):
        return ((self.viewModel.onBuyLevel, self.__onBuyLevel), (self.__gameEventController.onDivisionsExpChanged, self.__onDivisionsExpChanged))

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
        else:
            if event.contentID == R.views.historical_battles.lobby.tooltips.HbCoinTooltip():
                content = HbCoinTooltip()
            else:
                content = self.parentView.createToolTipContent(event, event.contentID)
            window = ToolTipWindow(event, content, self.getParentWindow())
            if window is not None:
                window.load()
                window.move(event.mouse.positionX, event.mouse.positionY)
        return

    def __onDivisionsExpChanged(self, divisionIds):
        with self.viewModel.transaction() as model:
            divisionsModels = model.getDivisions()
            for divisionModel in divisionsModels:
                subdivId = divisionModel.getDivisionID()
                if subdivId in divisionIds:
                    self.__updateDivisionModel(divisionModel, subdivId)

            divisionsModels.invalidate()

    def __getBackportTooltipData(self, event):
        data = None
        vehicleCD = event.getArgument('vehicleCD')
        if vehicleCD:
            data = backport.createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.HB_VEHICLE, specialArgs=[vehicleCD])
        return data

    def __updateDivisionModel(self, model, subdivid):
        subdiv = self.__gameEventController.frontController.getSubdivisionById(subdivid)
        model.setLevel(subdiv.getProgressionLevel())
        model.setExperience(subdiv.getEXP())

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            front = self.__gameEventController.frontController.getSelectedFront()
            frontID = front.getID()
            model.setFrontName(front.getName())
            divisions = model.getDivisions()
            divisions.clear()
            subDivisions = self.__gameEventController.frontController.getAllSubdivisions(frontID)
            for subId, sub in subDivisions.iteritems():
                division = DivisionModel()
                division.setDivisionID(subId)
                data = sub._getSubdivisionData()
                division.setLevel(sub.getProgressionLevel())
                division.setExperience(sub.getEXP())
                self.__setLevels(division, data)
                divisions.addViewModel(division)

            divisions.invalidate()

    def __setLevels(self, division, data):
        levels = division.getLevels()
        levels.clear()
        tankSets = data.get(SubdivDataIndices.TANKSETS, None)
        abilities = data.get(SubdivDataIndices.ABILITIES, None)
        lvlsExp = data.get(SubdivDataIndices.LEVELS_EXP, None)
        if not abilities or not lvlsExp:
            _logger.warning("Invalid subDivisionData. Check 'abilities' and 'levelsXp' nodes")
            return
        else:
            for lvlNum, tankSet in tankSets.iteritems():
                lvlModel = DivisionLevelModel()
                if len(lvlsExp) < lvlNum - 1:
                    _logger.warning("Mismatch between items amount in 'tankSets' node and 'levelsXp' node")
                    return
                lvlModel.setExperience(lvlsExp[lvlNum - 1])
                self.__setLevelVehicles(lvlModel, tankSet)
                self.__setLevelAbilities(lvlModel, abilities[:lvlNum])
                levels.addViewModel(lvlModel)

            levels.invalidate()
            return

    def __setLevelVehicles(self, levelModel, tankSet):
        vehs = levelModel.getVehicles()
        vehs.clear()
        for tankCD in tankSet:
            vehType = vehicles.getItemByCompactDescr(tankCD)
            vehicle = DivisionVehicleModel()
            vehicle.setName(vehType.i18nInfo.userString)
            vehicle.setNameShort(vehType.i18nInfo.shortString)
            vehicle.setIcon(vehType.name.split(':')[1])
            vehicle.setVehicleType(vehType.classTag)
            vehicle.setVehicleCD(tankCD)
            vehs.addViewModel(vehicle)

        vehs.invalidate()

    def __setLevelAbilities(self, levelModel, abilitiesData):
        abilities = levelModel.getAbilities()
        abilities.clear()
        equipmentsCache = vehicles.g_cache.equipments()
        for abilityID in abilitiesData:
            ability = DivisionAbilityModel()
            eq = equipmentsCache[abilityID]
            res = R.images.historical_battles.gui.maps.icons.artefact.c_80x80.dyn(eq.iconName)
            if res.exists():
                ability.setIcon(backport.image(res()))
                ability.setName(eq.name)
                abilities.addViewModel(ability)
            _logger.warning("Can't find icon %s", eq.iconName)

        abilities.invalidate()

    def __onBuyLevel(self, *args):
        subdivision = int(first(args).get('divisionId'))
        DivisionConfirmUpgradeViewWindow(subdivision, parent=self.getParentWindow()).load()

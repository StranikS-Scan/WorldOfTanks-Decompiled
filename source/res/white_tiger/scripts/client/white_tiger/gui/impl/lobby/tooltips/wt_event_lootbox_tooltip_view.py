# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/wt_event_lootbox_tooltip_view.py
import copy
import logging
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from frameworks.wulf import ViewSettings, Array
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import ILootBoxesController
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.wt_event_lootbox_tooltip_view_model import WtEventLootboxTooltipViewModel
from white_tiger.gui.impl.lobby.wt_event_constants import WhiteTigerLootBoxes
from white_tiger.gui.impl.lobby.packers.wt_event_bonuses_packers import getWtUIBonusPacker
_logger = logging.getLogger(__name__)

def getExtendBonusesByLootbox(probBonusesDict, customBonusData, isSortByWeight=True):
    from white_tiger.gui.wt_event_helpers import getCustomData
    extendedBonuses = []
    allBonuses = []
    for _, bonuses in probBonusesDict:
        allBonuses.extend(bonuses)

    for bonus in (b for b in allBonuses if b.isShowInGUI()):
        extendedBonus = copy.copy(bonus)
        extendData = getCustomData(extendedBonus, customBonusData)
        setattr(extendedBonus, 'wtExtendData', extendData)
        extendedBonuses.append(extendedBonus)

    return sorted(extendedBonuses, key=lambda x: x.wtExtendData['weight'], reverse=True) if isSortByWeight else extendedBonuses


def packBonuses(model, bonuses):
    bonusesPacker = getWtUIBonusPacker()
    for bonus in bonuses:
        bonusList = bonusesPacker.pack(bonus)
        for bModel in bonusList:
            model.addViewModel(bModel)


class WtEventLootBoxTooltipView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lootBoxesCtrl = dependency.descriptor(ILootBoxesController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.tooltips.LootBoxTooltipView(), model=WtEventLootboxTooltipViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WtEventLootBoxTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventLootBoxTooltipView, self)._onLoading(*args, **kwargs)
        isHunterLootBox = kwargs.get('isHunterLootBox')
        if isHunterLootBox is None:
            _logger.error('Incorrect type of the lootBox to show the tooltip')
            return
        else:
            boxType = WhiteTigerLootBoxes.WT_HUNTER if isHunterLootBox else WhiteTigerLootBoxes.WT_BOSS
            bonuses = self.__lootBoxesCtrl.getLootBoxesRewards(boxType)
            lootBox = self.__itemsCache.items.tokens.getLootBoxByType(boxType)
            customBonusData = lootBox.getCustomBonusData()
            bonusesByProb = bonuses.get('byProbabilities', [])
            extendedBonuses = getExtendBonusesByLootbox(bonusesByProb, customBonusData)
            bonusesArray = Array()
            vehicleBonusesArray = Array()
            notVehicleBonuses = []
            for bonus in extendedBonuses:
                if bonus.getName() == 'vehicles':
                    vehicleBonusesArray.addString(bonus.getVehicles()[0][0].shortUserName)
                notVehicleBonuses.append(bonus)

            packBonuses(bonusesArray, notVehicleBonuses)
            with self.viewModel.transaction() as model:
                model.setIsHunterLootBox(isHunterLootBox)
                model.setVehicleNames(vehicleBonusesArray)
                model.setBonuses(bonusesArray)
            return

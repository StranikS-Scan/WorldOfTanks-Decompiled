# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/congrats_main_reward_view.py
import itertools
from enum import Enum
from frameworks.wulf import Array, ViewSettings, WindowLayer
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.common.fade_manager import useDefaultFade
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.event_dispatcher import selectVehicleInHangar, showHangar
from gui.shared.utils.functions import replaceHyphenToUnderscore
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.lobby.congrats_main_reward_view_model import CongratsMainRewardViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.main_reward_bonus_model import MainRewardBonusModel
from historical_battles.gui.impl.lobby.base_event_view import BaseEventView
from historical_battles.gui.impl.lobby.hb_helpers.hangar_helpers import closeEvent
from historical_battles.gui.server_events.hb_awards_formatter import getHBCongratsFormatter
from ids_generators import SequenceIDGenerator
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

class _BonusTypes(Enum):
    DOSSIER = 'dossier'
    VEHICLES = 'vehicles'
    SLOTS = 'slots'
    TANKMEN = 'tankmen'


class CongratsMainRewardView(BaseEventView):
    _VEHICLE_FOR_COINS_QUESTS = ['hb22_mainPrize_vehicle_gift', 'hb22_medal']
    _VEHICLE_FOR_GOLD_QUESTS = ['hb22_mainPrize_vehicle_purchase', 'hb22_medal']
    _BONUSES_ORDER = (_BonusTypes.DOSSIER.value,
     _BonusTypes.VEHICLES.value,
     _BonusTypes.SLOTS.value,
     _BonusTypes.TANKMEN.value)
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, forGold, showHangarOnClose=False, *args, **kwargs):
        settings = ViewSettings(R.views.historical_battles.lobby.CongratsMainRewardView())
        settings.model = CongratsMainRewardViewModel()
        super(CongratsMainRewardView, self).__init__(settings, *args, **kwargs)
        questIDs = self._VEHICLE_FOR_GOLD_QUESTS if forGold else self._VEHICLE_FOR_COINS_QUESTS
        vehicle, bonuses = self.__parseQuests(questIDs)
        self.__bonuses = self.__getFormattedBonuses(bonuses)
        self.__vehicle = vehicle
        self.__idGen = SequenceIDGenerator()
        self.__bonusCache = {}
        self.__showHangarOnClose = showHangarOnClose

    @property
    def viewModel(self):
        return super(CongratsMainRewardView, self).getViewModel()

    def createToolTip(self, event):
        tooltipId = event.getArgument('tooltipId', None)
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs), self.getParentWindow())
                window.load()
        return super(CongratsMainRewardView, self).createToolTip(event)

    @useDefaultFade(layer=WindowLayer.SERVICE_LAYOUT)
    def destroyWindow(self):
        super(CongratsMainRewardView, self).destroyWindow()

    def _onLoading(self, *args, **kwargs):
        super(CongratsMainRewardView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self._fillModel(model)
        self._addListeners()

    def _finalize(self):
        self.__bonuses = None
        self.__bonusCache.clear()
        self._removeListeners()
        super(CongratsMainRewardView, self)._finalize()
        return

    def _addListeners(self):
        self.viewModel.onShowInHangar += self.__onShowInHangar
        self.viewModel.onClose += self.__onClose

    def _removeListeners(self):
        self.viewModel.onShowInHangar -= self.__onShowInHangar
        self.viewModel.onClose -= self.__onClose

    def _fillModel(self, model):
        model.vehicle.setId(self.__vehicle.intCD)
        model.vehicle.setName(self.__vehicle.userName)
        imgName = replaceHyphenToUnderscore(self.__vehicle.name.replace(':', '-'))
        model.vehicle.setImage(imgName)
        model.vehicle.setType(self.__vehicle.type)
        model.vehicle.setLevel(self.__vehicle.level)
        model.setRewards(self.__getRewardsArray())

    def __getRewardsArray(self):
        rewards = Array()
        for formattedBonus in self.__bonuses:
            model = MainRewardBonusModel()
            model.setIcon(self.__getBonusIcon(formattedBonus))
            model.setBonusType(formattedBonus.bonusName)
            if formattedBonus.label:
                model.setLabel(formattedBonus.label)
            self.__setTooltip(model, formattedBonus)
            rewards.addViewModel(model)

        rewards.invalidate()
        return rewards

    def __onShowInHangar(self, *_):
        closeEvent()
        selectVehicleInHangar(self.__vehicle.intCD)
        self.destroyWindow()

    def __onClose(self):
        if self.__showHangarOnClose:
            showHangar()
        self.destroyWindow()

    def __setTooltip(self, model, bonus):
        tooltipId = str(self.__idGen.next())
        self.__bonusCache[tooltipId] = bonus
        model.setTooltipId(tooltipId)

    def __parseQuests(self, questIDs):
        bonuses = []
        quests = self._eventsCache.getHiddenQuests(lambda q: q.getID() in questIDs)
        if quests:
            bonuses.extend(itertools.chain.from_iterable((q.getBonuses() for q in quests.itervalues())))
        vehicleBonus = next((b for b in bonuses if b.getName() == _BonusTypes.VEHICLES.value))
        vehicle, vehInfo = first(vehicleBonus.getVehicles())
        tankmenBonus = self.__getTankmenBonus(vehicle, vehInfo)
        if tankmenBonus is not None:
            bonuses.extend(tankmenBonus)
        bonuses = sorted(bonuses, key=self.__keySortOrder)
        return (vehicle, bonuses)

    @staticmethod
    def __getTankmenBonus(vehicle, vehInfo):
        tankmenInfo = []
        crewLvl = vehInfo.get('crewLvl')
        if crewLvl is not None:
            tankmenInfo = [ crew.strCD for _, crew in vehicle.getCrewBySkillLevels(crewLvl) ]
        elif _BonusTypes.TANKMEN.value in vehInfo:
            tankmenInfo = vehInfo.get(_BonusTypes.TANKMEN.value, [])
        tankmenBonus = getNonQuestBonuses(_BonusTypes.TANKMEN.value, tankmenInfo) if tankmenInfo else None
        return tankmenBonus

    def __keySortOrder(self, bonus):
        return self._BONUSES_ORDER.index(bonus.getName()) if bonus.getName() in self._BONUSES_ORDER else len(self._BONUSES_ORDER)

    @staticmethod
    def __getFormattedBonuses(bonuses):
        formatter = getHBCongratsFormatter()
        return formatter.format(bonuses)

    def __getBonusIcon(self, formattedBonus):
        imgPath = formattedBonus.images[AWARDS_SIZES.BIG]
        imgName = self.__getImgName(imgPath)
        if formattedBonus.bonusName == _BonusTypes.DOSSIER.value and 'achievement' in imgPath:
            getBonusIcon = R.images.gui.maps.icons.achievement.c_80x80.dyn(imgName)()
        else:
            getBonusIcon = R.images.gui.maps.icons.quests.bonuses.big.dyn(imgName)()
        return getBonusIcon

    @staticmethod
    def __getImgName(path):
        return '' if path is None else path.split('/')[-1].replace('.png', '')


class CongratsMainRewardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, forGold, showHangarOnClose, parent=None):
        super(CongratsMainRewardWindow, self).__init__(content=CongratsMainRewardView(forGold, showHangarOnClose), parent=parent)

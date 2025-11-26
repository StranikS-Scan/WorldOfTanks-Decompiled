# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/presenters/frontline_ability_presenter.py
from __future__ import absolute_import
import typing
from frontline.constants.common import BATTLE_ABILITY_GROUP_INDEX
from frontline.gui.frontline_helpers import AbilitiesTemplates
from frontline.gui.frontline_helpers import getSkillParams
from frontline.gui.impl.gen.view_models.views.lobby.components.loadout.battle_abilities_setup_model import BattleAbilitiesSetupModel
from frontline.gui.impl.gen.view_models.views.lobby.components.loadout.battle_ability_details import BattleAbilityDetails
from frontline.gui.impl.gen.view_models.views.lobby.components.loadout.battle_ability_level_model import BattleAbilityLevelModel
from frontline.gui.impl.gen.view_models.views.lobby.components.loadout.battle_ability_level_param_model import BattleAbilityLevelParamModel
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_const import FrontlineConst
from frontline.gui.impl.lobby.tank_setup.array_provider import BattleAbilityProvider
from frontline.gui.impl.lobby.tank_setup.configuration import EpicBattleTabs
from frontline.gui.impl.lobby.tank_setup.interactor import FrontlineInteractor
from frontline.gui.impl.lobby.tooltips.skill_order_tooltip import SkillOrderTooltip
import SoundGroups
from CurrentVehicle import g_currentVehicle
from account_helpers.settings_core.options import KeyboardSetting
from epic_constants import CATEGORIES_ORDER
from frameworks.wulf import Array
from gui.game_control.epic_meta_game_ctrl import EpicMetaGameSkill
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.lobby.hangar.presenters.loadout_presenter_base import LoadoutPresenterBase, LoadoutEntityProvider
from gui.impl.lobby.tank_setup.array_providers.base import BaseVehSectionContext
from gui.impl.lobby.tank_setup.tank_setup_sounds import TankSetupSoundEvents
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.shared import IItemsCache
from wg_async import wg_async, await_callback
from frontline.gui.frontline_helpers import isFinishedCycleState
if typing.TYPE_CHECKING:
    from gui.impl.lobby.tank_setup.interactors.base import InteractingItem
TEMPLATES = AbilitiesTemplates(R.strings.fl_battle_abilities_setup.infoPanel.param.valueTemplate)

class FrontlineAbilityPresenter(LoadoutPresenterBase[BattleAbilitiesSetupModel]):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, interactingItem, slotSelectionObserver):
        super(FrontlineAbilityPresenter, self).__init__(interactingItem, model=BattleAbilitiesSetupModel)
        self._sectionName = FrontlineConst.BATTLE_ABILITIES
        self._guiItemType = GUI_ITEM_TYPE.BATTLE_ABILITY
        self._currentSectionName = ''
        self._pendingPurchaseSkillIds = []
        self._pendingPurchaseItemIntCDs = []
        self._itemDetailsLevelMap = {}
        self._totalPurchasePrice = 0
        self._selectedSlotId = 0
        self.__epicSkills = self.__epicController.getEpicSkills()
        self.__slotSelectionObserver = slotSelectionObserver

    def createSlotActions(self):
        actions = {BaseSetupModel.ADD_ONE_SLOT_ACTION: self._onAdd}
        actions.update(super(FrontlineAbilityPresenter, self).createSlotActions())
        return actions

    def createToolTipContent(self, event, contentID):
        return SkillOrderTooltip() if contentID == R.views.frontline.mono.lobby.tooltips.skill_order_tooltip() else super(FrontlineAbilityPresenter, self).createToolTipContent(event, contentID)

    def updateBlock(self, viewModel):
        pass

    def _getKeySettings(self):
        pass

    def _getSlotIdxByCategory(self, category):
        for idx, slot in enumerate(self._vehicle.battleAbilities.slots):
            if category == tuple(slot.tags)[0]:
                return idx

        return None

    @property
    def _vehicle(self):
        return self.getVehicleItem().getItem()

    def _revertItem(self, slotID):
        item = self._interactor.getInstalledLayout()[slotID]
        self._selectItem(slotID, item.intCD)

    def _selectItem(self, slotID, itemCD):
        self._selectedSlotId = slotID
        self.__slotSelectionObserver.onPanelSlotSelect(self._currentSectionName, BATTLE_ABILITY_GROUP_INDEX, slotID)
        super(FrontlineAbilityPresenter, self)._selectItem(slotID, int(itemCD))

    def _getEvents(self):
        return super(FrontlineAbilityPresenter, self)._getEvents() + ((self.__epicController.onUpdated, self.__onEpicUpdated),
         (self.__epicController.onBattleAbilitiesUpdated, self.__onBattleAbilitiesUpdated),
         (self.getViewModel().onApplyToTypeChanged, self.__onApplyToTypeChanged),
         (self.getViewModel().onCurrentAbilityLevelChanged, self.__onCurrentAbilityLevelChanged),
         (g_currentVehicle.onChanged, self.__onChangedVehicle),
         (self.getViewModel().dealPanel.onDealCancelled, self.__onDealCancelled))

    def _createProvider(self, vehInteractingItem):
        self._provider = LoadoutEntityProvider(vehInteractingItem, FrontlineInteractor, {EpicBattleTabs.BATTLE_ABILITY: BattleAbilityProvider})

    def _updateModel(self, *_):
        dataProvider = self._provider.dataProviders[EpicBattleTabs.BATTLE_ABILITY]
        self._pendingPurchaseSkillIds = []
        self._pendingPurchaseItemIntCDs = []
        self._totalPurchasePrice = 0
        currentItems = self._interactor.getChangedList()
        for item in currentItems:
            skill = self.__epicSkills[item.innationID]
            if not skill.isActivated:
                self._pendingPurchaseSkillIds.append(skill.skillID)
                self._pendingPurchaseItemIntCDs.append(item.intCD)
                self._totalPurchasePrice += skill.price

        with self.getViewModel().transaction() as vm:
            dataProvider.fillArray(vm.getSlots(), BaseVehSectionContext(self._currentSlotIndex))
            vehicle = g_currentVehicle.item
            vm.setVehicleType(vehicle.type)
            vm.setIsCycleFinished(isFinishedCycleState())
            vm.setIsTypeSelected(False)
            vm.setPointsAmount(self.__epicController.getSkillPoints())
            vm.setTotalPurchasePrice(self._totalPurchasePrice)
            categoriesOrder = vm.getCategoriesOrder()
            categoriesOrder.clear()
            for category in CATEGORIES_ORDER:
                categoriesOrder.addString(category)

            categoriesOrder.invalidate()
            keyNames = vm.getKeyNames()
            keyNames.clear()
            for keySetting in self._getKeySettings():
                keyNames.addString(KeyboardSetting(keySetting).getKeyName())

            keyNames.invalidate()
        self.__updateDetails()

    def _onRevertItem(self, args):
        SoundGroups.g_instance.playSound2D(TankSetupSoundEvents.CONSUMABLES_DEMOUNT)
        super(FrontlineAbilityPresenter, self)._onRevertItem(args)

    def _onSlotSelected(self, slotIndex, sectionName, sectionSwitched):
        self._currentSectionName = sectionName
        self._selectedSlotId = slotIndex
        super(FrontlineAbilityPresenter, self)._onSlotSelected(slotIndex, sectionName, sectionSwitched)

    def _onAdd(self, args):
        itemIntCD = int(args.get('intCD'))
        self._interactor.buyMore(itemIntCD)

    def _update(self):
        self._updateInteractor()
        self.__updateProvider()
        self._updateModel()

    def __applyAbilitiesToTypeSettings(self, state):
        self._interactor.setCheckboxState(state)
        self.getViewModel().setIsTypeSelected(state)

    def __updateProvider(self):
        dataProvider = self._provider.dataProviders[EpicBattleTabs.BATTLE_ABILITY]
        dataProvider.updateItems()

    def __updateDetails(self):
        if not self.__epicController.isEnabled():
            return
        item = self.__getCurrentLayoutItem(self._selectedSlotId)
        if not item:
            return
        detailsModel = self.getViewModel().details
        with detailsModel.transaction() as vm:
            skill = self.__epicSkills[item.innationID]
            info = skill.getSkillInfo()
            needFullUpdate = vm.getIntCD() != item.intCD
            vm.setIntCD(item.intCD)
            vm.setName(info.name)
            vm.setCategory(skill.category)
            vm.setDescription(info.longDescr)
            vm.setIsActivated(skill.isActivated)
            vm.setSelectedLevel(self._itemDetailsLevelMap.get(item.intCD, 0))
            if needFullUpdate:
                levels = vm.getLevelInfos()
                levels.clear()
                self.__fillDetailsSkillLevels(levels, skill)

    def __fillDetailsSkillLevels(self, levels, skillData):
        skillParams = getSkillParams(skillData)
        for lvl, skillLevelData in skillData.levels.iteritems():
            levelModel = BattleAbilityLevelModel()
            levels.addViewModel(levelModel)
            levelModel.setId(skillLevelData.eqID)
            params = levelModel.getParams()
            for paramList in skillParams[lvl].values():
                for param in paramList:
                    skillParam = BattleAbilityLevelParamModel()
                    skillParam.setId(param.get('id'))
                    skillParam.setName(param.get('name'))
                    skillParam.setValue(param.get('value'))
                    skillParam.setSign(param.get('sign'))
                    skillParam.setValueTemplate(param.get('valueTemplate'))
                    params.addViewModel(skillParam)

    @wg_async
    def __onDealCancelled(self, _=None):
        self.getViewModel().dealPanel.setCanAccept(self._interactor.hasChanged())
        yield await_callback(self._interactor.applyQuit)(skipApplyAutoRenewal=False)

    def __onApplyToTypeChanged(self, *_):
        state = not self.getViewModel().getIsTypeSelected()
        self.__applyAbilitiesToTypeSettings(state)

    def __onBattleAbilitiesUpdated(self):
        self._update()

    def __onEpicUpdated(self, diff):
        if 'isEnabled' in diff and not self.__epicController.isEnabled():
            return
        if 'abilityPts' in diff:
            pointsAmount = diff['abilityPts']
            self.getViewModel().setPointsAmount(pointsAmount)
        self._update()

    def __onChangedVehicle(self):
        self._updateModel()

    def __onCurrentAbilityLevelChanged(self, params):
        level = params.get('level', 0)
        item = self.__getCurrentLayoutItem(self._selectedSlotId)
        self._itemDetailsLevelMap[item.intCD] = level
        detailsModel = self.getViewModel().details
        with detailsModel.transaction() as vm:
            vm.setSelectedLevel(level)

    def __getCurrentLayoutItem(self, slotId):
        return self._interactor.getCurrentLayout()[slotId]

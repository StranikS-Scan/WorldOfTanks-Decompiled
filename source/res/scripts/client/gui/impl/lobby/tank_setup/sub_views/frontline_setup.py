# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/sub_views/frontline_setup.py
import typing
from BWUtil import AsyncReturn
from skeletons.account_helpers.settings_core import ISettingsCore
from wg_async import wg_async, wg_await, await_callback
from gui.impl.lobby.tank_setup.tank_setup_sounds import playSound, TankSetupSoundEvents
from gui.impl.lobby.tank_setup.configurations.epic_battle_ability import EpicBattleTabsController, EpicBattleDealPanel
from gui.impl.lobby.tank_setup.sub_views.base_equipment_setup import BaseEquipmentSetupSubView
from gui.shared.event_dispatcher import showFrontlineInfoWindow
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, i18n
from epic_constants import CATEGORIES_ORDER
from frontline.gui.impl.gen.view_models.views.lobby.views.info_page_scroll_to_section import InfoPageScrollToSection
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IEpicBattleMetaGameController
from CurrentVehicle import g_currentVehicle
from uilogging.epic_battle.constants import EpicBattleLogKeys, EpicBattleLogActions, EpicBattleLogButtons, EpicBattleLogAdditionalInfo
from uilogging.epic_battle.loggers import EpicBattleTooltipLogger
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.battle_ability_level_model import BattleAbilityLevelModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.battle_ability_level_param_model import BattleAbilityLevelParamModel
from items import vehicles
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import createEpicParam
from gui.impl import backport
from gui.shared.tooltips.battle_ability_tooltip_params import g_battleAbilityTooltipMgr
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.frontline_setup_model import FrontlineSetupModel
    from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.battle_ability_details import BattleAbilityDetails
    from gui.game_control.epic_meta_game_ctrl import EpicMetaGameSkill
    from frameworks.wulf import Array
TEMPLATE_DIR = R.strings.tank_setup.abilities.details.param.valueTemplate
TEMPLATE_DEFAULT = TEMPLATE_DIR.default()
TEMPLATE_SECONDS = TEMPLATE_DIR.seconds()
TEMPLATE_METERS = TEMPLATE_DIR.meters()
TEMPLATE_PERCENTS = TEMPLATE_DIR.percents()
TEMPLATE_PERCENTS_BY_SECOND = TEMPLATE_DIR.percentsBySecond()
SKILL_PARAM_TEMPLATES = {'FixedTextParam': TEMPLATE_DEFAULT,
 'DirectNumericTextParam': TEMPLATE_DEFAULT,
 'DirectSecondsTextParam': TEMPLATE_SECONDS,
 'DirectMetersTextParam': TEMPLATE_METERS,
 'MulDirectPercentageTextParam': TEMPLATE_PERCENTS,
 'AddDirectPercentageTextParam': TEMPLATE_PERCENTS_BY_SECOND,
 'MulReciprocalPercentageTextParam': TEMPLATE_PERCENTS,
 'AddReciprocalPercentageTextParam': TEMPLATE_PERCENTS,
 'ShellStunSecondsTextParam': TEMPLATE_SECONDS,
 'MultiMetersTextParam': TEMPLATE_METERS,
 'NestedMetersTextParam': TEMPLATE_METERS,
 'NestedSecondsTextParam': TEMPLATE_SECONDS,
 'MulNestedPercentageTextParam': TEMPLATE_PERCENTS,
 'AddNestedPercentageTextParam': TEMPLATE_PERCENTS,
 'NestedShellStunSecondsTextParam': TEMPLATE_SECONDS,
 'MulNestedPercentageTextTupleValueParam': TEMPLATE_PERCENTS}
HIDDEN_PARAMS = ['inactivationDelay', '#epic_battle:abilityInfo/params/fl_regenerationKit/minesDamageReduceFactor/value', 'projectilesNumber']
PLUS_SIGN = '+'
SKILL_PARAM_SIGN = {'increaseFactors/crewRolesFactor': PLUS_SIGN,
 'resupplyCooldownFactor': PLUS_SIGN,
 'resupplyHealthPointsFactor': PLUS_SIGN,
 'captureSpeedFactor': PLUS_SIGN,
 'captureBlockBonusTime': PLUS_SIGN}

class FLScenarioInfoBtnHintChecker(object):
    __settingsCore = dependency.descriptor(ISettingsCore)

    def check(self, aliasId):
        return not bool(self.__settingsCore.serverSettings.getOnceOnlyHintsSetting(aliasId))


class EpicBattleSetupSubView(BaseEquipmentSetupSubView):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    _appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ('__tooltipMgr', '__uiEpicBattleLogger', '__pendingPurchaseSkillIds', '__pendingPurchaseItemIntCDs', '__totalPurchasePrice', '__selectedSlotId', '__itemDetailsLevelMap', '__isCurrentlyActiveSubView')

    def __init__(self, viewModel, interactor):
        super(EpicBattleSetupSubView, self).__init__(viewModel, interactor)
        self.__tooltipMgr = None
        self.__uiEpicBattleLogger = EpicBattleTooltipLogger()
        self.__pendingPurchaseSkillIds = []
        self.__pendingPurchaseItemIntCDs = []
        self.__itemDetailsLevelMap = {}
        self.__totalPurchasePrice = 0
        self.__selectedSlotId = 0
        self.__isCurrentlyActiveSubView = False
        app = self._appLoader.getApp()
        if app is not None:
            self.__tooltipMgr = app.getToolTipMgr()
        with self._viewModel.transaction() as vm:
            vehicle = g_currentVehicle.item
            vm.setVehicleType(vehicle.type)
            vm.setIsTypeSelected(False)
            vm.setPointsAmount(self.__epicController.getSkillPoints())
            categoriesOrder = vm.getCategoriesOrder()
            for category in CATEGORIES_ORDER:
                categoriesOrder.addString(category)

        return

    def onLoading(self, currentSlotID, *args, **kwargs):
        super(EpicBattleSetupSubView, self).onLoading(currentSlotID, *args, **kwargs)
        self.__selectedSlotId = currentSlotID
        self.__isCurrentlyActiveSubView = True
        self.__updateDetails()
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.OPEN, item=EpicBattleLogKeys.SKILLS_VIEW, parentScreen=EpicBattleLogKeys.HANGAR)
        self.__uiEpicBattleLogger.initialize(EpicBattleLogKeys.SKILLS_VIEW)
        self.__uiEpicBattleLogger.startAction(EpicBattleLogActions.VIEW_WATCHED.value)

    def finalize(self):
        super(EpicBattleSetupSubView, self).finalize()
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLOSE, item=EpicBattleLogKeys.SKILLS_VIEW, parentScreen=EpicBattleLogKeys.HANGAR)
        self.__resumeViewWatchedLogger()
        self.__uiEpicBattleLogger.stopAction(EpicBattleLogActions.VIEW_WATCHED, EpicBattleLogKeys.SKILLS_VIEW, EpicBattleLogKeys.HANGAR, timeLimit=self.__uiEpicBattleLogger.TIME_LIMIT)
        self.__uiEpicBattleLogger.reset()

    def updateSlots(self, slotID, fullUpdate=True, updateData=True):
        self.__selectedSlotId = slotID
        self.__resumeViewWatchedLogger()
        self._viewModel.setIsLocked(self.__hasBattleAbilities())
        super(EpicBattleSetupSubView, self).updateSlots(slotID, True, updateData)
        self.__updateDetails()

    def revertItem(self, slotID):
        self._interactor.revertSlot(slotID)
        self.update()

    @wg_async
    def canQuit(self, skipApplyAutoRenewal=None):
        if self._asyncActionLock.isLocked:
            raise AsyncReturn(False)
        currentItems = self._interactor.getChangedList()
        result = True
        hasEnoughPoints = self.__epicController.getSkillPoints() >= self.__totalPurchasePrice
        hasItemsToPurchase = self._interactor.hasChanged() and len(currentItems) == len(self.__pendingPurchaseSkillIds)
        if hasItemsToPurchase and hasEnoughPoints:
            isOk, data = yield wg_await(self._asyncActionLock.tryAsyncCommand(self.__purchaseSelectedAbilities))
            if isOk:
                isOK = yield await_callback(self._onConfirm)(skipDialog=True)
                if isOK:
                    playSound(TankSetupSoundEvents.ACCEPT)
            elif data.get('rollBack', False):
                self._interactor.revert()
                self.update()
            else:
                result = False
            if result:
                yield await_callback(self._interactor.applyQuit)(skipApplyAutoRenewal=skipApplyAutoRenewal)
        else:
            for slotID, item in enumerate(self._interactor.getCurrentLayout()):
                if item.intCD in self.__pendingPurchaseItemIntCDs:
                    self._interactor.revertSlot(slotID)

            self.update()
            result = yield wg_await(super(EpicBattleSetupSubView, self).canQuit(skipApplyAutoRenewal))
        if result:
            self.__isCurrentlyActiveSubView = False
            self.__uiEpicBattleLogger.suspendAction(EpicBattleLogActions.VIEW_WATCHED.value)
        raise AsyncReturn(result)

    def update(self, fullUpdate=False):
        super(EpicBattleSetupSubView, self).update(fullUpdate)
        self.__updateDetails()

    def _onDealConfirmed(self, _=None):
        super(EpicBattleSetupSubView, self)._onDealConfirmed(_)
        info = EpicBattleLogAdditionalInfo.APPLY_TO_CLASS.value if self._viewModel.getIsTypeSelected() else EpicBattleLogAdditionalInfo.APPLY_TO_VEHICLE.value
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, item=EpicBattleLogButtons.CONFIRM.value, parentScreen=EpicBattleLogKeys.SETUP_VIEW.value, info=info)

    def _onDealCancelled(self, _=None):
        super(EpicBattleSetupSubView, self)._onDealCancelled(_)
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, item=EpicBattleLogButtons.CANCEL.value, parentScreen=EpicBattleLogKeys.SETUP_VIEW.value)

    def _createTabsController(self):
        return EpicBattleTabsController()

    def _getDealPanel(self):
        return EpicBattleDealPanel

    def _addListeners(self):
        super(EpicBattleSetupSubView, self)._addListeners()
        self._viewModel.showInfoPage += self.__showInfoPage
        self._viewModel.purchaseSelectedAbilities += self.__purchaseSelectedAbilities
        self._viewModel.onChangeApplyAbilitiesToTypeSettings += self.__onChangeApplyAbilitiesToTypeSettings
        self._viewModel.setCurrentSlotDetailsLevel += self.__setCurrentSlotDetailsLevel
        self.__epicController.onUpdated += self.__onEpicUpdated

    def _removeListeners(self):
        self._viewModel.showInfoPage -= self.__showInfoPage
        self._viewModel.purchaseSelectedAbilities -= self.__purchaseSelectedAbilities
        self._viewModel.onChangeApplyAbilitiesToTypeSettings -= self.__onChangeApplyAbilitiesToTypeSettings
        self._viewModel.setCurrentSlotDetailsLevel -= self.__setCurrentSlotDetailsLevel
        self.__epicController.onUpdated -= self.__onEpicUpdated
        super(EpicBattleSetupSubView, self)._removeListeners()

    def _updateDealPanel(self):
        super(EpicBattleSetupSubView, self)._updateDealPanel()
        if self._viewModel is None:
            return
        else:
            self.__pendingPurchaseSkillIds = []
            self.__pendingPurchaseItemIntCDs = []
            self.__totalPurchasePrice = 0
            currentItems = self._interactor.getChangedList()
            epicSkills = self.__epicController.getEpicSkills()
            for item in currentItems:
                skill = epicSkills[item.innationID]
                if not skill.isActivated:
                    self.__pendingPurchaseSkillIds.append(skill.skillID)
                    self.__pendingPurchaseItemIntCDs.append(item.intCD)
                    self.__totalPurchasePrice += skill.price

            with self._viewModel.transaction() as vm:
                vm.setTotalPurchasePrice(self.__totalPurchasePrice)
            return

    def _selectItem(self, slotID, item):
        self.__selectedSlotId = slotID
        super(EpicBattleSetupSubView, self)._selectItem(slotID, item)

    def _setTab(self, tabName):
        if self._currentTabName != tabName:
            super(EpicBattleSetupSubView, self)._setTab(tabName)
            self.__updateProvider()

    def __resumeViewWatchedLogger(self):
        if not self.__isCurrentlyActiveSubView:
            self.__isCurrentlyActiveSubView = True
            self.__uiEpicBattleLogger.resumeAction(EpicBattleLogActions.VIEW_WATCHED.value)

    def __onEpicUpdated(self, diff):
        if 'isEnabled' in diff and not self.__epicController.isEnabled():
            return
        if 'abilityPts' in diff:
            pointsAmount = diff['abilityPts']
            self._viewModel.setPointsAmount(pointsAmount)
        self.__updateProvider()
        self.update()

    def __updateProvider(self):
        self._provider.updateAbiblities()

    def __onChangeApplyAbilitiesToTypeSettings(self, *_):
        state = not self._viewModel.getIsTypeSelected()
        self._interactor.setCheckboxState(state)
        self._viewModel.setIsTypeSelected(state)
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, item=EpicBattleLogButtons.CHECKBOX.value, parentScreen=EpicBattleLogKeys.SETUP_VIEW.value)

    def __onPurchaseConfirmed(self, skillIds, callback):
        self._interactor.buyAbilities(skillIds, callback)

    @wg_async
    def __purchaseSelectedAbilities(self):
        result = True
        data = {}
        if self.__pendingPurchaseSkillIds:
            dialogResult = yield self._interactor.showBuyConfirmDialog(self.__pendingPurchaseSkillIds)
            isOk, data = dialogResult.result
            if isOk:
                result = yield await_callback(self.__onPurchaseConfirmed)(self.__pendingPurchaseSkillIds)
            else:
                result = False
        raise AsyncReturn((result, data))

    def __showInfoPage(self, *_):
        showFrontlineInfoWindow(autoscrollSection=InfoPageScrollToSection.BATTLE_SCENARIOS)
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK, item=EpicBattleLogButtons.INFO_PAGE, parentScreen=EpicBattleLogKeys.SETUP_VIEW)

    def __setCurrentSlotDetailsLevel(self, params):
        level = params.get('level', 0)
        item = self._interactor.getCurrentLayout()[self.__selectedSlotId]
        self.__itemDetailsLevelMap[item.intCD] = level
        detailsModel = self._viewModel.details
        with detailsModel.transaction() as vm:
            vm.setSelectedLevel(level)

    def __hasBattleAbilities(self):
        return bool(self._itemsCache.items.getItems(GUI_ITEM_TYPE.BATTLE_ABILITY, REQ_CRITERIA.UNLOCKED))

    def __updateDetails(self):
        if not self.__epicController.isEnabled():
            return
        item = self._interactor.getCurrentLayout()[self.__selectedSlotId]
        if not item:
            return
        detailsModel = self._viewModel.details
        with detailsModel.transaction() as vm:
            epicSkills = self.__epicController.getEpicSkills()
            skill = epicSkills[item.innationID]
            info = skill.getSkillInfo()
            needFullUpdate = vm.getIntCD() != item.intCD
            vm.setIntCD(item.intCD)
            vm.setName(info.name)
            vm.setCategory(skill.category)
            vm.setDescription(info.longDescr)
            vm.setIsActivated(skill.isActivated)
            if item.intCD in self.__itemDetailsLevelMap:
                vm.setSelectedLevel(self.__itemDetailsLevelMap[item.intCD])
            else:
                vm.setSelectedLevel(0)
            if needFullUpdate:
                levels = vm.getLevelInfos()
                levels.clear()
                self.__fillDetailsSkillLevels(levels, skill)

    @staticmethod
    def __fillDetailsSkillLevels(levels, skillData):
        equipments = vehicles.g_cache.equipments()
        for _, skillLevelData in skillData.levels.iteritems():
            curLvlEq = equipments[skillLevelData.eqID]
            levelModel = BattleAbilityLevelModel()
            levels.addViewModel(levelModel)
            levelModel.setId(skillLevelData.eqID)
            params = levelModel.getParams()
            paramId = 0
            for tooltipIdentifier in curLvlEq.tooltipIdentifiers:
                if tooltipIdentifier in HIDDEN_PARAMS:
                    continue
                param = createEpicParam(curLvlEq, tooltipIdentifier)
                if param:
                    tooltipName, tooltipRenderer = g_battleAbilityTooltipMgr.getTooltipInfo(tooltipIdentifier)
                    paramId += 1
                    skillParam = BattleAbilityLevelParamModel()
                    skillParam.setId(tooltipIdentifier)
                    skillParam.setName(i18n.makeString(tooltipName) if i18n.isValidKey(tooltipName) else '')
                    skillParam.setValue(str(param))
                    skillParam.setSign(SKILL_PARAM_SIGN.get(tooltipIdentifier, ''))
                    skillParam.setValueTemplate(str(backport.text(TEMPLATE_DEFAULT if isinstance(param, str) else SKILL_PARAM_TEMPLATES.get(tooltipRenderer, TEMPLATE_DEFAULT))))
                    params.addViewModel(skillParam)

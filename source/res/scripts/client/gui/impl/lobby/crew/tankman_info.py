# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tankman_info.py
import itertools
import typing
from frameworks.wulf import ViewSettings
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.dialogs.dialogs import showRetrainDialog
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.tankman_info_model import TankmanInfoModel
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.crew.base_crew_view import BaseCrewSoundView
from gui.impl.lobby.crew.tooltips.premium_vehicle_tooltip import PremiumVehicleTooltip
from gui.impl.lobby.crew.tooltips.training_level_tooltip import TrainingLevelTooltip
from gui.impl.lobby.crew.utils import VEHICLE_TAGS_FILTER, playRecruitVoiceover
from gui.shared import event_dispatcher
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.money import Money, Currency
from helpers import dependency
from items import tankmen
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import ISpecialSoundCtrl
from skeletons.gui.shared import IItemsCache
from uilogging.crew.loggers import CrewTankmanInfoLogger
from uilogging.crew.logging_constants import CrewPersonalFileKeys
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
ALT_VOICES_PREVIEW = itertools.cycle(('vo_enemy_hp_damaged_by_projectile_by_player', 'vo_enemy_fire_started_by_player', 'vo_enemy_killed_by_player'))

class TankmanInfo(BaseCrewSoundView):
    __slots__ = ('_tankman', '_tankmanCurrentVehicle', '_voiceoverParams', '_retrainPrice', '_toolTipMgr', '_uiLogger', '__sound')
    LAYOUT_DYN_ACCESSOR = R.views.lobby.crew.widgets.TankmanInfo
    _MODEL_CLASS = TankmanInfoModel
    _itemsCache = dependency.descriptor(IItemsCache)
    _appLoader = dependency.descriptor(IAppLoader)
    _specialSounds = dependency.descriptor(ISpecialSoundCtrl)

    def __init__(self, tankmanId, layoutID=None, isUiLoggingDisabled=True):
        settings = ViewSettings(layoutID or self.LAYOUT_DYN_ACCESSOR())
        settings.model = self._MODEL_CLASS()
        self._tankman = self._itemsCache.items.getTankman(tankmanId)
        self._tankmanCurrentVehicle = self._itemsCache.items.getVehicle(self._tankman.vehicleInvID)
        self._voiceoverParams = self._getUniqueVoiceoverParams()
        self._updateRetrainPrice()
        self._toolTipMgr = self._appLoader.getApp().getToolTipMgr()
        self._uiLogger = CrewTankmanInfoLogger(isUiLoggingDisabled)
        self.__sound = None
        super(TankmanInfo, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def setTankmanId(self, tankmanId):
        self._tankman = self._itemsCache.items.getTankman(tankmanId)
        self._tankmanCurrentVehicle = self._itemsCache.items.getVehicle(self._tankman.vehicleInvID)
        if self._tankman:
            self._voiceoverParams = self._getUniqueVoiceoverParams()
            self._updateRetrainPrice()
            self._updateViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId', None)
            self._uiLogger.onBeforeTooltipOpened(tooltipId)
            if tooltipId == TooltipConstants.SKILL:
                args = [str(event.getArgument('skillName')),
                 self._tankman.invID,
                 event.getArgument('level', None),
                 False,
                 True,
                 self.getParentWindow()]
                self._toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.CREW_PERK_GF, args, event.mouse.positionX, event.mouse.positionY)
                return TOOLTIPS_CONSTANTS.CREW_PERK_GF
            if tooltipId == TOOLTIPS_CONSTANTS.COMMANDER_BONUS:
                args = [self.getParentWindow()]
                self._toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.COMMANDER_BONUS, args, event.mouse.positionX, event.mouse.positionY)
                return TOOLTIPS_CONSTANTS.COMMANDER_BONUS
            if tooltipId == TooltipConstants.TANKMAN:
                args = (self.getParentWindow(), self._tankman.invID)
                self._toolTipMgr.onCreateWulfTooltip(TooltipConstants.TANKMAN, args, event.mouse.positionX, event.mouse.positionY)
                return TooltipConstants.TANKMAN
        return super(TankmanInfo, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            if self._retrainPrice.isActionPrice():
                specialAlias = (None,
                 None,
                 self._retrainPrice.price.toMoneyTuple(),
                 self._retrainPrice.defPrice.toMoneyTuple(),
                 True,
                 False,
                 None,
                 True)
                return createBackportTooltipContent(specialAlias=TOOLTIPS_CONSTANTS.ACTION_PRICE, specialArgs=specialAlias)
        if contentID == R.views.lobby.crew.tooltips.PremiumVehicleTooltip():
            return PremiumVehicleTooltip(vehicleCD=self._tankman.vehicleNativeDescr.type.compactDescr)
        elif contentID == R.views.lobby.crew.tooltips.TrainingLevelTooltip():
            return TrainingLevelTooltip(self._tankman.invID)
        elif contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        else:
            return super(TankmanInfo, self).createToolTipContent(event, contentID)

    def _updateRetrainPrice(self):
        shop = self._itemsCache.items.shop
        tankmanCost = shop.tankmanCost
        defTankmanCost = shop.defaults.tankmanCost
        credit = tankmanCost[1][Currency.CREDITS]
        defCredit = defTankmanCost[1][Currency.CREDITS]
        gold = tankmanCost[2][Currency.GOLD]
        defGold = defTankmanCost[2][Currency.GOLD]
        creditAction = credit != defCredit
        goldAction = gold != defGold
        self._retrainPrice = ItemPrice(price=Money(credits=credit if creditAction else None, gold=gold if goldAction else None), defPrice=Money(credits=defCredit if creditAction else None, gold=defGold if goldAction else None))
        return

    def _getUniqueVoiceoverParams(self):
        specialVoiceTag = tankmen.getSpecialVoiceTag(self._tankman)
        return self._specialSounds.getVoiceoverByTankmanTag(specialVoiceTag)

    def _onLoading(self, *args, **kwargs):
        super(TankmanInfo, self)._onLoading(*args, **kwargs)
        self._updateViewModel()
        self._uiLogger.initialize()

    def _finalize(self):
        self._uiLogger.finalize()
        if self.__sound and self.__sound.isPlaying:
            self.__sound.stop()
        self.__sound = None
        super(TankmanInfo, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onPlayUniqueVoice, self.__onPlayUniqueVoice),
         (self.viewModel.onChangeVehicle, self.__onChangeVehicle),
         (self.viewModel.onRetrain, self.__onRetrain),
         (self._itemsCache.onSyncCompleted, self._onCacheResync))

    def _updateViewModel(self):
        with self.viewModel.transaction() as vm:
            self._fillViewModel(vm)

    def _fillViewModel(self, vm):
        self._setTankmanInfo(vm)
        self._setVehicleInfo(vm)
        vm.setHasRetrainDiscount(self._retrainPrice.isActionPrice())

    def _setTankmanInfo(self, vm):
        vm.setIconName(self._tankman.getExtensionLessIconWithSkin())
        vm.setIsInSkin(self._tankman.isInSkin)
        vm.setFullName(self._tankman.getFullUserNameWithSkin())
        vm.setDescription(self._tankman.getDescription())
        vm.setIsFemale(self._tankman.isFemale)
        vm.setRole(self._tankman.role)
        vm.setInvId(self._tankman.invID)
        vm.setHasUniqueSound(self._voiceoverParams is not None)
        vm.setIsCrewLocked(self._tankmanCurrentVehicle and self._tankmanCurrentVehicle.isCrewLocked)
        vm.setRealRoleLevel(int(self._tankman.realRoleLevel.lvl))
        vm.setNativeTankRealRoleLevel(self._tankman.nativeTankRealRoleLevel)
        vm.setRoleLevel(self._tankman.roleLevel)
        return

    def _setVehicleInfo(self, vm):
        nativeVehicle = self._itemsCache.items.getItemByCD(self._tankman.vehicleNativeDescr.type.compactDescr)
        if self._tankmanCurrentVehicle:
            fillVehicleModel(vm.currentVehicle, self._tankmanCurrentVehicle, VEHICLE_TAGS_FILTER)
            vm.currentVehicle.setIsPremium(self._tankmanCurrentVehicle.isPremium)
        if nativeVehicle:
            fillVehicleModel(vm.nativeVehicle, nativeVehicle, VEHICLE_TAGS_FILTER)

    def _onCacheResync(self, reason, _):
        if reason in (CACHE_SYNC_REASON.STATS_RESYNC, CACHE_SYNC_REASON.SHOW_GUI):
            return
        else:
            tankman = self._itemsCache.items.getTankman(self._tankman.invID)
            if tankman is None:
                return
            self._tankman = tankman
            self._updateRetrainPrice()
            self._updateViewModel()
            return

    @wg_async
    def __onRetrain(self):
        self._uiLogger.logClick(CrewPersonalFileKeys.RETRAIN_BUTTON)
        vehicleIntCD = self._tankmanCurrentVehicle.intCD if self._tankmanCurrentVehicle else self._itemsCache.items.getItemByCD(self._tankman.vehicleNativeDescr.type.compactDescr).intCD
        yield wg_await(showRetrainDialog([self._tankman.invID], vehicleIntCD))

    def __onChangeVehicle(self):
        self._uiLogger.logClick(CrewPersonalFileKeys.CHANGE_SPECIALIZATION_BUTTON)
        event_dispatcher.showTankChange(tankmanInvID=self._tankman.invID, previousViewID=self.getParentView().currentTabId)

    def __onPlayUniqueVoice(self):
        if self._voiceoverParams is None:
            return
        else:
            self.__sound = playRecruitVoiceover(self._voiceoverParams)
            self._uiLogger.logClick(CrewPersonalFileKeys.VOICEOVER_BUTTON)
            return

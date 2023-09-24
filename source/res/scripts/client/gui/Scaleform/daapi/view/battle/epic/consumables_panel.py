# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/consumables_panel.py
from ReservesEvents import randomReservesEvents
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers.epic_game import searchRankForSlot
from items.vehicles import getVehicleClassFromVehicleType
from gui.impl import backport
from gui.impl.gen import R
from functools import partial
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_TYPE_CAPS
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from frontline.gui.frontline_helpers import getReserveIconPath
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IEpicBattleMetaGameController
from items import EQUIPMENT_TYPES

class EpicBattleConsumablesPanel(ConsumablesPanel):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _EMPTY_LOCKED_SLOT = -1
    _GLOW_DELAY = 0.5
    _WAITED_SLOT_GLOW_TIME = 3
    _R_EPIC_EQUIPMENT_ICON = R.images.gui.maps.icons.epicBattles.skills.c_48x48
    __EMPTY_SCALE_FORM_KEY = -1

    def __init__(self):
        super(EpicBattleConsumablesPanel, self).__init__()
        self.__battleReserveSlots = dict()
        self.__glowUpdateInfo = dict()
        self.__indicatedSlots = set()
        self.__currentSlotIdx = None
        return

    def _addListeners(self):
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onSlotWaited += self._onSlotWaited
            eqCtrl.onSlotBlocked += self._onSlotBlocked
        randomReservesEvents.onShownPanel += self._updateLockedSlot
        super(EpicBattleConsumablesPanel, self)._addListeners()
        return

    def _removeListeners(self):
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onSlotWaited -= self._onSlotWaited
            eqCtrl.onSlotBlocked -= self._onSlotBlocked
        randomReservesEvents.onShownPanel -= self._updateLockedSlot
        super(EpicBattleConsumablesPanel, self)._removeListeners()
        return

    def _getPanelSettings(self):
        return CONSUMABLES_PANEL_SETTINGS.EPIC_BATTLE_SETTINGS_ID

    def _reset(self):
        super(EpicBattleConsumablesPanel, self)._reset()
        self.__battleReserveSlots.clear()

    def _updateEquipmentSlotTooltipText(self, idx, item):
        self.as_updateTooltipS(idx=idx, tooltipStr=self._getToolTipEquipmentSlot(item, idx))

    def _getKeyHandler(self, intCD, isEntityRequired, idx=0):
        return partial(self._handleEquipmentPressedStack, intCD, idx) if self.__epicController.hasBonusCap(BONUS_TYPE_CAPS.EPIC_RANDOM_RESERVES) and not isEntityRequired else super(EpicBattleConsumablesPanel, self)._getKeyHandler(intCD, isEntityRequired, idx)

    def _setKeyHandler(self, item, bwKey, idx):
        if item.getQuantity() > 0 and bwKey not in self._keys:
            if self.__epicController.hasBonusCap(BONUS_TYPE_CAPS.EPIC_RANDOM_RESERVES):
                handler = partial(self._handleEquipmentPressedStack, self._cds[idx], idx)
                self._keys[bwKey] = handler
            else:
                super(EpicBattleConsumablesPanel, self)._setKeyHandler(item, bwKey, idx)

    def _handleEquipmentPressedStack(self, intCD, idx):
        serverIdx = idx - self._ORDERS_START_IDX
        self._handleEquipmentPressed(intCD, idx=serverIdx)

    def _getToolTipEquipmentSlot(self, item, idx=None):
        return TOOLTIPS_CONSTANTS.FRONTLINE_RANDOM_RESERVE if self.__epicController.hasBonusCap(BONUS_TYPE_CAPS.EPIC_RANDOM_RESERVES) and not self._isEquipmentSlot(self.__currentSlotIdx if idx is None else idx) else super(EpicBattleConsumablesPanel, self)._getToolTipEquipmentSlot(item)

    def _getSlotIndex(self, index):
        return self._ORDERS_START_IDX + index

    def _onEquipmentAdded(self, intCD, item):
        if item and item.index > 0:
            index = item.index
            slotIndex = self._getSlotIndex(index - 1)
            self._addEquipmentSlot(slotIndex, intCD, item)
        else:
            super(EpicBattleConsumablesPanel, self)._onEquipmentAdded(intCD, item)

    def __addEquipmentSlotS(self, index, bwKey, sfKey, quantity, timeRemaining, reloadingTime, iconPath, tooltipText, animation):
        self.as_addEquipmentSlotS(idx=index, keyCode=bwKey, sfKeyCode=sfKey, quantity=quantity, timeRemaining=timeRemaining, reloadingTime=reloadingTime, iconPath=iconPath, tooltipText=tooltipText, animation=animation)

    def _onSlotBlocked(self, slotId):
        index = self._getSlotIndex(slotId)
        self.as_hideGlowS(index)
        self.as_resetS([index])
        bwKey, _ = self._genKey(slotId)
        self.__addEquipmentSlotS(index, bwKey, self.__EMPTY_SCALE_FORM_KEY, 0, 0, 0, '', self._getToolTipEquipmentSlot(None, slotId), ANIMATION_TYPES.NONE)
        return

    def _onSlotWaited(self, slotId, quantity):
        index = self._getSlotIndex(slotId)
        bwKey, sfKey = self._genKey(index)
        self.__addEquipmentSlotS(index, bwKey, sfKey, quantity + 1, 0, 0, getReserveIconPath('empty_slot'), '', ANIMATION_TYPES.NONE)
        if index not in self.__indicatedSlots:
            self.__addLockedInformationToEpicEquipment(index)

    def _addEquipmentSlot(self, idx, intCD, item):
        if item is None:
            return super(EpicBattleConsumablesPanel, self)._addEquipmentSlot(idx, intCD, item)
        else:
            if self.__epicController.hasBonusCap(BONUS_TYPE_CAPS.EPIC_RANDOM_RESERVES):
                self.as_hideGlowS(idx)
                self._updateEquipmentGlow(idx, item)
            self.__currentSlotIdx = idx
            quantity = item.getQuantity()
            descriptor = item.getDescriptor()
            if quantity > 1 and descriptor.equipmentType == EQUIPMENT_TYPES.battleAbilities:
                self.delayCallback(self._GLOW_DELAY, self.__possibleStacksDelayCB, idx, quantity)
                self.delayCallback(self._GLOW_DELAY + self._EQUIPMENT_GLOW_TIME, self.__stacksHideGrowDelayCB, idx)
            super(EpicBattleConsumablesPanel, self)._addEquipmentSlot(idx, intCD, item)
            if idx < self._ORDERS_START_IDX:
                return
            if idx not in self.__battleReserveSlots:
                self.__battleReserveSlots[idx] = (intCD, item.getQuantity())
                self.__addEquipmentLevelToSlot(idx, item)
            if not self.__epicController.hasBonusCap(BONUS_TYPE_CAPS.EPIC_RANDOM_RESERVES):
                self.__addLockedInformationToEpicEquipment(idx)
            return

    def _getEquipmentIcon(self, idx, item, icon):
        return backport.image(self._R_EPIC_EQUIPMENT_ICON.dyn(icon)()) if idx in self.__battleReserveSlots else super(EpicBattleConsumablesPanel, self)._getEquipmentIcon(idx, item, icon)

    def _resetEquipmentSlot(self, idx, intCD, item):
        super(EpicBattleConsumablesPanel, self)._resetEquipmentSlot(idx, intCD, item)
        if idx not in self.__battleReserveSlots:
            return
        self.__battleReserveSlots[idx] = (intCD, item.getQuantity())
        self.__addEquipmentLevelToSlot(idx, item)
        if item.getQuantity() > 0:
            self.__glowUpdateInfo[idx] = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_UPGRADE
            self.delayCallback(self._GLOW_DELAY, self.__updateEquipmentGlowCB)

    def __possibleStacksDelayCB(self, idx, quantity):
        self.as_showPossibleStacksS(idx, quantity)
        self.as_updateStacksS(idx, quantity)

    def __stacksHideGrowDelayCB(self, idx, opt=0):
        self.as_hideGlowS(idx)
        self.as_showPossibleStacksS(idx, 0)

    def _updateLockedSlot(self, slotId):
        index = self._getSlotIndex(slotId)
        self.as_updateLockedInformationS(index, self._EMPTY_LOCKED_SLOT, '')
        if index not in self.__indicatedSlots:
            self.__indicatedSlots.add(index)
            self.__glowUpdateInfo[index] = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL
            self.delayCallback(self._GLOW_DELAY, self.__updateEquipmentGlowCB)
            self.delayCallback(self._GLOW_DELAY + self._WAITED_SLOT_GLOW_TIME, self.__stacksHideGrowDelayCB, index)

    def _updateEquipmentSlot(self, idx, item):
        idx = item.index - 1 + self._ORDERS_START_IDX if item and item.index > 0 else idx
        super(EpicBattleConsumablesPanel, self)._updateEquipmentSlot(idx, item)
        if idx not in self.__battleReserveSlots:
            return
        _, prevQuantity = self.__battleReserveSlots[idx]
        quantity = item.getQuantity()
        if prevQuantity < quantity:
            self.as_updateLockedInformationS(idx, self._EMPTY_LOCKED_SLOT, '')
            self.__battleReserveSlots[idx] = (self._cds[idx], quantity)
            if quantity > 1:
                self.delayCallback(self._GLOW_DELAY, self.__possibleStacksDelayCB, idx, quantity)
                self.delayCallback(self._GLOW_DELAY + self._EQUIPMENT_GLOW_TIME, self.__stacksHideGrowDelayCB, idx)
                self.__glowUpdateInfo[idx] = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL
            else:
                self.__glowUpdateInfo[idx] = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_UNLOCK
            self.delayCallback(self._GLOW_DELAY, self.__updateEquipmentGlowCB)
        elif quantity < 1 and not self.__epicController.hasBonusCap(BONUS_TYPE_CAPS.EPIC_RANDOM_RESERVES):
            self.__addLockedInformationToEpicEquipment(idx)
        self.__addEquipmentLevelToSlot(idx, item)

    def __updateEquipmentGlowCB(self):
        for idx in self.__glowUpdateInfo:
            self.as_setGlowS(idx, self.__glowUpdateInfo[idx])

        self.__glowUpdateInfo.clear()

    def _onEquipmentReset(self, oldIntCD, intCD, item):
        index = item.index - 1 + self._ORDERS_START_IDX if item and item.index > 0 else -1
        if index >= 0:
            self._resetEquipmentSlot(index, intCD, item)
        else:
            super(EpicBattleConsumablesPanel, self)._onEquipmentReset(oldIntCD, intCD, item)

    def __addLockedInformationToEpicEquipment(self, idx):
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        playerDataComp = getattr(componentSystem, 'playerDataComponent', None)
        vehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if not all((playerDataComp, vehicle, arena)):
            return
        else:
            vehClass = getVehicleClassFromVehicleType(vehicle.typeDescriptor.type)
            if self.__epicController.hasBonusCap(BONUS_TYPE_CAPS.EPIC_RANDOM_RESERVES):
                slotEventsConfig = [[0],
                 [1],
                 [2],
                 [],
                 [],
                 []]
            else:
                slotEventsConfig = arena.settings.get('epic_config', {}).get('epicMetaGame', {}).get('inBattleReservesByRank').get('slotActions', {}).get(vehClass, {})
                if not slotEventsConfig:
                    return
            unlockedSlotIdx = idx - self._ORDERS_START_IDX
            rank = searchRankForSlot(unlockedSlotIdx, slotEventsConfig)
            currentRank = playerDataComp.playerRank if playerDataComp.playerRank is not None else 0
            if rank is None or rank <= currentRank - 1:
                return
            rank += 1
            tooltipId = TOOLTIPS_CONSTANTS.EPIC_RANK_UNLOCK_INFO if rank > 1 or self.__epicController.hasBonusCap(BONUS_TYPE_CAPS.EPIC_RANDOM_RESERVES) else ''
            self.as_updateLockedInformationS(idx, rank, tooltipId)
            return

    def __addEquipmentLevelToSlot(self, idx, item):
        itemName = item.getDescriptor().name
        if 'level' not in itemName:
            return
        levelStr = itemName.partition('level')[-1]
        if not levelStr.isdigit():
            return
        if self.__sessionProvider.isReplayPlaying:
            randomReservesEvents.onSelectedReserve(item.getDescriptor().compactDescr, False)
        self.as_updateLevelInformationS(idx, int(levelStr))

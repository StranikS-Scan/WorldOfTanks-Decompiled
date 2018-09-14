# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event_mark1/consumables_panel.py
from gui.battle_control import g_sessionProvider
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from helpers.i18n import makeString
from gui.Scaleform.daapi.view.meta.EventConsumablesPanelMeta import EventConsumablesPanelMeta
from gui.battle_control.controllers.event_mark1.bonus_ctrl import EXTRA_BIG_GUN, EXTRA_MACHINE_GUN
_AMMO_BIG_GUN_ICON = '../maps/icons/ammopanel/battle_ammo/HIGH_EXPLOSIVE.png'
_AMMO_MACHINE_GUN_ICON = '../maps/icons/ammopanel/battle_ammo/ARMOR_PIERCING.png'
_FIRST_SLOT_IDX = 0
_SECOND_SLOT_IDX = 1

class Mark1ConsumablesPanel(EventConsumablesPanelMeta):
    """
    In Mark1 event only one shell is always available
    """

    def __init__(self):
        super(Mark1ConsumablesPanel, self).__init__()
        self.__playerVehicleID = 0
        self.__firstTooltip = ''
        self.__bigGunTooltip = ''

    def _populate(self):
        super(Mark1ConsumablesPanel, self)._populate()
        arenaDP = g_sessionProvider.getCtx().getArenaDP()
        self.__playerVehicleID = arenaDP.getPlayerVehicleID()
        bonusCtrl = g_sessionProvider.dynamic.mark1Bonus
        if bonusCtrl is not None:
            bonusCtrl.onBonusBigGunTaken += self.__onBonusBigGunTaken
            bonusCtrl.onBonusMachineGunTaken += self.__onBonusMachineGunTaken
            bonusCtrl.onBonusEnded += self.__onBonusEnded
            bonus = bonusCtrl.getVehicleBonus(self.__playerVehicleID)
            if bonus == EXTRA_BIG_GUN:
                self.__onBonusBigGunTaken(self.__playerVehicleID)
                self.__updateQuantityFirstSlot()
            elif bonus == EXTRA_MACHINE_GUN:
                self.__onBonusMachineGunTaken(self.__playerVehicleID)
                self.__updateQuantityFirstSlot()
        return

    def _dispose(self):
        bonusCtrl = g_sessionProvider.dynamic.mark1Bonus
        if bonusCtrl is not None:
            bonusCtrl.onBonusBigGunTaken -= self.__onBonusBigGunTaken
            bonusCtrl.onBonusMachineGunTaken -= self.__onBonusMachineGunTaken
            bonusCtrl.onBonusEnded -= self.__onBonusEnded
        super(Mark1ConsumablesPanel, self)._dispose()
        return

    def as_addShellSlotS(self, idx, keyCode, sfKeyCode, quantity, clipCapacity, shellIconPath, noShellIconPath, tooltipText):
        if idx == _FIRST_SLOT_IDX:
            self.__firstTooltip = tooltipText
            super(Mark1ConsumablesPanel, self).as_addShellSlotS(idx, keyCode, sfKeyCode, quantity, clipCapacity, shellIconPath, noShellIconPath, tooltipText)
        elif idx == _SECOND_SLOT_IDX:
            self.__bigGunTooltip = tooltipText

    def as_setItemQuantityInSlotS(self, idx, quantity):
        super(Mark1ConsumablesPanel, self).as_setItemQuantityInSlotS(_FIRST_SLOT_IDX, quantity)

    def as_setNextShellS(self, idx):
        super(Mark1ConsumablesPanel, self).as_setNextShellS(_FIRST_SLOT_IDX)

    def as_setCurrentShellS(self, idx):
        super(Mark1ConsumablesPanel, self).as_setCurrentShellS(_FIRST_SLOT_IDX)
        if idx == _FIRST_SLOT_IDX:
            self.__updateQuantityFirstSlot()

    def as_setCoolDownTimeS(self, idx, timeRemaining):
        super(Mark1ConsumablesPanel, self).as_setCoolDownTimeS(_FIRST_SLOT_IDX, timeRemaining)

    def as_setCoolDownPosAsPercentS(self, idx, percent):
        super(Mark1ConsumablesPanel, self).as_setCoolDownPosAsPercentS(_FIRST_SLOT_IDX, percent)

    def _ConsumablesPanel__handleAmmoPressed(self, intCD):
        pass

    def __onBonusBigGunTaken(self, vehicleID):
        if vehicleID == self.__playerVehicleID:
            self.as_updateBonusNotificationS(True, self.__getBonusString(INGAME_GUI.MARK1_BONUS_BIGSIZE_BIGGUN), _AMMO_BIG_GUN_ICON, self.__bigGunTooltip)

    def __onBonusMachineGunTaken(self, vehicleID):
        if vehicleID == self.__playerVehicleID:
            self.as_updateBonusNotificationS(True, self.__getBonusString(INGAME_GUI.MARK1_BONUS_BIGSIZE_MACHINEGUN), _AMMO_MACHINE_GUN_ICON, self.__firstTooltip)

    def __getBonusString(self, strId):
        return '<font size="14">' + makeString(INGAME_GUI.MARK1_BONUS_HEADER) + '</font><br/><font size="18">' + makeString(strId) + '</font>'

    def __onBonusEnded(self, vehicleID):
        if vehicleID == self.__playerVehicleID:
            self.as_updateBonusNotificationS(False, '', _AMMO_MACHINE_GUN_ICON, self.__firstTooltip)
            self.__updateQuantityFirstSlot()

    def __updateQuantityFirstSlot(self):
        ammoCtrl = g_sessionProvider.shared.ammo
        if ammoCtrl is not None:
            quantity, _ = ammoCtrl.getCurrentShells()
            self.as_setItemQuantityInSlotS(_FIRST_SLOT_IDX, quantity)
        return

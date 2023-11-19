# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/battle/battle_upgrade_panel.py
import BigWorld
import WWISE
from ReservesEvents import randomReservesEvents
from frontline.gui.frontline_helpers import getReserveIconPath, getHotKeyListByIndex, getHotKeyVkListByIndex
from aih_constants import CTRL_MODE_NAME
from constants import UpgradeProhibitionReason
from frontline.gui.sounds.sound_constants import FL_BATTLE_UPGRADE_PANEL_SOUND_EVENTS
from gui.Scaleform.daapi.view.meta.EpicBattleUpgradePanelMeta import EpicBattleUpgradePanelMeta
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency, i18n
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IEpicBattleMetaGameController

class _AttentionEffectPlayer(object):
    __slots__ = ('__viewRef', '__callbackID', '__delayTime', '__isPlaying')
    __UPGRADE_ATTENTION_TIME = 10

    def __init__(self, viewRef):
        super(_AttentionEffectPlayer, self).__init__()
        self.__viewRef = viewRef
        self.__callbackID = None
        self.__delayTime = self.__UPGRADE_ATTENTION_TIME
        self.__isPlaying = False
        return

    def setVisible(self, visible):
        if visible:
            self.playSound(FL_BATTLE_UPGRADE_PANEL_SOUND_EVENTS.UPGRADE_PANEL_SHOW)
            if self.__callbackID is not None or self.__isPlaying:
                self.__stopEffect()
            self.__startTimer()
        else:
            self.playSound(FL_BATTLE_UPGRADE_PANEL_SOUND_EVENTS.UPGRADE_PANEL_HIDE)
            self.__stopEffect()
        return

    @staticmethod
    def playSound(eventName):
        WWISE.WW_eventGlobal(eventName)

    def destroy(self):
        self.__viewRef = None
        self.__disposeTimer()
        return

    def __startTimer(self):
        self.__callbackID = BigWorld.callback(self.__delayTime, self.__onDelayFinished)

    def __disposeTimer(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __stopAnimation(self):
        if self.__isPlaying:
            self.__viewRef.as_hideNotificationAnimS()
            self.__isPlaying = False

    def __stopEffect(self):
        self.__disposeTimer()
        self.__stopAnimation()

    def __onDelayFinished(self):
        self.__callbackID = None
        self.__isPlaying = True
        self.__viewRef.as_showNotificationAnimS()
        return


class EpicBattleUpgradePanel(EpicBattleUpgradePanelMeta, IArenaVehiclesController):
    __slots__ = ('__attentionEffect', '__offer', '__cooldownID', '__showCooldownID', '__canSelect', '__canShowNextTime', '__isInGameMessage', '__lastStatus')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __FIRST_OFFER_INDEX = 0
    __SECOND_OFFER_INDEX = 1
    __TIME_WAITING_MESSAGE = 1

    def __init__(self):
        super(EpicBattleUpgradePanel, self).__init__()
        self.__attentionEffect = _AttentionEffectPlayer(self)
        self.__offer = []
        self.__cooldownID = None
        self.__showCooldownID = None
        self.__canSelect = False
        self.__canShowNextTime = True
        self.__isInGameMessage = False
        self.__lastStatus = False
        self.__slotIdx = None
        self.__prevCamera = None
        return

    def onSelectItem(self, itemID):
        if self.__canSelect:
            self.__attentionEffect.playSound(FL_BATTLE_UPGRADE_PANEL_SOUND_EVENTS.ON_SELECT)
            self.as_showSelectAnimS(self.__FIRST_OFFER_INDEX if self.__offer[self.__FIRST_OFFER_INDEX] == itemID else self.__SECOND_OFFER_INDEX)
            self.setVisible(False)
            BigWorld.player().cell.setupRandomAmmo(itemID)
            self.__canSelect = False
            self.__offer = []
            if self.__hasInstalledStackReserve() and self.__epicController.isReserveStack(self.__getEquipmentByIntCD(itemID).extraName()):
                self.__attentionEffect.playSound(FL_BATTLE_UPGRADE_PANEL_SOUND_EVENTS.ON_SELECT_STACK_RESERVE)

    def _populate(self):
        super(EpicBattleUpgradePanel, self)._populate()
        randomReservesEvents.onShowPanel += self.__onShowReservePanel
        randomReservesEvents.onSelectedReserve += self.__selectedReserve
        randomReservesEvents.onUpdate += self.__onUpdateReservePanel
        randomReservesEvents.hidePanel += self.__hidePanel
        randomReservesEvents.showPanel += self.__showPanel
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            player.inputHandler.onCameraChanged += self.__onCameraChanged
        return

    def _dispose(self):
        randomReservesEvents.onShowPanel -= self.__onShowReservePanel
        randomReservesEvents.onSelectedReserve -= self.__selectedReserve
        randomReservesEvents.onUpdate -= self.__onUpdateReservePanel
        randomReservesEvents.hidePanel -= self.__hidePanel
        randomReservesEvents.showPanel -= self.__showPanel
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            player.inputHandler.onCameraChanged -= self.__onCameraChanged
        self.__stopPreviousTimer()
        self.__stopPreviousShowTimer()
        self.__sessionProvider.removeArenaCtrl(self)
        self.__attentionEffect.destroy()
        self.__attentionEffect = None
        super(EpicBattleUpgradePanel, self)._dispose()
        return

    def __stopPreviousShowTimer(self):
        if self.__showCooldownID is not None:
            BigWorld.cancelCallback(self.__showCooldownID)
            self.__showCooldownID = None
        return

    def setVisible(self, status):
        if self.__hasOffer() and self.__lastStatus != status:
            self.__attentionEffect.setVisible(status)
            self.as_setVisibleS(status)
            self.__lastStatus = status
            if status:
                randomReservesEvents.onShownPanel(self.__slotIdx)
                self.__canSelect = True

    def __onCameraChanged(self, cameraName, _=None):
        if cameraName == CTRL_MODE_NAME.ARCADE and self.__prevCamera:
            self.__enablePanel()
        elif cameraName in [CTRL_MODE_NAME.MAP_CASE_EPIC, CTRL_MODE_NAME.MAP_CASE, CTRL_MODE_NAME.MAP_CASE_ARCADE_EPIC_MINEFIELD]:
            self.__disablePanel()
        self.__prevCamera = cameraName

    def __hidePanel(self, isInGameMessage=False):
        self.__isInGameMessage = isInGameMessage
        self.__canSelect = False
        self.setVisible(False)
        self.__stopPreviousShowTimer()

    def __show(self):
        self.setVisible(True)
        self.__stopPreviousShowTimer()
        self.__isInGameMessage = False

    def __showPanel(self):
        if self.__canShowNextTime:
            self.__stopPreviousShowTimer()
            self.__showCooldownID = BigWorld.callback(self.__TIME_WAITING_MESSAGE, self.__show)

    def __disablePanel(self):
        self.__canSelect = False
        self.as_toggleAlertStateS(True, backport.text(self.__getR().alert()))

    def __enablePanel(self):
        self.__cooldownID = None
        self.__canSelect = True
        self.as_toggleAlertStateS(False)
        return

    def __stopPreviousTimer(self):
        if self.__cooldownID is not None:
            BigWorld.cancelCallback(self.__cooldownID)
            self.__cooldownID = None
        return

    def __setCooldown(self, cooldownTime, reason):
        if cooldownTime > 0:
            self.__disablePanel()
            self.__stopPreviousTimer()
            self.__cooldownID = BigWorld.callback(cooldownTime, self.__enablePanel)

    @staticmethod
    def __getR():
        return R.strings.fl_upgrade_panel

    @staticmethod
    def __getEquipmentByIntCD(intCD):
        equipments = vehicles.g_cache.equipments()
        _, _, equipmentID = vehicles.parseIntCompactDescr(intCD)
        return equipments[equipmentID]

    def __getInstalledEquipments(self):
        return self.__sessionProvider.shared.equipments.getOrderedEquipments()

    def __getShortDescription(self, equipment):
        techName = self.__epicController.getReserveTechName(equipment.extraName())
        return backport.text(self.__getR().shortDescription.reserve.dyn(techName)()) if techName else ''

    def __getReserveInfo(self, equipment, level, index):
        category = self.__epicController.getReserveCategory(equipment.extraName())
        reserveInfo = {'header': i18n.makeString(equipment.userString),
         'description': self.__getShortDescription(equipment),
         'module': {'icon': getReserveIconPath(equipment.iconName),
                    'intCD': equipment.compactDescr,
                    'level': level,
                    'available': True},
         'category': category,
         'hotKeys': getHotKeyListByIndex(index),
         'hotKeysVKeys': getHotKeyVkListByIndex(index)}
        return reserveInfo

    def __getDescription(self, firstEquipment, secondEquipment):
        description = ''
        isFirstStack = self.__epicController.isReserveStack(firstEquipment.extraName())
        isSecondStack = self.__epicController.isReserveStack(secondEquipment.extraName())
        if self.__hasInstalledStackReserve() and (isFirstStack or isSecondStack):
            isSecondInstalled = self.__isReserveInstalled(secondEquipment)
            isFirstInstalled = self.__isReserveInstalled(firstEquipment)
            if isFirstInstalled and isFirstStack and isSecondInstalled and isSecondStack:
                return backport.text(self.__getR().description.second.reserve(), first_reserve_name=firstEquipment.userString, second_reserve_name=secondEquipment.userString)
            if isFirstInstalled and isFirstStack or isSecondInstalled and isSecondStack:
                return backport.text(self.__getR().description.one.reserve(), reserve_name=firstEquipment.userString if isFirstInstalled else secondEquipment.userString)
        return description

    def __getNumberName(self, number):
        return backport.text(self.__getR().dyn('number_{}'.format(number))())

    def __hasOffer(self):
        return bool(self.__offer)

    def __selectedReserve(self, value, isIndex=True):
        if self.__hasOffer():
            self.onSelectItem(self.__offer[value] if isIndex else value)

    def __onUpdateReservePanel(self, cooldownTime, reason):
        if reason == UpgradeProhibitionReason.COMBATING:
            self.__setCooldown(cooldownTime, reason)
        else:
            self.__canShowNextTime = False
            self.__hidePanel()

    def __onShowReservePanel(self, offer, level, slotIdx):
        if not offer:
            return
        self.__slotIdx = slotIdx
        self.__offer = offer
        firstOfferReserve, secondOfferReserve = offer
        firstOfferReserveLevel, secondOfferReserveLevel = level
        firstEquipment = self.__getEquipmentByIntCD(firstOfferReserve)
        secondEquipment = self.__getEquipmentByIntCD(secondOfferReserve)
        description = self.__getDescription(firstEquipment, secondEquipment)
        data = {'firstItem': self.__getReserveInfo(firstEquipment, firstOfferReserveLevel, self.__FIRST_OFFER_INDEX),
         'secondItem': self.__getReserveInfo(secondEquipment, secondOfferReserveLevel, self.__SECOND_OFFER_INDEX),
         'title': backport.text(self.__getR().title(), number_name=self.__getNumberName(slotIdx + 1)),
         'description': description,
         'isInitData': True}
        self.as_setDataS(data)
        if not self.__isInGameMessage:
            self.__showPanel()

    def __hasInstalledStackReserve(self):
        return any([ self.__epicController.isReserveStack(e.getDescriptor().extraName()) for e in self.__getInstalledEquipments() ])

    def __isReserveInstalled(self, equipment):
        return any([ e.getDescriptor().iconName == equipment.iconName for e in self.__getInstalledEquipments() ])

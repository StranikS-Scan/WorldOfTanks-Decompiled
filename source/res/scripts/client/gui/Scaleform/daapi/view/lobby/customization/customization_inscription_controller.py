# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_inscription_controller.py
import SoundGroups
from account_helpers.AccountSettings import AccountSettings, CUSTOMIZATION_SECTION
from gui import makeHtmlString
from gui import SystemMessages
from gui.customization.shared import C11nId
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.Scaleform.daapi.view.lobby.customization.shared import SEASON_TYPE_TO_INFOTYPE_MAP, formatPersonalNumber, fitPersonalNumber
from gui.Scaleform.daapi.view.lobby.customization.sound_constants import SOUNDS
from gui.Scaleform.daapi.view.meta.CustomizationInscriptionControllerMeta import CustomizationInscriptionControllerMeta
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.Scaleform.locale.READABLE_KEY_NAMES import READABLE_KEY_NAMES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared import g_eventBus
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from items.components.c11n_components import isPersonalNumberAllowed
from helpers.i18n import makeString as _ms
from skeletons.gui.customization import ICustomizationService
_ERROR_ICON_DESC = {'image': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_INSCRIPTION_CONTROLLER_ICON_ERROR}
_ENTER_ICON_DESC = {'image': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_INSCRIPTION_CONTROLLER_ENTER_BTN}
_BACKSPACE_ICON_DESC = {'image': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_INSCRIPTION_CONTROLLER_BSPACE_BTN}
_DEL_ICON_DESC = {'text': READABLE_KEY_NAMES.KEY_DELETE}
_PRESS_ENTER_HINT_SHOWN_FIELD = 'isPressEnterHintShown'
_ENTER_NUMBER_HINT_SHOWN_FIELD = 'isEnterNumberHintShown'
_DEFAULT_HINT_DURATION = 3000
_DEFAULT_HINT_DELAY = 3000
_EMPTY_NUMBER = ''

class CustomizationInscriptionController(CustomizationInscriptionControllerMeta, CallbackDelayer):
    service = dependency.descriptor(ICustomizationService)

    def __init__(self):
        CustomizationInscriptionControllerMeta.__init__(self)
        CallbackDelayer.__init__(self)
        self.__shownNumber = _EMPTY_NUMBER
        self.__ctx = None
        self.__isProhibitedHintShown = False
        self.__visible = False
        self.__digitsCount = 3
        self.__attachedAnchor = C11nId()
        self.__clearedNumber = None
        return

    def _populate(self):
        self.__ctx = self.service.getCtx()
        self.__ctx.onPersonalNumberCleared += self.__onPersonalNumberCleared
        g_eventBus.addListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)

    def _dispose(self):
        self.__ctx.onPersonalNumberCleared -= self.__onPersonalNumberCleared
        g_eventBus.removeListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)
        self.__ctx = None
        return

    @property
    def visible(self):
        return self.__visible

    @property
    def _digitsCount(self):
        return self.__digitsCount

    @_digitsCount.setter
    def _digitsCount(self, digitsCount):
        if self.__digitsCount == digitsCount:
            return
        self.__digitsCount = digitsCount
        if self.visible:
            self.as_showS(self._digitsCount)

    def handleLobbyClick(self):
        if self.visible:
            self.finish(cancelIfEmpty=True)
            return True
        return False

    def handleEscBtn(self):
        if self.visible:
            self.cancel()
            return True
        return False

    def handleDelBtn(self):
        return True if self.visible else False

    def show(self, anchor):
        self.__attachedAnchor = anchor
        self.__prohibitedHintShown(False)
        self.stopCallback(self.__prohibitedHintShown)
        self.as_showS(self._digitsCount)
        self.__visible = True
        self.__ctx.vehicleAnchorsUpdater.displayLine(True)
        self.__shownNumber = _EMPTY_NUMBER
        if self.__clearedNumber is not None:
            self.__showProhibitedHint(self.__clearedNumber)
        else:
            self.__showPromptHint()
        self.__ctx.changePersonalNumberValue(self.__shownNumber)
        self.__ctx.onEditModeStarted()
        return

    def hide(self):
        if not self.visible:
            return
        self.__visible = False
        self.as_hideS()
        self.__shownNumber = _EMPTY_NUMBER
        self.__ctx.vehicleAnchorsUpdater.displayLine(False)
        self.__ctx.c11CameraManager.enableMovementByMouse()
        self.__ctx.onEditModeFinished()

    def update(self, anchor):
        slotId = self.__ctx.getSlotIdByAnchorId(anchor)
        if slotId is not None:
            item = self.__ctx.getItemFromRegion(slotId)
            component = self.__ctx.getComponentFromRegion(slotId)
        else:
            self.hide()
            return
        if item is not None and item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER:
            self._digitsCount = item.digitsCount
        else:
            self.hide()
            return
        if self.visible:
            if item.digitsCount <= len(self.__shownNumber):
                number = fitPersonalNumber(self.__shownNumber, item.digitsCount)
                if isPersonalNumberAllowed(number):
                    self.__shownNumber = number
                else:
                    self.__shownNumber = _EMPTY_NUMBER
                    self.__showProhibitedHint(number)
            if self.__ctx.storedPersonalNumber is not None:
                storedNumber = fitPersonalNumber(self.__ctx.storedPersonalNumber, item.digitsCount)
                self.__ctx.storePersonalNumber(storedNumber)
            self.__ctx.changePersonalNumberValue(self.__shownNumber, slotId)
            return
        elif not component.isFilled():
            self.show(anchor)
            return
        else:
            if len(component.number) != item.digitsCount:
                number = fitPersonalNumber(component.number, item.digitsCount)
                number = formatPersonalNumber(number, item.digitsCount)
                if isPersonalNumberAllowed(number):
                    self.__ctx.changePersonalNumberValue(number, slotId)
                    component.number = number
                    self.__ctx.storePersonalNumber(number, item.digitsCount)
                else:
                    self.__ctx.clearStoredPersonalNumber()
                    self.show(anchor)
                    self.__showProhibitedHint(number)
            return

    def sendChar(self, char):
        if len(self.__shownNumber) == self._digitsCount:
            SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_NUMBER_OVER)
            self.__showEditHint()
            return
        newNumber = self.__shownNumber + char
        if len(newNumber) == self._digitsCount and not isPersonalNumberAllowed(newNumber):
            self.__showProhibitedHint(newNumber)
        else:
            self.__shownNumber = newNumber
            self.__ctx.changePersonalNumberValue(self.__shownNumber)
            SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_NUMBER)
            if len(self.__shownNumber) == self._digitsCount:
                self.__showConfirmitionHint()
            else:
                self.__showPromptHint()
        self.__manageCamera()

    def removeChar(self):
        SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_BACKSPACE)
        self.__shownNumber = self.__shownNumber[:-1]
        self.__ctx.changePersonalNumberValue(self.__shownNumber)
        self.__showPromptHint()
        self.__manageCamera()

    def deleteAll(self):
        SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_DELETE)
        self.__shownNumber = _EMPTY_NUMBER
        self.__ctx.changePersonalNumberValue(self.__shownNumber)

    def finish(self, cancelIfEmpty=False, removeProhibited=False):
        if not self.visible:
            return
        if self.__shownNumber == _EMPTY_NUMBER:
            if cancelIfEmpty:
                self.cancel(removeProhibited)
            else:
                self.__showPromptHint(showImmediately=True)
            return
        newNumber = formatPersonalNumber(self.__shownNumber, self._digitsCount)
        if not isPersonalNumberAllowed(newNumber):
            if removeProhibited:
                slotId = self.__ctx.getSlotIdByAnchorId(self.__attachedAnchor)
                item = self.__ctx.getItemFromRegion(slotId)
                self.__showProhibitedNumberSystemMsg(item, newNumber)
                self.__ctx.removeItemFromSlot(self.__ctx.currentSeason, slotId)
            else:
                if self.__isProhibitedHintShown:
                    return
                self.__prohibitedHintShown(True)
                self.__showProhibitedHint(newNumber)
                self.delayCallback(_DEFAULT_HINT_DURATION * 0.001, self.__prohibitedHintShown, value=False)
        else:
            SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_ENTER)
            slotId = self.__ctx.getSlotIdByAnchorId(self.__attachedAnchor)
            self.__ctx.changePersonalNumberValue(newNumber, slotId)
            self.__ctx.clearStoredPersonalNumber()
            self.hide()

    def cancel(self, removeProhibited=False):
        if not self.visible:
            return
        else:
            slotId = self.__ctx.getSlotIdByAnchorId(self.__attachedAnchor)
            item = self.__ctx.getItemFromRegion(slotId)
            SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_ESC)
            if item is not None and item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER:
                if self.__ctx.storedPersonalNumber is not None:
                    storedNumber = fitPersonalNumber(self.__ctx.storedPersonalNumber, item.digitsCount)
                    storedNumber = formatPersonalNumber(storedNumber, item.digitsCount)
                    if isPersonalNumberAllowed(storedNumber):
                        self.__ctx.changePersonalNumberValue(storedNumber, slotId)
                        self.__ctx.clearStoredPersonalNumber()
                    elif removeProhibited:
                        self.__showProhibitedNumberSystemMsg(item, storedNumber)
                        self.__ctx.removeItemFromSlot(self.__ctx.currentSeason, slotId)
                    else:
                        self.__shownNumber = _EMPTY_NUMBER
                        self.__ctx.changePersonalNumberValue(self.__shownNumber, slotId)
                        self.__showProhibitedHint(storedNumber)
                        self.__ctx.clearStoredPersonalNumber()
                        return
                else:
                    self.__ctx.removeItemFromSlot(self.__ctx.currentSeason, slotId)
            self.hide()
            return

    def __handleLobbyViewMouseEvent(self, event):
        if self.visible:
            ctx = event.ctx
            if ctx['dx'] or ctx['dy']:
                self.finish(cancelIfEmpty=True)

    def __manageCamera(self):
        isCameraRotationEnabled = True
        if self.visible:
            formattedNumber = formatPersonalNumber(self.__shownNumber, self._digitsCount)
            isCameraRotationEnabled = isPersonalNumberAllowed(formattedNumber)
        self.__ctx.c11CameraManager.enableMovementByMouse(enableRotation=isCameraRotationEnabled)

    def __prohibitedHintShown(self, value):
        self.__isProhibitedHintShown = value

    def __showProhibitedNumberSystemMsg(self, item, number):
        seasonName = _ms(SEASON_TYPE_TO_INFOTYPE_MAP[self.__ctx.currentSeason])
        msg = _ms(SYSTEM_MESSAGES.CUSTOMIZATION_PERSONAL_NUMBER_PROHIBITED, value=text_styles.critical(number), itemType=item.userType, itemName=item.userName, seasonName=seasonName)
        msgType = SystemMessages.SM_TYPE.Error
        SystemMessages.pushMessage(msg, msgType)

    def __showProhibitedHint(self, number):
        if self.__clearedNumber == number:
            self.__clearedNumber = None
        message = makeHtmlString('html_templates:lobby/customization', 'inscription_hint', {'value': number})
        icons = [_ERROR_ICON_DESC]
        hintVO = self.__getHintVO(message, icons=icons, duration=_DEFAULT_HINT_DURATION)
        self.as_invalidInscriptionS(hintVO)
        return

    def __showEditHint(self):
        message = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_INSCRIPTIONCONTROLLER_EDIT_BUTTONS
        icons = [_BACKSPACE_ICON_DESC, _DEL_ICON_DESC]
        hintVO = self.__getHintVO(message, icons=icons, duration=_DEFAULT_HINT_DURATION)
        self.as_showHintS(hintVO)

    def __showConfirmitionHint(self):
        message = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_INSCRIPTIONCONTROLLER_ENTRY_COMPLETED
        icons = [_ENTER_ICON_DESC]
        hintDelay, hintDuration = self.__calcHintTimings(_PRESS_ENTER_HINT_SHOWN_FIELD)
        hintVO = self.__getHintVO(message, icons=icons, duration=hintDuration, delay=hintDelay)
        self.as_showHintS(hintVO)

    def __showPromptHint(self, showImmediately=False):
        message = _ms(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_INSCRIPTIONCONTROLLER_PROMPT, start=formatPersonalNumber('1', self._digitsCount), end='9' * self._digitsCount)
        if showImmediately:
            delay, duration = 0, _DEFAULT_HINT_DURATION
        else:
            delay, duration = self.__calcHintTimings(_ENTER_NUMBER_HINT_SHOWN_FIELD)
        hintVO = self.__getHintVO(message, duration=duration, delay=delay)
        self.as_showHintS(hintVO)

    def __getHintVO(self, hintMessage, icons=None, duration=0, delay=0):
        return {'hintMessage': hintMessage,
         'icons': icons,
         'duration': duration,
         'delay': delay}

    def __onPersonalNumberCleared(self, number):
        self.__clearedNumber = number

    @staticmethod
    def __calcHintTimings(accountSettingName):
        hintDuration = _DEFAULT_HINT_DURATION
        hintDelay = _DEFAULT_HINT_DELAY
        custSett = AccountSettings.getSettings(CUSTOMIZATION_SECTION)
        if not custSett.get(accountSettingName, False):
            hintDuration = 0
            hintDelay = 0
            custSett[accountSettingName] = True
            AccountSettings.setSettings(CUSTOMIZATION_SECTION, custSett)
        return (hintDelay, hintDuration)

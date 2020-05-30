# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_inscription_controller.py
import SoundGroups
from account_helpers.AccountSettings import AccountSettings, CUSTOMIZATION_SECTION
from gui import SystemMessages
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.customization.shared import SEASON_TYPE_TO_INFOTYPE_MAP, formatPersonalNumber, fitPersonalNumber, EMPTY_PERSONAL_NUMBER
from gui.Scaleform.daapi.view.lobby.customization.sound_constants import SOUNDS
from gui.Scaleform.daapi.view.meta.CustomizationInscriptionControllerMeta import CustomizationInscriptionControllerMeta
from gui.Scaleform.locale.READABLE_KEY_NAMES import READABLE_KEY_NAMES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.shared import g_eventBus
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.i18n import makeString as _ms
from items.components.c11n_components import isPersonalNumberAllowed
from items.customizations import PersonalNumberComponent
from skeletons.gui.customization import ICustomizationService
_ERROR_ICON_DESC = {'image': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_INSCRIPTION_CONTROLLER_ICON_ERROR}
_ENTER_ICON_DESC = {'image': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_INSCRIPTION_CONTROLLER_ENTER_BTN}
_BACKSPACE_ICON_DESC = {'image': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_INSCRIPTION_CONTROLLER_BSPACE_BTN}
_DEL_ICON_DESC = {'text': READABLE_KEY_NAMES.KEY_DELETE}
_PRESS_ENTER_HINT_SHOWN_FIELD = 'isPressEnterHintShown'
_ENTER_NUMBER_HINT_SHOWN_FIELD = 'isEnterNumberHintShown'
_DEFAULT_HINT_DURATION = 3000
_DEFAULT_HINT_DELAY = 3000

class CustomizationInscriptionController(CustomizationInscriptionControllerMeta, CallbackDelayer):
    service = dependency.descriptor(ICustomizationService)

    def __init__(self):
        CustomizationInscriptionControllerMeta.__init__(self)
        CallbackDelayer.__init__(self)
        self.__currentNumber = None
        self.__ctx = None
        self.__isProhibitedHintShown = False
        self.__visible = False
        self.__digitsCount = 3
        self.__slotId = None
        self.__storedNumber = None
        self.__clearedNumber = None
        return

    def _populate(self):
        self.__ctx = self.service.getCtx()
        self.__ctx.events.onPersonalNumberCleared += self.__onPersonalNumberCleared
        g_eventBus.addListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)

    def _dispose(self):
        self.__ctx.events.onPersonalNumberCleared -= self.__onPersonalNumberCleared
        g_eventBus.removeListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)
        self.__ctx = None
        return

    @property
    def visible(self):
        return self.__visible

    @property
    def _component(self):
        if self.__slotId is None:
            return
        else:
            component = self.__ctx.mode.getComponentFromSlot(self.__slotId)
            if component is None:
                return
            return None if component.customType != PersonalNumberComponent.customType else component

    @property
    def _digitsCount(self):
        return self.__digitsCount

    @_digitsCount.setter
    def _digitsCount(self, digitsCount):
        if self.__digitsCount == digitsCount:
            return
        else:
            self.__digitsCount = digitsCount
            if self.visible and self._digitsCount is not None:
                self.as_showS(self._digitsCount)
            self.__manageCamera()
            return

    @property
    def _currentNumber(self):
        return self.__currentNumber

    @_currentNumber.setter
    def _currentNumber(self, number):
        if not self.visible:
            return
        elif self.__currentNumber == number:
            return
        elif self._component is None:
            return
        else:
            self.__currentNumber = number
            self._component.number = self.__currentNumber
            self.__ctx.refreshOutfit()
            self.__manageCamera()
            self.__ctx.events.onComponentChanged(self.__slotId, False)
            return

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

    def start(self, slotId):
        item = self.__ctx.mode.getItemFromSlot(slotId)
        if item is None or item.itemTypeID != GUI_ITEM_TYPE.PERSONAL_NUMBER:
            return
        else:
            self.__slotId = slotId
            self._digitsCount = item.digitsCount
            self._currentNumber = EMPTY_PERSONAL_NUMBER
            component = self.__ctx.mode.getComponentFromSlot(slotId)
            if component is not None and component.isFilled():
                self.__storedNumber = component.number
            self.show()
            return

    def finish(self, cancelIfEmpty=False):
        if not self.visible:
            return
        if self._currentNumber == EMPTY_PERSONAL_NUMBER:
            if cancelIfEmpty:
                self.cancel()
            else:
                self.__showPromptHint(showImmediately=True)
            return
        newNumber = formatPersonalNumber(self._currentNumber, self._digitsCount)
        if isPersonalNumberAllowed(newNumber):
            SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_ENTER)
            self._currentNumber = newNumber
            self.hide()
        elif not self.__isProhibitedHintShown:
            self.__prohibitedHintShown(True)
            self.__showProhibitedHint(newNumber)
            self.delayCallback(_DEFAULT_HINT_DURATION * 0.001, lambda : self.__prohibitedHintShown(False))

    def cancel(self):
        if not self.visible:
            return
        else:
            if self.__storedNumber is None:
                self.hide()
                self.__ctx.mode.removeItem(self.__slotId)
            else:
                newNumber = fitPersonalNumber(self.__storedNumber, self._digitsCount)
                newNumber = formatPersonalNumber(newNumber, self._digitsCount)
                if isPersonalNumberAllowed(newNumber):
                    self._currentNumber = newNumber
                    self.hide()
                else:
                    self.__showProhibitedHint(newNumber)
                    self.__storedNumber = None
            SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_ESC)
            return

    def stop(self):
        if not self.visible:
            return
        else:
            newNumber = formatPersonalNumber(self._currentNumber, self._digitsCount)
            if isPersonalNumberAllowed(newNumber):
                self._currentNumber = newNumber
                self.hide()
                return
            if self.__storedNumber is not None:
                newNumber = formatPersonalNumber(self.__storedNumber, self._digitsCount)
                if isPersonalNumberAllowed(newNumber):
                    self._currentNumber = newNumber
                    self.hide()
                    return
            item = self.__ctx.mode.getItemFromSlot(self.__slotId)
            if item is not None:
                self.__showProhibitedNumberSystemMsg(item, newNumber)
            self.hide()
            self.__ctx.mode.removeItem(self.__slotId)
            return

    def show(self):
        if self.visible:
            return
        self.__prohibitedHintShown(False)
        self.stopCallback(self.__prohibitedHintShown)
        self.as_showS(self._digitsCount)
        self.__visible = True
        self.__ctx.vehicleAnchorsUpdater.displayLine(True)
        self._currentNumber = EMPTY_PERSONAL_NUMBER
        self.__showPromptHint()
        self.__ctx.mode.enableEditMode(enabled=True)

    def hide(self):
        if not self.visible:
            return
        else:
            self.__visible = False
            self.as_hideS()
            self.__currentNumber = None
            self.__storedNumber = None
            self.__ctx.vehicleAnchorsUpdater.displayLine(False)
            self.__ctx.c11nCameraManager.enableMovementByMouse()
            self.__ctx.mode.enableEditMode(enabled=False)
            return

    def update(self, slotId):
        item = self.__ctx.mode.getItemFromSlot(slotId)
        if item is not None and item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER:
            self._digitsCount = item.digitsCount
        else:
            self.hide()
            return
        if self.visible:
            if item.digitsCount <= len(self.__currentNumber):
                newNumber = fitPersonalNumber(self._currentNumber, item.digitsCount)
                newNumber = formatPersonalNumber(newNumber, item.digitsCount)
                if isPersonalNumberAllowed(newNumber):
                    self._currentNumber = newNumber
                else:
                    self._currentNumber = EMPTY_PERSONAL_NUMBER
                    self.__showProhibitedHint(newNumber)
            return
        else:
            component = self.__ctx.mode.getComponentFromSlot(slotId)
            if component is not None and not component.isFilled():
                self.start(slotId)
            return

    def sendChar(self, char):
        if len(self._currentNumber) == self._digitsCount:
            SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_NUMBER_OVER)
            self.__showEditHint()
            return
        newNumber = self._currentNumber + char
        if len(newNumber) == self._digitsCount and not isPersonalNumberAllowed(newNumber):
            self.__showProhibitedHint(newNumber)
            return
        self._currentNumber = newNumber
        SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_NUMBER)
        if len(self._currentNumber) == self._digitsCount:
            self.__showConfirmitionHint()
        else:
            self.__showPromptHint()

    def removeChar(self):
        SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_BACKSPACE)
        self._currentNumber = self._currentNumber[:-1]
        self.__showPromptHint()

    def deleteAll(self):
        SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_DELETE)
        self._currentNumber = EMPTY_PERSONAL_NUMBER

    def __handleLobbyViewMouseEvent(self, event):
        if self.visible:
            ctx = event.ctx
            if ctx['dx'] or ctx['dy']:
                self.finish(cancelIfEmpty=True)

    def __manageCamera(self):
        isCameraRotationEnabled = True
        if self.visible:
            formattedNumber = formatPersonalNumber(self._currentNumber, self._digitsCount)
            isCameraRotationEnabled = isPersonalNumberAllowed(formattedNumber)
        self.__ctx.c11nCameraManager.enableMovementByMouse(enableRotation=isCameraRotationEnabled)

    def __prohibitedHintShown(self, value):
        self.__isProhibitedHintShown = value

    def __showProhibitedNumberSystemMsg(self, item, number):
        seasonName = _ms(SEASON_TYPE_TO_INFOTYPE_MAP[self.__ctx.season])
        msg = _ms(SYSTEM_MESSAGES.CUSTOMIZATION_PERSONAL_NUMBER_PROHIBITED, value=text_styles.critical(number), itemType=item.userType, itemName=item.userName, seasonName=seasonName)
        msgType = SystemMessages.SM_TYPE.Error
        SystemMessages.pushMessage(msg, msgType)

    def __showProhibitedHint(self, number):
        message = makeHtmlString('html_templates:lobby/customization', 'inscription_hint', {'value': number})
        icons = [_ERROR_ICON_DESC]
        hintVO = self.__getHintVO(message, icons=icons, duration=_DEFAULT_HINT_DURATION)
        self.as_invalidInscriptionS(hintVO)

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
        self.__showProhibitedHint(number)

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

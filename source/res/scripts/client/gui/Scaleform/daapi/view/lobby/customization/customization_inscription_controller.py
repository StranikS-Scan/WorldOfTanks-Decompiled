# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_inscription_controller.py
import SoundGroups
from account_helpers.AccountSettings import AccountSettings, CUSTOMIZATION_SECTION
from gui import makeHtmlString
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.customization.shared import SEASON_TYPE_TO_INFOTYPE_MAP
from gui.Scaleform.daapi.view.lobby.customization.sound_constants import SOUNDS
from gui.Scaleform.daapi.view.meta.CustomizationInscriptionControllerMeta import CustomizationInscriptionControllerMeta
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.Scaleform.locale.READABLE_KEY_NAMES import READABLE_KEY_NAMES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from items.components.c11n_components import isPersonalNumberAllowed
from items.components.c11n_constants import NUMBER_OF_PERSONAL_NUMBER_DIGITS
from helpers.i18n import makeString as _ms
from skeletons.gui.customization import ICustomizationService
_ERROR_ICON_DESC = {'image': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_INSCRIPTION_CONTROLLER_ICON_ERROR}
_ENTER_ICON_DESC = {'image': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_INSCRIPTION_CONTROLLER_ENTER_BTN}
_BACKSPACE_ICON_DESC = {'image': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_INSCRIPTION_CONTROLLER_BSPACE_BTN}
_DEL_ICON_DESC = {'text': READABLE_KEY_NAMES.KEY_DELETE}

class PersonalNumEditStatuses(object):
    EDIT_MODE_STARTED = 1
    EDIT_MODE_FINISHED = 2
    EDIT_MODE_CANCELLED = 3


class PersonalNumEditCommands(object):
    CANCEL_EDIT_MODE = 1
    FINISH_BY_CLICK = 2
    CANCEL_BY_ESC = 3
    CANCEL_BY_INSCRIPTION_SELECT = 4


_PRESS_ENTER_HINT_SHOWN_FIELD = 'isPressEnterHintShown'
_ENTER_NUMBER_HINT_SHOWN_FIELD = 'isEnterNumberHintShown'
_DEFAULT_HINT_DURATION = 3000
_DEFAULT_HINT_DELAY = 3000

class CustomizationInscriptionController(CustomizationInscriptionControllerMeta):
    service = dependency.descriptor(ICustomizationService)

    def __init__(self):
        super(CustomizationInscriptionController, self).__init__()
        self.__shownNumber = ''
        self.__ctx = None
        return

    def _populate(self):
        self.__ctx = self.service.getCtx()
        self.__ctx.onPersonalNumberEditModeCmdSent += self.__onNumberEditModeCommand

    def _dispose(self):
        self.__ctx.onPersonalNumberEditModeCmdSent -= self.__onNumberEditModeCommand
        self.__ctx = None
        return

    def show(self):
        self.as_showS(NUMBER_OF_PERSONAL_NUMBER_DIGITS)
        self.__ctx.vehicleAnchorsUpdater.displayLine(True)
        if self.__shownNumber:
            self.__ctx.changePersonalNumberValue(self.__shownNumber)
            self.as_showHintS(self.__getHintVO(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_INSCRIPTIONCONTROLLER_PROMPT, duration=_DEFAULT_HINT_DURATION, delay=_DEFAULT_HINT_DELAY))
        else:
            self.__shownNumber = ''
            self.__ctx.changePersonalNumberValue(self.__shownNumber)
            hintDelay, hintDuration = self.__calcHintTimings(_ENTER_NUMBER_HINT_SHOWN_FIELD)
            self.as_showHintS(self.__getHintVO(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_INSCRIPTIONCONTROLLER_PROMPT, duration=hintDuration, delay=hintDelay))

    def sendChar(self, char):
        if len(self.__shownNumber) == NUMBER_OF_PERSONAL_NUMBER_DIGITS:
            SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOISE_NUMBER_OVER)
            self.as_showHintS(self.__getHintVO(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_INSCRIPTIONCONTROLLER_EDIT_BUTTONS, icons=[_BACKSPACE_ICON_DESC, _DEL_ICON_DESC], duration=_DEFAULT_HINT_DURATION))
            return
        newNumber = self.__shownNumber + char
        if len(newNumber) == NUMBER_OF_PERSONAL_NUMBER_DIGITS and not isPersonalNumberAllowed(newNumber):
            self.as_invalidInscriptionS(self.__getHintVO(makeHtmlString('html_templates:lobby/customization', 'inscription_hint', {'value': newNumber}), icons=[_ERROR_ICON_DESC], duration=_DEFAULT_HINT_DURATION))
        else:
            self.__shownNumber = newNumber
            self.__ctx.changePersonalNumberValue(self.__shownNumber)
            SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_NUMBER)
            if len(self.__shownNumber) == NUMBER_OF_PERSONAL_NUMBER_DIGITS:
                hintDelay, hintDuration = self.__calcHintTimings(_PRESS_ENTER_HINT_SHOWN_FIELD)
                self.as_showHintS(self.__getHintVO(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_INSCRIPTIONCONTROLLER_ENTRY_COMPLETED, icons=[_ENTER_ICON_DESC], duration=hintDuration, delay=hintDelay))

    def removeChar(self):
        SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_BACKSPACE)
        self.__shownNumber = self.__shownNumber[:-1]
        self.__ctx.changePersonalNumberValue(self.__shownNumber)
        self.as_showHintS(self.__getHintVO(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_INSCRIPTIONCONTROLLER_PROMPT, duration=_DEFAULT_HINT_DURATION, delay=_DEFAULT_HINT_DELAY))

    def deleteAll(self):
        SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_DELETE)
        self.__shownNumber = ''
        self.__ctx.changePersonalNumberValue(self.__shownNumber)

    def finish(self):
        if self.__shownNumber == '':
            self.as_showHintS(self.__getHintVO(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_INSCRIPTIONCONTROLLER_PROMPT, duration=_DEFAULT_HINT_DURATION))
            return
        newNumber = '0' * (NUMBER_OF_PERSONAL_NUMBER_DIGITS - len(self.__shownNumber)) + self.__shownNumber
        if not isPersonalNumberAllowed(newNumber):
            self.as_invalidInscriptionS(self.__getHintVO(makeHtmlString('html_templates:lobby/customization', 'inscription_hint', {'value': newNumber}), icons=[_ERROR_ICON_DESC], duration=_DEFAULT_HINT_DURATION))
        else:
            self.__ctx.changePersonalNumberValue(newNumber)
            self.hide()
            self.__ctx.onPersonalNumberEditModeChanged(PersonalNumEditStatuses.EDIT_MODE_FINISHED)
            self.__shownNumber = ''

    def __onNumberEditModeCommand(self, state):
        if state == PersonalNumEditCommands.FINISH_BY_CLICK:
            if self.__shownNumber != '':
                self.finish()
            else:
                self.__cancelEditMode(showPropSheetAfter=False)
        elif state is PersonalNumEditCommands.CANCEL_EDIT_MODE:
            self.__ctx.numberEditModeActive = False
            newNumber = '0' * (NUMBER_OF_PERSONAL_NUMBER_DIGITS - len(self.__shownNumber)) + self.__shownNumber
            if self.__shownNumber != '' and isPersonalNumberAllowed(newNumber):
                self.__ctx.changePersonalNumberValue(newNumber)
                self.hide()
                self.__ctx.onPersonalNumberEditModeChanged(PersonalNumEditStatuses.EDIT_MODE_FINISHED, False)
                self.__shownNumber = ''
            elif self.__shownNumber != '':
                self.__showProhibitedNumberSystemMsg(newNumber)
                self.__cancelEditMode(showPropSheetAfter=False)
            else:
                self.__cancelEditMode(showPropSheetAfter=False)
        elif state is PersonalNumEditCommands.CANCEL_BY_ESC:
            self.__cancelEditMode(showPropSheetAfter=True)
        elif state is PersonalNumEditCommands.CANCEL_BY_INSCRIPTION_SELECT:
            self.__ctx.numberEditModeActive = False
            SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_ESC)
            self.__ctx.refreshOutfit()

    def hide(self):
        self.as_hideS()
        self.__shownNumber = ''
        self.__ctx.vehicleAnchorsUpdater.displayLine(False)

    def __getHintVO(self, hintMessage, icons=None, duration=0, delay=0):
        return {'hintMessage': hintMessage,
         'icons': icons,
         'duration': duration,
         'delay': delay}

    def __cancelEditMode(self, showPropSheetAfter=True):
        self.__ctx.numberEditModeActive = False
        selectedItem = self.__ctx.getItemFromSelectedRegion()
        SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_ESC)
        if self.__ctx.storedInscriptionSlotInfo != (None, None) and selectedItem and selectedItem.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER:
            self.__ctx.restoreInscriptionSlotContent()
        elif self.__ctx.isAnyAnchorSelected and selectedItem and selectedItem.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER:
            self.__ctx.removeItemFromSlot(self.__ctx.currentSeason, self.__ctx.selectedSlot, refresh=True)
        self.hide()
        self.__ctx.onPersonalNumberEditModeChanged(PersonalNumEditStatuses.EDIT_MODE_CANCELLED, showPropSheetAfter)
        self.__ctx.refreshOutfit()
        return None

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

    def __showProhibitedNumberSystemMsg(self, number):
        selectedItem = self.__ctx.getItemFromSelectedRegion()
        seasonName = _ms(SEASON_TYPE_TO_INFOTYPE_MAP[self.__ctx.currentSeason])
        msg = _ms(SYSTEM_MESSAGES.CUSTOMIZATION_PERSONAL_NUMBER_PROHIBITED, value=text_styles.critical(number), itemName=selectedItem.userName, seasonName=seasonName)
        msgType = SystemMessages.SM_TYPE.Error
        SystemMessages.pushMessage(msg, msgType)

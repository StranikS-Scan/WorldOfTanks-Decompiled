# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_inscription_controller.py
from typing import TYPE_CHECKING
import SoundGroups
from Event import Event, EventManager
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.customization.customization_marker_edit_mode_model import InscriptionStateEnum
from gui.impl.gen.view_models.views.lobby.customization.customization_markers_model import CustomizationMarkersModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.customization.settings_constants import APPLY_TO_ALL_SEASONS_ENABLED, CustomizationSettingsSerializable
from gui.impl.lobby.customization.shared import EMPTY_PERSONAL_NUMBER, SEASON_TYPE_TO_INFOTYPE_MAP, fitPersonalNumber, formatPersonalNumber
from gui.impl.lobby.customization.sound_constants import SOUNDS
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency, time_utils
from helpers.CallbackDelayer import CallbackDelayer
from helpers.events_handler import EventsHandler
from items.components.c11n_components import isPersonalNumberAllowed
from items.components.c11n_constants import SeasonType
from items.customizations import PersonalNumberComponent
from skeletons.gui.customization import ICustomizationService
if TYPE_CHECKING:
    from typing import Optional
    from gui.impl.lobby.customization.customization_main_view import CustomizationMainView

class CustomizationInscriptionController(EventsHandler, CallbackDelayer, CustomizationSettingsSerializable):
    __service = dependency.descriptor(ICustomizationService)
    __PRESS_ENTER_INSCRIPTION_SHOWN_FIELD = 'isPressEnterHintShown'
    __ENTER_NUMBER_INSCRIPTION_SHOWN_FIELD = 'isEnterNumberHintShown'
    __DEFAULT_INSCRIPTION_DURATION = 3000
    __DEFAULT_INSCRIPTION_DELAY = 3000

    def __init__(self, mainView):
        CallbackDelayer.__init__(self)
        self.__currentNumber = None
        self.__ctx = self.__service.getCtx()
        self.__mainView = mainView
        self.__isProhibitedInscriptionShown = False
        self.__visible = False
        self.__digitsCount = 0
        self.__slotId = None
        self.__storedNumber = None
        self.__clearedNumber = None
        self.__storedSeason = None
        self.__eventsManager = EventManager()
        self.onEdited = Event(self.__eventsManager)
        self._subscribe()
        return

    @property
    def viewModel(self):
        return self.__mainView.viewModel.markersModel

    def fini(self):
        self.__ctx = None
        self.__eventsManager.clear()
        self._unsubscribe()
        self._dumpSettings()
        return

    def _getEvents(self):
        return ((self.__ctx.events.onPersonalNumberCleared, self.__onPersonalNumberCleared),
         (self.viewModel.onRemoveChar, self.__onRemoveChar),
         (self.viewModel.onDeleteAllChars, self.__onDeleteAllChars),
         (self.viewModel.onEnterInput, self.__onEnterInput),
         (self.viewModel.onAddChar, self.__onAddChar))

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
        self.__digitsCount = digitsCount
        editModel = self.viewModel.editModeData
        editModel.setEditDigitsCount(digitsCount)
        self.__manageCamera()

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

    @property
    def _isApplyToAllSeasonsSelected(self):
        return self.getSetting(APPLY_TO_ALL_SEASONS_ENABLED, False)

    def handleLobbyClick(self):
        if self.visible:
            self.finish(cancelIfEmpty=True)
        return self.visible

    def handleLobbyViewMouseEvent(self, ctx):
        if self.visible:
            if ctx['dx'] or ctx['dy']:
                self.finish(cancelIfEmpty=True)

    def start(self, slotId):
        self.__storedSeason = self.__ctx.season
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
                self.__showPromptInscription(showImmediately=True)
            return
        newNumber = formatPersonalNumber(self._currentNumber, self._digitsCount)
        if isPersonalNumberAllowed(newNumber):
            SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_ENTER)
            self._currentNumber = newNumber
            self.hide()
        elif not self.__isProhibitedInscriptionShown:
            self.__prohibitedInscriptionShown(True)
            self.__showProhibitedInscription(newNumber)
            self.delayCallback(self.__DEFAULT_INSCRIPTION_DURATION * 0.001, lambda : self.__prohibitedInscriptionShown(False))

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
                    self.__showProhibitedInscription(newNumber)
                    self.__storedNumber = None
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
            item = self.__ctx.mode.getItemFromSlot(self.__slotId, self.__storedSeason)
            if item is not None:
                self.__showProhibitedNumberSystemMsg(item, newNumber)
            self.hide()
            if self._isApplyToAllSeasonsSelected:
                for season in SeasonType.COMMON_SEASONS:
                    self.__ctx.mode.removeItem(self.__slotId, season)

            else:
                self.__ctx.mode.removeItem(self.__slotId, self.__storedSeason)
            return

    def show(self):
        if self.visible:
            return
        self.__prohibitedInscriptionShown(False)
        self.stopCallback(self.__prohibitedInscriptionShown)
        self.__visible = True
        self._currentNumber = EMPTY_PERSONAL_NUMBER
        self.__showPromptInscription()
        self.__ctx.mode.enableEditMode(enabled=True, slotId=self.__slotId)

    def hide(self):
        if not self.visible:
            return
        else:
            self.__fillInscriptionModel(InscriptionStateEnum.EMPTY, 0, 0)
            self.__visible = False
            self.__currentNumber = None
            self.__storedNumber = None
            self.__ctx.c11nCameraManager.enableMovementByMouse()
            self.__ctx.mode.enableEditMode(enabled=False, slotId=self.__slotId)
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
                    self.onEdited(slotId)
                else:
                    self._currentNumber = EMPTY_PERSONAL_NUMBER
                    self.__showProhibitedInscription(newNumber)
            return
        else:
            component = self.__ctx.mode.getComponentFromSlot(slotId)
            if component is not None and not component.isFilled():
                self.start(slotId)
            return

    @args2params(str)
    def __onAddChar(self, char):
        if len(self._currentNumber) == self._digitsCount:
            SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_NUMBER_OVER)
            self.__showEditInscription()
            return
        newNumber = self._currentNumber + char
        if len(newNumber) == self._digitsCount and not isPersonalNumberAllowed(newNumber):
            self.__showProhibitedInscription(newNumber)
            SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_NUMBER_DENIED)
            return
        self._currentNumber = newNumber
        SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_NUMBER)
        if len(self._currentNumber) == self._digitsCount:
            self.__showConfirmationInscription()
        else:
            self.__showPromptInscription()

    def __onEnterInput(self):
        self.finish()

    def __onRemoveChar(self):
        SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_BACKSPACE)
        self._currentNumber = self._currentNumber[:-1]
        self.__showPromptInscription()

    def __onDeleteAllChars(self):
        SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_DELETE)
        self._currentNumber = EMPTY_PERSONAL_NUMBER

    def __manageCamera(self):
        isCameraRotationEnabled = True
        if self.visible:
            formattedNumber = formatPersonalNumber(self._currentNumber, self._digitsCount)
            isCameraRotationEnabled = isPersonalNumberAllowed(formattedNumber)
        self.__ctx.c11nCameraManager.enableMovementByMouse(enableRotation=isCameraRotationEnabled)

    def __prohibitedInscriptionShown(self, value):
        self.__isProhibitedInscriptionShown = value

    def __showProhibitedNumberSystemMsg(self, item, number):
        if self._isApplyToAllSeasonsSelected:
            rMessageID = R.strings.system_messages.customization.personal_number_prohibited_all_seasons()
        else:
            rMessageID = R.strings.system_messages.customization.personal_number_prohibited()
        SystemMessages.pushMessage(backport.text(rMessageID, value=text_styles.critical(number), itemType=item.userType, itemName=item.userName, seasonName=SEASON_TYPE_TO_INFOTYPE_MAP[self.__storedSeason]), SystemMessages.SM_TYPE.Error)

    def __showProhibitedInscription(self, number):
        self.__fillInscriptionModel(InscriptionStateEnum.NOTAVAILABLEENTER, 0, self.__DEFAULT_INSCRIPTION_DURATION, number)

    def __showEditInscription(self):
        self.__fillInscriptionModel(InscriptionStateEnum.EDITENTER, 0, self.__DEFAULT_INSCRIPTION_DURATION)

    def __showConfirmationInscription(self):
        inscriptionDelay, inscriptionDuration = self.__calcInscriptionTimings(self.__PRESS_ENTER_INSCRIPTION_SHOWN_FIELD)
        self.__fillInscriptionModel(InscriptionStateEnum.SUBMITENTER, inscriptionDelay, inscriptionDuration)

    def __showPromptInscription(self, showImmediately=False):
        if showImmediately:
            inscriptionDelay, inscriptionDuration = 0, self.__DEFAULT_INSCRIPTION_DURATION
        else:
            inscriptionDelay, inscriptionDuration = self.__calcInscriptionTimings(self.__ENTER_NUMBER_INSCRIPTION_SHOWN_FIELD)
        editModel = self.viewModel.editModeData
        firstEnterRange = editModel.getInscriptionFirstEnterRange()
        firstEnterRange.clear()
        firstEnterRange.addString(formatPersonalNumber('1', self._digitsCount))
        firstEnterRange.addString('9' * self._digitsCount)
        editModel.setStartTimestamp(time_utils.getCurrentTimestamp())
        if self.__storedNumber is None:
            editModel.setInscriptionState(InscriptionStateEnum.FIRSTENTER)
        editModel.setInscriptionDelay(inscriptionDelay)
        editModel.setInscriptionDuration(inscriptionDuration)
        return

    def __fillInscriptionModel(self, inscriptionState, inscriptionDelay, inscriptionDuration, invalidInscriptionNumber=''):
        editModel = self.viewModel.editModeData
        editModel.setInscriptionState(inscriptionState)
        editModel.setInscriptionDelay(inscriptionDelay)
        editModel.setInscriptionDuration(inscriptionDuration)
        editModel.setStartTimestamp(time_utils.getCurrentTimestamp())
        editModel.setInvalidInscriptionNumber(invalidInscriptionNumber)

    def __onPersonalNumberCleared(self, number):
        self.__showProhibitedInscription(number)

    def __calcInscriptionTimings(self, accountSettingName):
        inscriptionDuration = self.__DEFAULT_INSCRIPTION_DURATION
        inscriptionDelay = self.__DEFAULT_INSCRIPTION_DELAY
        if not self.getSetting(accountSettingName, False):
            inscriptionDuration = 0
            inscriptionDelay = 0
            self.setSetting(accountSettingName, True)
        return (inscriptionDelay, inscriptionDuration)

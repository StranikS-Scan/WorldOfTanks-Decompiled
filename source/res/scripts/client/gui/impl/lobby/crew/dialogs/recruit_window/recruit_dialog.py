# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/recruit_window/recruit_dialog.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.lobby.crew.dialogs.base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui.impl.lobby.crew.dialogs.recruit_window.recruit_content import NO_DATA_VALUE, RecruitContent
from gui.impl.gen.view_models.views.lobby.crew.dialogs.recruit_window.recruit_dialog_template_view_model import RecruitDialogTemplateViewModel
from gui.shared.event_dispatcher import showRecruitConfirmIrrelevantConversionDialog
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.quests import PMGetTankwomanReward
from items import vehicles
from gui.impl.lobby.crew.dialogs.recruit_window.recruit_dialog_utils import getIcon, getTitle, getIconBackground, getIconName, getTitleFromTokenData
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.gen.resources import R
from gui import SystemMessages, _logger
from gui.shared.gui_items.processors.tankman import TankmanTokenRecruit, TankmanUnload, TankmanEquip
from gui.shared.utils import decorators
from helpers import dependency
from skeletons.gui.game_control import ISpecialSoundCtrl
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from sound_gui_manager import CommonSoundSpaceSettings
from gui.server_events.pm_constants import SOUNDS, PERSONAL_MISSIONS_SILENT_SOUND_SPACE
from gui.sounds.filters import States, StatesGroup
from uilogging.crew.logging_constants import CrewDialogKeys
from wg_async import AsyncEvent, wg_await, BrokenPromiseError, AsyncReturn, wg_async
from gui.shared.gui_items.Tankman import NO_TANKMAN

class BaseRecruitDialog(BaseCrewDialogTemplateView):
    __slots__ = ('_selectedNation', '_selectedVehType', '_selectedVehicle', '_selectedSpecialization', '_recruitContent')
    _eventsCache = dependency.descriptor(IEventsCache)
    LAYOUT_ID = R.views.lobby.crew.dialogs.RecruitDialog()
    VIEW_MODEL = RecruitDialogTemplateViewModel

    def __init__(self, **kwargs):
        super(BaseRecruitDialog, self).__init__(loggingKey=CrewDialogKeys.RECRUIT, **kwargs)
        self._selectedNation = NO_DATA_VALUE
        self._selectedVehType = NO_DATA_VALUE
        self._selectedVehicle = NO_DATA_VALUE
        self._selectedSpecialization = NO_DATA_VALUE
        self._recruitContent = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def _addButtons(self):
        self.addButton(ConfirmButton(R.strings.dialogs.recruitWindow.submit(), isDisabled=True))
        self.addButton(CancelButton(R.strings.dialogs.recruitWindow.cancel()))

    def _onRecruitContentChanged(self, nation, vehType, vehicle, specialization):
        self._selectedNation = nation
        self._selectedVehType = vehType
        self._selectedVehicle = vehicle
        self._selectedSpecialization = specialization
        submitBtn = self.getButton(DialogButtons.SUBMIT)
        if submitBtn is not None:
            submitBtn.isDisabled = any((v == NO_DATA_VALUE for v in (nation,
             vehType,
             vehicle,
             specialization)))
        return


class TokenRecruitDialog(BaseRecruitDialog):
    __slots__ = ('__tokenName', '__tokenData', '__vehicleSlotToUnpack', '__vehicle')
    _itemsCache = dependency.descriptor(IItemsCache)
    _specialSounds = dependency.descriptor(ISpecialSoundCtrl)
    __SOUND_SETTINGS = CommonSoundSpaceSettings(name='hangar', entranceStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_GARAGE,
     StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_OFF}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=SOUNDS.WOMAN_AWARD_WINDOW, exitEvent='')
    _COMMON_SOUND_SPACE = __SOUND_SETTINGS

    def __init__(self, ctx=None, **kwargs):
        super(TokenRecruitDialog, self).__init__(**kwargs)
        self.__tokenName = ctx['tokenName']
        self.__tokenData = ctx['tokenData']
        self.__vehicleSlotToUnpack = ctx['slot']
        self.__vehicle = ctx['vehicle']

    def _onLoading(self, *args, **kwargs):
        super(TokenRecruitDialog, self)._onLoading(*args, **kwargs)
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        self.viewModel.setText(getTitleFromTokenData(self.__tokenData))
        self.viewModel.setHasVoiceover(bool(self.__tokenData.getSpecialVoiceTag(self._specialSounds)))
        self._addButtons()
        predefinedData = {'predefinedNations': self.__tokenData.getNations(),
         'predefinedRoles': self.__tokenData.getRoles(),
         'isFemale': self.__tokenData.isFemale(),
         'slotToUnpack': self.__vehicleSlotToUnpack,
         'predefinedVehicle': self.__vehicle}
        self._recruitContent = RecruitContent(model=self.viewModel.recruitContent, predefinedData=predefinedData)
        self._recruitContent.onRecruitContentChanged += self._onRecruitContentChanged
        self._recruitContent.onLoading()
        self._recruitContent.subscribe()
        iconID, hasBackground = getIcon(getIconName(self.__tokenData.getSmallIcon()), self.__tokenData.isFemale())
        self.viewModel.iconModel.icon.setPath(iconID)
        if not hasBackground:
            self.viewModel.iconModel.bgIcon.setPath(getIconBackground(self.__tokenData.getSourceID(), self.__tokenData.getSmallIcon()))

    def _finalize(self):
        super(TokenRecruitDialog, self)._finalize()
        if self._recruitContent is not None:
            self._recruitContent.onRecruitContentChanged -= self._onRecruitContentChanged
            self._recruitContent.unsubscribe()
        return

    def _hasIrrelevantSkils(self, vehicle):
        tman = self.__tokenData.getFakeTankmanInVehicle(vehicle, self._selectedSpecialization)
        return any((skill for skill in tman.descriptor.irrelevantSkills))

    @wg_async
    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            vehicle = self._itemsCache.items.getItemByCD(int(self._selectedVehicle))
            if vehicle and self._hasIrrelevantSkils(vehicle):
                confirmResult = yield wg_await(showRecruitConfirmIrrelevantConversionDialog({'tokenData': self.__tokenData,
                 'selectedRole': self._selectedSpecialization,
                 'selectedVehicle': vehicle}))
                if not confirmResult.result or not confirmResult.result[0]:
                    return
            self._submit()
        super(TokenRecruitDialog, self)._setResult(result)

    def _submit(self):
        tankmen = self.__vehicle.getTankmanIDBySlotIdx(self.__vehicleSlotToUnpack) if self.__vehicle else NO_TANKMAN
        if tankmen != NO_TANKMAN:
            self._unloadOldTankman()
        else:
            self._unpackTokenRecruit()

    @decorators.adisp_process('updating')
    def _unpackTokenRecruit(self):
        _, _, vehTypeID = vehicles.parseIntCompactDescr(int(self._selectedVehicle))
        res = yield TankmanTokenRecruit(int(self._selectedNation), int(vehTypeID), self._selectedSpecialization, self.__tokenName, self.__tokenData).request()
        if res.userMsg:
            SystemMessages.pushMessage(res.userMsg, type=res.sysMsgType)
        if res.success:
            if self.__vehicleSlotToUnpack != -1:
                tmn = self._itemsCache.items.getTankman(res.auxData)
                self._equipTankman(tmn)

    @decorators.adisp_process('unloading')
    def _unloadOldTankman(self):
        result = yield TankmanUnload(self.__vehicle.invID, self.__vehicleSlotToUnpack).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self._unpackTokenRecruit()

    @decorators.adisp_process('equipping')
    def _equipTankman(self, newTankman):
        result = yield TankmanEquip(newTankman.invID, self.__vehicle.invID, self.__vehicleSlotToUnpack).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)


class QuestRecruitDialog(BaseRecruitDialog):
    __slots__ = ('__mission', '__isFemale', '__vehicleSlotToUnpack', '__vehicle', '__inventoryUpdateEvent')
    _itemsCache = dependency.descriptor(IItemsCache)
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_SILENT_SOUND_SPACE

    def __init__(self, ctx=None, **kwargs):
        super(QuestRecruitDialog, self).__init__(**kwargs)
        self.__mission = self._eventsCache.getPersonalMissions().getAllQuests().get(ctx['questID'])
        self.__isFemale = ctx['isFemale']
        self.__vehicleSlotToUnpack = ctx['slot']
        self.__vehicle = ctx['vehicle']
        self.__inventoryUpdateEvent = AsyncEvent(state=False, scope=None)
        return

    def _onLoading(self, *args, **kwargs):
        super(QuestRecruitDialog, self)._onLoading(*args, **kwargs)
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        self.viewModel.setText(getTitle())
        self._addButtons()
        predefinedData = {'isFemale': self.__isFemale,
         'slotToUnpack': self.__vehicleSlotToUnpack,
         'predefinedVehicle': self.__vehicle}
        self._recruitContent = RecruitContent(model=self.viewModel.recruitContent, predefinedData=predefinedData)
        self._recruitContent.onRecruitContentChanged += self._onRecruitContentChanged
        self._recruitContent.onLoading()
        self._recruitContent.subscribe()
        iconID, hasBackground = getIcon(isFemale=self.__isFemale)
        self.viewModel.iconModel.icon.setPath(iconID)
        if not hasBackground:
            self.viewModel.iconModel.bgIcon.setPath(getIconBackground())
        super(QuestRecruitDialog, self)._onLoading(*args, **kwargs)

    def _onLoaded(self, *args, **kwargs):
        super(QuestRecruitDialog, self)._onLoaded(*args, **kwargs)
        self.soundManager.playInstantSound(SOUNDS.WOMAN_AWARD_WINDOW)

    def _finalize(self):
        super(QuestRecruitDialog, self)._finalize()
        if self._recruitContent is not None:
            self._recruitContent.onRecruitContentChanged -= self._onRecruitContentChanged
            self._recruitContent.unsubscribe()
        g_clientUpdateManager.removeObjectCallbacks(self)
        return

    def _getCallbacks(self):
        return (('inventory', self._onInventoryUpdate),)

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            tmanID = self.__vehicle.getTankmanIDBySlotIdx(self.__vehicleSlotToUnpack) if self.__vehicle else NO_TANKMAN
            if tmanID != NO_TANKMAN:
                self._unloadOldTankman()
            else:
                self._unpackQuestRecruit()
        super(QuestRecruitDialog, self)._setResult(result)

    @decorators.adisp_process('updating')
    def _unpackQuestRecruit(self):
        _, _, vehTypeID = vehicles.parseIntCompactDescr(int(self._selectedVehicle))
        res = yield PMGetTankwomanReward(self.__mission, int(self._selectedNation), int(vehTypeID), self._selectedSpecialization).request()
        if res.userMsg:
            SystemMessages.pushMessage(res.userMsg, type=res.sysMsgType)
        if res.success and self.__vehicleSlotToUnpack != -1:
            self._waitForInventoryUpdate()

    @wg_async
    def _waitForInventoryUpdate(self):
        try:
            yield wg_await(self.__inventoryUpdateEvent.wait())
            super(QuestRecruitDialog, self)._setResult(DialogButtons.SUBMIT)
        except BrokenPromiseError:
            _logger.debug('%s has been destroyed without user decision', self)

        raise AsyncReturn(DialogButtons.SUBMIT)

    @decorators.adisp_process('unloading')
    def _unloadOldTankman(self):
        result = yield TankmanUnload(self.__vehicle.invID, self.__vehicleSlotToUnpack).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self._unpackQuestRecruit()

    @decorators.adisp_process('equipping')
    def _equipTankman(self, newTankman):
        result = yield TankmanEquip(newTankman.invID, self.__vehicle.invID, self.__vehicleSlotToUnpack).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def _onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.TANKMAN in invDiff:
            tmenCompDescr = invDiff[GUI_ITEM_TYPE.TANKMAN].get('compDescr', {})
            for key, _ in tmenCompDescr.items():
                tmn = self._itemsCache.items.getTankman(key)
                if tmn and self._selectedVehicle == tmn.vehicleNativeDescr.type.compactDescr and self._selectedSpecialization == tmn.role:
                    self._equipTankman(tmn)
                    self.__inventoryUpdateEvent.set()
                    return

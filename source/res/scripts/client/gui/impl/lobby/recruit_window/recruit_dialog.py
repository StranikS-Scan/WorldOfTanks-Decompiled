# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/recruit_window/recruit_dialog.py
from gui.impl.lobby.recruit_window.recruit_content import DEFAULT_VALUE, RecruitContent
from gui.impl.gen.view_models.views.lobby.recruit_window.recruit_dialog_template_view_model import RecruitDialogTemplateViewModel
from gui.server_events import recruit_helper
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.gui_items.processors.quests import PMGetTankwomanReward
from items import vehicles
from gui.impl.lobby.recruit_window.recruit_dialog_utils import getIcon, getTitle, getIconBackground, getIconName
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.gen.resources import R
from gui import SystemMessages
from gui.shared.gui_items.processors.tankman import TankmanTokenRecruit
from gui.shared.utils import decorators
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from sound_gui_manager import CommonSoundSpaceSettings
from gui.server_events.pm_constants import SOUNDS, PERSONAL_MISSIONS_SILENT_SOUND_SPACE
from gui.sounds.filters import States, StatesGroup

class BaseRecruitDialog(DialogTemplateView):
    __slots__ = ('_selectedNation', '_selectedVehType', '_selectedVehicle', '_selectedSpecialization', '_recruitContent')
    _eventsCache = dependency.descriptor(IEventsCache)
    LAYOUT_ID = R.views.lobby.recruit_window.RecruitDialog()
    VIEW_MODEL = RecruitDialogTemplateViewModel

    def __init__(self):
        super(BaseRecruitDialog, self).__init__()
        self._selectedNation = DEFAULT_VALUE
        self._selectedVehType = DEFAULT_VALUE
        self._selectedVehicle = DEFAULT_VALUE
        self._selectedSpecialization = DEFAULT_VALUE
        self._recruitContent = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BaseRecruitDialog, self)._onLoading(*args, **kwargs)
        g_eventBus.handleEvent(events.GameEvent(events.GameEvent.HIDE_LOBBY_SUB_CONTAINER_ITEMS), scope=EVENT_BUS_SCOPE.GLOBAL)

    def _finalize(self):
        super(BaseRecruitDialog, self)._finalize()
        g_eventBus.handleEvent(events.GameEvent(events.GameEvent.REVEAL_LOBBY_SUB_CONTAINER_ITEMS), scope=EVENT_BUS_SCOPE.GLOBAL)

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
            submitBtn.isDisabled = any((v == DEFAULT_VALUE for v in (nation,
             vehType,
             vehicle,
             specialization)))
        return


class TokenRecruitDialog(BaseRecruitDialog):
    __slots__ = ('__tokenName', '__tokenData')
    _itemsCache = dependency.descriptor(IItemsCache)
    __SOUND_SETTINGS = CommonSoundSpaceSettings(name='hangar', entranceStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_GARAGE,
     StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_OFF}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=SOUNDS.WOMAN_AWARD_WINDOW, exitEvent='')
    _COMMON_SOUND_SPACE = __SOUND_SETTINGS

    def __init__(self, ctx=None):
        super(TokenRecruitDialog, self).__init__()
        self.__tokenName = ctx['tokenName']
        self.__tokenData = ctx['tokenData']

    def _onLoading(self, *args, **kwargs):
        super(TokenRecruitDialog, self)._onLoading(*args, **kwargs)
        name = self.__tokenData.getFullUserNameByNation().strip()
        if self.__tokenData.getSmallIcon() in (recruit_helper._TANKWOMAN_ICON, recruit_helper._TANKMAN_ICON):
            name = None
        self.viewModel.setText(getTitle(name))
        self._addButtons()
        predefinedData = {'predefinedNations': self.__tokenData.getNations(),
         'predefinedRoles': self.__tokenData.getRoles(),
         'isFemale': self.__tokenData.isFemale()}
        self._recruitContent = RecruitContent(model=self.viewModel.recruitContent, predefinedData=predefinedData)
        self._recruitContent.onRecruitContentChanged += self._onRecruitContentChanged
        self._recruitContent.onLoading()
        self._recruitContent.subscribe()
        iconID, hasBackground = getIcon(getIconName(self.__tokenData.getSmallIcon()), self.__tokenData.isFemale())
        self.viewModel.iconModel.icon.setPath(iconID)
        if not hasBackground:
            self.viewModel.iconModel.bgIcon.setPath(getIconBackground(self.__tokenData.getSourceID()))
        return

    def _finalize(self):
        super(TokenRecruitDialog, self)._finalize()
        if self._recruitContent is not None:
            self._recruitContent.onRecruitContentChanged -= self._onRecruitContentChanged
            self._recruitContent.unsubscribe()
        return

    @decorators.adisp_process('updating')
    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            _, _, vehTypeID = vehicles.parseIntCompactDescr(int(self._selectedVehicle))
            res = yield TankmanTokenRecruit(int(self._selectedNation), int(vehTypeID), self._selectedSpecialization, self.__tokenName, self.__tokenData).request()
            if res.userMsg:
                SystemMessages.pushMessage(res.userMsg, type=res.sysMsgType)
            if res.success:
                self._closeClickHandler()
                return
        super(TokenRecruitDialog, self)._setResult(result)


class QuestRecruitDialog(BaseRecruitDialog):
    __slots__ = ('__mission', '__isFemale')
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_SILENT_SOUND_SPACE

    def __init__(self, ctx=None):
        super(QuestRecruitDialog, self).__init__()
        self.__mission = self._eventsCache.getPersonalMissions().getAllQuests().get(ctx['questID'])
        self.__isFemale = ctx['isFemale']

    def _onLoading(self, *args, **kwargs):
        super(QuestRecruitDialog, self)._onLoading(*args, **kwargs)
        self.viewModel.setText(getTitle())
        self._addButtons()
        predefinedData = {'isFemale': self.__isFemale}
        self._recruitContent = RecruitContent(model=self.viewModel.recruitContent, predefinedData=predefinedData)
        self._recruitContent.onRecruitContentChanged += self._onRecruitContentChanged
        self._recruitContent.onLoading()
        self._recruitContent.subscribe()
        iconID, hasBackground = getIcon(isFemale=self.__isFemale)
        self.viewModel.iconModel.icon.setPath(iconID)
        if not hasBackground:
            self.viewModel.iconModel.bgIcon.setPath(getIconBackground())
        super(QuestRecruitDialog, self)._onLoading(*args, **kwargs)

    def _onLoaded(self):
        super(QuestRecruitDialog, self)._onLoaded()
        self.soundManager.playInstantSound(SOUNDS.WOMAN_AWARD_WINDOW)

    def _finalize(self):
        super(QuestRecruitDialog, self)._finalize()
        if self._recruitContent is not None:
            self._recruitContent.onRecruitContentChanged -= self._onRecruitContentChanged
            self._recruitContent.unsubscribe()
        return

    @decorators.adisp_process('updating')
    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            _, _, vehTypeID = vehicles.parseIntCompactDescr(int(self._selectedVehicle))
            res = yield PMGetTankwomanReward(self.__mission, int(self._selectedNation), int(vehTypeID), self._selectedSpecialization).request()
            if res.userMsg:
                SystemMessages.pushMessage(res.userMsg, type=res.sysMsgType)
            if res.success:
                self._closeClickHandler()
                return
        super(QuestRecruitDialog, self)._setResult(result)

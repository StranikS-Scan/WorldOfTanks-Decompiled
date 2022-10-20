# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/preview_view.py
import HWAccountSettings
import adisp
import WWISE
import SoundGroups
from gui.impl import backport
from gui.shared.utils.performance_analyzer import PerformanceGroup
from halloween.skeletons.gui.game_event_controller import IHalloweenProgressController
from items import tankmen
from shared_utils import findFirst
from wg_async import wg_await
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui import GUI_SETTINGS
from gui.impl.gen import R
from gui.impl.pub.fade_manager import FadeManager
from gui.impl.pub.lobby_window import LobbyWindow
from halloween.gui.impl.gen.view_models.views.lobby.common.crew_item_model import CrewItemModel
from halloween.gui.impl.gen.view_models.views.lobby.preview_view_model import PreviewViewModel, PreviewTypeEnum
from halloween.gui.impl.lobby.base_event_view import BaseEventView, isNewIntro, isNewOutro
from halloween.gui.impl.lobby.tooltips.crew_tooltip import CrewTooltip
from halloween.hw_constants import AccountSettingsKeys, PhaseType
from halloween.gui.impl.lobby.tooltips.simply_format_tooltip import SimplyFormatTooltipView
from halloween.gui.sounds.sound_constants import WITCHES_SOUND_SPACE, WitchesMetaState, WitchesMetaEvents, HANGAR_WITCHES_VO_PREVIEW, WITCHES_VIEW_OPENED
from helpers import dependency
from skeletons.gui.game_control import IExternalLinksController
PORTAL_URL_KEY = 'portalLink'
_PreviewTypeToSound = {PreviewTypeEnum.INTRO.value: WitchesMetaState.WINDOW_INTRO,
 PreviewTypeEnum.HISTORY.value: WitchesMetaState.WINDOW_HISTORY,
 PreviewTypeEnum.WITCHES.value: WitchesMetaState.WINDOW_WITCHES,
 PreviewTypeEnum.OUTRO.value: WitchesMetaState.WINDOW_OUTRO}

class PreviewView(BaseEventView):
    __slots__ = ('__selectedPhase', '__onClose', '__portalLink')
    layoutID = R.views.halloween.lobby.PreviewView()
    __externalLinks = dependency.descriptor(IExternalLinksController)
    _hwController = dependency.descriptor(IHalloweenProgressController)
    _COMMON_SOUND_SPACE = WITCHES_SOUND_SPACE

    def __init__(self, layoutID=None, selectedPhase=0, onClose=None, *args, **kwargs):
        settings = ViewSettings(layoutID or self.layoutID)
        settings.model = PreviewViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(PreviewView, self).__init__(settings)
        self.__selectedPhase = selectedPhase
        self.__onClose = onClose
        self.__currentSoundEvent = None
        self.__portalLink = GUI_SETTINGS.lookup(PORTAL_URL_KEY)
        return

    @property
    def viewModel(self):
        return super(PreviewView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.halloween.lobby.tooltips.SimplyFormatTooltip():
            slide = event.getArgument('slide', 0)
            header = event.getArgument('header', '')
            body = event.getArgument('body', '')
            if slide:
                header = backport.text(R.strings.hw_lobby.previewScreen.carousel.tooltip.dyn(slide).head())
                phase = self._hwController.phasesHalloween.getPhaseByIndex(self.__selectedPhase)
                if not phase:
                    return None
                start = '{}, {}'.format(backport.getShortDateFormat(phase.getStartTime()), backport.getShortTimeFormat(phase.getStartTime()))
                end = '{}, {}'.format(backport.getShortDateFormat(phase.getFinishTime()), backport.getShortTimeFormat(phase.getFinishTime()))
                body = backport.text(R.strings.hw_lobby.previewScreen.carousel.tooltip.dyn(slide).body(), date_start=start, date_end=end, number=backport.text(R.strings.tooltips.level.num(int(self.__selectedPhase))()))
            return SimplyFormatTooltipView(header, body)
        elif contentID == R.views.halloween.lobby.tooltips.CrewTooltip():
            phaseIndex = event.getArgument('id')
            return CrewTooltip(phaseIndex=phaseIndex)
        else:
            return super(PreviewView, self).createToolTipContent(event, contentID)

    def _subscribe(self):
        super(PreviewView, self)._subscribe()
        self.viewModel.onBack += self.__onBack
        self.viewModel.onDownloadClick += self.__onDownloadClick
        self.viewModel.onSoundBtnClick += self.__onSoundBtnClick
        self.viewModel.onSlideClick += self.__onSlideClick

    def _unsubscribe(self):
        super(PreviewView, self)._unsubscribe()
        self.viewModel.onBack -= self.__onBack
        self.viewModel.onDownloadClick -= self.__onDownloadClick
        self.viewModel.onSoundBtnClick -= self.__onSoundBtnClick
        self.viewModel.onSlideClick -= self.__onSlideClick

    def _initialize(self):
        super(PreviewView, self)._initialize()
        viewType = str(self.viewModel.getType().value)
        WWISE.WW_setState(WitchesMetaState.GROUP, _PreviewTypeToSound.get(viewType, WitchesMetaState.ON))
        self.__sendSoundEvents(viewType)

    def _finalize(self):
        WWISE.WW_setState(WitchesMetaState.GROUP, WitchesMetaState.WINDOW_META)
        self.__sendSoundEvents()
        super(PreviewView, self)._finalize()

    def _fillViewModel(self):
        super(PreviewView, self)._fillViewModel()
        self.__update()

    def __onSlideClick(self, args):
        if not args:
            return
        slide = args.get('slide')
        WWISE.WW_setState(WitchesMetaState.GROUP, _PreviewTypeToSound.get(str(slide), WitchesMetaState.ON))
        if slide == PreviewTypeEnum.INTRO.value:
            self.__setNew(AccountSettingsKeys.VIEWED_WITHES_INTRO)
            self.__update()
        elif slide == PreviewTypeEnum.OUTRO.value:
            self.__setNew(AccountSettingsKeys.VIEWED_WITHES_OUTRO)
            self.__update()
        self.__sendSoundEvents(str(slide))

    def __setNew(self, key):
        viewed = HWAccountSettings.getSettings(key)
        if self.__selectedPhase not in viewed:
            viewed.append(self.__selectedPhase)
            HWAccountSettings.setSettings(key, viewed)

    @adisp.adisp_process
    def __onBack(self):
        with FadeManager(WindowLayer.SERVICE_LAYOUT) as fadeManager:
            yield wg_await(fadeManager.show())
            if self.__onClose:
                self.__onClose()
            self.destroyWindow()
            yield wg_await(fadeManager.hide())

    def __onDownloadClick(self):
        wallpaper = GUI_SETTINGS.phases.get('phase{}'.format(int(self.__selectedPhase)), None)
        url = self.__portalLink + ('' if wallpaper is None else wallpaper)
        self.__externalLinks.open(url)
        return

    def __onSoundBtnClick(self):
        SoundGroups.g_instance.playSound2D(HANGAR_WITCHES_VO_PREVIEW)

    def __update(self):
        with self.viewModel.transaction() as model:
            self.viewModel.setIsDownloadDisabled(self.__portalLink is None or self.__portalLink == '')
            phase = self._hwController.phasesHalloween.getPhaseByIndex(self.__selectedPhase)
            if phase:
                currentPerformanceGroup = self._eventController.getPerformanceGroup()
                model.setIsPerformanceRiskLow(currentPerformanceGroup == PerformanceGroup.LOW_RISK)
                model.setSelectedPhase(self.__selectedPhase)
                model.setType(PreviewTypeEnum.HISTORY)
                model.setNewIntro(isNewIntro(phase))
                model.setNewOutro(isNewOutro(phase))
                model.setDisabledIntro(phase.isLock())
                model.setDisabledOutro(phase.isLock() or not phase.hasPlayerTmanBonus())
            phases = self._hwController.phasesHalloween.getPhasesByType(PhaseType.REGULAR)
            crewListModels = model.crewListBlock.getCrewList()
            crewListModels.clear()
            for phase in phases:
                itemModel = CrewItemModel()
                tankmanTokenArgs = phase.getTmanTokenBonus().split(':')
                if not tankmanTokenArgs:
                    continue
                groupName = tankmanTokenArgs[3]
                group = findFirst(lambda g, name=groupName: g.name == name, tankmen.getNationGroups(0, isPremium=True).itervalues())
                roles = group.rolesList
                if not roles:
                    continue
                itemModel.setId(phase.phaseIndex)
                itemModel.setRole(roles[0])
                itemModel.setGroup(groupName)
                itemModel.setIsAvailable(phase.hasPlayerTmanBonus())
                crewListModels.addViewModel(itemModel)

            crewListModels.invalidate()
        return

    def __sendSoundEvents(self, viewType=None):
        if self.__currentSoundEvent is not None:
            SoundGroups.g_instance.playSound2D(self.__currentSoundEvent.replace(WitchesMetaEvents.ENTER, WitchesMetaEvents.EXIT))
            self.__currentSoundEvent = None
        if viewType is None:
            return
        else:
            state = str(viewType)
            if state in (PreviewTypeEnum.INTRO.value, PreviewTypeEnum.OUTRO.value):
                event = WitchesMetaEvents.PATTERN.format(phase=int(self.__selectedPhase), view=WitchesMetaEvents.INTRO if state == PreviewTypeEnum.INTRO.value else WitchesMetaEvents.OUTRO, state=WitchesMetaEvents.ENTER)
                SoundGroups.g_instance.playSound2D(event)
                self.__currentSoundEvent = event
            elif state == PreviewTypeEnum.WITCHES.value:
                SoundGroups.g_instance.playSound2D(WITCHES_VIEW_OPENED)
            return


class PreviewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, selectedPhase=0, parent=None, onClose=None, *args, **kwargs):
        super(PreviewWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN, content=PreviewView(selectedPhase=selectedPhase, onClose=onClose, *args, **kwargs), layer=WindowLayer.FULLSCREEN_WINDOW, parent=parent)

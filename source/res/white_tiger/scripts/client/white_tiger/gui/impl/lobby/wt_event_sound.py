# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_event_sound.py
import Math
import WWISE
import SoundGroups
from cgf_components import sound_helpers
from cgf_obsolete_script.py_component import Component
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager, SoundManagerStates
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_portal_model import PortalType
from white_tiger.gui.impl.lobby.wt_event_constants import WhiteTigerLootBoxes
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import IWhiteTigerController
from skeletons.gui.shared import IItemsCache
_EVENT_CUSTOM_SOUND_BANK_SET = 'white_tiger_2022'

class _WTEventLootboxPortalTypeStates(CONST_CONTAINER):
    GROUP = 'STATE_white_tiger_lootbox'
    HUNTER_PORTAL = 'STATE_white_tiger_lootbox_portal_01'
    BOSS_PORTAL = 'STATE_white_tiger_lootbox_portal_02'
    TANK_PORTAL = 'STATE_white_tiger_lootbox_portal_03'
    HUNTER_PORTAL_EVENT = 'ev_white_tiger_hangar_lootbox_portal_01_enter'
    BOSS_PORTAL_EVENT = 'ev_white_tiger_hangar_lootbox_portal_02_enter'
    TANK_PORTAL_EVENT = 'ev_white_tiger_hangar_lootbox_portal_03_enter'
    PORTAL_GENERAL = 'STATE_white_tiger_lootbox_portal_general'
    LOOTBOX_BACK_TO_PORTALS = 'ev_white_tiger_hangar_lootbox_portals_exit'
    PORTALS = {PortalType.HUNTER: HUNTER_PORTAL,
     PortalType.BOSS: BOSS_PORTAL,
     PortalType.TANK: TANK_PORTAL}
    PORTAL_EVENTS = {PortalType.HUNTER: HUNTER_PORTAL_EVENT,
     PortalType.BOSS: BOSS_PORTAL_EVENT,
     PortalType.TANK: TANK_PORTAL_EVENT}


class _WTEventLootboxPortalStates(CONST_CONTAINER):
    GROUP = 'STATE_hangar_place'
    LOOTBOX_PORTAL_ENTER_EVENT = 'ev_white_tiger_hangar_lootbox_enter'
    LOOTBOX_PORTAL_EXIT_EVENT = 'ev_white_tiger_hangar_lootbox_exit'
    LOOTBOX_PORTAL_ENTER = 'STATE_hangar_place_lootboxes'


class _WTEventLootboxPortalAwards(CONST_CONTAINER):
    GROUP = 'STATE_overlay_hangar_general'
    LOOTBOX_ITEM = 'ev_white_tiger_hangar_lootbox_item'
    LOOTBOX_ITEM_LAUNCH_MASS = 'ev_white_tiger_hangar_lootbox_launch_mass'
    LOOTBOX_ITEM_VEHICLE = 'ev_white_tiger_hangar_lootbox_video_tank_01'
    ENTER_AWARDS_STATE = 'STATE_overlay_hangar_general_on'
    EXIT_AWARDS_STATE = 'STATE_overlay_hangar_general_off'


class _WTEventPortalVideos(CONST_CONTAINER):
    GROUP = ''
    PLAY = 'STATE_video_overlay_on'
    STOP = 'STATE_video_overlay_off'
    VIDEO_1 = 'ev_white_tiger_hangar_lootbox_launch_video_01'
    VIDEO_2 = 'ev_white_tiger_hangar_lootbox_launch_video_02'
    VIDEO_3 = 'ev_white_tiger_hangar_lootbox_launch_video_03'


class _WTEventSounds(CONST_CONTAINER):
    HANGAR_ENTER = 'ev_white_tiger_hangar_enter'
    HANGAR_EXIT = 'ev_white_tiger_hangar_exit'
    CAMERA_FLY_FORWARD = 'ev_white_tiger_hangar_camera_fly_forward'
    CAMERA_FLY_BACKWARD = 'ev_white_tiger_hangar_camera_fly_backward'
    PROGRESSION_ENTER = 'ev_white_tiger_hangar_collections_enter'
    PROGRESSION_EXIT = 'ev_white_tiger_hangar_collections_exit'
    PROGRESSION_LEVEL_CHANGED = 'bp_improved_reward'
    PROGRESSION_PROGRESS_BAR_START = 'ev_white_tiger_hangar_ui_progress_bar_start'
    PROGRESSION_PROGRESS_BAR_STOP = 'ev_white_tiger_hangar_ui_progress_bar_stop'
    BOSS_WIDGET_APPEARS = 'ev_white_tiger_widget_icon_generator_01'


class WTEventAwardsScreenSound(CONST_CONTAINER):
    _COLLECTION_PROGRESS = 'ev_white_tiger_hangar_lootbox_collections'
    _COLLECTION_DONE = 'ev_white_tiger_hangar_lootbox_collection_all'
    _SCREEN_CLOSED = 'ev_white_tiger_hangar_lootbox_collections_close'

    @classmethod
    def playProgressionProgressSound(cls):
        sound_helpers.play2d(cls._COLLECTION_PROGRESS)

    @classmethod
    def playProgressionDoneSound(cls):
        sound_helpers.play2d(cls._COLLECTION_DONE)

    @classmethod
    def playProgressionClosed(cls):
        sound_helpers.play2d(cls._SCREEN_CLOSED)


class WTEventAwardsScreenVideoSound(CONST_CONTAINER):
    _PORTAL_TO_SOUND = {WhiteTigerLootBoxes.WT_HUNTER: 'ev_white_tiger_hangar_lootbox_launch_video_01',
     WhiteTigerLootBoxes.WT_BOSS: 'ev_white_tiger_hangar_lootbox_launch_video_02'}

    @classmethod
    def playVideoSound(cls, lbType):
        evt = cls._PORTAL_TO_SOUND.get(lbType)
        if evt:
            sound_helpers.play2d(evt)


class WTEventHangarEnterSound(object):

    def __init__(self):
        self.__isSelected = False

    def clear(self):
        self.__isSelected = False

    def update(self, isSelected):
        if isSelected != self.__isSelected:
            self.__isSelected = isSelected
            self.__playSound()

    def onDisconnected(self):
        self.loadEventCustomSoundBanks(False)

    def loadEventCustomSoundBanks(self, load=True):
        if load:
            WWISE.WW_loadCustomSoundBanks(_EVENT_CUSTOM_SOUND_BANK_SET)
        else:
            WWISE.WW_unloadCustomSoundBanks()

    def __playSound(self):
        if self.__isSelected:
            self.loadEventCustomSoundBanks()
            sound_helpers.play2d(_WTEventSounds.HANGAR_ENTER)
        else:
            sound_helpers.play2d(_WTEventSounds.HANGAR_EXIT)
            self.loadEventCustomSoundBanks(False)


class LootBoxAreaSound(object):

    def __init__(self):
        super(LootBoxAreaSound, self).__init__()
        self.__isInAreaNow = False

    def enter(self):
        if not self.__isInAreaNow:
            self.__isInAreaNow = True
            WWISE.WW_setState(_WTEventLootboxPortalTypeStates.GROUP, _WTEventLootboxPortalTypeStates.PORTAL_GENERAL)
            sound_helpers.play2d(_WTEventLootboxPortalStates.LOOTBOX_PORTAL_ENTER_EVENT)

    def leave(self):
        if self.__isInAreaNow:
            self.__isInAreaNow = False
            sound_helpers.play2d(_WTEventLootboxPortalStates.LOOTBOX_PORTAL_EXIT_EVENT)


class _SoundComponent(Component):

    def __init__(self, soundTargetNode, eventID, soundObjectName):
        self.__soundObject = SoundGroups.g_instance.WWgetSoundObject(soundObjectName, Math.Matrix(soundTargetNode))
        self.__eventID = eventID

    def deactivate(self):
        self.stop()
        super(_SoundComponent, self).deactivate()

    def destroy(self):
        self.stop()
        self.__soundObject.stopAll()
        self.__soundObject = None
        return

    def play(self):
        if self.__soundObject is not None:
            self.__soundObject.play(self.__eventID)
        return

    def stop(self):
        if self.__soundObject is not None:
            self.__soundObject.stopAll()
        return


class _TicketSoundComponent(_SoundComponent):
    __evtCtrl = dependency.descriptor(IWhiteTigerController)

    def __init__(self, soundTargetNode, eventID, soundObjectName):
        super(_TicketSoundComponent, self).__init__(soundTargetNode, eventID, soundObjectName)
        self.__hasTickets = False

    def play(self):
        self.__hasTickets = self.__evtCtrl.getTicketCount() > 0
        if self.__hasTickets:
            super(_TicketSoundComponent, self).play()
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})

    def stop(self):
        super(_TicketSoundComponent, self).stop()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onTokensUpdate(self, diff):
        config = self.__evtCtrl.getConfig()
        if config.ticketToken in diff:
            newHasTicketsVal = self.__evtCtrl.getTicketCount() > 0
            if self.__hasTickets != newHasTicketsVal:
                self.__hasTickets = newHasTicketsVal
                if self.__hasTickets:
                    self.play()
                else:
                    self.stop()


class WTEventVehicleSoundPlayer(object):
    _SOUND_MAPPING = {'ussr:R97_Object_140_hound_TLXXL': (_SoundComponent, ('ev_white_tiger_hangar_electric_substance_Ob140', 'SoundObject_Ob140')),
     'france:F18_Bat_Chatillon25t_hound_TLXXL': (_SoundComponent, ('ev_white_tiger_hangar_electric_substance_B25t', 'SoundObject_B25t')),
     'usa:A120_M48A5_hound_TLXXL': (_SoundComponent, ('ev_white_tiger_hangar_electric_substance_M48P', 'SoundObject_M48P')),
     'czech:Cz04_T50_51_Waf_Hound_3DSt': (_SoundComponent, ('ev_white_tiger_hangar_electric_substance_TVP', 'SoundObject_TVP')),
     'germany:G98_Waffentrager_E100_TLXXL': (_TicketSoundComponent, ('ev_white_tiger_hangar_electric_substance_wt', 'SoundObject_E100_TLXXL')),
     'germany:G98_Waffentrager_E100_TLXXL_S': (_SoundComponent, ('ev_white_tiger_hangar_electric_substance_wt', 'SoundObject_E100_TLXXL_S'))}
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self._soundComponents = {}
        self.__currentTypeDescriptorName = None
        return

    def playSound(self, targetNode, newVehName):
        if self.__currentTypeDescriptorName != newVehName:
            if self.__currentTypeDescriptorName:
                self.stopSound(self.__currentTypeDescriptorName)
            self.__currentTypeDescriptorName = newVehName
            soundComponent = self.__getSoundComponent(targetNode, newVehName)
            soundComponent.play()

    def stopSound(self, vehName):
        self.__currentTypeDescriptorName = None
        soundComponent = self._soundComponents.get(vehName)
        if soundComponent:
            soundComponent.stop()
        return

    def stopAll(self):
        self.__currentTypeDescriptorName = None
        for soundComponent in self._soundComponents.itervalues():
            soundComponent.stop()

        return

    def destroy(self):
        for soundComponent in self._soundComponents.itervalues():
            soundComponent.destroy()

        self._soundComponents = {}

    def __getSoundComponent(self, targetNode, vehName):
        if vehName not in self._soundComponents:
            cmpClass, cmpArgs = self._SOUND_MAPPING[vehName]
            self._soundComponents[vehName] = cmpClass(targetNode, *cmpArgs)
        return self._soundComponents[vehName]


class WhiteTigerCutSceneSounds(CONST_CONTAINER):
    VIDEO_INTRO = 'ev_white_tiger_cutscene_intro'
    VIDEO_OUTRO = 'ev_white_tiger_cutscene_outro'
    VIDEO_PAUSE = 'ev_white_tiger_cutscene_pause'
    VIDEO_RESUME = 'ev_white_tiger_cutscene_resume'
    VIDEO_STOP = 'ev_white_tiger_cutscene_stop'


class WhiteTigerCutSceneVideoSoundControl(IVideoSoundManager):
    __VIDEO_TO_SOUND = {'wt_intro': WhiteTigerCutSceneSounds.VIDEO_INTRO,
     'wt_outro': WhiteTigerCutSceneSounds.VIDEO_OUTRO}

    def __init__(self, videoID):
        self.__videoID = videoID
        self.__state = None
        return

    def start(self):
        sound = self.__VIDEO_TO_SOUND.get(self.__videoID, None)
        if sound and not self.__state:
            WWISE.WW_eventGlobal(sound)
            self.__state = SoundManagerStates.PLAYING
        return

    def stop(self):
        if self.__state != SoundManagerStates.STOPPED:
            WWISE.WW_eventGlobal(WhiteTigerCutSceneSounds.VIDEO_STOP)
            self.__state = SoundManagerStates.STOPPED

    def pause(self):
        WWISE.WW_eventGlobal(WhiteTigerCutSceneSounds.VIDEO_PAUSE)
        self.__state = SoundManagerStates.PAUSE

    def unpause(self):
        WWISE.WW_eventGlobal(WhiteTigerCutSceneSounds.VIDEO_RESUME)
        self.__state = SoundManagerStates.PLAYING


class WhiteTigerVehicleAwardViewSounds(CONST_CONTAINER):
    VIDEO_START = 'ev_white_tiger_portal_video_start'
    VIDEO_PAUSE = 'ev_white_tiger_portal_video_pause'
    VIDEO_RESUME = 'ev_white_tiger_portal_video_resume'
    VIDEO_STOP = 'ev_white_tiger_portal_video_stop'


class WhiteTigerVehicleAwardViewSoundControl(IVideoSoundManager):

    def __init__(self):
        super(WhiteTigerVehicleAwardViewSoundControl, self).__init__()
        self.__state = None
        return

    def start(self):
        if not self.__state:
            sound = WhiteTigerVehicleAwardViewSounds.VIDEO_START
            WWISE.WW_eventGlobal(sound)
            self.__state = SoundManagerStates.PLAYING

    def stop(self):
        if self.__state != SoundManagerStates.STOPPED:
            sound = WhiteTigerVehicleAwardViewSounds.VIDEO_STOP
            WWISE.WW_eventGlobal(sound)
            self.__state = SoundManagerStates.STOPPED

    def pause(self):
        sound = WhiteTigerVehicleAwardViewSounds.VIDEO_PAUSE
        WWISE.WW_eventGlobal(sound)
        self.__state = SoundManagerStates.PAUSE

    def unpause(self):
        sound = WhiteTigerVehicleAwardViewSounds.VIDEO_RESUME
        WWISE.WW_eventGlobal(sound)
        self.__state = SoundManagerStates.PLAYING


def playLootBoxPortalExit():
    WWISE.WW_setState(_WTEventLootboxPortalTypeStates.GROUP, _WTEventLootboxPortalTypeStates.PORTAL_GENERAL)
    WWISE.WW_setState(_WTEventLootboxPortalStates.GROUP, _WTEventLootboxPortalStates.LOOTBOX_PORTAL_ENTER)
    sound_helpers.play2d(_WTEventLootboxPortalTypeStates.LOOTBOX_BACK_TO_PORTALS)


def playLootBoxAwardsReceived(count):
    if count > 1:
        sound_helpers.play2d(_WTEventLootboxPortalAwards.LOOTBOX_ITEM_LAUNCH_MASS)


def playLootBoxAwardsExit():
    pass


def changePortalState(portalType):
    WWISE.WW_setState(_WTEventLootboxPortalTypeStates.GROUP, _WTEventLootboxPortalTypeStates.PORTALS[portalType])
    sound_helpers.play2d(_WTEventLootboxPortalTypeStates.PORTAL_EVENTS[portalType])


def playProgressionViewEnter():
    sound_helpers.play2d(_WTEventSounds.PROGRESSION_ENTER)


def playProgressionLevelChanged():
    sound_helpers.play2d(_WTEventSounds.PROGRESSION_LEVEL_CHANGED)


def playProgressionViewExit():
    sound_helpers.play2d(_WTEventSounds.PROGRESSION_EXIT)


def playHangarCameraFly(forward=True):
    if forward:
        sound_helpers.play2d(_WTEventSounds.CAMERA_FLY_FORWARD)
    else:
        sound_helpers.play2d(_WTEventSounds.CAMERA_FLY_BACKWARD)


def playProgressBarGrowing(isGrowing):
    if isGrowing:
        sound_helpers.play2d(_WTEventSounds.PROGRESSION_PROGRESS_BAR_START)
    else:
        sound_helpers.play2d(_WTEventSounds.PROGRESSION_PROGRESS_BAR_STOP)


def playBossWidgetAppears():
    sound_helpers.play2d(_WTEventSounds.BOSS_WIDGET_APPEARS)


def playVehicleAwardReceivedFromPortal():
    sound_helpers.play2d(_WTEventLootboxPortalAwards.LOOTBOX_ITEM_VEHICLE)

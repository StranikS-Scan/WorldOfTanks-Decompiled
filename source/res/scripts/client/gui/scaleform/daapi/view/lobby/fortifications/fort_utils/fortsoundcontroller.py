# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/fort_utils/FortSoundController.py
import BigWorld
from ClientFortifiedRegion import BUILDING_UPDATE_REASON
import MusicController
import SoundGroups
import FMOD
from constants import FORT_BUILDING_TYPE
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.app_loader.decorators import sf_lobby
from gui.shared.SoundEffectsId import SoundEffectsId
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
if FMOD.enabled:
    PARAM_NAME_BUILDING_NUMBER = 'buildings_number'
    PARAM_NAME_TRANSPORT_MODE = 'transport_mode'
    PARAM_NAME_DEFENCE_PERIOD = 'defence_period'

class _FortSoundController(FortViewHelper):

    @sf_lobby
    def app(self):
        return None

    def init(self):
        SoundGroups.g_instance.onVolumeChanged += self.__onVolumeChanged
        self.startFortListening()
        if FMOD.enabled:
            BigWorld.wg_setCategoryVolume('hangar_v2', 0.0)
        MusicController.g_musicController.stop()
        params = {PARAM_NAME_BUILDING_NUMBER: 0,
         PARAM_NAME_TRANSPORT_MODE: 0,
         PARAM_NAME_DEFENCE_PERIOD: 0}
        MusicController.g_musicController.play(MusicController.AMBIENT_EVENT_LOBBY_FORT, params)

    def fini(self):
        if FMOD.enabled:
            BigWorld.wg_setCategoryVolume('hangar_v2', SoundGroups.g_instance.getVolume('ambient'))
        MusicController.g_musicController.stop()
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOBBY)
        MusicController.g_musicController.play(MusicController.AMBIENT_EVENT_LOBBY)
        self.stopFortListening()
        SoundGroups.g_instance.onVolumeChanged -= self.__onVolumeChanged

    def onClientStateChanged(self, state):
        if state.getStateID() in (CLIENT_FORT_STATE.WIZARD, CLIENT_FORT_STATE.HAS_FORT):
            self.setBuildingsMode()

    def onBuildingChanged(self, buildingTypeID, reason, ctx = None):
        if reason == BUILDING_UPDATE_REASON.UPDATED:
            self.setBuildingsMode()
        elif reason == BUILDING_UPDATE_REASON.COMPLETED:
            self.setBuildingsMode()
        elif reason == BUILDING_UPDATE_REASON.DELETED:
            self.setBuildingsMode()

    def onDefenceHourStateChanged(self):
        self.setDefencePeriodMode()

    def setTransportingMode(self, enabled):
        MusicController.g_musicController.setEventParam(MusicController.AMBIENT_EVENT_LOBBY_FORT, PARAM_NAME_TRANSPORT_MODE, int(enabled))

    def setBuildingsMode(self):
        fort = self.fortCtrl.getFort()
        MusicController.g_musicController.setEventParam(MusicController.AMBIENT_EVENT_LOBBY_FORT, PARAM_NAME_BUILDING_NUMBER, len(fort.getBuildingsCompleted(FORT_BUILDING_TYPE.MILITARY_BASE)))

    def setDefencePeriodMode(self):
        fort = self.fortCtrl.getFort()
        MusicController.g_musicController.setEventParam(MusicController.AMBIENT_EVENT_LOBBY_FORT, PARAM_NAME_DEFENCE_PERIOD, int(fort.isOnDefenceHour()))

    def playCreateFort(self):
        self.__playSound(SoundEffectsId.FORT_CREATE)

    def playDeleteBuilding(self):
        self.__playSound(SoundEffectsId.FORT_DEMOUNT_BUILDING)

    def playCompletedBuilding(self, uid):
        self.__playSound(SoundEffectsId.getEndBuildingProcess(uid))

    def playCreateBuilding(self):
        self.__playSound(SoundEffectsId.FORT_ENTERED_FOUNDATION_STATE)

    def playUpgradeBuilding(self):
        self.__playSound(SoundEffectsId.FORT_UPGRADE_BUILDING)

    def playAttachedToBuilding(self):
        self.__playSound(SoundEffectsId.FORT_FIXED_IN_BUILDING)

    def playDeleteDirection(self):
        self.__playSound(SoundEffectsId.FORT_DIRECTION_CLOSE)

    def playCreateDirection(self):
        self.__playSound(SoundEffectsId.FORT_DIRECTION_CREATE)

    def playCreateOrder(self):
        self.__playSound(SoundEffectsId.FORT_ORDER_INPROGRESS)

    def playReadyOrder(self):
        self.__playSound(SoundEffectsId.FORT_ORDER_ISREADY)

    def playActivateOrder(self, orderID):
        self.__playSound('activate_' + orderID)

    def playEnterTransport(self):
        self.__playSound(SoundEffectsId.TRANSPORT_ENTER)

    def playExitTransport(self):
        self.__playSound(SoundEffectsId.TRANSPORT_EXIT)

    def playFirstStepTransport(self):
        self.__playSound(SoundEffectsId.TRANSPORT_FIRST_STEP)

    def playNextStepTransport(self):
        self.__playSound(SoundEffectsId.TRANSPORT_NEXT_STEP)

    def playStartTransport(self):
        self.__playSound(SoundEffectsId.TRANSPORT_APPROVE)

    def playDefencePeriodActivated(self):
        self.__playSound(SoundEffectsId.ACTIVATE_DEFENCE_PERIOD)

    def playDefencePeriodDeactivated(self):
        self.__playSound(SoundEffectsId.DEACTIVATE_DEFENCE_PERIOD)

    def playBattleRoomTimerAlert(self):
        self.__playSound(SoundEffectsId.BATTLE_ROOM_TIMER_ALERT)

    def playEnemyDirectionHover(self):
        self.__playSound(SoundEffectsId.ENEMY_DIRECTION_HOVER)

    def playEnemyDirectionSelected(self):
        self.__playSound(SoundEffectsId.ENEMY_DIRECTION_SELECTED)

    def playMyDirectionSelected(self):
        self.__playSound(SoundEffectsId.MY_DIRECTION_SELECTED)

    def playFortClanWarDeclared(self):
        self.__playSound(SoundEffectsId.FORT_CLAN_WAR_DECLARED)

    def playFortClanWarResult(self, result):
        self.__playSound('fortClanWarResult_' + result)

    def __playSound(self, soundID):
        app = self.app
        if app is not None and app.soundManager is not None:
            app.soundManager.playEffectSound(soundID)
        return

    def __onVolumeChanged(self, categoryName, volume):
        if categoryName == 'ambient':
            if FMOD.enabled:
                BigWorld.wg_setCategoryVolume('hangar_v2', 0)


g_fortSoundController = _FortSoundController()

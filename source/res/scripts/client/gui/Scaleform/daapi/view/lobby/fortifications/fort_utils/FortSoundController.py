# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/fort_utils/FortSoundController.py
from gui.app_loader.decorators import sf_lobby
from gui.shared.SoundEffectsId import SoundEffectsId

class _FortSoundController(object):

    @sf_lobby
    def app(self):
        return None

    def init(self):
        pass

    def fini(self):
        pass

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


g_fortSoundController = _FortSoundController()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DGSoundAbstractComponent.py
import enum
import typing
import BigWorld
from dyn_components_groups import groupComponent
from script_component.DynamicScriptComponent import DynamicScriptComponent
from xml_config_specs import StrParam, EnumParam, ListParam, ObjParam

@enum.unique
class DGSoundComponentPlayMode(str, enum.Enum):
    NONE = 'none'
    SELF = 'self'
    OTHERS = 'others'
    ALL = 'all'


@groupComponent(soundEvents=ListParam(valueParam=ObjParam(activation=StrParam(), deactivation=StrParam(), playTo=EnumParam(enum=DGSoundComponentPlayMode, default=DGSoundComponentPlayMode.SELF))))
class DGSoundAbstractComponent(DynamicScriptComponent):

    def __init__(self, *_, **__):
        super(DGSoundAbstractComponent, self).__init__()
        self._activationIsPlayed = False

    def onDestroy(self):
        if self._activationIsPlayed:
            for config in self.groupComponentConfig.soundEvents:
                self._playSound(config.playTo, config.deactivation)

        super(DGSoundAbstractComponent, self).onDestroy()

    def _onAvatarReady(self):
        self._activationIsPlayed = True
        for config in self.groupComponentConfig.soundEvents:
            self._playSound(config.playTo, config.activation)

    def _isPlayerVehicle(self):
        avatar = BigWorld.player()
        return False if not avatar else self.entity.id == avatar.playerVehicleID

    def _needToPlay(self, param):
        playTo = getattr(DGSoundComponentPlayMode, param.upper())
        if playTo == DGSoundComponentPlayMode.ALL:
            return True
        if playTo == DGSoundComponentPlayMode.SELF and self._isPlayerVehicle():
            return True
        return True if playTo == DGSoundComponentPlayMode.OTHERS and not self._isPlayerVehicle() else False

    def _playSound(self, playTo, soundName):
        if soundName and self._needToPlay(playTo):
            self._play(soundName)

    def _play(self, soundName):
        raise NotImplementedError

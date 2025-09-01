# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSBuffSoundComponent.py
import BigWorld
import enum
import SoundGroups
from dyn_components_groups import groupComponent
from script_component.DynamicScriptComponent import DynamicScriptComponent
from xml_config_specs import StrParam, ListParam, ObjParam

class LSBuffSoundComponentPlayMode(enum.IntEnum):
    NONE = 0
    SELF = 1
    OTHERS = 2
    ALL = 3


@groupComponent(soundEvents=ListParam(valueParam=ObjParam(activationSound3D=StrParam(), deactivationSound3D=StrParam(), playTo=StrParam(default='self'), activationSound2D=StrParam(), deactivationSound2D=StrParam())))
class LSBuffSoundComponent(DynamicScriptComponent):

    def __init__(self, *args, **kwargs):
        super(LSBuffSoundComponent, self).__init__()
        self._activationIsPlayed = False
        if BigWorld.player().userSeesWorld():
            self._playActivation()

    def _onAvatarReady(self):
        if not self._activationIsPlayed:
            self._playActivation()

    def _playActivation(self):
        self._activationIsPlayed = True
        for config in self.groupComponentConfig.soundEvents:
            if self._needToPlay(config.playTo):
                if config.activationSound3D and self.soundObject:
                    self.soundObject.play(config.activationSound3D)
                if config.activationSound2D:
                    SoundGroups.g_instance.playSound2D(config.activationSound2D)

    def onDestroy(self):
        if self._activationIsPlayed:
            for config in self.groupComponentConfig.soundEvents:
                if self._needToPlay(config.playTo):
                    if config.deactivationSound3D and self.soundObject:
                        self.soundObject.play(config.deactivationSound3D)
                    if config.deactivationSound2D:
                        SoundGroups.g_instance.playSound2D(config.deactivationSound2D)

        super(LSBuffSoundComponent, self).onDestroy()

    @property
    def soundObject(self):
        comp = self.entity.dynamicComponents.get('LSVehicleSoundComponent')
        return comp.soundObject if comp else None

    def _isVehicleObservedByAvatar(self):
        avatar = BigWorld.player()
        return False if not avatar else self.entity.id == avatar.playerVehicleID

    def _needToPlay(self, param):
        playTo = getattr(LSBuffSoundComponentPlayMode, param.upper())
        if playTo == LSBuffSoundComponentPlayMode.ALL:
            return True
        if playTo == LSBuffSoundComponentPlayMode.SELF and self._isVehicleObservedByAvatar():
            return True
        return True if playTo == LSBuffSoundComponentPlayMode.OTHERS and not self._isVehicleObservedByAvatar() else False

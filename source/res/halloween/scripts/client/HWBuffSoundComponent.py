# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWBuffSoundComponent.py
from __future__ import absolute_import
import BigWorld
import enum
import SoundGroups
from dyn_components_groups import groupComponent
from script_component.DynamicScriptComponent import DynamicScriptComponent
from xml_config_specs import StrParam, ListParam, ObjParam, BoolParam

class HWBuffSoundComponentPlayMode(enum.IntEnum):
    NONE = 0
    SELF = 1
    OTHERS = 2
    ALL = 3


_INTERNAL_OBJ_NAME_PATTER = 'HWBuffSoundComponent:{}'

@groupComponent(soundEvents=ListParam(valueParam=ObjParam(activationSound3D=StrParam(), deactivationSound3D=StrParam(), playTo=StrParam(default='self'), activationSound2D=StrParam(), deactivationSound2D=StrParam(), playSoundPos=StrParam())), createSoundObject=BoolParam())
class HWBuffSoundComponent(DynamicScriptComponent):

    def __init__(self, *args, **kwargs):
        super(HWBuffSoundComponent, self).__init__()
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
                if config.playSoundPos:
                    SoundGroups.g_instance.playSoundPos(config.playSoundPos, self.entity.position)

    def onDestroy(self):
        if self._activationIsPlayed:
            for config in self.groupComponentConfig.soundEvents:
                if self._needToPlay(config.playTo):
                    if config.deactivationSound3D and self.soundObject:
                        self.soundObject.play(config.deactivationSound3D)
                    if config.deactivationSound2D:
                        SoundGroups.g_instance.playSound2D(config.deactivationSound2D)

        if self.groupComponentConfig.createSoundObject and hasattr(self, '_soundObjectInternal'):
            self._soundObjectInternal.stopAll()
            self._soundObjectInternal = None
        super(HWBuffSoundComponent, self).onDestroy()
        return

    @property
    def soundObject(self):
        if self.groupComponentConfig.createSoundObject:
            if not hasattr(self, '_soundObjectInternal'):
                self._soundObjectInternal = SoundGroups.g_instance.WWgetSoundObject(_INTERNAL_OBJ_NAME_PATTER.format(self.entity.id), self.entity.matrix)
            return self._soundObjectInternal
        else:
            comp = self.entity.dynamicComponents.get('HWVehicleSoundComponent')
            return comp.soundObject if comp else None

    def _isVehicleObservedByAvatar(self):
        avatar = BigWorld.player()
        return False if not avatar else self.entity.id == avatar.playerVehicleID

    def _needToPlay(self, param):
        playTo = getattr(HWBuffSoundComponentPlayMode, param.upper())
        if playTo == HWBuffSoundComponentPlayMode.ALL:
            return True
        if playTo == HWBuffSoundComponentPlayMode.SELF and self._isVehicleObservedByAvatar():
            return True
        return True if playTo == HWBuffSoundComponentPlayMode.OTHERS and not self._isVehicleObservedByAvatar() else False

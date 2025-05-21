# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSBuffDissolveComponent.py
import weakref
import BigWorld
from dyn_components_groups import groupComponent
from script_component.DynamicScriptComponent import DynamicScriptComponent
from xml_config_specs import FloatParam
from functools import partial
from math_utils import clamp, clamp01

class DissolveUpdater(object):
    __slots__ = ('dissolveHandler', 'componentRef', 'entityRef', 'appearanceRef', 'dissolveFactor', 'fadeInTime', 'fadeOutTime', 'maxDissolveFactor')
    UPDATE_RATE = 0.05

    def __init__(self, componentRef, entityRef, appearanceRef, dissolveFactor, fadeInTime, fadeOutTime, maxDissolveFactor):
        super(DissolveUpdater, self).__init__()
        self.dissolveHandler = BigWorld.PyDissolveHandler()
        self.componentRef = componentRef
        self.entityRef = entityRef
        self.appearanceRef = appearanceRef
        self.dissolveFactor = clamp01(dissolveFactor)
        self.fadeInTime = max(0.0001, fadeInTime)
        self.fadeOutTime = max(0.0001, fadeOutTime)
        self.maxDissolveFactor = clamp01(maxDissolveFactor)

    def start(self):
        appearance = self.appearanceRef()
        for fashion in appearance.fashions:
            if not fashion:
                continue
            fashion.addMaterialHandler(self.dissolveHandler)
            fashion.addTrackMaterialHandler(self.dissolveHandler)

        self.dissolveHandler.setEnabled(True)
        DissolveUpdater._updateDissolve(self)

    def stop(self):
        if not self.appearanceRef():
            return
        else:
            self.dissolveHandler.setEnabled(False)
            for fashion in self.appearanceRef().fashions:
                if not fashion:
                    continue
                fashion.removeMaterialHandler(self.dissolveHandler)

            self.dissolveHandler = None
            return

    @classmethod
    def _updateDissolve(cls, updater):
        if updater.entityRef() is None or updater.entityRef().isDestroyed or updater.entityRef().health <= 0:
            updater.stop()
            return
        else:
            prevFactor = updater.dissolveFactor
            velocity = updater.maxDissolveFactor / updater.fadeInTime if updater.componentRef() else -updater.maxDissolveFactor / updater.fadeOutTime
            updater.dissolveFactor = clamp(0.0, updater.maxDissolveFactor, updater.dissolveFactor + cls.UPDATE_RATE * velocity)
            if prevFactor != updater.dissolveFactor:
                updater.dissolveHandler.setDissolveFactor(updater.dissolveFactor)
            if not updater.componentRef() and updater.dissolveFactor <= 0.0:
                updater.stop()
                return
            BigWorld.callback(cls.UPDATE_RATE, partial(cls._updateDissolve, updater))
            return


@groupComponent(fadeInTime=FloatParam(1.0), fadeOutTime=FloatParam(1.0), maxDissolveFactor=FloatParam(1.0))
class LSBuffDissolveComponent(DynamicScriptComponent):

    def _onAvatarReady(self):
        super(LSBuffDissolveComponent, self)._onAvatarReady()
        appearance = self.entity.appearance
        if appearance is None:
            self.entity.onAppearanceReady += self._onAppearanceReady
        elif not appearance.damageState.isCurrentModelDamaged:
            self._onAppearanceReady()
        return

    def onDestroy(self):
        self.entity.onAppearanceReady -= self._onAppearanceReady

    def _onAppearanceReady(self):
        appearance = self.entity.appearance
        self.entity.onAppearanceReady -= self._onAppearanceReady
        if appearance.damageState.isCurrentModelDamaged:
            return
        DissolveUpdater(componentRef=weakref.ref(self), entityRef=weakref.ref(self.entity), appearanceRef=weakref.ref(appearance), dissolveFactor=0.0, fadeInTime=self.groupComponentConfig.fadeInTime, fadeOutTime=self.groupComponentConfig.fadeOutTime, maxDissolveFactor=self.groupComponentConfig.maxDissolveFactor).start()

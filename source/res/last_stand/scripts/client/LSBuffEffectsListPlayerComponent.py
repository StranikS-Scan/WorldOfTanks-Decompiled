# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSBuffEffectsListPlayerComponent.py
import ResMgr
from functools import partial
from dyn_components_groups import groupComponent
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
from last_stand.ls_buff_effect_component_common import LSBuffEffectComponentCommon
from xml_config_specs import StrParam, ListParam, ObjParam
from helpers.CallbackDelayer import CallbackDelayer
_START_EFFECTS_DELAY = 0.1

@groupComponent(effects=ListParam(valueParam=ObjParam(effect=StrParam(), visibleTo=StrParam(default='all'), sniperModeVisibleTo=StrParam(default='all'))))
class LSBuffEffectsListPlayerComponent(LSBuffEffectComponentCommon):

    def __init__(self):
        super(LSBuffEffectsListPlayerComponent, self).__init__()
        self._callbackDelayer = CallbackDelayer()
        count = len(self.groupComponentConfig.effects)
        self.__playerEffects = [None] * count
        self._effectsHideInSniperMode = []
        return

    def onDestroy(self):
        super(LSBuffEffectsListPlayerComponent, self).onDestroy()
        self._callbackDelayer.destroy()
        self.__playerEffects = []
        self._effectsHideInSniperMode = []

    @property
    def _componentConfigs(self):
        return self.groupComponentConfig.effects

    def _activateEffects(self):
        appearance = self.entity.appearance
        if appearance is None or not appearance.isConstructed:
            return
        else:
            self._callbackDelayer.clearCallbacks()
            self._effectsHideInSniperMode = []
            effectsToStart = []
            for i, effect in enumerate(self.__playerEffects):
                config = self.groupComponentConfig.effects[i]
                if not config.effect or not self._isVisible(config.visibleTo):
                    if effect is not None:
                        effect.stop()
                        self.__playerEffects[i] = None
                    continue
                if effect is not None:
                    if self._needsListenToSniperMode(config.sniperModeVisibleTo):
                        self._effectsHideInSniperMode.append(effect)
                    continue
                section = ResMgr.openSection(config.effect)
                effectData = effectsFromSection(section)
                effect = EffectsListPlayer(effectData.effectsList, effectData.keyPoints, debugParent=self)
                self.__playerEffects[i] = effect
                effectsToStart.append(i)

            if effectsToStart:
                self._callbackDelayer.delayCallback(_START_EFFECTS_DELAY, partial(self.__activateEffectsDelayed, effectsToStart))
            return

    def _deactivateEffects(self):
        self._callbackDelayer.clearCallbacks()
        for i, effect in enumerate(self.__playerEffects):
            if effect is not None:
                effect.stop()
                self.__playerEffects[i] = None

        return

    def _onSniperModeChanged(self, isEnabled):
        for effect in self._effectsHideInSniperMode:
            if isEnabled:
                effect.stop()
            effect.play(self.entity.appearance.compoundModel)

    def __activateEffectsDelayed(self, effectsToStart):
        for pos in effectsToStart:
            effect = self.__playerEffects[pos]
            config = self.groupComponentConfig.effects[pos]
            if self._needsListenToSniperMode(config.sniperModeVisibleTo):
                self._effectsHideInSniperMode.append(effect)
                if self._isInSniperMode:
                    continue
            effect.play(self.entity.appearance.compoundModel)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/impl/effects.py
import typing
import logging
from gui.Scaleform.genConsts.TUTORIAL_EFFECT_TYPES import TUTORIAL_EFFECT_TYPES
from gui.impl.gen.view_models.common.tutorial.visible_effect_model import VisibleEffectModel
from gui.impl.gen.view_models.common.tutorial.enabled_effect_model import EnabledEffectModel
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.common.tutorial.effect_model import EffectModel
_logger = logging.getLogger(__name__)

class IEffectsFactory(object):

    def createEffect(self, effectType):
        raise NotImplementedError

    def updateEffect(self, effect, effectData):
        raise NotImplementedError


class Factory(IEffectsFactory):
    __slots__ = ('__effectsMap', '__updatersMap')

    def __init__(self):
        super(Factory, self).__init__()
        self.__effectsMap = {TUTORIAL_EFFECT_TYPES.DISPLAY: VisibleEffectModel,
         TUTORIAL_EFFECT_TYPES.ENABLED: EnabledEffectModel}
        self.__updatersMap = {TUTORIAL_EFFECT_TYPES.DISPLAY: self.__updateVisibleEffect,
         TUTORIAL_EFFECT_TYPES.ENABLED: self.__updateEnabledEffect}

    def createEffect(self, effectType):
        effect = None
        if effectType in self.__effectsMap:
            effect = self.__effectsMap[effectType]()
            effect.setType(effectType)
        else:
            _logger.error("Can't create effect model by unsupported type: %s", effectType)
        return effect

    def updateEffect(self, effect, effectData):
        effectType = effect.getType()
        if effectType in self.__updatersMap:
            updater = self.__updatersMap[effectType]
            updater(effect, effectData)
        else:
            _logger.error("Can't update unsupported effect, type: %s", effectType)

    @staticmethod
    def __updateVisibleEffect(effect, effectData):
        effect.setVisible(effectData['visible'])

    @staticmethod
    def __updateEnabledEffect(effect, effectData):
        effect.setEnabled(effectData['enabled'])


def getFactory():
    return Factory()

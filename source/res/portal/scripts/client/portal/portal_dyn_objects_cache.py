# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/portal_dyn_objects_cache.py
from dyn_objects_cache import _CommonForBattleRoyaleAndEpicBattleDynObjects, _createTerrainCircleSettings
from dyn_objects_cache import _MinesEffects, _MinesPlantEffect, _MinesDestroyEffect, _TeamRelatedEffect

class _EpicMinesIdleBlueEffect(_TeamRelatedEffect):
    _SECTION_NAME = 'epicMinesIdleBlueEffect'


class PortalDynObjects(_CommonForBattleRoyaleAndEpicBattleDynObjects):

    def __init__(self):
        super(PortalDynObjects, self).__init__()
        self.__minesEffects = None
        self.__influenceZoneCircleEffect = None
        return

    def init(self, dataSection):
        if not self._initialized:
            self.__minesEffects = _MinesEffects(plantEffect=_MinesPlantEffect(dataSection), idleEffect=_EpicMinesIdleBlueEffect(dataSection), destroyEffect=_MinesDestroyEffect(dataSection), blowUpEffectName='epicMinesBlowUpEffect', placeMinesEffect='epicMinesDecalEffect', activationEffect='epicMinesActivationDecalEffect')
            self.__influenceZoneCircleEffect = _createTerrainCircleSettings(dataSection['InfluenceZoneCircleVisual'])
        super(PortalDynObjects, self).init(dataSection)

    def getMinesEffect(self):
        return self.__minesEffects

    def getInfluenceZoneCircleEffect(self):
        return self.__influenceZoneCircleEffect

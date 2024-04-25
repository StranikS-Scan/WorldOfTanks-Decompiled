# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/hb_dyn_objects_cache.py
from dyn_objects_cache import _EpicBattleDynObjects, _createTerrainCircleSettings
from dyn_objects_cache import _MinesEffects, _MinesPlantEffect, _MinesDestroyEffect, _TeamRelatedEffect

class _EpicMinesIdleYellowEffect(_TeamRelatedEffect):
    _SECTION_NAME = 'epicMinesIdleYellowEffect'


class HistoricalBattlesDynObjects(_EpicBattleDynObjects):

    def __init__(self):
        super(HistoricalBattlesDynObjects, self).__init__()
        self.__circleRestrictionEffect = None
        self.__minesYellowEffects = None
        return

    def init(self, dataSection):
        if not self._initialized:
            self.__circleRestrictionEffect = _createTerrainCircleSettings(dataSection['EquipmentCircleRestrictionVisual'])
            self.__minesYellowEffects = _MinesEffects(plantEffect=_MinesPlantEffect(dataSection), idleEffect=_EpicMinesIdleYellowEffect(dataSection), destroyEffect=_MinesDestroyEffect(dataSection), blowUpEffectName='epicMinesBlowUpEffect', placeMinesEffect='epicMinesDecalEffect', activationEffect='epicMinesActivationDecalEffect')
        super(HistoricalBattlesDynObjects, self).init(dataSection)

    def getCircleRestrictionEffect(self):
        return self.__circleRestrictionEffect['ally']

    def getTacticalMinesEffect(self):
        return self.__minesYellowEffects

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/common/fall_tanks_common/items/artefacts.py
import importlib
artefacts = importlib.import_module('items.artefacts')

class FallTanksAbilityDashEquipment(artefacts.VisualScriptEquipment, object):
    __slots__ = ('duration', 'cooldownSeconds')

    @property
    def tooltipParams(self):
        params = super(FallTanksAbilityDashEquipment, self).tooltipParams
        return params

    def _readConfig(self, xmlCtx, section):
        super(FallTanksAbilityDashEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class FallTanksAbilityShieldEquipment(artefacts.VisualScriptEquipment, object):
    __slots__ = ('duration', 'cooldownSeconds')

    @property
    def tooltipParams(self):
        params = super(FallTanksAbilityShieldEquipment, self).tooltipParams
        return params

    def _readConfig(self, xmlCtx, section):
        super(FallTanksAbilityShieldEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()

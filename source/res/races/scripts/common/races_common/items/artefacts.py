# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/common/races_common/items/artefacts.py
import importlib
artefacts = importlib.import_module('items.artefacts')

class RacesShieldEquipment(artefacts.VisualScriptEquipment, object):
    __slots__ = ('duration', 'gravityFactor', 'cooldownSeconds', 'radius')

    @property
    def tooltipParams(self):
        params = super(RacesShieldEquipment, self).tooltipParams
        params['cooldown'] = self.cooldownSeconds
        params['duration'] = self.duration
        params['cooldownSeconds'] = self.cooldownSeconds
        params['radius'] = self.radius
        return params

    def _readConfig(self, xmlCtx, section):
        super(RacesShieldEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.gravityFactor = section.readFloat('gravityFactor')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self.radius = section.readFloat('radius')
        self._exportSlotsToVSE()


class RacesRapidShellingEquipment(artefacts.VisualScriptEquipment, object):
    __slots__ = ('duration', 'shellID', 'shotSpeed', 'gunReloadTime', 'shellingTotalTime')

    @property
    def tooltipParams(self):
        params = super(RacesRapidShellingEquipment, self).tooltipParams
        params['duration'] = self.duration
        params['shellID'] = self.shellID
        params['shotSpeed'] = self.shotSpeed
        return params

    def _readConfig(self, xmlCtx, section):
        super(RacesRapidShellingEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.shellID = section.readInt('shellID')
        self.shotSpeed = section.readInt('shotSpeed')
        self.gunReloadTime = section.readFloat('gunReloadTime')
        self.shellingTotalTime = section.readFloat('shellingTotalTime')
        self._exportSlotsToVSE()


class RacesPowerImpulseEquipment(artefacts.VisualScriptEquipment, object):
    __slots__ = ('radius', 'duration', 'cooldownSeconds', 'power')

    @property
    def tooltipParams(self):
        params = super(RacesPowerImpulseEquipment, self).tooltipParams
        params['radius'] = self.radius
        return params

    def _readConfig(self, xmlCtx, section):
        super(RacesPowerImpulseEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.radius = section.readFloat('radius')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self.power = section.readFloat('power')
        self._exportSlotsToVSE()


class RacesRocketBoosterEquipment(artefacts.VisualScriptEquipment, object):
    __slots__ = ('duration', 'cooldownSeconds')

    @property
    def tooltipParams(self):
        params = super(RacesRocketBoosterEquipment, self).tooltipParams
        return params

    def _readConfig(self, xmlCtx, section):
        super(RacesRocketBoosterEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()

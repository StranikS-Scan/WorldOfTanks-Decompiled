# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/armor/config/models.py
from __future__ import absolute_import
import typing
from dict2model import models

class ColorListModel(models.Model):
    __slots__ = ('normalArmor', 'spacedArmor', 'ricochet', 'noDamage')

    def __init__(self, normalArmor, spacedArmor, ricochet, noDamage):
        super(ColorListModel, self).__init__()
        self.normalArmor = normalArmor
        self.spacedArmor = spacedArmor
        self.ricochet = ricochet
        self.noDamage = noDamage

    def __repr__(self):
        return '<ColorListModel(normalArmor={}, spacedArmor={}, ricochet={}, no_damage={})>'.format(self.normalArmor, self.spacedArmor, self.ricochet, self.noDamage)


class ArmorScaleModel(models.Model):
    __slots__ = ('min', 'max')

    def __init__(self, min, max):
        super(ArmorScaleModel, self).__init__()
        self.min = min
        self.max = max

    def __repr__(self):
        return '<ArmorScaleModel(min={}, max={})>'.format(self.min, self.max)


class TierModel(models.Model):
    __slots__ = ('number', 'normalArmor', 'spacedArmor', 'defaultVehicle')

    def __init__(self, number, normalArmor, spacedArmor, defaultVehicle):
        super(TierModel, self).__init__()
        self.number = number
        self.normalArmor = normalArmor
        self.spacedArmor = spacedArmor
        self.defaultVehicle = defaultVehicle

    def __repr__(self):
        return '<TierModel(number={}, normalArmor={}, spacedArmor={}, defaultVehicle={})>'.format(self.number, self.normalArmor, self.spacedArmor, self.defaultVehicle)


class TierListModel(models.Model):
    __slots__ = ('tier',)

    def __init__(self, tier):
        super(TierListModel, self).__init__()
        self.tier = tier

    def __repr__(self):
        return '<TierListModel(tier={})>'.format(self.tier)

    def getTierModel(self, tier):
        return next((m for m in self.tier if m.number == tier))


class ConfigModel(models.Model):
    __slots__ = ('tierList', 'colorList', 'blindColorList', 'blendingAlpha')

    def __init__(self, tierList, colorList, blindColorList, blendingAlpha):
        super(ConfigModel, self).__init__()
        self.tierList = tierList
        self.colorList = colorList
        self.blindColorList = blindColorList
        self.blendingAlpha = blendingAlpha

    def getActualColorList(self, isColorBlind):
        return self.blindColorList if isColorBlind else self.colorList

    def _reprArgs(self):
        return 'tierList={}, colorList={}, blindColorList={}, blendingAlpha={}'.format(self.tierList, self.colorList, self.blindColorList, self.blendingAlpha)

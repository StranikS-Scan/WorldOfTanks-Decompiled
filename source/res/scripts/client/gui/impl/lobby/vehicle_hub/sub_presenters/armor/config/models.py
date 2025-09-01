# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/armor/config/models.py
from __future__ import absolute_import
import typing
from dict2model import models

class ColorListModel(models.Model):
    __slots__ = ('normalArmor', 'spacedArmor')

    def __init__(self, normalArmor, spacedArmor):
        super(ColorListModel, self).__init__()
        self.normalArmor = normalArmor
        self.spacedArmor = spacedArmor

    def __repr__(self):
        return '<ColorListModel(normalArmor={}, spacedArmor={})>'.format(self.normalArmor, self.spacedArmor)


class ArmorScaleModel(models.Model):
    __slots__ = ('min', 'max')

    def __init__(self, min, max):
        super(ArmorScaleModel, self).__init__()
        self.min = min
        self.max = max

    def __repr__(self):
        return '<ArmorScaleModel(min={}, max={})>'.format(self.min, self.max)


class TierModel(models.Model):
    __slots__ = ('number', 'normalArmor', 'spacedArmor')

    def __init__(self, number, normalArmor, spacedArmor):
        super(TierModel, self).__init__()
        self.number = number
        self.normalArmor = normalArmor
        self.spacedArmor = spacedArmor

    def __repr__(self):
        return '<TierModel(number={}, normalArmor={}, spacedArmor={})>'.format(self.number, self.normalArmor, self.spacedArmor)


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

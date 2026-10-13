# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/battle_results/components.py
from __future__ import absolute_import
from gui.battle_results.components import base

class EventPointsItem(base.StatsItem):

    def _convert(self, value, reusable):
        return value['avatar']['eventPoints']


class VehicleCommanderIDItem(base.StatsItem):

    def _convert(self, value, reusable):
        return reusable.getPersonalVehiclesInfo(value).vehicleCommanderID


class VehicleDoubleDamage(base.StatsItem):

    def _convert(self, value, reusable):
        return reusable.getPersonalVehiclesInfo(value).doubleTotalDamage

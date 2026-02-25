# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_menu_entries/__init__.py
from __future__ import absolute_import
from CurrentVehicle import g_currentVehicle

def isVehicleUnavailable():
    return g_currentVehicle.item.isInBattle or g_currentVehicle.item.isInPrebattle

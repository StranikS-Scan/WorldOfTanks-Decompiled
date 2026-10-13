# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_mechanics/factories/engine_mechanics.py
from __future__ import absolute_import
from future.utils import viewitems
from gui.shared.gui_items.vehicle_mechanics.mechanic_detectors import ENGINE_MECHANIC_DETECTORS
from gui.shared.gui_items.vehicle_mechanics.factories.base_factory import BaseMechanicFactory
from gui.shared.items_parameters.params_cache import g_paramsCache

class EngineMechanicFactory(BaseMechanicFactory):

    @classmethod
    def _getMechanicsChecks(cls, guiItem, vehDescr):
        if vehDescr is not None:
            return [ (detector(vehDescr), mechanic) for mechanic, (_, detector) in viewitems(ENGINE_MECHANIC_DETECTORS) ]
        else:
            return [ (g_paramsCache.hasEngineMechanic(guiItem.intCD, mechanic), mechanic) for mechanic in ENGINE_MECHANIC_DETECTORS ]

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/anomaly_recipes_view.py
from __future__ import absolute_import
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from halloween.gui.impl.battle.anomaly_recipes_view import AnomalyRecipesView

class HWAnomalyRecipesView(InjectComponentAdaptor):
    __slots__ = ()

    def _makeInjectView(self):
        return AnomalyRecipesView()

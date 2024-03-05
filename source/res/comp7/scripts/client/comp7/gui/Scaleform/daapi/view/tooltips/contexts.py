# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/tooltips/contexts.py
from gui.shared.tooltips.contexts import HangarParamContext
from comp7.gui.Scaleform.daapi.view.lobby.hangar.comp7_vehicle import g_comp7Vehicle
from comp7.gui.Scaleform.daapi.view.lobby.hangar.comp7_vehicle_parameters import comp7VehiclesComparator

class Comp7ParamContext(HangarParamContext):

    def getComparator(self):
        return comp7VehiclesComparator(g_comp7Vehicle.item, g_comp7Vehicle.defaultItem)

    def buildItem(self, *args, **kwargs):
        return g_comp7Vehicle.item

    @staticmethod
    def getBattleModifiersType():
        pass

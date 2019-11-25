# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/maps_blacklist_widget_slot_model.py
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_slot_model import MapsBlacklistSlotModel

class MapsBlacklistWidgetSlotModel(MapsBlacklistSlotModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(MapsBlacklistWidgetSlotModel, self).__init__(properties=properties, commands=commands)

    def getIsShowMode(self):
        return self._getBool(5)

    def setIsShowMode(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(MapsBlacklistWidgetSlotModel, self)._initialize()
        self._addBoolProperty('isShowMode', False)

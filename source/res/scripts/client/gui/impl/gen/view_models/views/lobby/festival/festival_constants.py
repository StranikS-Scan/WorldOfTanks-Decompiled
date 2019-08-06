# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_constants.py
from frameworks.wulf import ViewModel

class FestivalConstants(ViewModel):
    __slots__ = ()
    ITEM_TOOLTIP_TYPE = 'festivalItem'
    MG_WIDGET_STATE_ACTIVE = 'active'
    MG_WIDGET_STATE_WAITING = 'waiting'
    MG_WIDGET_STATE_LOCKED = 'locked'
    CRD_WIDTH_SMALL = 160
    CRD_WIDTH_BIG = 200
    CRD_HEIGHT_SMALL = 90
    CRD_HEIGHT_BIG = 120

    def _initialize(self):
        super(FestivalConstants, self)._initialize()

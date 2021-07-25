# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/context_menus/detachment_context_menus.py
from frameworks.wulf import ViewModel

class DetachmentContextMenus(ViewModel):
    __slots__ = ()
    RECRUIT_CARD_CONTEXT_MENU = 'recruitCardContextMenu'
    DETACHMENT_CARD_CONTEXT_MENU = 'detachmentCardContextMenu'
    VEHICLE_SLOT_CONTEXT_MENU = 'vehicleSlotContextMenu'
    INSTRUCTOR_SLOT_CONTEXT_MENU = 'instructorSlotContextMenu'

    def __init__(self, properties=0, commands=0):
        super(DetachmentContextMenus, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(DetachmentContextMenus, self)._initialize()

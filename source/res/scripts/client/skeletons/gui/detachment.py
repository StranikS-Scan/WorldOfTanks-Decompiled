# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/detachment.py
import typing
if typing.TYPE_CHECKING:
    import crew2.detachment_states
    from gui.shared.gui_items import ItemsCollection
    from gui.shared.gui_items.detachment import Detachment
    from gui.shared.gui_items.instructor import Instructor
    from skeletons.gui.shared.utils.requesters import IInventoryRequester

class IDetachmentCache(object):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def update(self, diff):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    @property
    def inventory(self):
        raise NotImplementedError

    def getDetachments(self, criteria=None):
        raise NotImplementedError

    def getDetachment(self, invID):
        raise NotImplementedError

    def getInstructors(self, criteria=None, withHidden=False):
        raise NotImplementedError

    def getInstructor(self, invID):
        raise NotImplementedError


class IDetachementStates(object):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    @property
    def states(self):
        raise NotImplementedError

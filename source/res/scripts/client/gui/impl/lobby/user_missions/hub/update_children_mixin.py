# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/update_children_mixin.py
from future.utils import iteritems
from gui.impl.pub.view_component import ViewComponent

class UpdateChildrenMixin(ViewComponent):

    def update(self):
        for _, child in iteritems(self._childrenByUid):
            if isinstance(child, UpdateChildrenMixin):
                child.update()

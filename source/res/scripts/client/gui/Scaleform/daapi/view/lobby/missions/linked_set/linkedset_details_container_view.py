# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/linked_set/linkedset_details_container_view.py
from gui.Scaleform.daapi.view.meta.LinkedSetDetailsContainerViewMeta import LinkedSetDetailsContainerViewMeta
from gui.Scaleform.genConsts.LINKEDSET_ALIASES import LINKEDSET_ALIASES

class LinkedSetDetailsView(LinkedSetDetailsContainerViewMeta):

    def __init__(self, ctx=None):
        super(LinkedSetDetailsView, self).__init__()
        self.ctx = ctx

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(LinkedSetDetailsView, self)._onRegisterFlashComponent(viewPy, alias)
        viewPy.setOpener(self)

    def _populate(self):
        super(LinkedSetDetailsView, self)._populate()
        data = {'linkage': LINKEDSET_ALIASES.LINKED_SET_DETAILS_VIEW_LINKAGE,
         'bgWidth': 753,
         'bgHeight': 549}
        self.as_setInitDataS(data)

    def closeView(self):
        self.destroy()

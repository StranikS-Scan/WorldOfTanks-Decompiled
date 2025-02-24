# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/base_crew_dialog_template_view.py
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.lobby.crew.crew_sounds import CREW_SOUND_OVERLAY_SPACE

class BaseCrewDialogTemplateView(DialogTemplateView):
    __slots__ = ('_isClosed',)
    _COMMON_SOUND_SPACE = CREW_SOUND_OVERLAY_SPACE

    def __init__(self, layoutID=None, uniqueID=None, *args, **kwargs):
        super(BaseCrewDialogTemplateView, self).__init__(layoutID, uniqueID, *args, **kwargs)
        self._isClosed = False

    def _closeClickHandler(self, args=None):
        self._isClosed = True
        super(BaseCrewDialogTemplateView, self)._closeClickHandler(args)

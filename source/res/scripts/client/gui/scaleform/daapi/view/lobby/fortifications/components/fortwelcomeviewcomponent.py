# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortWelcomeViewComponent.py
from gui.Scaleform.daapi.view.meta.FortWelcomeViewMeta import FortWelcomeViewMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE

class FortWelcomeViewComponent(FortWelcomeViewMeta, FortViewHelper):

    def __init__(self):
        super(FortWelcomeViewComponent, self).__init__()

    def onViewReady(self):
        g_eventBus.handleEvent(events.FortEvent(events.FortEvent.VIEW_LOADED), scope=EVENT_BUS_SCOPE.FORT)

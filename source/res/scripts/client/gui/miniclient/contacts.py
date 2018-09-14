# Embedded file name: scripts/client/gui/miniclient/contacts.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import events, g_eventBus
from helpers import aop

class _CreateSquadAspect(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.SQUAD_PROMO_WINDOW))


class CreateSquadPointcut(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.user_cm_handlers', 'BaseUserCMHandler', 'createSquad', aspects=(_CreateSquadAspect,))

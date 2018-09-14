# Embedded file name: scripts/client/gui/miniclient/personal_quests/pointcuts.py
import aspects
from helpers import aop

class OnViewPopulate(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.server_events.QuestsPersonalWelcomeView', 'QuestsPersonalWelcomeView', '_populate', aspects=(aspects.OnViewPopulate,))


class PersonalQuestsTabSelect(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.server_events.EventsWindow', 'EventsWindow', 'onTabSelected', aspects=(aspects.PersonalQuestsTabSelect,))

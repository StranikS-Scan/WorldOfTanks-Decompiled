# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWGettingFatApple.py
import BigWorld
from halloween.gui.shared import events as hw_events
from gui.shared import g_eventBus, EVENT_BUS_SCOPE

class HWGettingFatApple(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(HWGettingFatApple, self).__init__()
        self.__updateBuffPanel(True)

    def onDestroy(self):
        self.__updateBuffPanel(False)

    def __updateBuffPanel(self, isShow):
        tooltip = {'params': {},
         'tag': 'hwGettingFatApple'}
        context = {'id': 'hwGettingFatApple',
         'iconName': 'hwGettingFatApple',
         'tooltip': tooltip,
         'vehicleID': self.entity.id}
        event = hw_events.BuffGUIEvent.ON_APPLY if isShow else hw_events.BuffGUIEvent.ON_UNAPPLY
        g_eventBus.handleEvent(hw_events.BuffGUIEvent(event, ctx=context), scope=EVENT_BUS_SCOPE.BATTLE)

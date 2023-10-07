# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/bootcamp_quest_component.py
from frameworks.wulf import ViewFlags
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.bootcamp.bootcamp_quest_widget_view import BootcampQuestWidgetView
from gui.Scaleform.daapi.view.meta.DailyQuestMeta import DailyQuestMeta

class BootcampQuestComponent(InjectComponentAdaptor, DailyQuestMeta):

    def _makeInjectView(self):
        return BootcampQuestWidgetView(flags=ViewFlags.VIEW)

    def updateWidgetLayout(self, value):
        pass

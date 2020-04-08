# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/pre_launch.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.pre_launch.pre_launch_view import PreLaunchView

class PreLaunch(InjectComponentAdaptor):

    def _makeInjectView(self):
        return PreLaunchView()

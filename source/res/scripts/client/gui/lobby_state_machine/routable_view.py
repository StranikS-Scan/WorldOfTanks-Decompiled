# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lobby_state_machine/routable_view.py
from __future__ import absolute_import
import typing
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel

class IRoutableView(object):

    def getRouterModel(self):
        raise NotImplementedError()

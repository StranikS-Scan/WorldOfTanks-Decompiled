# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/tooltips/simple_tooltip_view.py
from gui.impl.gen.view_models.views.lobby.wot_anniversary.tooltips.simple_tooltip_model import SimpleTooltipModel
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class SimpleTooltip(ViewImpl):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wot_anniversary.tooltips.SimpleTooltip(), model=SimpleTooltipModel(), args=args, kwargs=kwargs)
        super(SimpleTooltip, self).__init__(settings)

    def _onLoading(self, payload):
        with self.getViewModel().transaction() as vm:
            vm.setPayload(payload)

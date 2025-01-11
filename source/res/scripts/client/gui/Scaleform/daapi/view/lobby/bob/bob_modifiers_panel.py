# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/bob/bob_modifiers_panel.py
from gui.bob.bob_constants import BOB_SEASON_MODIFIERS_DOMAIN
from gui.impl.lobby.bob.bob_modifiers_domain_tooltip_view import BobModifiersDomainTooltipView
from frameworks.wulf import ViewFlags, ViewSettings, ViewModel
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class BobModifiersPanelInject(InjectComponentAdaptor):
    __slots__ = ('__view',)

    def __init__(self):
        super(BobModifiersPanelInject, self).__init__()
        self.__view = None
        return

    def _makeInjectView(self, *args):
        self.__view = BobModifiersPanel()
        return self.__view

    def _dispose(self):
        self.__view = None
        super(BobModifiersPanelInject, self)._dispose()
        return


class BobModifiersPanel(ViewImpl):

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.bob.SeasonModifier())
        settings.flags = flags
        settings.model = ViewModel()
        super(BobModifiersPanel, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        return BobModifiersDomainTooltipView(BOB_SEASON_MODIFIERS_DOMAIN)

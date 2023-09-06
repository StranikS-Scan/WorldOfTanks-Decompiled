# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/hangar/comp7_modifiers_panel.py
from comp7.constants import COMP7_SEASON_MODIFIERS_DOMAIN
from comp7.gui.impl.lobby.tooltips.comp7_modifiers_domain_tooltip_view import Comp7ModifiersDomainTooltipView
from frameworks.wulf import ViewFlags, ViewSettings, ViewModel
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class Comp7ModifiersPanelInject(InjectComponentAdaptor):
    __slots__ = ('__view',)

    def __init__(self):
        super(Comp7ModifiersPanelInject, self).__init__()
        self.__view = None
        return

    def _makeInjectView(self, *args):
        self.__view = Comp7ModifiersPanel()
        return self.__view

    def _dispose(self):
        self.__view = None
        super(Comp7ModifiersPanelInject, self)._dispose()
        return


class Comp7ModifiersPanel(ViewImpl):

    def __init__(self, flags=ViewFlags.COMPONENT):
        settings = ViewSettings(R.views.lobby.comp7.SeasonModifier())
        settings.flags = flags
        settings.model = ViewModel()
        super(Comp7ModifiersPanel, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        return Comp7ModifiersDomainTooltipView(COMP7_SEASON_MODIFIERS_DOMAIN)

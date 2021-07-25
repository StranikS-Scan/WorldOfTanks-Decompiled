# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/dialog_template_tooltip.py
import typing
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import TooltipType
if typing.TYPE_CHECKING:
    from typing import Callable, Optional
    from frameworks.wulf import View
    from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import DialogTemplateGenericTooltipViewModel

class DialogTemplateTooltip(object):
    __slots__ = ('__tooltipFactory', '__isBackportTooltip', '__viewModel')

    def __init__(self, tooltipFactory=None, isBackportTooltip=False, viewModel=None):
        super(DialogTemplateTooltip, self).__init__()
        self.__viewModel = viewModel
        self.__tooltipFactory = tooltipFactory
        self.__isBackportTooltip = isBackportTooltip

    @property
    def tooltipFactory(self):
        return self.__tooltipFactory

    @tooltipFactory.setter
    def tooltipFactory(self, value):
        if self.__tooltipFactory != value:
            self.__tooltipFactory = value
            self.__updateTooltipType()

    @property
    def isBackportTooltip(self):
        return self.__isBackportTooltip

    @isBackportTooltip.setter
    def isBackportTooltip(self, value):
        if self.__isBackportTooltip != value:
            self.__isBackportTooltip = value
            self.__updateTooltipType()

    def initialize(self, viewModel):
        self.__viewModel = viewModel
        self.__updateTooltipType()

    def dispose(self):
        self.__viewModel = None
        self.__tooltipFactory = None
        return

    def __updateTooltipType(self):
        if self.__viewModel is not None:
            if self.__tooltipFactory is None:
                tooltipType = TooltipType.ABSENT
            elif self.__isBackportTooltip:
                tooltipType = TooltipType.BACKPORT
            else:
                tooltipType = TooltipType.NORMAL
            if self.__viewModel is not None:
                self.__viewModel.setType(tooltipType)
        return

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/lobby/meta_view/subviews/__init__.py
from frameworks.wulf.view.submodel_presenter import SubModelPresenter

class SubViewBase(SubModelPresenter):
    __slots__ = ()

    @property
    def viewId(self):
        raise NotImplementedError

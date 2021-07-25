# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/common/base_sub_model_view.py
import typing
from frameworks.wulf import ViewModel
TViewModel = typing.TypeVar('TViewModel', bound=ViewModel)

class BaseSubModelView(typing.Generic[TViewModel], object):
    __slots__ = ('_viewModel', '_isLoaded')

    def __init__(self, viewModel):
        self._viewModel = viewModel
        self._isLoaded = False

    def isLoaded(self):
        return self._isLoaded

    def onLoading(self, *args, **kwargs):
        self._isLoaded = True

    def initialize(self, *args, **kwargs):
        self._addListeners()

    def update(self, *args, **kwargs):
        pass

    def finalize(self):
        self._removeListeners()
        self._viewModel = None
        return

    def _addListeners(self):
        pass

    def _removeListeners(self):
        pass

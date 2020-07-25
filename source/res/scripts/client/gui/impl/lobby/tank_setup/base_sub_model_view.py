# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/base_sub_model_view.py


class BaseSubModelView(object):
    __slots__ = ('_viewModel', '_isLoaded')

    def __init__(self, viewModel):
        self._viewModel = viewModel
        self._isLoaded = False

    def isLoaded(self):
        return self._isLoaded

    def onLoading(self, *args, **kwargs):
        self._isLoaded = True

    def initialize(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass

    def finalize(self):
        self._viewModel = None
        return

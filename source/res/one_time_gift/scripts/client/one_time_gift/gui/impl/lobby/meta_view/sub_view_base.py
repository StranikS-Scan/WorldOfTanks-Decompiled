# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/lobby/meta_view/sub_view_base.py
import logging
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from shared_utils import safeCall
_logger = logging.getLogger(__name__)

class SubViewBase(SubModelPresenter):

    def __init__(self, viewModel, parentView):
        self._onConfirmCallback = None
        self._onCloseCallback = None
        self._onErrorCallback = None
        self._onCloseCallbackCalled = False
        super(SubViewBase, self).__init__(viewModel, parentView)
        return

    @property
    def viewId(self):
        raise NotImplementedError

    def initialize(self, onConfirmCallback=None, onCloseCallback=None, onErrorCallback=None):
        self._onConfirmCallback = onConfirmCallback
        self._onCloseCallback = onCloseCallback
        self._onErrorCallback = onErrorCallback
        self._onCloseCallbackCalled = False
        super(SubViewBase, self).initialize()

    def finalize(self):
        self._onConfirmCallback = None
        self._onCloseCallback = None
        self._onErrorCallback = None
        super(SubViewBase, self).finalize()
        return

    def _onClose(self, *_):
        _logger.debug('%s._onClose', self.__class__.__name__)
        if not self._onCloseCallbackCalled:
            safeCall(self._onCloseCallback)
            self._onCloseCallbackCalled = True

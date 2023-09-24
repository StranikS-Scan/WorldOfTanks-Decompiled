# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/personal_case/base_personal_case_view.py
from gui.impl.pub import ViewImpl
from uilogging.crew.loggers import CrewPersonalCaseTabLogger

class BasePersonalCaseView(ViewImpl):
    __slots__ = ('uiLogger',)

    def __init__(self, settings, **kwargs):
        self.uiLogger = CrewPersonalCaseTabLogger(self, kwargs.get('parentView'), settings.layoutID, kwargs.get('parentViewKey'))
        super(BasePersonalCaseView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        self.uiLogger.initialize()
        super(BasePersonalCaseView, self)._onLoading(*args, **kwargs)

    def _finalize(self):
        self.uiLogger.finalize()
        super(BasePersonalCaseView, self)._finalize()

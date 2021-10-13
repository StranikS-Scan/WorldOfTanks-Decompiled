# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/yha/yha_entry_point.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.yha.yha_entry_point_model import YhaEntryPointModel
from gui.impl.pub import ViewImpl
from helpers import dependency, time_utils
from skeletons.gui.game_control import IYearHareAffairController
from gui.Scaleform.daapi.view.meta.YHAEntrancePointWidgetMeta import YHAEntrancePointWidgetMeta
_logger = logging.getLogger(__name__)

class YhaEntryPointInjectWidget(YHAEntrancePointWidgetMeta):
    __slots__ = ('__view', '__isSmall')

    def __init__(self):
        super(YhaEntryPointInjectWidget, self).__init__()
        self.__isSmall = False

    def _dispose(self):
        self.__view = None
        super(YhaEntryPointInjectWidget, self)._dispose()
        return

    def setIsSmall(self, value):
        self.__isSmall = value
        if self.__view is not None:
            self.__view.setIsSmall(self.__isSmall)
        return

    def _makeInjectView(self):
        self.__view = YhaEntryPoint()
        self.__view.setIsSmall(self.__isSmall)
        return self.__view


class YhaEntryPoint(ViewImpl):
    __yhaController = dependency.descriptor(IYearHareAffairController)
    __slots__ = ('__isSmall',)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.yha.YhaEntryPoint())
        settings.flags = ViewFlags.COMPONENT
        settings.model = YhaEntryPointModel()
        self.__isSmall = False
        super(YhaEntryPoint, self).__init__(settings)

    @property
    def viewModel(self):
        return super(YhaEntryPoint, self).getViewModel()

    def setIsSmall(self, value):
        if self.viewModel.proxy:
            self.viewModel.setIsSmall(value)
        self.__isSmall = value

    def _onLoading(self, *_, **__):
        self.__update()

    def _initialize(self):
        super(YhaEntryPoint, self)._initialize()
        self.viewModel.onWidgetClick += self.__onWidgetClick
        self.__yhaController.onStateChanged += self.__onStateChanged

    def _finalize(self):
        self.viewModel.onWidgetClick -= self.__onWidgetClick
        self.__yhaController.onStateChanged -= self.__onStateChanged
        super(YhaEntryPoint, self)._finalize()

    def __onWidgetClick(self, _=None):
        self.__yhaController.showWindow()

    def __onStateChanged(self):
        self.__update()

    def __update(self):
        if not self.__yhaController.isEnabled():
            return
        else:
            finishTime = self.__yhaController.getFinishTime()
            if finishTime is not None:
                datetime = time_utils.getDateTimeInLocal(finishTime)
                month = backport.text(R.strings.menu.dateTime.months.dyn('c_{}'.format(datetime.month))())
                dueDate = backport.text(R.strings.yha.entryPoint.dueDate(), day=datetime.day, month=month)
            else:
                _logger.error('Missing finish time for YearHareAffair Event.')
                dueDate = ''
            self.viewModel.setDueDate(dueDate)
            return

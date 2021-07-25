# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/detachment/loggers.py
import typing
import logging
from uilogging.base.logger import BaseLogger
from uilogging.base.mixins import TimedActionMixin, LogOnceMixin
from uilogging.core.core_constants import LogLevels
from constants import ACTION
from wotdecorators import noexcept
from constants import GROUP
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.save_matrix_dialog_view_model import SaveMatrixDialogViewModel
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.detachment.common.toggle_filter_model import ToggleFilterModel, ToggleButtonBaseModel
    from gui.impl.gen.view_models.views.lobby.detachment.popovers.toggle_group_model import ToggleGroupModel
_FEATURE_NAME = 'detachment'
_NULL_GROUP = 'null'
_FLOW_GROUP = 'flow'
_MOVE_ACTION = 'move'
_logger = logging.getLogger(__name__)

class DetachmentLogger(TimedActionMixin, LogOnceMixin, BaseLogger):

    def __init__(self, group):
        super(DetachmentLogger, self).__init__(_FEATURE_NAME, group)

    @property
    def group(self):
        return self._group


class DetachmentToggleLogger(DetachmentLogger):

    @noexcept
    def logFilterChanged(self, filterModel, status):
        self.log(ACTION.TOGGLE_FILTER_CHANGED, filter=filterModel.getId(), status=status)


class InstructorListLogger(DetachmentToggleLogger):

    def __init__(self, group):
        super(InstructorListLogger, self).__init__(group)
        self._instructorViewGroup = group
        self._state = None
        return

    @noexcept
    def switchUnpacking(self, state, logFlow=True):
        if self._state == state:
            return
        self._state = state
        self.stopAction(ACTION.OPEN)
        if state:
            if logFlow:
                g_detachmentFlowLogger.flow(self._group, GROUP.INSTRUCTOR_TOKEN_LIST)
            self._group = GROUP.INSTRUCTOR_TOKEN_LIST
        else:
            if logFlow:
                g_detachmentFlowLogger.flow(self._group, self._instructorViewGroup)
            self._group = self._instructorViewGroup
        self.startAction(ACTION.OPEN)

    def reset(self):
        super(InstructorListLogger, self).reset()
        self._group = self._instructorViewGroup


class DetachmentFlowLogger(BaseLogger):

    def __init__(self):
        super(DetachmentFlowLogger, self).__init__(_FEATURE_NAME, _FLOW_GROUP)

    def dFlow(self, source, target):
        return self.dLog(_MOVE_ACTION, source=source, target=target)

    def flow(self, source, target):
        self.log(_MOVE_ACTION, source=source, target=target)


class DynamicGroupLogger(TimedActionMixin, BaseLogger):

    def __init__(self):
        super(DynamicGroupLogger, self).__init__(_FEATURE_NAME, _NULL_GROUP)

    def log(self, action, loglevel=LogLevels.INFO, **params):
        if self._group == _NULL_GROUP:
            _logger.warning('User class does not have its logging group specified!')
            return
        super(DynamicGroupLogger, self).log(action, loglevel, **params)

    @property
    def group(self):
        return self._group

    def setGroup(self, group):
        self._group = group

    def reset(self):
        super(DynamicGroupLogger, self).reset()
        self._group = _NULL_GROUP


class PerksMatrixDialogLogger(DynamicGroupLogger):

    def setOperationType(self, opType):
        if opType == SaveMatrixDialogViewModel.CLEAR_ALL:
            self._group = GROUP.PERK_MATRIX_DIALOGS_CLEAR_ALL


class DetachmentNullToggleLogger(DynamicGroupLogger):

    @noexcept
    def logFilterChanged(self, filterModel, status):
        _logger.warning("User class should have overriden its toggle mixin's uiLogger!")


class InstructorListNullLogger(DetachmentNullToggleLogger):

    def switchUnpacking(self, state, logFlow=True):
        _logger.warning('InstructorListNullLogger should be overriden in children of InstructorsViewBase!')


class DetachmentPopoverLogger(DynamicGroupLogger):

    @noexcept
    def logFilterChanged(self, groupModel, filterModel, status):
        self.log(ACTION.POPOVER_FILTER_CHANGED, popover_group=groupModel.getId(), filter=filterModel.getId(), status=status)


class DynamicGroupTooltipLogger(DynamicGroupLogger):

    def tooltipOpened(self):
        self.startAction(ACTION.TOOLTIP_WATCHED)

    def tooltipClosed(self, name):
        self.stopAction(ACTION.TOOLTIP_WATCHED, timeLimit=2, tooltip_name=name)


@noexcept
def setTTCAdapterGroup(ttcView, gfView):
    if ttcView is None or gfView is None:
        return
    else:
        ttcView.uiLogger.setGroup(gfView.uiLogger.group)
        return


g_detachmentFlowLogger = DetachmentFlowLogger()

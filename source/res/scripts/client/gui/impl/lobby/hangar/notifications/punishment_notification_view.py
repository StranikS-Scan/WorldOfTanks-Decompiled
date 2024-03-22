# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/notifications/punishment_notification_view.py
from enum import Enum
from frameworks.wulf import WindowFlags, ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import i18n, dependency
from gui.impl import backport
from gui.impl.dialogs.dialog_template_button import ConfirmButton
from gui.impl.dialogs.dialog_template_utils import toString
from gui.impl.gen.resources import R
from gui.impl.dialogs.widgets.icon_set import IconSet
from gui.impl.dialogs.widgets.warning_text import WarningText
from gui.impl.gen.view_models.views.lobby.hangar.dialogs.punishment_dialog_model import PunishmentDialogModel
from gui.shared.utils.functions import getArenaShortName, getArenaSubTypeName
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader
_LOC = R.strings.dialogs.punishmentWindow
_DEFAULT_ICON_RES = R.images.gui.maps.icons.lobby.dialog_warning
_BAN_ICON_RES = R.images.gui.maps.icons.lobby.dialog_ban
_DEFAULT_DIMMER_ALPHA = 0.6
_DEFAULT_INFO_TEXT = R.strings.dialogs.punishmentWindow.info
_BAN_REASON_TEXT = R.strings.dialogs.punishmentWindow.reason.mixed

def __getLocaleByGameplayName(path, gameplayName):
    if gameplayName and isinstance(gameplayName, basestring):
        accessor = path.dyn(gameplayName)
        if accessor.isValid():
            return accessor
    return path


def getPunishmentDialogLocale(localeKey, gameplayName):
    header = __getLocaleByGameplayName(_LOC.header.dyn(localeKey), gameplayName)
    message = __getLocaleByGameplayName(_LOC.message.dyn(localeKey), gameplayName)
    return (header, message)


class PunishmentDialogLocaleKeys(Enum):
    WARNING = 'warning'
    PENALTY = 'penalty'
    BAN = 'ban'


class PunishmentView(ViewImpl):
    __slots__ = ('__iconResID', '__title', '__text', '__dimmerAlpha', '__infoText', '__reason')
    LAYOUT_ID = R.views.lobby.hangar.notifications.PunishmentView()
    VIEW_MODEL = PunishmentDialogModel
    _guiLoader = dependency.instance(IGuiLoader)

    def __init__(self, title, text, reason, infoText=None, layoutID=None, iconResID=_DEFAULT_ICON_RES(), dimmerAlpha=_DEFAULT_DIMMER_ALPHA):
        settings = ViewSettings(layoutID or self.LAYOUT_ID)
        settings.model = self.VIEW_MODEL()
        super(PunishmentView, self).__init__(settings)
        self.__iconResID = iconResID
        self.__title = title
        self.__text = text
        self.__infoText = infoText
        self.__reason = reason
        self.__dimmerAlpha = dimmerAlpha

    @property
    def viewModel(self):
        return super(PunishmentView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PunishmentView, self)._onLoading(*args, **kwargs)
        self.viewModel.setDimmerAlpha(self.__dimmerAlpha)
        buttons = self.viewModel.getButtons()
        buttons.addViewModel(ConfirmButton(_LOC.cancel()).viewModel)
        self._updateViewModel()
        self._setComponents()
        self.viewModel.onButtonClicked += self._buttonClickHandler
        self.viewModel.onCloseClicked += self._closeClickHandler

    def _finalize(self):
        self.viewModel.onButtonClicked -= self._buttonClickHandler
        self.viewModel.onCloseClicked -= self._closeClickHandler
        super(PunishmentView, self)._finalize()

    def _updateViewModel(self):
        with self.viewModel.transaction() as vm:
            self._fillViewModel(vm)

    def _fillViewModel(self, vm):
        vm.setTitle(toString(self.__title))
        vm.setText(toString(self.__text))
        vm.focus.setFocusedIndex(0)
        if self.__infoText:
            vm.setInfoText(toString(self.__infoText))

    def _setComponents(self):
        iconLayoutID = R.views.dialogs.widgets.IconSet()
        self.setChildView(resourceID=R.views.dialogs.widgets.WarningText(), view=WarningText(text=self.__reason))
        self.setChildView(resourceID=iconLayoutID, view=IconSet(iconResID=self.__iconResID, layoutID=iconLayoutID))

    def _closeClickHandler(self, _=None):
        self.destroyWindow()

    def _buttonClickHandler(self, _=None):
        self.destroyWindow()


class WarningView(PunishmentView):

    def __init__(self, arenaTypeID, time, reason, isAFKViolation, layoutID=None):
        arenaName = getArenaShortName(arenaTypeID)
        gameplayName = getArenaSubTypeName(arenaTypeID)
        title, message = getPunishmentDialogLocale(PunishmentDialogLocaleKeys.WARNING.value, gameplayName)
        super(WarningView, self).__init__(layoutID=layoutID, text=backport.text(message(), arenaName=i18n.makeString(arenaName), time=time), title=title, reason=reason, infoText=_DEFAULT_INFO_TEXT() if isAFKViolation else None)
        return


class PenaltyView(PunishmentView):

    def __init__(self, arenaTypeID, time, reason, isAFKViolation, layoutID=None):
        arenaName = getArenaShortName(arenaTypeID)
        gameplayName = getArenaSubTypeName(arenaTypeID)
        title, message = getPunishmentDialogLocale(PunishmentDialogLocaleKeys.PENALTY.value, gameplayName)
        super(PenaltyView, self).__init__(layoutID=layoutID, iconResID=_BAN_ICON_RES(), text=backport.text(message(), arenaName=i18n.makeString(arenaName), time=time), title=title, reason=reason, infoText=_DEFAULT_INFO_TEXT() if isAFKViolation else None)
        return


class BanView(PunishmentView):

    def __init__(self, arenaTypeID, time, duration, layoutID=None):
        arenaName = getArenaShortName(arenaTypeID)
        gameplayName = getArenaSubTypeName(arenaTypeID)
        title, message = getPunishmentDialogLocale(PunishmentDialogLocaleKeys.BAN.value, arenaTypeID)
        mode = backport.text(R.strings.arenas.type.dyn(gameplayName).name())
        super(BanView, self).__init__(layoutID=layoutID, iconResID=_BAN_ICON_RES(), text=backport.text(message(), arenaName=i18n.makeString(arenaName), time=time, mode=mode), title=backport.text(title(), time=duration), reason=_BAN_REASON_TEXT())


class Comp7BanView(PunishmentView):

    def __init__(self, arenaTypeID, time, duration, penalty, isQualification, layoutID=None):
        arenaName = getArenaShortName(arenaTypeID)
        if isQualification:
            message = R.strings.dialogs.punishmentWindow.message.ban.comp7.qualification
        else:
            message = R.strings.dialogs.punishmentWindow.message.ban.comp7
        super(Comp7BanView, self).__init__(layoutID=layoutID, iconResID=_BAN_ICON_RES(), text=backport.text(message(), arenaName=i18n.makeString(arenaName), time=time, penalty=penalty), title=backport.text(R.strings.dialogs.punishmentWindow.header.ban(), time=duration), reason=_BAN_REASON_TEXT())


class AfkLeaverNotification(LobbyNotificationWindow):
    __slots__ = ('_blur',)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, content, parent=None):
        super(AfkLeaverNotification, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=content, parent=parent)
        self._blur = None
        return

    def _initialize(self):
        super(AfkLeaverNotification, self)._initialize()
        self._blur = CachedBlur(enabled=True, ownLayer=self.layer - 1)
        containerManager = self.__appLoader.getApp().containerManager
        if containerManager:
            containerManager.onViewAddedToContainer += self.__onViewLoaded

    def __onViewLoaded(self, _, *args):
        self._blur.enable()

    def _finalize(self):
        if self._blur:
            self._blur.fini()
        containerManager = self.__appLoader.getApp().containerManager
        if containerManager:
            containerManager.onViewAddedToContainer -= self.__onViewLoaded
        super(AfkLeaverNotification, self)._finalize()


class WarningNotificationWindow(AfkLeaverNotification):
    __slots__ = ('arenaTypeID', 'time', 'reason', 'isAFKViolation')

    def __init__(self, arenaTypeID, time, reason, isAFKViolation, parent=None):
        super(WarningNotificationWindow, self).__init__(content=WarningView(arenaTypeID, time, reason, isAFKViolation), parent=parent)
        self.arenaTypeID = arenaTypeID
        self.time = time
        self.reason = reason
        self.isAFKViolation = isAFKViolation

    def __eq__(self, other):
        return False if not isinstance(other, WarningNotificationWindow) else self.arenaTypeID == other.arenaTypeID and self.time == other.time and self.reason == other.reason and self.isAFKViolation == other.isAFKViolation


class PenaltyNotificationWindow(AfkLeaverNotification):
    __slots__ = ('arenaTypeID', 'time', 'reason', 'isAFKViolation')

    def __init__(self, arenaTypeID, time, reason, isAFKViolation, parent=None):
        super(PenaltyNotificationWindow, self).__init__(content=PenaltyView(arenaTypeID, time, reason, isAFKViolation), parent=parent)
        self.arenaTypeID = arenaTypeID
        self.time = time
        self.reason = reason
        self.isAFKViolation = isAFKViolation

    def __eq__(self, other):
        return False if not isinstance(other, PenaltyNotificationWindow) else self.arenaTypeID == other.arenaTypeID and self.time == other.time and self.reason == other.reason and self.isAFKViolation == other.isAFKViolation


class BanNotificationWindow(AfkLeaverNotification):
    __slots__ = ('arenaTypeID', 'time', 'duration')

    def __init__(self, arenaTypeID, time, duration, parent=None):
        super(BanNotificationWindow, self).__init__(content=BanView(arenaTypeID, time, duration), parent=parent)
        self.arenaTypeID = arenaTypeID
        self.time = time
        self.duration = duration

    def __eq__(self, other):
        return False if not isinstance(other, BanNotificationWindow) else self.arenaTypeID == other.arenaTypeID and self.time == other.time and self.duration == other.duration


class Comp7BanNotificationWindow(AfkLeaverNotification):
    __slots__ = ('arenaTypeID', 'time', 'duration', 'penalty', 'isQualification')

    def __init__(self, arenaTypeID, time, duration, penalty, isQualification, parent=None):
        super(Comp7BanNotificationWindow, self).__init__(content=Comp7BanView(arenaTypeID, time, duration, penalty, isQualification), parent=parent)
        self.arenaTypeID = arenaTypeID
        self.time = time
        self.duration = duration
        self.penalty = penalty
        self.isQualification = isQualification

    def __eq__(self, other):
        return False if not isinstance(other, Comp7BanNotificationWindow) else self.arenaTypeID == other.arenaTypeID and self.time == other.time and self.duration == other.duration and self.penalty == other.penalty and self.isQualification == other.isQualification

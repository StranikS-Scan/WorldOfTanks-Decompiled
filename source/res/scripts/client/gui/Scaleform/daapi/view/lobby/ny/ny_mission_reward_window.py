# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_mission_reward_window.py
import constants
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.ny import ny_common
from gui.Scaleform.daapi.view.meta.NYMissionRewardWindowMeta import NYMissionRewardWindowMeta
from gui.Scaleform.locale.NY import NY
from gui.shared import g_eventBus, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.new_year_types import NATIONAL_SETTINGS
from new_year.new_year_sounds import NYSoundEvents
from skeletons.new_year import INewYearController
_DATA_TEMPLATE = {'windowTitle': '',
 'header': '',
 'description': '',
 'rewardBtnLabel': NY.MISSIONREWARDWINDOW_REWARDBTNLABEL,
 'rewardsTotal': '',
 'setting': ''}

class NYMissionRewardWindow(NYMissionRewardWindowMeta):
    _newYearController = dependency.descriptor(INewYearController)

    def __init__(self, ctx):
        super(NYMissionRewardWindow, self).__init__()
        self.__rewardsTotal = ctx.get('rewards', 0)
        self.__setting = ctx.get('setting', ny_common.NO_SETTING_BOX_ID)

    def onGetRewardClick(self, settings):
        if self._newYearController.boxStorage.canOpen(self._newYearController.boxStorage.getItemIDBySetting(settings)):
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_NY_MISSIONS_REWARD_RECEIPT, name=VIEW_ALIAS.LOBBY_NY_MISSIONS_REWARD_RECEIPT, ctx={'nySettingID': settings}), EVENT_BUS_SCOPE.LOBBY)
            self.destroy()

    def onWindowClose(self):
        self.destroy()

    def onCloseClick(self):
        self.onWindowClose()

    def _populate(self):
        super(NYMissionRewardWindow, self)._populate()
        self._newYearController.boxStorage.onCountChanged += self.__onBoxesCountChanged
        self._newYearController.onStateChanged += self.__onNyStateChanged
        self.__updateData()
        NYSoundEvents.playSound(NYSoundEvents.ON_BOX_IS_GOT)

    def _dispose(self):
        self._newYearController.boxStorage.onCountChanged -= self.__onBoxesCountChanged
        self._newYearController.onStateChanged -= self.__onNyStateChanged
        super(NYMissionRewardWindow, self)._dispose()

    def __onNyStateChanged(self, _):
        if not self._newYearController.isAvailable():
            self.destroy()

    def __onBoxesCountChanged(self, _, __, addedInfo):
        descrs = self._newYearController.boxStorage.getDescriptors()
        for bId, count in addedInfo.iteritems():
            if self.__setting == (descrs[bId].setting or ny_common.NO_SETTING_BOX_ID):
                self.__rewardsTotal += count
                NYSoundEvents.playSound(NYSoundEvents.ON_BOX_IS_GOT)

        self.__updateData()

    def __updateData(self):
        data = _DATA_TEMPLATE
        data['rewardsTotal'] = 'x{}'.format(self.__rewardsTotal) if self.__rewardsTotal > 1 else ''
        if self.__setting in NATIONAL_SETTINGS:
            windowTitle = NY.MISSIONREWARDWINDOW_TITLE_SETTING
            header = NY.MISSIONREWARDWINDOW_HEADER_SETTING
            boxName = _ms(NY.missionrewardwindow_boxname(self.__setting))
            if constants.IS_SINGAPORE:
                description = _ms(NY.MISSIONREWARDWINDOW_ASIA_DESCRIPTION_SETTING, boxName=boxName)
            else:
                description = _ms(NY.MISSIONREWARDWINDOW_DESCRIPTION_SETTING, boxName=boxName)
        else:
            windowTitle = NY.MISSIONREWARDWINDOW_TITLE_ANY
            header = NY.MISSIONREWARDWINDOW_HEADER_ANY
            description = NY.MISSIONREWARDWINDOW_DESCRIPTION_ANY
        hasBoxes = self._newYearController.boxStorage.getItemIDBySetting(self.__setting)
        data['windowTitle'] = windowTitle
        data['header'] = header
        data['description'] = description
        data['setting'] = self.__setting
        data['warningLabel'] = '' if hasBoxes else NY.MISSIONREWARDWINDOW_WARNING_NOITEMS
        self.as_setDataS(data)

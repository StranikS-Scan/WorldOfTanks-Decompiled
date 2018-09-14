# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/settings/acoustic_popover.py
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.common.settings import acoustic_presets
from gui.Scaleform.daapi.view.meta.AcousticPopoverMeta import AcousticPopoverMeta
from gui.Scaleform.genConsts.ACOUSTICS import ACOUSTICS
from gui.Scaleform.locale.SETTINGS import SETTINGS
from helpers.i18n import makeString

class AcousticPopover(AcousticPopoverMeta):

    def __init__(self, ctx=None):
        super(AcousticPopover, self).__init__(ctx)
        assert ctx is not None, 'Context is required'
        self.__acousticType = ctx.get('data', ACOUSTICS.TYPE_ACOUSTIC_20)
        self.__player = acoustic_presets.createPlayer(self, self.__acousticType)
        return

    def setEnabled(self, isEnabled):
        self.as_setEnableS(isEnabled)

    def setItemsSelected(self, speakerIDs):
        self.as_onItemSelectS(speakerIDs)

    def setItemsPlay(self, speakerIDs):
        self.as_onItemPlayS(speakerIDs)

    def setPauseEnabled(self, isEnabled):
        self.as_updateBtnEnabledS(ACOUSTICS.ACTION_PAUSE, isEnabled)

    def setPlayEnabled(self, isEnabled):
        self.as_updateBtnEnabledS(ACOUSTICS.ACTION_PLAY, isEnabled)

    def onActionStart(self, actionID):
        if self.__player is not None:
            if actionID == ACOUSTICS.ACTION_PLAY:
                self.__player.play()
            elif actionID == ACOUSTICS.ACTION_PAUSE:
                self.__player.pause()
            elif actionID == ACOUSTICS.ACTION_REPEAT:
                self.__player.reset()
            else:
                LOG_ERROR('Action is not found', actionID)
        else:
            LOG_ERROR('Player is not created')
        return

    def onSpeakerClick(self, speakerID):
        if self.__player is not None:
            self.__player.click(speakerID)
        else:
            LOG_ERROR('Player is not created')
        return

    def _populate(self):
        super(AcousticPopover, self)._populate()
        self.as_setDataS({'title': '%s %s' % (makeString(SETTINGS.SOUNDS_ACOUSTICTYPE_POPOVER_TITLE), makeString(SETTINGS.sounds_acoustictype('popover/{}'.format(self.__acousticType)))),
         'sndType': self.__acousticType})
        if self.__player is not None:
            self.__player.setupInitState()
        return

    def as_disposeS(self):
        if self.__player is not None:
            self.__player.clear()
        super(AcousticPopover, self).as_disposeS()
        return

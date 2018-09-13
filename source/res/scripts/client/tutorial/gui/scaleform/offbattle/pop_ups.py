# Embedded file name: scripts/client/tutorial/gui/Scaleform/offbattle/pop_ups.py
import BigWorld, MusicController, SoundGroups
from tutorial.gui.Scaleform.meta.TutorialBattleNoResultsMeta import TutorialBattleNoResultsMeta
from tutorial.gui.Scaleform.pop_ups import TutorialDialog, TutorialWindow
from tutorial.gui.Scaleform.meta.TutorialBattleStatisticMeta import TutorialBattleStatisticMeta

class TutorialVideoDialog(TutorialDialog):

    def _populate(self):
        self.__setSoundMuted(False)
        super(TutorialVideoDialog, self)._populate()

    def _dispose(self):
        super(TutorialVideoDialog, self)._dispose()
        self.__setSoundMuted(True)

    def __setSoundMuted(self, isMuted):
        BigWorld.wg_setMovieSoundMuted(isMuted)
        SoundGroups.g_instance.enableAmbientAndMusic(isMuted)
        if isMuted:
            MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOBBY)
        else:
            MusicController.g_musicController.stop()


class TutorialBattleStatisticWindow(TutorialWindow, TutorialBattleStatisticMeta):

    def _populate(self):
        super(TutorialBattleStatisticWindow, self)._populate()
        self.as_setDataS(self._content.copy())

    def restart(self):
        self._onMouseClicked('restartID')

    def showVideoDialog(self):
        self._onMouseClicked('showVideoID')


class TutorialBattleNoResultWindow(TutorialWindow, TutorialBattleNoResultsMeta):

    def _populate(self):
        super(TutorialBattleNoResultWindow, self)._populate()
        self.as_setDataS(self._content.copy())

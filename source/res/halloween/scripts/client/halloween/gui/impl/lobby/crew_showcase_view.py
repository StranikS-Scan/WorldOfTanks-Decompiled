# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/crew_showcase_view.py
from __future__ import absolute_import
from frameworks.wulf import WindowFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.mapbox.sound import playSound
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.recruit_helper import getRecruitInfo
from halloween.gui.impl.gen.view_models.views.lobby.crew_member_view_model import CrewMemberViewModel, CrewStates
from halloween.gui.impl.gen.view_models.views.lobby.crew_showcase_view_model import CrewShowcaseViewModel
from halloween.gui.impl.lobby.base_view import BaseView
from halloween.gui.impl.lobby.hw_helpers import HalloweenBonusesAwardsComposer
from halloween.gui.impl.lobby.hw_helpers.bonuses_formatters import getHWTwitchAwardFormatter, getImgName
from halloween.gui.shared.event_dispatcher import showHalloweenShopBundle
from halloween.gui.sounds.sound_constants import CREW_SHOWCASE_ENTER, CREW_SHOWCASE_EXIT
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.skeletons.halloween_twitch_con_controller import IHalloweenTwitchConController
from helpers import dependency
from ids_generators import SequenceIDGenerator
from skeletons.gui.game_control import ISpecialSoundCtrl
from skeletons.gui.impl import IGuiLoader

class CrewShowcaseView(BaseView):
    _MAX_BONUSES_IN_VIEW = 1
    _guiLoader = dependency.descriptor(IGuiLoader)
    _hwArtifactsCtrl = dependency.descriptor(IHalloweenArtefactsController)
    _hwTwitchCtrl = dependency.descriptor(IHalloweenTwitchConController)
    _specialSounds = dependency.descriptor(ISpecialSoundCtrl)

    def __init__(self):
        settings = ViewSettings(R.views.halloween.mono.lobby.crew_showcase(), model=CrewShowcaseViewModel())
        super(CrewShowcaseView, self).__init__(settings)
        self.__bonusCache = {}
        self.__idGen = SequenceIDGenerator()

    @property
    def viewModel(self):
        return super(CrewShowcaseView, self).getViewModel()

    def _getEvents(self):
        return [(self.viewModel.onClose, self.__onClose),
         (self.viewModel.onShop, self.__onShop),
         (self.viewModel.onClaim, self.__onClose),
         (self.viewModel.onPlaySound, self.__onPlaySound),
         (self._hwTwitchCtrl.onTwitchConSettingsUpdated, self.__updateTwitch),
         (self._hwTwitchCtrl.onShopLimitsUpdated, self.__updateTwitch),
         (self._hwTwitchCtrl.onLimitsUpdated, self.__updateTwitch),
         (self._hwTwitchCtrl.onCertificateCountUpdated, self.__updateTwitch)]

    def _onLoading(self, *args, **kwargs):
        super(CrewShowcaseView, self)._onLoading()
        self.__fillViewModel()

    def _initialize(self, *args, **kwargs):
        super(CrewShowcaseView, self)._initialize(*args, **kwargs)
        playSound(CREW_SHOWCASE_ENTER)

    def _finalize(self):
        playSound(CREW_SHOWCASE_EXIT)
        super(CrewShowcaseView, self)._finalize()

    def __fillViewModel(self):
        with self.viewModel.transaction() as model:
            recruitInfo = [ getRecruitInfo(t) for c in self._hwTwitchCtrl.commanders() for r in c.bonuses for t in r.getTokens() ]
            if recruitInfo and recruitInfo[0]:
                skills = recruitInfo[0].getEarnedSkills(True)
                model.getSkills().clear()
                for skill in skills:
                    model.getSkills().addString(skill)

            crewMembers = model.getCrewMembers()
            crewMembers.clear()
            model.setGroupVoiceover(self._hwTwitchCtrl.getFullCrewSound())
            for commander in self._hwTwitchCtrl.commanders():
                crewMember = CrewMemberViewModel()
                crewMember.setId(commander.commanderID)
                crewMember.setHasVoiceover(bool(commander.sound))
                crewMember.setVoiceover(commander.sound)
                crewMember.setHasIsShop(self._hwTwitchCtrl.getRemainShopLimits(commander.commanderID) > 0 and bool(commander.url))
                crewMember.setState(self.__getStatus(commander))
                formatter = HalloweenBonusesAwardsComposer(self._MAX_BONUSES_IN_VIEW, getHWTwitchAwardFormatter())
                bonusRewards = formatter.getFormattedBonuses(commander.bonuses, AWARDS_SIZES.BIG)
                for bonus in bonusRewards:
                    tooltipId = '{}'.format(next(self.__idGen))
                    self.__bonusCache[tooltipId] = bonus
                    crewMember.setName(bonus.userName)
                    crewMember.setIcon(getImgName(bonus.getImage(AWARDS_SIZES.BIG)))
                    crewMember.setTooltipId(tooltipId)

                crewMembers.addViewModel(crewMember)

            crewMembers.invalidate()

    def __getStatus(self, commander):
        if self._hwTwitchCtrl.getRemainLimits(commander.commanderID) == 0 and commander.limit > 0:
            status = CrewStates.RECEIVED
        elif commander.limit > 0 and (self._hwTwitchCtrl.getCertificateCount() > 0 or self._hwArtifactsCtrl.isExistUnreceivedTwitchConCertificate()):
            status = CrewStates.INBASEREWARD
        elif self._hwTwitchCtrl.getRemainShopLimits(commander.commanderID) > 0 and commander.url:
            status = CrewStates.INSHOP
        else:
            status = CrewStates.RECEIVED
        return status

    def __onClose(self):
        self.destroyWindow()

    def __onShop(self, args=None):
        if args is None:
            return
        else:
            commanderID = args.get('commanderID', None)
            if commanderID:
                commander = self._hwTwitchCtrl.getCommanderByID(commanderID)
                if commander:
                    showHalloweenShopBundle(commander.url)
            return

    def __updateTwitch(self):
        if not self._hwTwitchCtrl.isPromoScreenEnabled():
            self.__onClose()
        else:
            self.__fillViewModel()

    def __onPlaySound(self, args=None):
        if args is None:
            return
        else:
            event = args.get('sound', '')
            if not event:
                return
            playSound(event)
            return


class CrewShowcaseWindow(LobbyWindow):

    def __init__(self, parent=None):
        super(CrewShowcaseWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=CrewShowcaseView(), parent=parent)

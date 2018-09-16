# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/football_card_collection_panel.py
import logging
import WWISE
import SoundGroups
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.CardCollectionMeta import CardCollectionMeta
from gui.Scaleform.daapi.view.meta.CardsPacketScreenMeta import CardsPacketScreenMeta
from gui.Scaleform.genConsts.FOOTBAL2018_CONSTANTS import FOOTBAL2018_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.locale.FOOTBALL2018 import FOOTBALL2018
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.awards_formatters import QuestsBonusComposer
from gui.server_events.awards_formatters import getFootballAwardPacker
from gui.server_events.bonuses import mergeBonuses
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.events import LoadViewEvent
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers import i18n
from items.football_config import DECK_TYPE, DECKS_NUM, STACK_MULTIPLIERS, MILESTONE_SCORES
from items.football_config import MILESTONE_SCORE, MILESTONE, getObtainedMilestones
from items.vehicles import VehicleDescriptor
from skeletons.gui.game_control import IFootballMetaGame
from skeletons.gui.server_events import IEventsCache
from gui.game_control.football_meta_game import Deck
from football_hangar_common import OsBitness
_logger = logging.getLogger(__name__)
_QUEST_FORMATTER = QuestsBonusComposer(getFootballAwardPacker())

class _GuiDataProvider(object):
    _BUFFON_SLOT_ID = 10
    _BACKSIDE_CARD_VO = {'roleImg': '',
     'roleText': '',
     'tooltipComplex': '',
     'nameText': '',
     'imgSrc': '',
     'valueText': '',
     'slotID': 0,
     'cardType': FOOTBAL2018_CONSTANTS.CARD_LOW,
     'bgSrc': RES_ICONS.MAPS_ICONS_FE18_CARDS_CARD_BACKSIDE,
     'extraBGFirstSrc': '',
     'extraBGSecondSrc': ''}
    _TIER_TO_STRING = (None, 'low', 'medium', 'high')
    _ROLE_TO_STRING = {DECK_TYPE.STRIKER: 'striker',
     DECK_TYPE.MIDFIELDER: 'midfielder',
     DECK_TYPE.DEFENDER: 'defender'}
    _DECKS_INDEXES_TO_SLOTS = (0, 1, 8, 9, 2, 3, 6, 7, 4, 5)
    _TIER_TO_BG = (RES_ICONS.MAPS_ICONS_FE18_CARDS_CARD_LOW, RES_ICONS.MAPS_ICONS_FE18_CARDS_CARD_MEDIUM, RES_ICONS.MAPS_ICONS_FE18_CARDS_CARD_HIGH)
    _DECK_TYPE_TO_ROLE_TEXT_DATA = {DECK_TYPE.STRIKER: (text_styles.hightlight(FOOTBALL2018.SPORT_ROLE_STRIKER), makeTooltip('#football2018:Sport_role_striker', '#football2018:Sport_role_striker_desc')),
     DECK_TYPE.MIDFIELDER: (text_styles.hightlight(FOOTBALL2018.SPORT_ROLE_MIDFIELDER), makeTooltip('#football2018:Sport_role_midfielder', '#football2018:Sport_role_midfielder_desc')),
     DECK_TYPE.DEFENDER: (text_styles.hightlight(FOOTBALL2018.SPORT_ROLE_DEFENDER), makeTooltip('#football2018:Sport_role_defender', '#football2018:Sport_role_defender_desc'))}
    _SLOTS_TO_VEHICLE = ('ussr:R45_IS-7', 'uk:GB91_Super_Conqueror', 'japan:J16_ST_B1', 'uk:GB86_Centurion_Action_X', 'ussr:R132_VNII_100LT', 'france:F88_AMX_13_105', 'ussr:R87_T62A', 'germany:G89_Leopard1', 'germany:G56_E-100', 'sweden:S16_Kranvagn')
    _SLOT_VEHICLES_DATA = tuple([ (VehicleDescriptor(typeName=_SLOTS_TO_VEHICLE[i]).type.shortUserString, '../maps/icons/fe18/cards/{}.png'.format(_SLOTS_TO_VEHICLE[i].replace(':', '-'))) for i in range(0, DECKS_NUM) ])
    _TIER_TO_UI_CARD_TYPES = (None,
     FOOTBAL2018_CONSTANTS.CARD_LOW,
     FOOTBAL2018_CONSTANTS.CARD_MEDIUM,
     FOOTBAL2018_CONSTANTS.CARD_HIGH)

    @classmethod
    def getDecksVOs(cls, decksList, isBuffonAvailable, isBuffonRecruited):
        decksList = [ cls.getDeckVO(idx, deck) for idx, deck in enumerate(decksList) ]
        decksList.append(cls.getBuffonVO(isBuffonAvailable, isBuffonRecruited))
        return decksList

    @classmethod
    def getDeckVO(cls, deckIndex, deck):
        deckRole = deck.type
        deckTier = deck.count
        roleText, roleTooltip = cls._DECK_TYPE_TO_ROLE_TEXT_DATA[deckRole]
        tierStr = cls._TIER_TO_STRING[deckTier]
        roleImg = '../maps/icons/fe18/cards/role_{}_{}.png'.format(tierStr, cls._ROLE_TO_STRING[deckRole]) if tierStr else ''
        slotID = cls._DECKS_INDEXES_TO_SLOTS[deckIndex]
        if deckTier > 0:
            vehicleName, vehicleImg = cls._SLOT_VEHICLES_DATA[slotID]
        else:
            vehicleName = vehicleImg = ''
        value = STACK_MULTIPLIERS[deckTier]
        topCardIndex = deckTier - 1
        midCardIndex = topCardIndex - 1
        botCardIndex = midCardIndex - 1
        return {'roleImg': roleImg,
         'roleText': roleText if deckTier == 0 else '',
         'tooltipComplex': roleTooltip,
         'nameText': text_styles.middleTitle(vehicleName),
         'imgSrc': vehicleImg,
         'valueText': str(value) if deckTier > 0 else '',
         'slotID': slotID,
         'cardType': cls._TIER_TO_UI_CARD_TYPES[deckTier],
         'bgSrc': cls._TIER_TO_BG[topCardIndex] if topCardIndex >= 0 else RES_ICONS.MAPS_ICONS_FE18_CARDS_EMPTYBG,
         'extraBGFirstSrc': cls._TIER_TO_BG[midCardIndex] if midCardIndex >= 0 else '',
         'extraBGSecondSrc': cls._TIER_TO_BG[botCardIndex] if botCardIndex >= 0 else ''}

    @classmethod
    def getBacksideVO(cls):
        return cls._BACKSIDE_CARD_VO

    @classmethod
    def getBuffonVO(cls, isBuffonAvailable, isBuffonRecruited):
        if isBuffonAvailable or isBuffonRecruited:
            bgSrc = RES_ICONS.MAPS_ICONS_FE18_CARDS_CARD_BUFFON
            roleText = text_styles.middleTitle(FOOTBALL2018.SPORT_ROLE_GOALKEEPER)
        else:
            bgSrc = RES_ICONS.MAPS_ICONS_FE18_CARDS_DISABLEDBG
            roleText = ''
        buffonVO = {'bgSrc': bgSrc,
         'showLock': not isBuffonAvailable and not isBuffonRecruited,
         'needPremiumAnimation': isBuffonAvailable and not isBuffonRecruited,
         'slotID': cls._BUFFON_SLOT_ID,
         'roleText': roleText,
         'tooltipSpecial': TOOLTIPS_CONSTANTS.FOOTBALL_BUFFON}
        if isBuffonAvailable:
            buffonVO['cardType'] = FOOTBAL2018_CONSTANTS.CARD_PREMIUM
        return buffonVO


class CardCollection(CardCollectionMeta):
    _eventsCache = dependency.descriptor(IEventsCache)
    _footballMetaGame = dependency.descriptor(IFootballMetaGame)

    def __init__(self, ctx):
        super(CardCollection, self).__init__(ctx)
        self._initedRewardsScreen = False
        self.__milestone = MILESTONE.NONE
        self.__packetsScreenOpened = False
        self.__overlayScreenOpened = False

    @property
    def cardsPacketScreen(self):
        component = self.getComponent(HANGAR_ALIASES.FOOTBALL_CARDS_PACKET_SCREEN)
        if not component:
            LOG_ERROR("Couldn't find {}".format(HANGAR_ALIASES.FOOTBALL_CARDS_PACKET_SCREEN))
        return component

    def buffonCardPurchaseButtonClicked(self):
        self.fireEvent(events.OpenLinkEvent(events.OpenLinkEvent.BUFFON_CARD_PURCHASE))

    def onClose(self, state):
        if state != 'main_state':
            if self.__packetsScreenOpened:
                packetsOpenScreen = self.cardsPacketScreen
                obtainedCards = packetsOpenScreen.getObtainedCards()
                if obtainedCards is not None:
                    obtainedCards = list(reversed(obtainedCards))
                    if obtainedCards:
                        self.as_submitTFMAssignedCardsListS({'cardsList': obtainedCards,
                         'cardsAintShowedYet': True})
                else:
                    self.__switchToHangar()
                self.__packetsScreenOpened = False
                packetsOpenScreen.onHide()
            elif state == 'result_state' and self._footballMetaGame.getMilestone() == MILESTONE.THIRD:
                if self._footballMetaGame.isBuffonAvailable():
                    self.as_submitTFMAssignedCardsListS({'cardsList': [_GuiDataProvider.getBuffonVO(self._footballMetaGame.isBuffonAvailable(), self._footballMetaGame.isBuffonRecruited())],
                     'cardsAintShowedYet': True})
            self.__overlayScreenOpened = False
            if self._footballMetaGame.getPackets():
                self.__showOpenPacketsScreen()
        else:
            self.__switchToHangar()
        return

    def addNewCardsButtonClicked(self):
        self.onClose('new_cards_state')

    def requestForShowingResultScreen(self):
        if self.__isMilestoneReached():
            self.__displayResultsScreen()
            self.__milestone = self._footballMetaGame.getMilestone()

    def displayBuffonRecruitmentScreen(self):
        self.fireEvent(LoadViewEvent(VIEW_ALIAS.FOOTBALL_BUFFON_RECRUITMENT_PANEL), EVENT_BUS_SCOPE.LOBBY)

    def playSoundFx(self, fxId):
        SoundGroups.g_instance.playSound2D(fxId)

    def rewardsScreenButtonClicked(self):
        self.__displayRewardsScreen()

    def resultsScreenButtonClicked(self):
        self.as_displayResultsS(False, self._footballMetaGame.isBuffonAvailable())

    def _populate(self):
        super(CardCollection, self)._populate()
        self.__setStaticData()
        self.__updateDecksUI()
        self.__milestone = self._footballMetaGame.getMilestone()
        self._footballMetaGame.onPacketsOpened += self.__onPacketsOpened
        self._footballMetaGame.onMilestoneReached += self.__onMilestoneReached
        self._footballMetaGame.onPacketsUpdated += self.__onPacketsReceived
        self.__updateState()
        self._eventsCache.onSyncCompleted += self.__onEventsSyncCompleted
        if self._footballMetaGame.getPackets():
            self.__showOpenPacketsScreen()
        if self._eventsCache.isEventEnabled():
            WWISE.WW_setState('STATE_ext_football_music', 'STATE_ext_football_music_metagame')

    def _dispose(self):
        self._footballMetaGame.onPacketsUpdated -= self.__onPacketsReceived
        self._footballMetaGame.onPacketsOpened -= self.__onPacketsOpened
        self._footballMetaGame.onMilestoneReached -= self.__onMilestoneReached
        self._eventsCache.onSyncCompleted -= self.__onEventsSyncCompleted
        super(CardCollection, self)._dispose()

    def __onPacketsOpened(self, _):
        self.__updateState()
        if not self.__packetsScreenOpened:
            self.__updateDecksUI()

    def __onPacketsReceived(self, *args, **kwargs):
        if self._footballMetaGame.getPackets() and not self.__overlayScreenOpened:
            self.__showOpenPacketsScreen()

    def __showOpenPacketsScreen(self):
        self.as_showCardsPacketScreenS()
        self.cardsPacketScreen.onShow()
        self.__packetsScreenOpened = True
        self.__overlayScreenOpened = True

    def __onMilestoneReached(self):
        self.__updateState()

    def __updateDecksUI(self):
        outcome = {'cardsList': _GuiDataProvider.getDecksVOs(self._footballMetaGame.getDecks(), self._footballMetaGame.isBuffonAvailable(), self._footballMetaGame.isBuffonRecruited())}
        self.as_submitTFMAssignedCardsListS(outcome)

    def __switchToHangar(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __setStaticData(self):
        icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_FE18_PURCHASEICON, 16, 16)
        purchaseBtnStr = '{} {}'.format(i18n.makeString(FOOTBALL2018.CARDCOLLECTION_CARD_SLOT_PURCHASE_BUTTON_LABEL), icon)
        self.as_setStaticDataS({'closeBtnLabel': i18n.makeString(FOOTBALL2018.CARDCOLLECTION_CLOSEBTN_LABEL),
         'TFMStaticVO': {'titleTFM': i18n.makeString(FOOTBALL2018.CARDCOLLECTION_TFM_TITLE),
                         'descriptionTFM': i18n.makeString(FOOTBALL2018.CARDCOLLECTION_TFM_DESCRIPTION),
                         'scoreLabelStr': i18n.makeString(FOOTBALL2018.CARDCOLLECTION_TFM_SCORE_LABEL),
                         'rewardsBtnStr': i18n.makeString(FOOTBALL2018.CARDCOLLECTION_TFM_REWARDBTN_LABEL),
                         'purchaseBtnStr': purchaseBtnStr,
                         'pbLeftLimit': MILESTONE_SCORE.FIRST,
                         'pbTopLimit': MILESTONE_SCORE.SECOND,
                         'pbRightLimit': MILESTONE_SCORE.THIRD},
         'highQualityAnimations': OsBitness.is64Bit()})

    def __displayRewardsScreen(self):
        if not self._initedRewardsScreen:
            self.as_initRewardsScreenS(self.__getRewardData())
            self._initedRewardsScreen = True
        self.as_displayRewardsS(True)
        self.__overlayScreenOpened = True

    def __displayResultsScreen(self):
        resultsScreenVO = self.__getResultsScreenVO()
        self.as_initResultsScreenS(resultsScreenVO)
        self.as_displayResultsS(True, self._footballMetaGame.isBuffonAvailable())
        self.__overlayScreenOpened = True

    def __updateState(self):
        self.__updateProgress()
        self.__updatePurchaseButton()

    def __updateProgress(self):
        progress = self._footballMetaGame.getProgress()
        self.as_updatePlayerCardPointsS(progress, self.__isMilestoneReached())

    def __updatePurchaseButton(self):
        if self._footballMetaGame.isBuffonRecruited() or self._footballMetaGame.isBuffonAvailable():
            show = False
        else:
            show = True
        self.as_showCardSlotPurchaseButtonS(show)

    def __onEventsSyncCompleted(self, *args):
        if not self._eventsCache.isEventEnabled():
            self.destroy()

    def __getMilestonesQuests(self, milestoneTokens):

        def filterMilestoneQuests(quest):
            return quest.getID() in milestoneTokens

        milestoneQuests = self._eventsCache.getHiddenQuests(filterMilestoneQuests)
        return milestoneQuests

    def __getBonusesForMilestones(self, milestoneTokens, merge=False):
        milestoneQuests = self.__getMilestonesQuests(milestoneTokens)
        bonuses = []
        for milestoneQuest in milestoneQuests.itervalues():
            bonuses.extend(milestoneQuest.getBonuses())

        bonuses = mergeBonuses(bonuses) if merge else bonuses
        return bonuses

    def __getRewardData(self):
        rewardVOs = {milestone:{'leftLimitValue': MILESTONE_SCORE.FIRST,
         'topLimitValue': MILESTONE_SCORE.SECOND,
         'rightLimitValue': MILESTONE_SCORE.THIRD,
         'columnScoreValue': MILESTONE_SCORES[milestone],
         'rewardsList': []} for milestone in MILESTONE.ALL}
        allMilestoneQuests = self.__getMilestonesQuests(MILESTONE.ALL)
        for milestoneToken, milestoneQuest in allMilestoneQuests.iteritems():
            bonuses = milestoneQuest.getBonuses()
            formattedBonuses = _QUEST_FORMATTER.getFormattedBonuses(bonuses, AWARDS_SIZES.BIG)
            rewardVOs[milestoneToken].update({'rewardsList': formattedBonuses})

        return {'titleStr': i18n.makeString(FOOTBALL2018.CARDCOLLECTION_REWARDS_SCREEN_TITLE),
         'fieldScoreLabelStr': i18n.makeString(FOOTBALL2018.CARDCOLLECTION_TFM_SCORE_LABEL),
         'columnLeft': rewardVOs[MILESTONE.FIRST],
         'columnCenter': rewardVOs[MILESTONE.SECOND],
         'columnRight': rewardVOs[MILESTONE.THIRD]}

    def __getResultsScreenVO(self):
        milestoneTokens = getObtainedMilestones(self.__milestone, self._footballMetaGame.getMilestone())
        bonuses = self.__getBonusesForMilestones(milestoneTokens, merge=True)
        formattedBonuses = _QUEST_FORMATTER.getFormattedBonuses(bonuses, AWARDS_SIZES.BIG)
        currentScore = self._footballMetaGame.getProgress()
        currentScoreStr = str(currentScore)
        screenVO = {'titleStr': FOOTBALL2018.CARDCOLLECTION_RESULTS_SCREEN_TITLE,
         'subtitleStr': i18n.makeString(FOOTBALL2018.CARDCOLLECTION_RESULTS_SCREEN_SUBTITLE, score=currentScoreStr),
         'progressLeftLimitValue': MILESTONE_SCORE.FIRST,
         'progressTopLimitValue': MILESTONE_SCORE.SECOND,
         'progressRightLimitValue': MILESTONE_SCORE.THIRD,
         'progressValue': currentScore,
         'progressScore': currentScoreStr,
         'progressScoreDesc': FOOTBALL2018.CARDCOLLECTION_RESULTS_SCREEN_PROGRESSSCOREDESC,
         'resultsList': formattedBonuses,
         'btnContinue': FOOTBALL2018.CARDCOLLECTION_RESULTS_SCREEN_BTNCONTINUE}
        return screenVO

    def __isMilestoneReached(self):
        return self._footballMetaGame.getMilestone() != self.__milestone


class OpenPacketsScreen(CardsPacketScreenMeta):
    _footballMetaGame = dependency.descriptor(IFootballMetaGame)

    def __init__(self):
        super(OpenPacketsScreen, self).__init__()
        self.__obtainedCards = None
        self.__isOpenRequestSent = False
        self.__cardCount = 0
        return

    def onShow(self):
        self.__obtainedCards = None
        self.__isOpenRequestSent = False
        self.__cardCount = 0
        self._footballMetaGame.onPacketsOpened += self.__onPacketsOpened
        self._footballMetaGame.onPacketsUpdated += self.__onPacketsUpdated
        self.__updateScreenData()
        return

    def onHide(self):
        self.__obtainedCards = None
        self._footballMetaGame.onPacketsOpened -= self.__onPacketsOpened
        self._footballMetaGame.onPacketsUpdated -= self.__onPacketsUpdated
        return

    def getObtainedCards(self):
        return self.__obtainedCards

    def onOpenCarsClick(self):
        self.__isOpenRequestSent = True
        self._footballMetaGame.openPackets()

    def _dispose(self):
        self._footballMetaGame.onPacketsOpened -= self.__onPacketsOpened
        self._footballMetaGame.onPacketsUpdated -= self.__onPacketsUpdated
        super(OpenPacketsScreen, self)._dispose()

    def __onPacketsOpened(self, changedDecks):
        decks = []
        decksVOs = []
        for deckIdx, deck in enumerate(changedDecks):
            if deck.diff:
                for tier in range(deck.count - deck.diff + 1, deck.count + 1):
                    tempDeck = Deck(type=deck.type, count=tier, diff=0)
                    d = (deckIdx, tempDeck)
                    decks.append(d)

        decks.sort(key=lambda i: i[1].count, reverse=True)
        decksVOs = [ _GuiDataProvider.getDeckVO(deck[0], deck[1]) for deck in decks ]
        compensated = []
        for _ in range(len(decksVOs), self.__cardCount):
            compensated.append(_GuiDataProvider.getBacksideVO())

        self.as_setCardsS(decksVOs + compensated)
        self.__obtainedCards = decksVOs

    def __onPacketsUpdated(self):
        self.__updateScreenData()

    def __updateScreenData(self):
        if self.__isOpenRequestSent:
            return
        packets = self._footballMetaGame.getPackets()
        self.__cardCount = 0
        for p in packets:
            self.__cardCount += sum(p)

        cntStr = i18n.makeString(FOOTBALL2018.CARDCOLLECTION_NEWCARDS_SCREEN_SUBTITLE, count=str(self.__cardCount))
        self.as_setDataS({'titleStr': text_styles.epicTitle(i18n.makeString(FOOTBALL2018.CARDCOLLECTION_NEWCARDS_SCREEN_TITLE)),
         'subTitleStr': text_styles.superPromoTitle(cntStr),
         'openPackBtnStr': i18n.makeString(FOOTBALL2018.CARDCOLLECTION_NEWCARDS_SCREEN_BTN_OPENPACK),
         'okBtnStr': i18n.makeString(FOOTBALL2018.CARDCOLLECTION_NEWCARDS_SCREEN_BTN_OK),
         'newCardCount': self.__cardCount})

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/collections_by_type.py
from chat_shared import SYS_MESSAGE_TYPE as _SM_TYPE
from gui.gift_system.proxy import GiftSystemMessagesProxy
from gui.shared.system_factory import registerMessengerClientFormatter, registerTokenQuestsSubFormatters, registerMessengerServerFormatter, registerLootBoxAutoOpenSubFormatters
from messenger.formatters import service_channel as _sc
from messenger.formatters import wot_plus as _wotPlusFormatters
from messenger.formatters import personal_reserves as _prFormatters
from messenger.formatters import auto_boxes_subformatters, token_quest_subformatters
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
registerLootBoxAutoOpenSubFormatters((auto_boxes_subformatters.EventBoxesFormatter(),
 auto_boxes_subformatters.EventLootBoxesFormatter(),
 auto_boxes_subformatters.NYPostEventBoxesFormatter(),
 auto_boxes_subformatters.NYGiftSystemSurpriseFormatter(),
 auto_boxes_subformatters.LunarNYEnvelopeAutoOpenFormatter(),
 auto_boxes_subformatters.LootBoxSystemAutoOpenFormatter()))
registerTokenQuestsSubFormatters((token_quest_subformatters.LootBoxTokenQuestFormatter(),
 token_quest_subformatters.RecruitQuestsFormatter(),
 token_quest_subformatters.RankedSeasonTokenQuestFormatter(),
 token_quest_subformatters.RankedFinalTokenQuestFormatter(),
 token_quest_subformatters.RankedYearLeaderFormatter(),
 token_quest_subformatters.SeniorityAwardsFormatter(),
 token_quest_subformatters.SeniorityAwardsVehicleSelectedFormatter(),
 token_quest_subformatters.PersonalMissionsTokenQuestsFormatter(),
 token_quest_subformatters.BattlePassDefaultAwardsFormatter(),
 token_quest_subformatters.BattlePassAutoSelectRewardsFormatter(),
 token_quest_subformatters.WotPlusAttendanceRewardsFormatter(),
 token_quest_subformatters.WotPlusAttendanceRewardsFormatterTestSMViewer(),
 token_quest_subformatters.BattleMattersAwardsFormatter(),
 token_quest_subformatters.Comp7RewardsFormatter(),
 token_quest_subformatters.WinbackRewardFormatter(),
 token_quest_subformatters.CrewPerksFormatter(),
 token_quest_subformatters.SteamCompletionFormatter(),
 token_quest_subformatters.SkipNotificationFormatter()))
_HANGAR_QUESTS_SUB_FORMATTERS = (token_quest_subformatters.BattleMattersAwardsFormatter(),)
_PERSONAL_MISSIONS_SUB_FORMATTERS = (token_quest_subformatters.PersonalMissionsFormatter(),)

def initRegistrationFormatters():
    registerMessengerServerFormatter(_SM_TYPE.serverReboot.index(), _sc.ServerRebootFormatter())
    registerMessengerServerFormatter(_SM_TYPE.serverRebootCancelled.index(), _sc.ServerRebootCancelledFormatter())
    registerMessengerServerFormatter(_SM_TYPE.battleResults.index(), _sc.BattleResultsFormatter())
    registerMessengerServerFormatter(_SM_TYPE.invoiceReceived.index(), _sc.InvoiceReceivedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.adminTextMessage.index(), _sc.AdminMessageFormatter())
    registerMessengerServerFormatter(_SM_TYPE.accountTypeChanged.index(), _sc.AccountTypeChangedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.giftReceived.index(), _sc.GiftReceivedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.autoMaintenance.index(), _sc.AutoMaintenanceFormatter())
    registerMessengerServerFormatter(_SM_TYPE.premiumBought.index(), _sc.PremiumBoughtFormatter())
    registerMessengerServerFormatter(_SM_TYPE.premiumExtended.index(), _sc.PremiumExtendedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.premiumExpired.index(), _sc.PremiumExpiredFormatter())
    registerMessengerServerFormatter(_SM_TYPE.premiumChanged.index(), _sc.PremiumChangedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.prbArenaFinish.index(), _sc.PrebattleArenaFinishFormatter())
    registerMessengerServerFormatter(_SM_TYPE.prbKick.index(), _sc.PrebattleKickFormatter())
    registerMessengerServerFormatter(_SM_TYPE.prbDestruction.index(), _sc.PrebattleDestructionFormatter())
    registerMessengerServerFormatter(_SM_TYPE.vehicleCamouflageTimedOut.index(), _sc.VehCamouflageTimedOutFormatter())
    registerMessengerServerFormatter(_SM_TYPE.vehiclePlayerEmblemTimedOut.index(), _sc.VehEmblemTimedOutFormatter())
    registerMessengerServerFormatter(_SM_TYPE.vehiclePlayerInscriptionTimedOut.index(), _sc.VehInscriptionTimedOutFormatter())
    registerMessengerServerFormatter(_SM_TYPE.vehTypeLockExpired.index(), _sc.VehicleTypeLockExpired())
    registerMessengerServerFormatter(_SM_TYPE.serverDowntimeCompensation.index(), _sc.ServerDowntimeCompensation())
    registerMessengerServerFormatter(_SM_TYPE.achievementReceived.index(), _sc.AchievementFormatter())
    registerMessengerServerFormatter(_SM_TYPE.converter.index(), _sc.ConverterFormatter())
    registerMessengerServerFormatter(_SM_TYPE.tokenQuests.index(), _sc.TokenQuestsFormatter())
    registerMessengerServerFormatter(_SM_TYPE.notificationsCenter.index(), _sc.NCMessageFormatter())
    registerMessengerServerFormatter(_SM_TYPE.clanEvent.index(), _sc.ClanMessageFormatter())
    registerMessengerServerFormatter(_SM_TYPE.fortEvent.index(), _sc.StrongholdMessageFormatter())
    registerMessengerServerFormatter(_SM_TYPE.vehicleRented.index(), _sc.VehicleRentedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.rentalsExpired.index(), _sc.RentalsExpiredFormatter())
    registerMessengerServerFormatter(_SM_TYPE.potapovQuestBonus.index(), _sc.TokenQuestsFormatter(subFormatters=_PERSONAL_MISSIONS_SUB_FORMATTERS))
    registerMessengerServerFormatter(_SM_TYPE.goodieRemoved.index(), _sc.GoodyRemovedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.goodiesExpired.index(), _sc.GoodiesExpiredFormatter())
    registerMessengerServerFormatter(_SM_TYPE.goodieDisabled.index(), _sc.GoodyDisabledFormatter())
    registerMessengerServerFormatter(_SM_TYPE.goodieEnabled.index(), _sc.GoodieEnabledFormatter())
    registerMessengerServerFormatter(_SM_TYPE.telecomOrderCreated.index(), _sc.TelecomReceivedInvoiceFormatter())
    registerMessengerServerFormatter(_SM_TYPE.telecomOrderUpdated.index(), _sc.TelecomStatusFormatter())
    registerMessengerServerFormatter(_SM_TYPE.telecomOrderDeleted.index(), _sc.TelecomRemovedInvoiceFormatter())
    registerMessengerServerFormatter(_SM_TYPE.prbVehicleKick.index(), _sc.PrbVehicleKickFormatter())
    registerMessengerServerFormatter(_SM_TYPE.prbVehicleKickFilter.index(), _sc.PrbVehicleKickFilterFormatter())
    registerMessengerServerFormatter(_SM_TYPE.vehicleGroupLocked.index(), _sc.RotationGroupLockFormatter())
    registerMessengerServerFormatter(_SM_TYPE.vehicleGroupUnlocked.index(), _sc.RotationGroupUnlockFormatter())
    registerMessengerServerFormatter(_SM_TYPE.rankedQuests.index(), _sc.RankedQuestFormatter())
    registerMessengerServerFormatter(_SM_TYPE.royaleQuests.index(), _sc.BRQuestsFormatter())
    registerMessengerServerFormatter(_SM_TYPE.hangarQuests.index(), _sc.TokenQuestsFormatter(subFormatters=_HANGAR_QUESTS_SUB_FORMATTERS))
    registerMessengerServerFormatter(_SM_TYPE.currencyUpdate.index(), _sc.CurrencyUpdateFormatter())
    registerMessengerServerFormatter(_SM_TYPE.personalMissionFailed.index(), _sc.PersonalMissionFailedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.customizationChanged.index(), _sc.CustomizationChangedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.lootBoxesAutoOpenReward.index(), _sc.LootBoxAutoOpenFormatter())
    registerMessengerServerFormatter(_SM_TYPE.progressiveReward.index(), _sc.ProgressiveRewardFormatter())
    registerMessengerServerFormatter(_SM_TYPE.piggyBankSmashed.index(), _sc.PiggyBankSmashedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.blackMapRemoved.index(), _sc.BlackMapRemovedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.enhancementRemoved.index(), _sc.EnhancementRemovedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.enhancementsWiped.index(), _sc.EnhancementsWipedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.battlePassReward.index(), _sc.BattlePassRewardFormatter())
    registerMessengerServerFormatter(_SM_TYPE.battlePassBought.index(), _sc.BattlePassBoughtFormatter())
    registerMessengerServerFormatter(_SM_TYPE.battlePassReachedCap.index(), _sc.BattlePassReachedCapFormatter())
    registerMessengerServerFormatter(_SM_TYPE.battlePassStyleRecieved.index(), _sc.BattlePassStyleReceivedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.battlePassSeasonEnd.index(), _sc.BattlePassSeasonEndFormatter())
    registerMessengerServerFormatter(_SM_TYPE.battlePassUseNonChapterPoints.index(), _sc.BattlePassFreePointsUsedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.collectibleVehiclesUnlocked.index(), _sc.CollectibleVehiclesUnlockedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.customizationProgress.index(), _sc.CustomizationProgressFormatter())
    registerMessengerServerFormatter(_SM_TYPE.dogTagsUnlockComponent.index(), _sc.DogTagComponentUnlockFormatter())
    registerMessengerServerFormatter(_SM_TYPE.dogTagsGradingChange.index(), _sc.DogTagComponentGradingFormatter())
    registerMessengerServerFormatter(_SM_TYPE.enhancementsWipedOnVehicles.index(), _sc.EnhancementsWipedOnVehiclesFormatter())
    registerMessengerServerFormatter(_SM_TYPE.prbWrongEnqueueDataKick.index(), _sc.PrbEventEnqueueDataFormatter())
    registerMessengerServerFormatter(_SM_TYPE.dedicationReward.index(), _sc.DedicationRewardFormatter())
    registerMessengerServerFormatter(_SM_TYPE.customizationProgressionChanged.index(), _sc.CustomizationProgressionChangedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.passiveXPActivated.index(), _wotPlusFormatters.PassiveXpActivatedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.passiveXPDeactivated.index(), _wotPlusFormatters.PassiveXpDeactivatedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.replacedConsumables.index(), _sc.ConsumableReplacedItemsFormatter())
    registerMessengerServerFormatter(_SM_TYPE.passiveXPSwitched.index(), _wotPlusFormatters.PassiveXpSwitchedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.wotPlusUnlocked.index(), _wotPlusFormatters.WotPlusUnlockedAwardFormatter())
    registerMessengerServerFormatter(_SM_TYPE.wotPlusRenewed.index(), _wotPlusFormatters.WotPlusRenewedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.wotPlusExcludedVehicleEnabled.index(), _sc.ExclusiveVehicleWotPlusFormatter(isEnabled=True))
    registerMessengerServerFormatter(_SM_TYPE.wotPlusExcludedVehicleExpired.index(), _sc.ExclusiveVehicleWotPlusFormatter(isEnabled=False))
    registerMessengerServerFormatter(_SM_TYPE.wotPlusExpired.index(), _wotPlusFormatters.WotPlusExpiredFormatter())
    registerMessengerServerFormatter(_SM_TYPE.bonusExcludedMap.index(), _sc.SimpleFormatter('BonusExcludedMapAvailable'))
    registerMessengerServerFormatter(_SM_TYPE.goldReserveIsFull.index(), _sc.SimpleFormatter('GoldReserveFullMessage'))
    registerMessengerServerFormatter(_SM_TYPE.passiveXPNoTank.index(), _sc.SimpleFormatter('PassiveXPNoTankMessage'))
    registerMessengerServerFormatter(_SM_TYPE.passiveXPIncompatibleCrewNewDay.index(), _sc.SimpleFormatter('PassiveXPIncompatibleCrewNewDayMessage'))
    registerMessengerServerFormatter(_SM_TYPE.passiveXPIncompatibleCrew.index(), _wotPlusFormatters.PassiveXpIncompatibleCrewFormatter())
    registerMessengerServerFormatter(_SM_TYPE.giftSystemMessage.index(), GiftSystemMessagesProxy())
    registerMessengerServerFormatter(_SM_TYPE.telecomMergeResults.index(), _sc.TelecomMergeResultsFormatter())
    registerMessengerServerFormatter(_SM_TYPE.epicSeasonEnd.index(), _sc.EpicSeasonEndFormatter())
    registerMessengerServerFormatter(_SM_TYPE.epicLevelUp.index(), _sc.EpicLevelUpFormatter())
    registerMessengerServerFormatter(_SM_TYPE.recertificationResetUsed.index(), _sc.RecertificationResetUsedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.recertificationReset.index(), _sc.RecertificationResetFormatter())
    registerMessengerServerFormatter(_SM_TYPE.recertificationAvailability.index(), _sc.RecertificationAvailabilityFormatter())
    registerMessengerServerFormatter(_SM_TYPE.recertificationFinancial.index(), _sc.RecertificationFinancialFormatter())
    registerMessengerServerFormatter(_SM_TYPE.resourceWellOperation.index(), _sc.ResourceWellOperationFormatter())
    registerMessengerServerFormatter(_SM_TYPE.resourceWellReward.index(), _sc.ResourceWellRewardFormatter())
    registerMessengerServerFormatter(_SM_TYPE.resourceWellNoVehicles.index(), _sc.ResourceWellNoVehiclesFormatter())
    registerMessengerServerFormatter(_SM_TYPE.customization2dProgressionChanged.index(), _sc.Customization2DProgressionChangedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.fairplay.index(), _sc.FairplayFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.SYS_MSG_TYPE, _sc.ClientSysMessageFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.PREMIUM_ACCOUNT_EXPIRY_MSG, _sc.PremiumAccountExpiryFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.AOGAS_NOTIFY_TYPE, _sc.AOGASNotifyFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.ACTION_NOTIFY_TYPE, _sc.ActionNotificationFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.KOREA_PARENTAL_CONTROL_TYPE, _sc.KoreaParentalControlFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.TECH_TREE_ACTION_DISCOUNT, _sc.TechTreeActionDiscountFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.BLUEPRINTS_CONVERT_SALE, _sc.BlueprintsConvertSaleFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.MAPBOX_PROGRESSION_REWARD, _sc.MapboxRewardReceivedFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.MAPBOX_EVENT_ENDED, _sc.MapboxEndedFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.MAPBOX_EVENT_STARTED, _sc.MapboxStartedFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.BATTLE_MATTERS_TOKEN_AWARD, _sc.BattleMattersTokenAward())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.WINBACK_SELECTABLE_REWARD, _sc.WinbackSelectableAward())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.WINBACK_BATTLERESULTS_REWARD, token_quest_subformatters.WinbackClientRewardFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.MAPBOX_SURVEY_AVAILABLE, _sc.MapboxSurveyAvailableFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.BATTLE_MATTERS_BATTLE_AWARD, token_quest_subformatters.BattleMattersClientAwardsFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.WOTPLUS_FEATURE_DISABLED, _sc.SimpleFormatter('WotPlusDisabled'))
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.INTEGRATED_AUCTION_LOST_RATE, _sc.IntegratedAuctionLostRateFormatter())
    registerMessengerServerFormatter(_SM_TYPE.collectionsItems.index(), _sc.CollectionsItemsFormatter())
    registerMessengerServerFormatter(_SM_TYPE.collectionsReward.index(), _sc.CollectionsRewardFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.ACHIEVEMENTS20_SM_TYPE, _sc.AchievementsSMFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.WOTPLUS_SUBSCRIPTION_UNLOCKED, _wotPlusFormatters.WotPlusUnlockedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.prestigeLevelChanged.index(), _sc.PrestigeFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.PERSONAL_RESERVES_FIRST_LOGIN, _prFormatters.ReleaseFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.PERSONAL_RESERVES_SOON_EXPIRATION, _prFormatters.PersonalReservesSoonExpirationFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.WOTPLUS_SUBSCRIBERS_ONBOARDING, _wotPlusFormatters.WotPlusSubscribersOnboardingFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.WOTPLUS_SWITCH, _wotPlusFormatters.WotPlusSwitchFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.ACHIEVEMENTS20_EARNING_SM_TYPE, _sc.AchievementsEarningSMFormatter())
    registerMessengerServerFormatter(_SM_TYPE.prbVehicleKickFromSquad.index(), _sc.PrbVehicleMaxTypeKickFormatter())
    registerMessengerServerFormatter(_SM_TYPE.skillsCrewBoostersConversion.index(), _sc.SkillsCrewBoostersConversionFormatter())
    registerMessengerServerFormatter(_SM_TYPE.passiveXPDeactivateDueToPostProgression.index(), _wotPlusFormatters.PassiveXPDeactivateDueToPostProgressionFormatter())
    registerMessengerServerFormatter(_SM_TYPE.crewBooksConversion.index(), _sc.CrewBooksConversionFormatter())
    registerMessengerServerFormatter(_SM_TYPE.postProgressionUnlocked.index(), _sc.PostProgressionUnlockedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.postProgressionCompleted.index(), _sc.PostProgressionCompletedFormatter())
    registerMessengerServerFormatter(_SM_TYPE.externalVehicleRentStarted.index(), _sc.ExternalVehicleRentFormatter(isStarted=True))
    registerMessengerServerFormatter(_SM_TYPE.externalVehicleRentExpired.index(), _sc.ExternalVehicleRentFormatter(isStarted=False))

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/views.py
from gui.impl.gen_utils import DynAccessor

class Views(DynAccessor):
    __slots__ = ()

    class _battle(DynAccessor):
        __slots__ = ()

        class _battleRoyale(DynAccessor):
            __slots__ = ()

            class _select_respawn(DynAccessor):
                __slots__ = ()
                SelectRespawn = DynAccessor(10)

            select_respawn = _select_respawn()

        battleRoyale = _battleRoyale()

        class _battle_notifier(DynAccessor):
            __slots__ = ()
            BattleNotifierView = DynAccessor(71)

        battle_notifier = _battle_notifier()

        class _battle_page(DynAccessor):
            __slots__ = ()
            EpicRespawnAmmunitionPanelView = DynAccessor(72)
            PersonalReservesTabView = DynAccessor(73)
            PrebattleAmmunitionPanelView = DynAccessor(74)
            TabView = DynAccessor(75)

        battle_page = _battle_page()

        class _death_cam(DynAccessor):
            __slots__ = ()
            DeathCamHudView = DynAccessor(76)
            DeathCamUIView = DynAccessor(77)
            MarkerView = DynAccessor(78)

        death_cam = _death_cam()

        class _dog_tags(DynAccessor):
            __slots__ = ()
            DogTagMarkerView = DynAccessor(79)

        dog_tags = _dog_tags()

        class _postmortem_panel(DynAccessor):
            __slots__ = ()
            PostmortemPanelView = DynAccessor(80)

        postmortem_panel = _postmortem_panel()

        class _prebattle(DynAccessor):
            __slots__ = ()
            PrebattleHintsView = DynAccessor(81)

        prebattle = _prebattle()

        class _timer(DynAccessor):
            __slots__ = ()
            TimerView = DynAccessor(82)

        timer = _timer()

    battle = _battle()

    class _common(DynAccessor):
        __slots__ = ()

        class _context_menu_window(DynAccessor):
            __slots__ = ()

            class _context_menu_content(DynAccessor):
                __slots__ = ()
                ContextMenuContent = DynAccessor(11)

            context_menu_content = _context_menu_content()

            class _context_menu_window(DynAccessor):
                __slots__ = ()
                ContextMenuWindow = DynAccessor(12)

            context_menu_window = _context_menu_window()

        context_menu_window = _context_menu_window()

        class _dialog_view(DynAccessor):
            __slots__ = ()

            class _dialog_window(DynAccessor):
                __slots__ = ()
                DialogWindow = DynAccessor(13)

            dialog_window = _dialog_window()

            class _simple_dialog_content(DynAccessor):
                __slots__ = ()
                SimpleDialogContent = DynAccessor(14)

            simple_dialog_content = _simple_dialog_content()

            class _components(DynAccessor):
                __slots__ = ()

                class _balance_contents(DynAccessor):
                    __slots__ = ()
                    CommonBalanceContent = DynAccessor(15)

                balance_contents = _balance_contents()

                class _checkbox_content(DynAccessor):
                    __slots__ = ()
                    CheckBoxDialogContent = DynAccessor(16)

                checkbox_content = _checkbox_content()

                class _dialog_prices_content(DynAccessor):
                    __slots__ = ()
                    DialogPricesContent = DynAccessor(17)

                dialog_prices_content = _dialog_prices_content()

                class _dialog_prices_tooltip(DynAccessor):
                    __slots__ = ()
                    DialogPricesTooltip = DynAccessor(18)

                dialog_prices_tooltip = _dialog_prices_tooltip()

            components = _components()

        dialog_view = _dialog_view()

        class _drop_down_menu_window(DynAccessor):
            __slots__ = ()

            class _drop_down_menu_content(DynAccessor):
                __slots__ = ()
                DropDownMenuContent = DynAccessor(19)

            drop_down_menu_content = _drop_down_menu_content()

            class _drop_down_menu_window(DynAccessor):
                __slots__ = ()
                DropDownMenuWindow = DynAccessor(20)

            drop_down_menu_window = _drop_down_menu_window()

        drop_down_menu_window = _drop_down_menu_window()

        class _pop_over_window(DynAccessor):
            __slots__ = ()

            class _backport_pop_over(DynAccessor):
                __slots__ = ()
                BackportPopOverContent = DynAccessor(21)
                BackportPopOverWindow = DynAccessor(22)

            backport_pop_over = _backport_pop_over()

            class _pop_over_window(DynAccessor):
                __slots__ = ()
                PopOverWindow = DynAccessor(23)

            pop_over_window = _pop_over_window()

        pop_over_window = _pop_over_window()

        class _standard_window(DynAccessor):
            __slots__ = ()

            class _standard_window(DynAccessor):
                __slots__ = ()
                StandardWindow = DynAccessor(24)

            standard_window = _standard_window()

        standard_window = _standard_window()

        class _tooltip_window(DynAccessor):
            __slots__ = ()

            class _advanced_tooltip_content(DynAccessor):
                __slots__ = ()
                AdvandcedTooltipContent = DynAccessor(25)
                AdvandcedAnimatedTooltipContent = DynAccessor(26)

            advanced_tooltip_content = _advanced_tooltip_content()

            class _backport_tooltip_content(DynAccessor):
                __slots__ = ()
                BackportTooltipContent = DynAccessor(27)

            backport_tooltip_content = _backport_tooltip_content()

            class _loot_box_compensation_tooltip(DynAccessor):
                __slots__ = ()
                LootBoxCompensationTooltipContent = DynAccessor(28)
                CrewSkinsCompensationTooltipContent = DynAccessor(29)
                LootBoxVehicleCompensationTooltipContent = DynAccessor(30)

            loot_box_compensation_tooltip = _loot_box_compensation_tooltip()

            class _simple_tooltip_content(DynAccessor):
                __slots__ = ()
                SimpleTooltipContent = DynAccessor(31)
                SimpleTooltipHtmlContent = DynAccessor(32)

            simple_tooltip_content = _simple_tooltip_content()

            class _tooltip_window(DynAccessor):
                __slots__ = ()
                TooltipWindow = DynAccessor(33)

            tooltip_window = _tooltip_window()

        tooltip_window = _tooltip_window()
        BackportContextMenu = DynAccessor(83)
        Browser = DynAccessor(84)
        FadingCoverView = DynAccessor(85)
        HintButton = DynAccessor(86)

        class _personal_reserves(DynAccessor):
            __slots__ = ()
            ReservesDisabledTooltip = DynAccessor(87)

        personal_reserves = _personal_reserves()

    common = _common()

    class _lobby(DynAccessor):
        __slots__ = ()

        class _battle_pass(DynAccessor):
            __slots__ = ()

            class _trophy_device_confirm_dialog(DynAccessor):
                __slots__ = ()
                TrophyDeviceConfirmDialogContent = DynAccessor(34)

            trophy_device_confirm_dialog = _trophy_device_confirm_dialog()
            BattlePassAwardsView = DynAccessor(140)
            BattlePassBuyLevelView = DynAccessor(141)
            BattlePassBuyView = DynAccessor(142)
            BattlePassEntryPointView = DynAccessor(143)
            BattlePassHowToEarnPointsView = DynAccessor(144)
            BattlePassIntroView = DynAccessor(145)
            BattlePassProgressionsView = DynAccessor(146)
            BattlePassVehicleAwardView = DynAccessor(147)
            ChapterChoiceView = DynAccessor(148)

            class _dialogs(DynAccessor):
                __slots__ = ()
                ChapterConfirm = DynAccessor(149)

            dialogs = _dialogs()
            ExtraIntroView = DynAccessor(150)
            FullscreenVideoView = DynAccessor(151)
            HolidayFinalView = DynAccessor(152)
            MainView = DynAccessor(153)
            PostProgressionView = DynAccessor(154)
            RewardsSelectionView = DynAccessor(155)
            RewardsViewContent = DynAccessor(156)

            class _sharedComponents(DynAccessor):
                __slots__ = ()
                AnimatedReward = DynAccessor(157)
                AttachmentOverlay = DynAccessor(158)
                AwardsWidget = DynAccessor(159)
                BuyButtons = DynAccessor(160)
                ChapterBackground = DynAccessor(161)
                CurrencyReward = DynAccessor(162)
                Emblem = DynAccessor(163)
                FormatRemainingDate = DynAccessor(164)
                Header = DynAccessor(165)
                LoupeButton = DynAccessor(166)
                RewardsBlock = DynAccessor(167)
                ScrollWithLips = DynAccessor(168)
                Slider = DynAccessor(169)
                TankmanSkills = DynAccessor(170)
                Title = DynAccessor(171)
                VehicleBonusList = DynAccessor(172)
                VehicleInfo = DynAccessor(173)
                VehicleList = DynAccessor(174)

            sharedComponents = _sharedComponents()
            TankmenVoiceoverView = DynAccessor(175)

            class _tooltips(DynAccessor):
                __slots__ = ()
                BattlePassCoinTooltipView = DynAccessor(176)
                BattlePassCompletedTooltipView = DynAccessor(177)
                BattlePassGoldMissionTooltipView = DynAccessor(178)
                BattlePassInProgressTooltipView = DynAccessor(179)
                BattlePassLockIconTooltipView = DynAccessor(180)
                BattlePassNoChapterTooltipView = DynAccessor(181)
                BattlePassOnPauseTooltipView = DynAccessor(182)
                BattlePassPointsView = DynAccessor(183)
                BattlePassQuestsChainTooltipView = DynAccessor(184)
                BattlePassTalerTooltip = DynAccessor(185)
                BattlePassUpgradeStyleTooltipView = DynAccessor(186)
                CrewMemberSkillTooltip = DynAccessor(187)
                RandomQuestTooltip = DynAccessor(188)

                class _sharedComponents(DynAccessor):
                    __slots__ = ()
                    BlockCompleted = DynAccessor(189)
                    Chose = DynAccessor(190)
                    FinalLevel = DynAccessor(191)
                    IconTextBlock = DynAccessor(192)
                    PerBattlePointsTable = DynAccessor(193)
                    Point = DynAccessor(194)
                    Rewards = DynAccessor(195)
                    Separator = DynAccessor(196)

                sharedComponents = _sharedComponents()
                VehiclePointsTooltipView = DynAccessor(197)

            tooltips = _tooltips()

        battle_pass = _battle_pass()

        class _blueprints(DynAccessor):
            __slots__ = ()

            class _fragments_balance_content(DynAccessor):
                __slots__ = ()
                FragmentsBalanceContent = DynAccessor(35)

            fragments_balance_content = _fragments_balance_content()

            class _blueprint_screen(DynAccessor):
                __slots__ = ()

                class _blueprint_screen(DynAccessor):
                    __slots__ = ()
                    BlueprintScreen = DynAccessor(36)

                blueprint_screen = _blueprint_screen()

            blueprint_screen = _blueprint_screen()
            Confirm = DynAccessor(198)

            class _tooltips(DynAccessor):
                __slots__ = ()
                BlueprintsAlliancesTooltipView = DynAccessor(199)

            tooltips = _tooltips()

        blueprints = _blueprints()

        class _common(DynAccessor):
            __slots__ = ()

            class _congrats(DynAccessor):
                __slots__ = ()

                class _common_congrats_view(DynAccessor):
                    __slots__ = ()
                    CommonCongratsView = DynAccessor(37)

                common_congrats_view = _common_congrats_view()

            congrats = _congrats()
            AwardsView = DynAccessor(208)
            BrowserView = DynAccessor(209)
            RewardSelection = DynAccessor(210)
            SelectableRewardBase = DynAccessor(211)
            SelectSlotSpecDialog = DynAccessor(212)

            class _tooltips(DynAccessor):
                __slots__ = ()
                ExtendedTextTooltip = DynAccessor(213)
                SelectedRewardsTooltipView = DynAccessor(214)
                SimpleIconTooltip = DynAccessor(215)

            tooltips = _tooltips()

        common = _common()

        class _marathon(DynAccessor):
            __slots__ = ()

            class _marathon_reward_view(DynAccessor):
                __slots__ = ()
                MarathonRewardView = DynAccessor(38)

            marathon_reward_view = _marathon_reward_view()
            RewardWindow = DynAccessor(316)

            class _tooltips(DynAccessor):
                __slots__ = ()
                RestRewardTooltip = DynAccessor(317)

            tooltips = _tooltips()

        marathon = _marathon()

        class _missions(DynAccessor):
            __slots__ = ()

            class _missions_tab_bar_view(DynAccessor):
                __slots__ = ()
                MissionsTabBarView = DynAccessor(39)

            missions_tab_bar_view = _missions_tab_bar_view()

        missions = _missions()

        class _nation_change(DynAccessor):
            __slots__ = ()

            class _nation_change_screen(DynAccessor):
                __slots__ = ()
                NationChangeScreen = DynAccessor(40)

            nation_change_screen = _nation_change_screen()

        nation_change = _nation_change()

        class _progressive_reward(DynAccessor):
            __slots__ = ()

            class _progressive_reward_award(DynAccessor):
                __slots__ = ()
                ProgressiveRewardAward = DynAccessor(41)

            progressive_reward_award = _progressive_reward_award()

            class _progressive_reward_view(DynAccessor):
                __slots__ = ()
                ProgressiveRewardView = DynAccessor(42)

            progressive_reward_view = _progressive_reward_view()

        progressive_reward = _progressive_reward()

        class _ranked(DynAccessor):
            __slots__ = ()

            class _ranked_year_award(DynAccessor):
                __slots__ = ()
                RankedYearAward = DynAccessor(43)

            ranked_year_award = _ranked_year_award()
            QualificationRewardsView = DynAccessor(365)
            RankedSelectableRewardView = DynAccessor(366)

            class _tooltips(DynAccessor):
                __slots__ = ()
                RankedBattlesRolesTooltipView = DynAccessor(367)

            tooltips = _tooltips()
            YearLeaderboardView = DynAccessor(368)

        ranked = _ranked()

        class _reward_window(DynAccessor):
            __slots__ = ()

            class _clan_reward_window_content(DynAccessor):
                __slots__ = ()
                ClanRewardWindowContent = DynAccessor(44)

            clan_reward_window_content = _clan_reward_window_content()

            class _piggy_bank_reward_window_content(DynAccessor):
                __slots__ = ()
                PiggyBankRewardWindowContent = DynAccessor(45)

            piggy_bank_reward_window_content = _piggy_bank_reward_window_content()

            class _reward_window_content(DynAccessor):
                __slots__ = ()
                RewardWindowContent = DynAccessor(46)

            reward_window_content = _reward_window_content()

            class _twitch_reward_window_content(DynAccessor):
                __slots__ = ()
                TwitchRewardWindowContent = DynAccessor(47)

            twitch_reward_window_content = _twitch_reward_window_content()

        reward_window = _reward_window()

        class _tooltips(DynAccessor):
            __slots__ = ()

            class _clans(DynAccessor):
                __slots__ = ()
                ClanShortInfoTooltipContent = DynAccessor(48)

            clans = _clans()
            AdditionalBattlePassRewardsTooltip = DynAccessor(415)
            AdditionalRewardsTooltip = DynAccessor(416)
            BattleResultsStatsTooltipView = DynAccessor(417)
            TankmanTooltipView = DynAccessor(418)
            VehPostProgressionEntryPointTooltip = DynAccessor(419)

        tooltips = _tooltips()

        class _account_completion(DynAccessor):
            __slots__ = ()
            AddCredentialsView = DynAccessor(106)
            ConfirmCredentialsView = DynAccessor(107)
            CurtainView = DynAccessor(108)
            SteamEmailConfirmRewardsView = DynAccessor(109)

            class _tooltips(DynAccessor):
                __slots__ = ()
                HangarTooltip = DynAccessor(110)

            tooltips = _tooltips()

        account_completion = _account_completion()

        class _account_dashboard(DynAccessor):
            __slots__ = ()
            AccountDashboard = DynAccessor(111)
            DailyExperienceView = DynAccessor(112)

        account_dashboard = _account_dashboard()

        class _achievements(DynAccessor):
            __slots__ = ()
            AchievementsMainView = DynAccessor(113)
            CatalogView = DynAccessor(114)

            class _dialogs(DynAccessor):
                __slots__ = ()
                EditConfirm = DynAccessor(115)

            dialogs = _dialogs()
            EarningPopUpView = DynAccessor(116)
            EditView = DynAccessor(117)
            RewardView = DynAccessor(118)

            class _tooltips(DynAccessor):
                __slots__ = ()
                AutoSettingTooltip = DynAccessor(119)
                BattlesKPITooltip = DynAccessor(120)
                EditingTooltip = DynAccessor(121)
                KPITooltip = DynAccessor(122)
                WOTPRMainTooltip = DynAccessor(123)
                WTRInfoTooltip = DynAccessor(124)
                WTRMainTooltip = DynAccessor(125)

            tooltips = _tooltips()

        achievements = _achievements()

        class _awards(DynAccessor):
            __slots__ = ()
            BadgeAwardView = DynAccessor(126)
            MultipleAwardsView = DynAccessor(127)

            class _tooltips(DynAccessor):
                __slots__ = ()
                RewardCompensationTooltip = DynAccessor(128)
                VehicleForChooseTooltip = DynAccessor(129)

            tooltips = _tooltips()

        awards = _awards()

        class _battle_matters(DynAccessor):
            __slots__ = ()
            BattleMattersEntryPointView = DynAccessor(130)
            BattleMattersExchangeRewards = DynAccessor(131)
            BattleMattersMainRewardView = DynAccessor(132)
            BattleMattersMainView = DynAccessor(133)
            BattleMattersPausedView = DynAccessor(134)
            BattleMattersRewardsView = DynAccessor(135)
            BattleMattersVehicleSelectionView = DynAccessor(136)

            class _popovers(DynAccessor):
                __slots__ = ()
                BattleMattersFilterPopoverView = DynAccessor(137)

            popovers = _popovers()

            class _tooltips(DynAccessor):
                __slots__ = ()
                BattleMattersEntryTooltipView = DynAccessor(138)
                BattleMattersTokenTooltipView = DynAccessor(139)

            tooltips = _tooltips()

        battle_matters = _battle_matters()

        class _clan_supply(DynAccessor):
            __slots__ = ()
            ClanSupply = DynAccessor(200)
            RewardsView = DynAccessor(201)

        clan_supply = _clan_supply()

        class _collection(DynAccessor):
            __slots__ = ()
            AwardsView = DynAccessor(202)
            CollectionItemPreview = DynAccessor(203)
            CollectionsMainView = DynAccessor(204)
            CollectionView = DynAccessor(205)
            IntroView = DynAccessor(206)

            class _tooltips(DynAccessor):
                __slots__ = ()
                CollectionItemTooltipView = DynAccessor(207)

            tooltips = _tooltips()

        collection = _collection()

        class _crew(DynAccessor):
            __slots__ = ()
            BarracksView = DynAccessor(216)
            ConversionConfirmView = DynAccessor(217)
            CrewHeaderTooltipView = DynAccessor(218)
            CrewPostProgressionView = DynAccessor(219)

            class _dialogs(DynAccessor):
                __slots__ = ()
                CrewBooksPurchaseDialog = DynAccessor(220)
                DismissTankmanDialog = DynAccessor(221)
                DocumentChangeDialog = DynAccessor(222)
                EnlargeBarracksDialog = DynAccessor(223)
                FillAllPerksDialog = DynAccessor(224)
                MentorAssignmentDialog = DynAccessor(225)
                PerksResetDialog = DynAccessor(226)
                RecruitConfirmIrrelevantDialog = DynAccessor(227)
                RecruitDialog = DynAccessor(228)
                RecruitNewTankmanDialog = DynAccessor(229)
                RestoreTankmanDialog = DynAccessor(230)
                RetrainMassiveDialog = DynAccessor(231)
                RetrainPremiumVehicleDialog = DynAccessor(232)
                RetrainSingleDialog = DynAccessor(233)
                SkillsTrainingConfirmDialog = DynAccessor(234)
                SkinApplyDialog = DynAccessor(235)

            dialogs = _dialogs()
            HangarCrewWidget = DynAccessor(236)
            HelpView = DynAccessor(237)
            JunkTankmenView = DynAccessor(238)
            MemberChangeView = DynAccessor(239)
            MentorAssigmentView = DynAccessor(240)

            class _personal_case(DynAccessor):
                __slots__ = ()
                PersonalDataView = DynAccessor(241)
                PersonalFileView = DynAccessor(242)
                ServiceRecordView = DynAccessor(243)

            personal_case = _personal_case()

            class _popovers(DynAccessor):
                __slots__ = ()
                FilterPopoverView = DynAccessor(244)

            popovers = _popovers()
            QuickTrainingView = DynAccessor(245)
            SkillsTrainingView = DynAccessor(246)
            TankChangeView = DynAccessor(247)
            TankmanContainerView = DynAccessor(248)

            class _tooltips(DynAccessor):
                __slots__ = ()
                AdvancedTooltipView = DynAccessor(249)
                BonusPerksTooltip = DynAccessor(250)
                BunksConfirmDiscountTooltip = DynAccessor(251)
                ConversionTooltip = DynAccessor(252)
                CrewBookMouseTooltip = DynAccessor(253)
                CrewPerksAdditionalTooltip = DynAccessor(254)
                CrewPerksTooltip = DynAccessor(255)
                DirectiveConversionTooltip = DynAccessor(256)
                DismissedToggleTooltip = DynAccessor(257)
                EmptySkillTooltip = DynAccessor(258)
                ExperienceStepperTooltip = DynAccessor(259)
                MentorAssignmentTooltip = DynAccessor(260)
                MentoringLicenseTooltip = DynAccessor(261)
                PostProgressionTooltip = DynAccessor(262)
                PremiumVehicleTooltip = DynAccessor(263)
                QualificationTooltip = DynAccessor(264)
                QuickTrainingDiscountTooltip = DynAccessor(265)
                QuickTrainingLostXpTooltip = DynAccessor(266)
                RetireUndertrainedTooltip = DynAccessor(267)
                SkillsEfficiencyTooltip = DynAccessor(268)
                SkillUntrainedAdditionalTooltip = DynAccessor(269)
                SkillUntrainedTooltip = DynAccessor(270)
                SortingDropdownTooltip = DynAccessor(271)
                SpecializationWotPlusTooltip = DynAccessor(272)
                TankmanTooltip = DynAccessor(273)
                VehCmpSkillsTooltip = DynAccessor(274)
                VehicleParamsTooltipView = DynAccessor(275)

            tooltips = _tooltips()

            class _widgets(DynAccessor):
                __slots__ = ()
                CrewBannerWidget = DynAccessor(276)
                CrewWidget = DynAccessor(277)
                FilterPanelWidget = DynAccessor(278)
                PriceList = DynAccessor(279)
                TankmanInfo = DynAccessor(280)

            widgets = _widgets()

        crew = _crew()

        class _crystalsPromo(DynAccessor):
            __slots__ = ()
            CrystalsPromoView = DynAccessor(281)

        crystalsPromo = _crystalsPromo()

        class _currency_reserves(DynAccessor):
            __slots__ = ()
            CurrencyReserves = DynAccessor(282)
            ReservesAwardView = DynAccessor(283)

        currency_reserves = _currency_reserves()

        class _customization(DynAccessor):
            __slots__ = ()
            CustomizationCart = DynAccessor(284)
            CustomizationRarityRewardScreen = DynAccessor(285)

            class _progression_styles(DynAccessor):
                __slots__ = ()
                OnboardingView = DynAccessor(286)
                StageSwitcher = DynAccessor(287)

            progression_styles = _progression_styles()

            class _progressive_items_reward(DynAccessor):
                __slots__ = ()
                ProgressiveItemsUpgradeView = DynAccessor(288)

            progressive_items_reward = _progressive_items_reward()

            class _progressive_items_view(DynAccessor):
                __slots__ = ()
                ProgressiveItemsView = DynAccessor(289)

            progressive_items_view = _progressive_items_view()

            class _style_unlocked_view(DynAccessor):
                __slots__ = ()
                StyleUnlockedView = DynAccessor(290)

            style_unlocked_view = _style_unlocked_view()

            class _vehicles_sidebar(DynAccessor):
                __slots__ = ()
                VehiclesSidebar = DynAccessor(291)

            vehicles_sidebar = _vehicles_sidebar()

        customization = _customization()

        class _dedication(DynAccessor):
            __slots__ = ()
            DedicationRewardView = DynAccessor(292)

        dedication = _dedication()

        class _dog_tags(DynAccessor):
            __slots__ = ()
            AnimatedDogTagGradeTooltip = DynAccessor(293)
            AnimatedDogTagsView = DynAccessor(294)
            CatalogAnimatedDogTagTooltip = DynAccessor(295)
            CustomizationConfirmDialog = DynAccessor(296)
            DedicationTooltip = DynAccessor(297)
            DogTagsView = DynAccessor(298)
            RankedEfficiencyTooltip = DynAccessor(299)
            ThreeMonthsTooltip = DynAccessor(300)
            TriumphTooltip = DynAccessor(301)

        dog_tags = _dog_tags()

        class _excluded_maps(DynAccessor):
            __slots__ = ()
            ExcludedMapsTooltip = DynAccessor(302)
            ExcludedMapsView = DynAccessor(303)

        excluded_maps = _excluded_maps()

        class _hangar(DynAccessor):
            __slots__ = ()
            BuyVehicleView = DynAccessor(304)

            class _notifications(DynAccessor):
                __slots__ = ()
                PunishmentView = DynAccessor(305)

            notifications = _notifications()

            class _subViews(DynAccessor):
                __slots__ = ()
                VehicleParams = DynAccessor(306)

            subViews = _subViews()
            VehicleParamsWidget = DynAccessor(307)

        hangar = _hangar()

        class _instructions(DynAccessor):
            __slots__ = ()
            BuyWindow = DynAccessor(308)
            SellWindow = DynAccessor(309)

        instructions = _instructions()

        class _live_ops_web_events(DynAccessor):
            __slots__ = ()
            EntryPoint = DynAccessor(310)
            EntryPointTooltip = DynAccessor(311)

        live_ops_web_events = _live_ops_web_events()

        class _mapbox(DynAccessor):
            __slots__ = ()
            MapBoxAwardsView = DynAccessor(312)
            MapBoxIntro = DynAccessor(313)
            MapBoxProgression = DynAccessor(314)
            MapBoxSurveyView = DynAccessor(315)

        mapbox = _mapbox()

        class _matchmaker(DynAccessor):
            __slots__ = ()
            ActiveTestConfirmView = DynAccessor(318)

        matchmaker = _matchmaker()

        class _mode_selector(DynAccessor):
            __slots__ = ()
            BattleSessionView = DynAccessor(319)
            ModeSelectorView = DynAccessor(320)

            class _tooltips(DynAccessor):
                __slots__ = ()
                AlertTooltip = DynAccessor(321)

                class _common(DynAccessor):
                    __slots__ = ()
                    Divider = DynAccessor(322)
                    GradientDecorator = DynAccessor(323)

                common = _common()
                SimplyFormatTooltip = DynAccessor(324)

            tooltips = _tooltips()

            class _widgets(DynAccessor):
                __slots__ = ()
                EpicWidget = DynAccessor(325)
                RankedWidget = DynAccessor(326)

            widgets = _widgets()

        mode_selector = _mode_selector()

        class _offers(DynAccessor):
            __slots__ = ()
            OfferBannerWindow = DynAccessor(327)
            OfferGiftsWindow = DynAccessor(328)
            OfferRewardWindow = DynAccessor(329)

        offers = _offers()

        class _personal_exchange_rates(DynAccessor):
            __slots__ = ()
            AllPersonalExchangesView = DynAccessor(330)
            ExperienceExchangeView = DynAccessor(331)
            GoldExchangeView = DynAccessor(332)

            class _tooltips(DynAccessor):
                __slots__ = ()
                ExchangeLimitTooltip = DynAccessor(333)
                ExchangeRateTooltip = DynAccessor(334)

            tooltips = _tooltips()

        personal_exchange_rates = _personal_exchange_rates()

        class _personal_reserves(DynAccessor):
            __slots__ = ()
            BoosterTooltip = DynAccessor(335)
            PersonalReservesTooltip = DynAccessor(336)
            PersonalReservesWidget = DynAccessor(337)
            QuestBoosterTooltip = DynAccessor(338)
            ReserveCard = DynAccessor(339)
            ReserveCardTooltip = DynAccessor(340)
            ReserveGroup = DynAccessor(341)
            ReservesActivationView = DynAccessor(342)
            ReservesIntroView = DynAccessor(343)

        personal_reserves = _personal_reserves()

        class _platoon(DynAccessor):
            __slots__ = ()
            AlertTooltip = DynAccessor(344)
            MembersWindow = DynAccessor(345)
            PlatoonDropdown = DynAccessor(346)
            SearchingDropdown = DynAccessor(347)
            SettingsPopover = DynAccessor(348)

            class _subViews(DynAccessor):
                __slots__ = ()
                Chat = DynAccessor(349)
                SettingsContent = DynAccessor(350)
                TiersLimit = DynAccessor(351)

            subViews = _subViews()
            WTRTooltip = DynAccessor(352)

        platoon = _platoon()

        class _player_subscriptions(DynAccessor):
            __slots__ = ()
            PlayerSubscriptions = DynAccessor(353)
            SubscriptionItem = DynAccessor(354)
            SubscriptionRewardView = DynAccessor(355)

        player_subscriptions = _player_subscriptions()

        class _premacc(DynAccessor):
            __slots__ = ()

            class _tooltips(DynAccessor):
                __slots__ = ()
                SquadBonusTooltip = DynAccessor(356)

            tooltips = _tooltips()

        premacc = _premacc()

        class _prestige(DynAccessor):
            __slots__ = ()

            class _sharedComponents(DynAccessor):
                __slots__ = ()
                PrestigeProgressSymbol = DynAccessor(357)
                PrestigeProgressTab = DynAccessor(358)

            sharedComponents = _sharedComponents()

            class _tooltips(DynAccessor):
                __slots__ = ()
                EliteLevelGradesTooltip = DynAccessor(359)

            tooltips = _tooltips()

            class _views(DynAccessor):
                __slots__ = ()
                GlobalOnboardingView = DynAccessor(360)
                PrestigeHangarEntryPoint = DynAccessor(361)
                PrestigeProfileTechniqueEmblemView = DynAccessor(362)
                PrestigeProfileTechniqueView = DynAccessor(363)
                PrestigeRewardView = DynAccessor(364)

            views = _views()

        prestige = _prestige()

        class _research(DynAccessor):
            __slots__ = ()
            BuyModuleDialogView = DynAccessor(369)
            InsufficientCreditsTooltip = DynAccessor(370)
            SoldModuleInfoTooltip = DynAccessor(371)

        research = _research()

        class _tanksetup(DynAccessor):
            __slots__ = ()
            AmmunitionPanel = DynAccessor(372)

            class _common(DynAccessor):
                __slots__ = ()
                Action = DynAccessor(373)
                CtaButtons = DynAccessor(374)
                DealPanel = DynAccessor(375)
                DemountKit = DynAccessor(376)
                ExtraImage = DynAccessor(377)
                FormatColorTagText = DynAccessor(378)
                Location = DynAccessor(379)
                MaybeWrapper = DynAccessor(380)
                Price = DynAccessor(381)
                SetupApp = DynAccessor(382)
                ShortenedText = DynAccessor(383)
                Slider = DynAccessor(384)

                class _SlotParts(DynAccessor):
                    __slots__ = ()
                    Bonus = DynAccessor(385)
                    Container = DynAccessor(386)
                    Count = DynAccessor(387)
                    Inside = DynAccessor(388)
                    Level = DynAccessor(389)

                SlotParts = _SlotParts()
                Specializations = DynAccessor(390)
                SwitchButton = DynAccessor(391)
                SwitchEquipment = DynAccessor(392)

                class _Transitions(DynAccessor):
                    __slots__ = ()
                    SlotTransitions = DynAccessor(393)

                Transitions = _Transitions()
                WeaponOccupancy = DynAccessor(394)

            common = _common()
            DeconstructionDeviceView = DynAccessor(395)

            class _dialogs(DynAccessor):
                __slots__ = ()
                Confirm = DynAccessor(396)
                ConfirmActionsWithEquipmentDialog = DynAccessor(397)
                DeconstructConfirm = DynAccessor(398)
                DeviceUpgradeDialog = DynAccessor(399)
                ExchangeToApplyEasyTankEquip = DynAccessor(400)
                ExchangeToBuyItems = DynAccessor(401)
                ExchangeToUpgradeItems = DynAccessor(402)
                NeedRepair = DynAccessor(403)
                RefillShells = DynAccessor(404)
                Sell = DynAccessor(405)

            dialogs = _dialogs()
            HangarAmmunitionSetup = DynAccessor(406)
            IntroScreen = DynAccessor(407)

            class _tooltips(DynAccessor):
                __slots__ = ()
                DeconstructFromInventoryTooltip = DynAccessor(408)
                DeconstructFromVehicleTooltip = DynAccessor(409)
                PopularLoadoutsTooltip = DynAccessor(410)
                SetupTabTooltipView = DynAccessor(411)
                WarningTooltipView = DynAccessor(412)

            tooltips = _tooltips()
            VehicleCompareAmmunitionPanel = DynAccessor(413)
            VehicleCompareAmmunitionSetup = DynAccessor(414)

        tanksetup = _tanksetup()

        class _vehicle_compare(DynAccessor):
            __slots__ = ()
            CompareModificationsPanelView = DynAccessor(420)
            CompareSkillsPanelView = DynAccessor(421)
            SelectSlotSpecCompareDialog = DynAccessor(422)
            SkillSelectView = DynAccessor(423)

            class _tooltips(DynAccessor):
                __slots__ = ()
                CrewRolesTooltip = DynAccessor(424)

            tooltips = _tooltips()

        vehicle_compare = _vehicle_compare()

        class _vehicle_preview(DynAccessor):
            __slots__ = ()

            class _buying_panel(DynAccessor):
                __slots__ = ()
                StyleBuyingPanel = DynAccessor(425)
                VPProgressionStylesBuyingPanel = DynAccessor(426)

            buying_panel = _buying_panel()

            class _tabs(DynAccessor):
                __slots__ = ()
                CrewTabView = DynAccessor(427)

            tabs = _tabs()

            class _top_panel(DynAccessor):
                __slots__ = ()
                TopPanelTabs = DynAccessor(428)

            top_panel = _top_panel()

        vehicle_preview = _vehicle_preview()

        class _veh_post_progression(DynAccessor):
            __slots__ = ()

            class _common(DynAccessor):
                __slots__ = ()
                Bonus = DynAccessor(429)
                Description = DynAccessor(430)
                Grid = DynAccessor(431)
                PersistentBonuses = DynAccessor(432)
                Slide = DynAccessor(433)
                SlideContent = DynAccessor(434)
                Slider = DynAccessor(435)
                TextSplit = DynAccessor(436)

            common = _common()
            PostProgressionInfo = DynAccessor(437)
            PostProgressionIntro = DynAccessor(438)
            PostProgressionResearchSteps = DynAccessor(439)

            class _tooltip(DynAccessor):
                __slots__ = ()

                class _common(DynAccessor):
                    __slots__ = ()
                    DisabledBlock = DynAccessor(440)
                    FeatureLevelSubtitle = DynAccessor(441)
                    Lock = DynAccessor(442)
                    NotEnoughCredits = DynAccessor(443)
                    PriceBlock = DynAccessor(444)
                    Separator = DynAccessor(445)

                common = _common()
                PairModificationTooltipView = DynAccessor(446)
                PostProgressionLevelTooltipView = DynAccessor(447)
                RoleSlotTooltipView = DynAccessor(448)
                SetupTooltipView = DynAccessor(449)

            tooltip = _tooltip()
            VehiclePostProgressionCmpView = DynAccessor(450)
            VehiclePostProgressionView = DynAccessor(451)

        veh_post_progression = _veh_post_progression()

        class _winback(DynAccessor):
            __slots__ = ()

            class _popovers(DynAccessor):
                __slots__ = ()
                WinbackLeaveModePopoverView = DynAccessor(452)

            popovers = _popovers()

            class _tooltips(DynAccessor):
                __slots__ = ()
                MainRewardTooltip = DynAccessor(453)
                ModeInfoTooltip = DynAccessor(454)
                SelectableRewardTooltip = DynAccessor(455)
                SelectedRewardsTooltip = DynAccessor(456)

            tooltips = _tooltips()
            WinbackDailyQuestsIntroView = DynAccessor(457)
            WinbackLeaveModeDialogView = DynAccessor(458)
            WinbackRewardView = DynAccessor(459)
            WinbackSelectableRewardView = DynAccessor(460)

        winback = _winback()

    lobby = _lobby()

    class _test_check_box_view(DynAccessor):
        __slots__ = ()
        TestCheckBoxView = DynAccessor(49)

    test_check_box_view = _test_check_box_view()

    class _test_text_button_view(DynAccessor):
        __slots__ = ()
        TestTextButtonView = DynAccessor(50)

    test_text_button_view = _test_text_button_view()

    class _windows_layout_view(DynAccessor):
        __slots__ = ()
        WindowsLayountView = DynAccessor(51)

    windows_layout_view = _windows_layout_view()

    class _blend_mode(DynAccessor):
        __slots__ = ()

        class _blend_mode(DynAccessor):
            __slots__ = ()
            BlendMode = DynAccessor(52)

        blend_mode = _blend_mode()

    blend_mode = _blend_mode()

    class _demo_view(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _demo_window_content(DynAccessor):
                __slots__ = ()
                DemoWindowContent = DynAccessor(53)
                ImageProps = DynAccessor(54)

            demo_window_content = _demo_window_content()

            class _demo_window_details_panel(DynAccessor):
                __slots__ = ()
                DemoWindowDetailsPanel = DynAccessor(55)

            demo_window_details_panel = _demo_window_details_panel()

            class _demo_window_image_panel(DynAccessor):
                __slots__ = ()
                DemoWindowImagePanel = DynAccessor(56)

            demo_window_image_panel = _demo_window_image_panel()

            class _image_preview_window_content(DynAccessor):
                __slots__ = ()
                ImagePreviewWindowContent = DynAccessor(57)

            image_preview_window_content = _image_preview_window_content()

        views = _views()

    demo_view = _demo_view()

    class _examples(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _test_dialogs_view(DynAccessor):
                __slots__ = ()
                TestDialogsView = DynAccessor(58)

            test_dialogs_view = _test_dialogs_view()

            class _test_expr_functions_view(DynAccessor):
                __slots__ = ()
                TestExprFunctionsView = DynAccessor(59)

            test_expr_functions_view = _test_expr_functions_view()

            class _test_sub_view(DynAccessor):
                __slots__ = ()
                TestSubView = DynAccessor(60)

            test_sub_view = _test_sub_view()

            class _test_view(DynAccessor):
                __slots__ = ()
                TestView = DynAccessor(61)

            test_view = _test_view()

            class _unbound_example(DynAccessor):
                __slots__ = ()
                UnboundExample = DynAccessor(62)

            unbound_example = _unbound_example()

        views = _views()

    examples = _examples()

    class _list_examples(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _list_examples_empty_render_window_content(DynAccessor):
                __slots__ = ()
                ListExamplesEmptyRenderWindowContent = DynAccessor(63)

            list_examples_empty_render_window_content = _list_examples_empty_render_window_content()

            class _list_examples_window_content(DynAccessor):
                __slots__ = ()
                ListExamplesWindowContent = DynAccessor(64)

            list_examples_window_content = _list_examples_window_content()

        views = _views()

    list_examples = _list_examples()

    class _rotation_pivot_view(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _rotation_pivot_view(DynAccessor):
                __slots__ = ()
                RotationAndPivotTestView = DynAccessor(65)

            rotation_pivot_view = _rotation_pivot_view()

        views = _views()

    rotation_pivot_view = _rotation_pivot_view()

    class _rotation_view(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _rotation_view(DynAccessor):
                __slots__ = ()
                RotationTestView = DynAccessor(66)

            rotation_view = _rotation_view()

        views = _views()

    rotation_view = _rotation_view()

    class _scale_view(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _scale_view(DynAccessor):
                __slots__ = ()
                ScaleTestView = DynAccessor(67)

            scale_view = _scale_view()

        views = _views()

    scale_view = _scale_view()

    class _test_uikit_buttons_view(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _test_uikit_buttons_view(DynAccessor):
                __slots__ = ()
                TestUikitButtonsView = DynAccessor(68)

            test_uikit_buttons_view = _test_uikit_buttons_view()

        views = _views()

    test_uikit_buttons_view = _test_uikit_buttons_view()

    class _test_uikit_view(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _test_uikit_view(DynAccessor):
                __slots__ = ()
                TestUikitView = DynAccessor(69)

            test_uikit_view = _test_uikit_view()

        views = _views()

    test_uikit_view = _test_uikit_view()

    class _wtypes_view(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _wtypes_demo_window_content(DynAccessor):
                __slots__ = ()
                WtypesDemoWindowContent = DynAccessor(70)

            wtypes_demo_window_content = _wtypes_demo_window_content()

        views = _views()

    wtypes_view = _wtypes_view()

    class _dialogs(DynAccessor):
        __slots__ = ()

        class _common(DynAccessor):
            __slots__ = ()
            DialogTemplateGenericTooltip = DynAccessor(88)

        common = _common()
        DefaultDialog = DynAccessor(89)

        class _sub_views(DynAccessor):
            __slots__ = ()

            class _common(DynAccessor):
                __slots__ = ()
                SimpleText = DynAccessor(90)
                SinglePrice = DynAccessor(91)

            common = _common()

            class _content(DynAccessor):
                __slots__ = ()
                SelectOptionContent = DynAccessor(92)
                SimpleTextContent = DynAccessor(93)
                SinglePriceContent = DynAccessor(94)
                TextWithWarning = DynAccessor(95)

            content = _content()

            class _footer(DynAccessor):
                __slots__ = ()
                SimpleTextFooter = DynAccessor(96)
                SinglePriceFooter = DynAccessor(97)

            footer = _footer()

            class _icon(DynAccessor):
                __slots__ = ()
                MultipleIconsSet = DynAccessor(98)

            icon = _icon()

            class _title(DynAccessor):
                __slots__ = ()
                SimpleTextTitle = DynAccessor(99)

            title = _title()

            class _topRight(DynAccessor):
                __slots__ = ()
                MoneyBalance = DynAccessor(100)

            topRight = _topRight()

        sub_views = _sub_views()

        class _widgets(DynAccessor):
            __slots__ = ()
            IconSet = DynAccessor(101)
            MoneyBalance = DynAccessor(102)
            SinglePrice = DynAccessor(103)
            WarningText = DynAccessor(104)

        widgets = _widgets()

    dialogs = _dialogs()

    class _loading(DynAccessor):
        __slots__ = ()
        GameLoadingView = DynAccessor(105)

    loading = _loading()

    class _mono(DynAccessor):
        __slots__ = ()

        class _battle_pass(DynAccessor):
            __slots__ = ()

            class _dialogs(DynAccessor):
                __slots__ = ()
                chapter_confirm = DynAccessor(461)

            dialogs = _dialogs()
            full_screen_video = DynAccessor(462)
            how_to_earn_points = DynAccessor(463)
            main = DynAccessor(464)
            rewards_screen = DynAccessor(465)
            rewards_selection = DynAccessor(466)
            tankmen_screen = DynAccessor(467)

            class _tooltips(DynAccessor):
                __slots__ = ()
                bpcoin = DynAccessor(468)
                bptaler = DynAccessor(469)
                bp_points = DynAccessor(470)
                completed = DynAccessor(471)
                crew_member_skill = DynAccessor(472)
                gold_mission = DynAccessor(473)
                in_progress = DynAccessor(474)
                lock_icon = DynAccessor(475)
                no_chapter = DynAccessor(476)
                on_pause = DynAccessor(477)
                quest_chain = DynAccessor(478)
                random_quest = DynAccessor(479)
                upgrade_style = DynAccessor(480)
                vehicle_bp_points = DynAccessor(481)

            tooltips = _tooltips()
            vehicle_cap_award = DynAccessor(482)

        battle_pass = _battle_pass()

        class _crew(DynAccessor):
            __slots__ = ()
            welcome_screen = DynAccessor(483)

        crew = _crew()

        class _dialogs(DynAccessor):
            __slots__ = ()
            default_dialog = DynAccessor(484)
            pro_boost_switch_dialog = DynAccessor(485)
            research_confirm_dialog = DynAccessor(486)
            wot_plus_activated_dialog = DynAccessor(487)

        dialogs = _dialogs()

        class _hangar(DynAccessor):
            __slots__ = ()
            footer = DynAccessor(488)
            header = DynAccessor(489)
            main = DynAccessor(490)

            class _overlays(DynAccessor):
                __slots__ = ()
                playlist = DynAccessor(491)

            overlays = _overlays()
            tooltips = DynAccessor(492)
            vehicle_tooltip = DynAccessor(493)

        hangar = _hangar()

        class _integrated_auction(DynAccessor):
            __slots__ = ()

            class _tooltips(DynAccessor):
                __slots__ = ()
                auction_event_banner_tooltip = DynAccessor(494)

            tooltips = _tooltips()

        integrated_auction = _integrated_auction()

        class _lobby(DynAccessor):
            __slots__ = ()
            collector20_reward = DynAccessor(495)
            elite_window = DynAccessor(496)
            select_vehicle = DynAccessor(497)

            class _veh_skill_tree(DynAccessor):
                __slots__ = ()
                comparison = DynAccessor(498)

                class _dialogs(DynAccessor):
                    __slots__ = ()
                    alternate_configuration = DynAccessor(499)

                dialogs = _dialogs()
                intro_page = DynAccessor(500)

                class _notifications(DynAccessor):
                    __slots__ = ()
                    perk_available = DynAccessor(501)

                notifications = _notifications()
                rarity_reward_screen = DynAccessor(502)
                reward_screen = DynAccessor(503)

            veh_skill_tree = _veh_skill_tree()

        lobby = _lobby()

        class _lootbox(DynAccessor):
            __slots__ = ()
            auto_open = DynAccessor(504)
            info_page = DynAccessor(505)
            main = DynAccessor(506)

            class _tooltips(DynAccessor):
                __slots__ = ()
                box_compensation = DynAccessor(507)
                box_tooltip = DynAccessor(508)
                entry_point = DynAccessor(509)
                guaranteed_reward_info = DynAccessor(510)
                random_national_bonus = DynAccessor(511)
                statistics_category = DynAccessor(512)

            tooltips = _tooltips()

        lootbox = _lootbox()

        class _maps_training(DynAccessor):
            __slots__ = ()
            maps_training_page = DynAccessor(513)
            maps_training_queue = DynAccessor(514)
            maps_training_result = DynAccessor(515)
            scenario_tooltip = DynAccessor(516)

        maps_training = _maps_training()

        class _personal_missions_30(DynAccessor):
            __slots__ = ()
            assembling_video = DynAccessor(517)
            campaign_selector = DynAccessor(518)
            intro_screen = DynAccessor(519)
            main = DynAccessor(520)
            rewards = DynAccessor(521)

            class _tooltips(DynAccessor):
                __slots__ = ()
                missions_category_tooltip = DynAccessor(522)
                mission_progress_tooltip = DynAccessor(523)
                param_tooltip = DynAccessor(524)

            tooltips = _tooltips()

        personal_missions_30 = _personal_missions_30()

        class _pet_system(DynAccessor):
            __slots__ = ()
            event_view = DynAccessor(525)
            fullscreen_event_view = DynAccessor(526)
            info_page = DynAccessor(527)
            pet_house_marker = DynAccessor(528)
            pet_storage = DynAccessor(529)

            class _tooltips(DynAccessor):
                __slots__ = ()
                pet_storage_tooltip = DynAccessor(530)
                pet_tooltip = DynAccessor(531)
                synergy_tooltip = DynAccessor(532)

            tooltips = _tooltips()

        pet_system = _pet_system()

        class _post_battle(DynAccessor):
            __slots__ = ()
            flag = DynAccessor(533)
            random = DynAccessor(534)

            class _tooltips(DynAccessor):
                __slots__ = ()
                critical_damage = DynAccessor(535)

            tooltips = _tooltips()

        post_battle = _post_battle()

        class _seniority_awards(DynAccessor):
            __slots__ = ()

            class _notifications(DynAccessor):
                __slots__ = ()
                manual_claim = DynAccessor(536)
                tokens = DynAccessor(537)
                vehicles = DynAccessor(538)

            notifications = _notifications()
            rewards = DynAccessor(539)

            class _tooltips(DynAccessor):
                __slots__ = ()
                seniority_tooltip = DynAccessor(540)

            tooltips = _tooltips()
            vehicle_rewards = DynAccessor(541)

        seniority_awards = _seniority_awards()

        class _stronghold_event(DynAccessor):
            __slots__ = ()

            class _tooltips(DynAccessor):
                __slots__ = ()
                event_banner_tooltip = DynAccessor(542)

            tooltips = _tooltips()

        stronghold_event = _stronghold_event()

        class _tech_tree(DynAccessor):
            __slots__ = ()
            main = DynAccessor(543)

        tech_tree = _tech_tree()

        class _template(DynAccessor):
            __slots__ = ()
            main = DynAccessor(544)

        template = _template()

        class _tooltips(DynAccessor):
            __slots__ = ()
            tooltips = DynAccessor(545)

        tooltips = _tooltips()

        class _user_missions(DynAccessor):
            __slots__ = ()

            class _hub(DynAccessor):
                __slots__ = ()
                mission_hub_intro_view = DynAccessor(547)

            hub = _hub(546)
            info_page = DynAccessor(548)

            class _tooltips(DynAccessor):
                __slots__ = ()
                all_quests_done_tooltip = DynAccessor(549)
                daily_quest_tooltip = DynAccessor(550)
                daily_reroll_tooltip = DynAccessor(551)
                param_tooltip = DynAccessor(552)
                pm3_banner_tooltip = DynAccessor(553)
                weekly_quest_tooltip = DynAccessor(554)

            tooltips = _tooltips()

        user_missions = _user_missions()

        class _vehicle_hub(DynAccessor):
            __slots__ = ()
            main = DynAccessor(555)

            class _tooltips(DynAccessor):
                __slots__ = ()
                armor_tooltip = DynAccessor(556)
                back_to_main_progression_tooltip = DynAccessor(557)
                minor_short_tooltip = DynAccessor(558)
                minor_tooltip = DynAccessor(559)
                perk_tooltip = DynAccessor(560)
                prestige_reward_tooltip = DynAccessor(561)
                vanity_entry_point_tooltip = DynAccessor(562)

            tooltips = _tooltips()

        vehicle_hub = _vehicle_hub()

        class _demos(DynAccessor):
            __slots__ = ()
            data_layer = DynAccessor(767)

            class _entry(DynAccessor):
                __slots__ = ()

                class _pages(DynAccessor):
                    __slots__ = ()

                    class _tech_ui(DynAccessor):
                        __slots__ = ()

                        class _pages(DynAccessor):
                            __slots__ = ()

                            class _param_tooltip(DynAccessor):
                                __slots__ = ()
                                tooltips = DynAccessor(769)

                            param_tooltip = _param_tooltip()

                        pages = _pages()

                    tech_ui = _tech_ui()

                pages = _pages()

            entry = _entry(768)

            class _notifications(DynAccessor):
                __slots__ = ()
                test_notification = DynAccessor(770)

            notifications = _notifications()

        demos = _demos()

    mono = _mono()

    class _battle_modifiers(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()

            class _tooltips(DynAccessor):
                __slots__ = ()
                ModifiersDomainTooltipView = DynAccessor(563)

            tooltips = _tooltips()

        lobby = _lobby()

    battle_modifiers = _battle_modifiers()

    class _battle_royale(DynAccessor):
        __slots__ = ()

        class _battle(DynAccessor):
            __slots__ = ()

            class _views(DynAccessor):
                __slots__ = ()
                LeaveBattleView = DynAccessor(564)

            views = _views()

        battle = _battle()

        class _lobby(DynAccessor):
            __slots__ = ()
            BattleRoyaleBattleCard = DynAccessor(565)

            class _views(DynAccessor):
                __slots__ = ()
                PreBattleView = DynAccessor(566)

            views = _views()

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _lobby(DynAccessor):
                __slots__ = ()
                battle_quest_awards_view = DynAccessor(567)
                battle_results = DynAccessor(568)
                hangar = DynAccessor(569)
                info_page = DynAccessor(570)
                progression_main_view = DynAccessor(571)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    ability = DynAccessor(572)
                    all_quests_done_tooltip = DynAccessor(573)
                    banner = DynAccessor(574)
                    battle_selector = DynAccessor(575)
                    ceasefire = DynAccessor(576)
                    commander = DynAccessor(577)
                    leaderboard_reward_tooltip_view = DynAccessor(578)
                    progression_quest = DynAccessor(579)
                    progression_widget = DynAccessor(580)
                    proxy_currency_tooltip = DynAccessor(581)
                    respawn = DynAccessor(582)
                    reward_currency_tooltip = DynAccessor(583)
                    shop_button = DynAccessor(584)
                    upgrades_button = DynAccessor(585)
                    vehicle = DynAccessor(586)

                tooltips = _tooltips()

            lobby = _lobby()

        mono = _mono()

    battle_royale = _battle_royale()

    class _comp7(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()
            Comp7BattleCard = DynAccessor(587)
            MembersWindow = DynAccessor(588)
            PlatoonDropdown = DynAccessor(589)
            RewardsSelectionScreen = DynAccessor(590)

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _battle(DynAccessor):
                __slots__ = ()
                ban_progression = DynAccessor(591)
                ban_view = DynAccessor(592)
                ban_widget = DynAccessor(593)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    ban_show_tooltip = DynAccessor(594)

                tooltips = _tooltips()

            battle = _battle()

            class _lobby(DynAccessor):
                __slots__ = ()

                class _dialogs(DynAccessor):
                    __slots__ = ()
                    purchase_dialog = DynAccessor(595)

                dialogs = _dialogs()
                flag = DynAccessor(596)
                hangar = DynAccessor(597)
                intro_screen = DynAccessor(598)
                meta_root_view = DynAccessor(599)
                no_vehicles_screen = DynAccessor(600)
                post_battle_results_view = DynAccessor(601)
                rewards_screen = DynAccessor(602)
                season_statistics = DynAccessor(603)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    battles_indicator_tooltip = DynAccessor(604)
                    crew_members_tooltip = DynAccessor(605)
                    damage_indicator_tooltip = DynAccessor(606)
                    day_tooltip = DynAccessor(607)
                    division_tooltip = DynAccessor(608)
                    entry_point_tooltip = DynAccessor(609)
                    fifth_rank_tooltip = DynAccessor(610)
                    general_rank_tooltip = DynAccessor(611)
                    last_update_tooltip = DynAccessor(612)
                    prestige_indicator_tooltip = DynAccessor(613)
                    prestige_points_info_tooltip = DynAccessor(614)
                    progression_table_tooltip = DynAccessor(615)
                    progression_tooltip = DynAccessor(616)
                    rank_compatibility_tooltip = DynAccessor(617)
                    rank_inactivity_tooltip = DynAccessor(618)
                    rank_indicator_tooltip = DynAccessor(619)
                    season_point_tooltip = DynAccessor(620)
                    sixth_rank_tooltip = DynAccessor(621)
                    style3d_tooltip = DynAccessor(622)
                    tournament_entry_point_tooltip = DynAccessor(623)
                    weekly_quest_widget_tooltip = DynAccessor(624)
                    wins_indicator_tooltip = DynAccessor(625)

                tooltips = _tooltips()

                class _tournaments(DynAccessor):
                    __slots__ = ()
                    ols_view = DynAccessor(626)
                    wci_view = DynAccessor(627)

                tournaments = _tournaments()
                whats_new_view = DynAccessor(628)

            lobby = _lobby()

        mono = _mono()

    comp7 = _comp7()

    class _comp7_light(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()
            Comp7LightBattleCard = DynAccessor(629)
            MembersWindow = DynAccessor(630)
            PlatoonDropdown = DynAccessor(631)

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _lobby(DynAccessor):
                __slots__ = ()
                battle_quest_awards_view = DynAccessor(632)
                entry_point_tooltip = DynAccessor(633)
                hangar = DynAccessor(634)
                intro_screen = DynAccessor(635)
                leaderboard_reward_tooltip_view = DynAccessor(636)
                no_vehicles_screen = DynAccessor(637)
                progression_main_view = DynAccessor(638)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    all_quests_done_tooltip = DynAccessor(639)
                    battle_quest_tooltip = DynAccessor(640)

                tooltips = _tooltips()

            lobby = _lobby()

        mono = _mono()

    comp7_light = _comp7_light()

    class _frontline(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()
            RewardsSelectionView = DynAccessor(641)
            WelcomeView = DynAccessor(642)

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _lobby(DynAccessor):
                __slots__ = ()

                class _dialogs(DynAccessor):
                    __slots__ = ()
                    battle_abilities_confirm_dialog = DynAccessor(643)

                dialogs = _dialogs()
                hangar = DynAccessor(644)
                info_view = DynAccessor(645)
                post_battle_results_view = DynAccessor(646)
                post_battle_rewards_view = DynAccessor(647)
                progression_screen = DynAccessor(648)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    banner_tooltip = DynAccessor(649)
                    battle_ability_alt_tooltip = DynAccessor(650)
                    battle_ability_tooltip = DynAccessor(651)
                    level_reserves_tooltip = DynAccessor(652)
                    skill_order_tooltip = DynAccessor(653)

                tooltips = _tooltips()

            lobby = _lobby()

        mono = _mono()

    frontline = _frontline()

    class _fun_random(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()

            class _feature(DynAccessor):
                __slots__ = ()
                FunRandomModeSubSelector = DynAccessor(654)

            feature = _feature()

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _lobby(DynAccessor):
                __slots__ = ()
                battle_results = DynAccessor(655)
                hangar = DynAccessor(656)
                progression = DynAccessor(657)
                rewards = DynAccessor(658)
                tier_list = DynAccessor(659)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    battle_results_economic_tooltip = DynAccessor(660)
                    entry_point_tooltip = DynAccessor(661)
                    loot_box_tooltip = DynAccessor(662)
                    progression_tooltip = DynAccessor(663)

                tooltips = _tooltips()

            lobby = _lobby()

        mono = _mono()

    fun_random = _fun_random()

    class _last_stand(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()
            MembersWindow = DynAccessor(664)

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _battle(DynAccessor):
                __slots__ = ()
                battle_loading = DynAccessor(665)
                help_view = DynAccessor(666)
                tab_screen = DynAccessor(667)

            battle = _battle()

            class _lobby(DynAccessor):
                __slots__ = ()
                attachments_reward_view = DynAccessor(668)
                battle_result_view = DynAccessor(669)

                class _dialogs(DynAccessor):
                    __slots__ = ()
                    abilities_incomplete_confirm = DynAccessor(670)

                dialogs = _dialogs()
                difficulty_congratulation_view = DynAccessor(671)
                hangar = DynAccessor(672)
                meta_intro = DynAccessor(673)
                narration_view = DynAccessor(674)
                prebattle_queue_view = DynAccessor(675)
                promo_view = DynAccessor(676)
                reward_path_view = DynAccessor(677)
                stage_reward_view = DynAccessor(678)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    additional_data_tooltip = DynAccessor(679)
                    banner_tooltip = DynAccessor(680)
                    battle_pass_tooltip = DynAccessor(681)
                    booster_tooltip = DynAccessor(682)
                    daily_quests_tooltip = DynAccessor(683)
                    difficulty_tooltip = DynAccessor(684)
                    points_tooltip = DynAccessor(685)
                    reward_path_tooltip = DynAccessor(686)
                    simple_format_tooltip = DynAccessor(687)
                    vehicle_tooltip = DynAccessor(688)

                tooltips = _tooltips()

            lobby = _lobby()

        mono = _mono()

    last_stand = _last_stand()

    class _open_bundle(DynAccessor):
        __slots__ = ()

        class _mono(DynAccessor):
            __slots__ = ()

            class _lobby(DynAccessor):
                __slots__ = ()
                attachments_preview = DynAccessor(689)
                confirmation = DynAccessor(690)
                intro = DynAccessor(691)
                main = DynAccessor(692)

                class _notifications(DynAccessor):
                    __slots__ = ()
                    special_rewards_notification = DynAccessor(693)
                    start_notification = DynAccessor(694)

                notifications = _notifications()

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    event_banner = DynAccessor(695)
                    fixed_rewards = DynAccessor(696)

                tooltips = _tooltips()

            lobby = _lobby()

        mono = _mono()

    open_bundle = _open_bundle()

    class _resource_well(DynAccessor):
        __slots__ = ()

        class _mono(DynAccessor):
            __slots__ = ()

            class _lobby(DynAccessor):
                __slots__ = ()
                award_view = DynAccessor(697)
                completed_progression_view = DynAccessor(698)
                no_serial_vehicles_confirm = DynAccessor(699)
                no_vehicles_confirm = DynAccessor(700)
                progression_view = DynAccessor(701)
                resources_loading_confirm = DynAccessor(702)
                resources_loading_view = DynAccessor(703)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    event_banner_tooltip = DynAccessor(704)
                    max_progress_tooltip = DynAccessor(705)
                    progress_tooltip = DynAccessor(706)
                    serial_number_tooltip = DynAccessor(707)
                    simple_tooltip = DynAccessor(708)

                tooltips = _tooltips()
                vehicle_preview_bottom_panel = DynAccessor(709)

            lobby = _lobby()

        mono = _mono()

    resource_well = _resource_well()

    class _server_side_replay(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()
            MetaReplaysView = DynAccessor(710)

            class _popovers(DynAccessor):
                __slots__ = ()
                ReplaysFilterPopover = DynAccessor(711)

            popovers = _popovers()

        lobby = _lobby()

    server_side_replay = _server_side_replay()

    class _story_mode(DynAccessor):
        __slots__ = ()

        class _mono(DynAccessor):
            __slots__ = ()

            class _battle(DynAccessor):
                __slots__ = ()
                epilogue_window = DynAccessor(712)
                onboarding_battle_result_view = DynAccessor(713)
                prebattle_window = DynAccessor(714)

            battle = _battle()

            class _lobby(DynAccessor):
                __slots__ = ()
                battle_result_view = DynAccessor(715)
                congratulations_window = DynAccessor(716)
                event_welcome_view = DynAccessor(717)
                mission_selection_view = DynAccessor(718)
                newbie_advertising_view = DynAccessor(719)
                onboarding_queue_view = DynAccessor(720)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    badge_tooltip = DynAccessor(721)
                    battle_result_stat_tooltip = DynAccessor(722)
                    difficulty_tooltip = DynAccessor(723)
                    event_banner_tooltip = DynAccessor(724)
                    medal_tooltip = DynAccessor(725)
                    mission_tooltip = DynAccessor(726)
                    newbie_banner_tooltip = DynAccessor(727)

                tooltips = _tooltips()

            lobby = _lobby()

        mono = _mono()

    story_mode = _story_mode()
    Anchor = DynAccessor(728)

    class _child_views_demo(DynAccessor):
        __slots__ = ()
        ChildDemoView = DynAccessor(729)
        MainView = DynAccessor(730)

    child_views_demo = _child_views_demo()
    Comp7DemoPageView = DynAccessor(731)
    ComponentsDemo = DynAccessor(732)
    DataLayerDemoView = DynAccessor(733)
    DataTrackerDemo = DynAccessor(734)
    DeathCamDemoView = DynAccessor(735)
    DemoContextMenu = DynAccessor(736)
    Easings = DynAccessor(737)
    GameLoadingDebugView = DynAccessor(738)
    GFCharset = DynAccessor(739)
    GFComponents = DynAccessor(740)
    GFDemoPopover = DynAccessor(741)
    GFDemoRichTooltipWindow = DynAccessor(742)
    GFDemoWindow = DynAccessor(743)
    GFHooksDemo = DynAccessor(744)
    GFInjectView = DynAccessor(745)
    GFInputCases = DynAccessor(746)
    GFSimpleTooltipWindow = DynAccessor(747)
    GFWebSubDemoWindow = DynAccessor(748)

    class _gf_dialogs_demo(DynAccessor):
        __slots__ = ()
        DefaultDialogProxy = DynAccessor(749)
        GFDialogsDemo = DynAccessor(750)

        class _sub_views(DynAccessor):
            __slots__ = ()
            DummyContent = DynAccessor(751)
            DummyFooter = DynAccessor(752)
            DummyIcon = DynAccessor(753)
            DummyStepper = DynAccessor(754)
            DummyTitle = DynAccessor(755)
            DummyTopRight = DynAccessor(756)

        sub_views = _sub_views()

    gf_dialogs_demo = _gf_dialogs_demo()

    class _gf_viewer(DynAccessor):
        __slots__ = ()
        GFViewerWindow = DynAccessor(757)

    gf_viewer = _gf_viewer()

    class _igb_demo(DynAccessor):
        __slots__ = ()
        BrowserFullscreenWindow = DynAccessor(758)
        BrowserWindow = DynAccessor(759)
        MainView = DynAccessor(760)

    igb_demo = _igb_demo()
    LocaleDemo = DynAccessor(761)
    MediaWrapperDemo = DynAccessor(762)
    MixBlendMode = DynAccessor(763)
    MixBlendModeAnimation = DynAccessor(764)
    ModeSelectorDemo = DynAccessor(765)
    ModeSelectorToolsetView = DynAccessor(766)
    ParallaxExample = DynAccessor(771)
    ParallaxViewer = DynAccessor(772)
    PluralLocView = DynAccessor(773)
    PropsSupportDemo = DynAccessor(774)
    ReactSpringVizualizer = DynAccessor(775)
    SelectableRewardDemoView = DynAccessor(776)
    StructuralDataBindDemo = DynAccessor(777)

    class _sub_views_demo(DynAccessor):
        __slots__ = ()
        GFSubViewsDemo = DynAccessor(778)

        class _sub_views(DynAccessor):
            __slots__ = ()
            CustomizationCartProxy = DynAccessor(779)
            ProgressiveItemsViewProxy = DynAccessor(780)

        sub_views = _sub_views()

    sub_views_demo = _sub_views_demo()
    UILoggerDemo = DynAccessor(781)
    VideoSupportView = DynAccessor(782)
    W2CTestPageWindow = DynAccessor(783)
    WgcgMockView = DynAccessor(784)

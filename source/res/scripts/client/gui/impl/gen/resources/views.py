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
            Confirm = DynAccessor(140)

            class _tooltips(DynAccessor):
                __slots__ = ()
                BlueprintsAlliancesTooltipView = DynAccessor(141)

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
            AwardsView = DynAccessor(150)
            BrowserView = DynAccessor(151)
            RewardSelection = DynAccessor(152)
            SelectableRewardBase = DynAccessor(153)
            SelectSlotSpecDialog = DynAccessor(154)

            class _tooltips(DynAccessor):
                __slots__ = ()
                ExtendedTextTooltip = DynAccessor(155)
                SelectedRewardsTooltipView = DynAccessor(156)
                SimpleIconTooltip = DynAccessor(157)

            tooltips = _tooltips()

        common = _common()

        class _marathon(DynAccessor):
            __slots__ = ()

            class _marathon_reward_view(DynAccessor):
                __slots__ = ()
                MarathonRewardView = DynAccessor(38)

            marathon_reward_view = _marathon_reward_view()
            RewardWindow = DynAccessor(258)

            class _tooltips(DynAccessor):
                __slots__ = ()
                RestRewardTooltip = DynAccessor(259)

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
            QualificationRewardsView = DynAccessor(307)
            RankedSelectableRewardView = DynAccessor(308)

            class _tooltips(DynAccessor):
                __slots__ = ()
                RankedBattlesRolesTooltipView = DynAccessor(309)

            tooltips = _tooltips()
            YearLeaderboardView = DynAccessor(310)

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
            AdditionalBattlePassRewardsTooltip = DynAccessor(357)
            AdditionalRewardsTooltip = DynAccessor(358)
            BattleResultsStatsTooltipView = DynAccessor(359)
            TankmanTooltipView = DynAccessor(360)
            VehPostProgressionEntryPointTooltip = DynAccessor(361)

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
            ClanSupply = DynAccessor(142)
            RewardsView = DynAccessor(143)

        clan_supply = _clan_supply()

        class _collection(DynAccessor):
            __slots__ = ()
            AwardsView = DynAccessor(144)
            CollectionItemPreview = DynAccessor(145)
            CollectionsMainView = DynAccessor(146)
            CollectionView = DynAccessor(147)
            IntroView = DynAccessor(148)

            class _tooltips(DynAccessor):
                __slots__ = ()
                CollectionItemTooltipView = DynAccessor(149)

            tooltips = _tooltips()

        collection = _collection()

        class _crew(DynAccessor):
            __slots__ = ()
            BarracksView = DynAccessor(158)
            ConversionConfirmView = DynAccessor(159)
            CrewHeaderTooltipView = DynAccessor(160)
            CrewPostProgressionView = DynAccessor(161)

            class _dialogs(DynAccessor):
                __slots__ = ()
                CrewBooksPurchaseDialog = DynAccessor(162)
                DismissTankmanDialog = DynAccessor(163)
                DocumentChangeDialog = DynAccessor(164)
                EnlargeBarracksDialog = DynAccessor(165)
                FillAllPerksDialog = DynAccessor(166)
                MentorAssignmentDialog = DynAccessor(167)
                PerksResetDialog = DynAccessor(168)
                RecruitConfirmIrrelevantDialog = DynAccessor(169)
                RecruitDialog = DynAccessor(170)
                RecruitNewTankmanDialog = DynAccessor(171)
                RestoreTankmanDialog = DynAccessor(172)
                RetrainMassiveDialog = DynAccessor(173)
                RetrainPremiumVehicleDialog = DynAccessor(174)
                RetrainSingleDialog = DynAccessor(175)
                SkillsTrainingConfirmDialog = DynAccessor(176)
                SkinApplyDialog = DynAccessor(177)

            dialogs = _dialogs()
            HangarCrewWidget = DynAccessor(178)
            HelpView = DynAccessor(179)
            JunkTankmenView = DynAccessor(180)
            MemberChangeView = DynAccessor(181)
            MentorAssigmentView = DynAccessor(182)

            class _personal_case(DynAccessor):
                __slots__ = ()
                PersonalDataView = DynAccessor(183)
                PersonalFileView = DynAccessor(184)
                ServiceRecordView = DynAccessor(185)

            personal_case = _personal_case()

            class _popovers(DynAccessor):
                __slots__ = ()
                FilterPopoverView = DynAccessor(186)

            popovers = _popovers()
            QuickTrainingView = DynAccessor(187)
            SkillsTrainingView = DynAccessor(188)
            TankChangeView = DynAccessor(189)
            TankmanContainerView = DynAccessor(190)

            class _tooltips(DynAccessor):
                __slots__ = ()
                AdvancedTooltipView = DynAccessor(191)
                BonusPerksTooltip = DynAccessor(192)
                BunksConfirmDiscountTooltip = DynAccessor(193)
                ConversionTooltip = DynAccessor(194)
                CrewBookMouseTooltip = DynAccessor(195)
                CrewPerksAdditionalTooltip = DynAccessor(196)
                CrewPerksTooltip = DynAccessor(197)
                DirectiveConversionTooltip = DynAccessor(198)
                DismissedToggleTooltip = DynAccessor(199)
                EmptySkillTooltip = DynAccessor(200)
                ExperienceStepperTooltip = DynAccessor(201)
                MentorAssignmentTooltip = DynAccessor(202)
                MentoringLicenseTooltip = DynAccessor(203)
                PostProgressionTooltip = DynAccessor(204)
                PremiumVehicleTooltip = DynAccessor(205)
                QualificationTooltip = DynAccessor(206)
                QuickTrainingDiscountTooltip = DynAccessor(207)
                QuickTrainingLostXpTooltip = DynAccessor(208)
                RetireUndertrainedTooltip = DynAccessor(209)
                SkillsEfficiencyTooltip = DynAccessor(210)
                SkillUntrainedAdditionalTooltip = DynAccessor(211)
                SkillUntrainedTooltip = DynAccessor(212)
                SortingDropdownTooltip = DynAccessor(213)
                SpecializationWotPlusTooltip = DynAccessor(214)
                TankmanTooltip = DynAccessor(215)
                VehCmpSkillsTooltip = DynAccessor(216)
                VehicleParamsTooltipView = DynAccessor(217)

            tooltips = _tooltips()

            class _widgets(DynAccessor):
                __slots__ = ()
                CrewBannerWidget = DynAccessor(218)
                CrewWidget = DynAccessor(219)
                FilterPanelWidget = DynAccessor(220)
                PriceList = DynAccessor(221)
                TankmanInfo = DynAccessor(222)

            widgets = _widgets()

        crew = _crew()

        class _crystalsPromo(DynAccessor):
            __slots__ = ()
            CrystalsPromoView = DynAccessor(223)

        crystalsPromo = _crystalsPromo()

        class _currency_reserves(DynAccessor):
            __slots__ = ()
            CurrencyReserves = DynAccessor(224)
            ReservesAwardView = DynAccessor(225)

        currency_reserves = _currency_reserves()

        class _customization(DynAccessor):
            __slots__ = ()
            CustomizationCart = DynAccessor(226)
            CustomizationRarityRewardScreen = DynAccessor(227)

            class _progression_styles(DynAccessor):
                __slots__ = ()
                OnboardingView = DynAccessor(228)
                StageSwitcher = DynAccessor(229)

            progression_styles = _progression_styles()

            class _progressive_items_reward(DynAccessor):
                __slots__ = ()
                ProgressiveItemsUpgradeView = DynAccessor(230)

            progressive_items_reward = _progressive_items_reward()

            class _progressive_items_view(DynAccessor):
                __slots__ = ()
                ProgressiveItemsView = DynAccessor(231)

            progressive_items_view = _progressive_items_view()

            class _style_unlocked_view(DynAccessor):
                __slots__ = ()
                StyleUnlockedView = DynAccessor(232)

            style_unlocked_view = _style_unlocked_view()

            class _vehicles_sidebar(DynAccessor):
                __slots__ = ()
                VehiclesSidebar = DynAccessor(233)

            vehicles_sidebar = _vehicles_sidebar()

        customization = _customization()

        class _dedication(DynAccessor):
            __slots__ = ()
            DedicationRewardView = DynAccessor(234)

        dedication = _dedication()

        class _dog_tags(DynAccessor):
            __slots__ = ()
            AnimatedDogTagGradeTooltip = DynAccessor(235)
            AnimatedDogTagsView = DynAccessor(236)
            CatalogAnimatedDogTagTooltip = DynAccessor(237)
            CustomizationConfirmDialog = DynAccessor(238)
            DedicationTooltip = DynAccessor(239)
            DogTagsView = DynAccessor(240)
            RankedEfficiencyTooltip = DynAccessor(241)
            ThreeMonthsTooltip = DynAccessor(242)
            TriumphTooltip = DynAccessor(243)

        dog_tags = _dog_tags()

        class _excluded_maps(DynAccessor):
            __slots__ = ()
            ExcludedMapsTooltip = DynAccessor(244)
            ExcludedMapsView = DynAccessor(245)

        excluded_maps = _excluded_maps()

        class _hangar(DynAccessor):
            __slots__ = ()
            BuyVehicleView = DynAccessor(246)

            class _notifications(DynAccessor):
                __slots__ = ()
                PunishmentView = DynAccessor(247)

            notifications = _notifications()

            class _subViews(DynAccessor):
                __slots__ = ()
                VehicleParams = DynAccessor(248)

            subViews = _subViews()
            VehicleParamsWidget = DynAccessor(249)

        hangar = _hangar()

        class _instructions(DynAccessor):
            __slots__ = ()
            BuyWindow = DynAccessor(250)
            SellWindow = DynAccessor(251)

        instructions = _instructions()

        class _live_ops_web_events(DynAccessor):
            __slots__ = ()
            EntryPoint = DynAccessor(252)
            EntryPointTooltip = DynAccessor(253)

        live_ops_web_events = _live_ops_web_events()

        class _mapbox(DynAccessor):
            __slots__ = ()
            MapBoxAwardsView = DynAccessor(254)
            MapBoxIntro = DynAccessor(255)
            MapBoxProgression = DynAccessor(256)
            MapBoxSurveyView = DynAccessor(257)

        mapbox = _mapbox()

        class _matchmaker(DynAccessor):
            __slots__ = ()
            ActiveTestConfirmView = DynAccessor(260)

        matchmaker = _matchmaker()

        class _mode_selector(DynAccessor):
            __slots__ = ()
            BattleSessionView = DynAccessor(261)
            ModeSelectorView = DynAccessor(262)

            class _tooltips(DynAccessor):
                __slots__ = ()
                AlertTooltip = DynAccessor(263)

                class _common(DynAccessor):
                    __slots__ = ()
                    Divider = DynAccessor(264)
                    GradientDecorator = DynAccessor(265)

                common = _common()
                SimplyFormatTooltip = DynAccessor(266)

            tooltips = _tooltips()

            class _widgets(DynAccessor):
                __slots__ = ()
                EpicWidget = DynAccessor(267)
                RankedWidget = DynAccessor(268)

            widgets = _widgets()

        mode_selector = _mode_selector()

        class _offers(DynAccessor):
            __slots__ = ()
            OfferBannerWindow = DynAccessor(269)
            OfferGiftsWindow = DynAccessor(270)
            OfferRewardWindow = DynAccessor(271)

        offers = _offers()

        class _personal_exchange_rates(DynAccessor):
            __slots__ = ()
            AllPersonalExchangesView = DynAccessor(272)
            ExperienceExchangeView = DynAccessor(273)
            GoldExchangeView = DynAccessor(274)

            class _tooltips(DynAccessor):
                __slots__ = ()
                ExchangeLimitTooltip = DynAccessor(275)
                ExchangeRateTooltip = DynAccessor(276)

            tooltips = _tooltips()

        personal_exchange_rates = _personal_exchange_rates()

        class _personal_reserves(DynAccessor):
            __slots__ = ()
            BoosterTooltip = DynAccessor(277)
            PersonalReservesTooltip = DynAccessor(278)
            PersonalReservesWidget = DynAccessor(279)
            QuestBoosterTooltip = DynAccessor(280)
            ReserveCard = DynAccessor(281)
            ReserveCardTooltip = DynAccessor(282)
            ReserveGroup = DynAccessor(283)
            ReservesActivationView = DynAccessor(284)
            ReservesIntroView = DynAccessor(285)

        personal_reserves = _personal_reserves()

        class _platoon(DynAccessor):
            __slots__ = ()
            AlertTooltip = DynAccessor(286)
            MembersWindow = DynAccessor(287)
            PlatoonDropdown = DynAccessor(288)
            SearchingDropdown = DynAccessor(289)
            SettingsPopover = DynAccessor(290)

            class _subViews(DynAccessor):
                __slots__ = ()
                Chat = DynAccessor(291)
                SettingsContent = DynAccessor(292)
                TiersLimit = DynAccessor(293)

            subViews = _subViews()
            WTRTooltip = DynAccessor(294)

        platoon = _platoon()

        class _player_subscriptions(DynAccessor):
            __slots__ = ()
            PlayerSubscriptions = DynAccessor(295)
            SubscriptionItem = DynAccessor(296)
            SubscriptionRewardView = DynAccessor(297)

        player_subscriptions = _player_subscriptions()

        class _premacc(DynAccessor):
            __slots__ = ()

            class _tooltips(DynAccessor):
                __slots__ = ()
                SquadBonusTooltip = DynAccessor(298)

            tooltips = _tooltips()

        premacc = _premacc()

        class _prestige(DynAccessor):
            __slots__ = ()

            class _sharedComponents(DynAccessor):
                __slots__ = ()
                PrestigeProgressSymbol = DynAccessor(299)
                PrestigeProgressTab = DynAccessor(300)

            sharedComponents = _sharedComponents()

            class _tooltips(DynAccessor):
                __slots__ = ()
                EliteLevelGradesTooltip = DynAccessor(301)

            tooltips = _tooltips()

            class _views(DynAccessor):
                __slots__ = ()
                GlobalOnboardingView = DynAccessor(302)
                PrestigeHangarEntryPoint = DynAccessor(303)
                PrestigeProfileTechniqueEmblemView = DynAccessor(304)
                PrestigeProfileTechniqueView = DynAccessor(305)
                PrestigeRewardView = DynAccessor(306)

            views = _views()

        prestige = _prestige()

        class _research(DynAccessor):
            __slots__ = ()
            BuyModuleDialogView = DynAccessor(311)
            InsufficientCreditsTooltip = DynAccessor(312)
            SoldModuleInfoTooltip = DynAccessor(313)

        research = _research()

        class _tanksetup(DynAccessor):
            __slots__ = ()
            AmmunitionPanel = DynAccessor(314)

            class _common(DynAccessor):
                __slots__ = ()
                Action = DynAccessor(315)
                CtaButtons = DynAccessor(316)
                DealPanel = DynAccessor(317)
                DemountKit = DynAccessor(318)
                ExtraImage = DynAccessor(319)
                FormatColorTagText = DynAccessor(320)
                Location = DynAccessor(321)
                MaybeWrapper = DynAccessor(322)
                Price = DynAccessor(323)
                SetupApp = DynAccessor(324)
                ShortenedText = DynAccessor(325)
                Slider = DynAccessor(326)

                class _SlotParts(DynAccessor):
                    __slots__ = ()
                    Bonus = DynAccessor(327)
                    Container = DynAccessor(328)
                    Count = DynAccessor(329)
                    Inside = DynAccessor(330)
                    Level = DynAccessor(331)

                SlotParts = _SlotParts()
                Specializations = DynAccessor(332)
                SwitchButton = DynAccessor(333)
                SwitchEquipment = DynAccessor(334)

                class _Transitions(DynAccessor):
                    __slots__ = ()
                    SlotTransitions = DynAccessor(335)

                Transitions = _Transitions()
                WeaponOccupancy = DynAccessor(336)

            common = _common()
            DeconstructionDeviceView = DynAccessor(337)

            class _dialogs(DynAccessor):
                __slots__ = ()
                Confirm = DynAccessor(338)
                ConfirmActionsWithEquipmentDialog = DynAccessor(339)
                DeconstructConfirm = DynAccessor(340)
                DeviceUpgradeDialog = DynAccessor(341)
                ExchangeToApplyEasyTankEquip = DynAccessor(342)
                ExchangeToBuyItems = DynAccessor(343)
                ExchangeToUpgradeItems = DynAccessor(344)
                NeedRepair = DynAccessor(345)
                RefillShells = DynAccessor(346)
                Sell = DynAccessor(347)

            dialogs = _dialogs()
            HangarAmmunitionSetup = DynAccessor(348)
            IntroScreen = DynAccessor(349)

            class _tooltips(DynAccessor):
                __slots__ = ()
                DeconstructFromInventoryTooltip = DynAccessor(350)
                DeconstructFromVehicleTooltip = DynAccessor(351)
                PopularLoadoutsTooltip = DynAccessor(352)
                SetupTabTooltipView = DynAccessor(353)
                WarningTooltipView = DynAccessor(354)

            tooltips = _tooltips()
            VehicleCompareAmmunitionPanel = DynAccessor(355)
            VehicleCompareAmmunitionSetup = DynAccessor(356)

        tanksetup = _tanksetup()

        class _vehicle_compare(DynAccessor):
            __slots__ = ()
            CompareModificationsPanelView = DynAccessor(362)
            CompareSkillsPanelView = DynAccessor(363)
            SelectSlotSpecCompareDialog = DynAccessor(364)
            SkillSelectView = DynAccessor(365)

            class _tooltips(DynAccessor):
                __slots__ = ()
                CrewRolesTooltip = DynAccessor(366)

            tooltips = _tooltips()

        vehicle_compare = _vehicle_compare()

        class _vehicle_preview(DynAccessor):
            __slots__ = ()

            class _buying_panel(DynAccessor):
                __slots__ = ()
                StyleBuyingPanel = DynAccessor(367)
                VPProgressionStylesBuyingPanel = DynAccessor(368)

            buying_panel = _buying_panel()

            class _tabs(DynAccessor):
                __slots__ = ()
                CrewTabView = DynAccessor(369)

            tabs = _tabs()

            class _top_panel(DynAccessor):
                __slots__ = ()
                TopPanelTabs = DynAccessor(370)

            top_panel = _top_panel()

        vehicle_preview = _vehicle_preview()

        class _veh_post_progression(DynAccessor):
            __slots__ = ()

            class _common(DynAccessor):
                __slots__ = ()
                Bonus = DynAccessor(371)
                Description = DynAccessor(372)
                Grid = DynAccessor(373)
                PersistentBonuses = DynAccessor(374)
                Slide = DynAccessor(375)
                SlideContent = DynAccessor(376)
                Slider = DynAccessor(377)
                TextSplit = DynAccessor(378)

            common = _common()
            PostProgressionInfo = DynAccessor(379)
            PostProgressionIntro = DynAccessor(380)
            PostProgressionResearchSteps = DynAccessor(381)

            class _tooltip(DynAccessor):
                __slots__ = ()

                class _common(DynAccessor):
                    __slots__ = ()
                    DisabledBlock = DynAccessor(382)
                    FeatureLevelSubtitle = DynAccessor(383)
                    Lock = DynAccessor(384)
                    NotEnoughCredits = DynAccessor(385)
                    PriceBlock = DynAccessor(386)
                    Separator = DynAccessor(387)

                common = _common()
                PairModificationTooltipView = DynAccessor(388)
                PostProgressionLevelTooltipView = DynAccessor(389)
                RoleSlotTooltipView = DynAccessor(390)
                SetupTooltipView = DynAccessor(391)

            tooltip = _tooltip()
            VehiclePostProgressionCmpView = DynAccessor(392)
            VehiclePostProgressionView = DynAccessor(393)

        veh_post_progression = _veh_post_progression()

        class _winback(DynAccessor):
            __slots__ = ()

            class _popovers(DynAccessor):
                __slots__ = ()
                WinbackLeaveModePopoverView = DynAccessor(394)

            popovers = _popovers()

            class _tooltips(DynAccessor):
                __slots__ = ()
                MainRewardTooltip = DynAccessor(395)
                ModeInfoTooltip = DynAccessor(396)
                SelectableRewardTooltip = DynAccessor(397)
                SelectedRewardsTooltip = DynAccessor(398)

            tooltips = _tooltips()
            WinbackDailyQuestsIntroView = DynAccessor(399)
            WinbackLeaveModeDialogView = DynAccessor(400)
            WinbackRewardView = DynAccessor(401)
            WinbackSelectableRewardView = DynAccessor(402)

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

        class _attachments_preview(DynAccessor):
            __slots__ = ()
            attachments_preview = DynAccessor(403)

        attachments_preview = _attachments_preview()

        class _battle_pass(DynAccessor):
            __slots__ = ()

            class _dialogs(DynAccessor):
                __slots__ = ()
                chapter_confirm = DynAccessor(404)

            dialogs = _dialogs()
            full_screen_video = DynAccessor(405)
            how_to_earn_points = DynAccessor(406)
            intro = DynAccessor(407)
            main = DynAccessor(408)
            rewards_screen = DynAccessor(409)
            rewards_selection = DynAccessor(410)
            tankmen_screen = DynAccessor(411)

            class _tooltips(DynAccessor):
                __slots__ = ()
                bpcoin = DynAccessor(412)
                bptaler = DynAccessor(413)
                bp_points = DynAccessor(414)
                completed = DynAccessor(415)
                crew_member_skill = DynAccessor(416)
                gold_mission = DynAccessor(417)
                in_progress = DynAccessor(418)
                lock_icon = DynAccessor(419)
                no_chapter = DynAccessor(420)
                on_pause = DynAccessor(421)
                quest_chain = DynAccessor(422)
                random_quest = DynAccessor(423)
                reward_compensation = DynAccessor(424)
                upgrade_style = DynAccessor(425)
                vehicle_bp_points = DynAccessor(426)

            tooltips = _tooltips()
            vehicle_cap_award = DynAccessor(427)

        battle_pass = _battle_pass()

        class _challenges(DynAccessor):
            __slots__ = ()
            awards_view = DynAccessor(428)

            class _dialogs(DynAccessor):
                __slots__ = ()
                challenge_dialog = DynAccessor(429)

            dialogs = _dialogs()
            main = DynAccessor(430)

        challenges = _challenges()

        class _crew(DynAccessor):
            __slots__ = ()
            welcome_screen = DynAccessor(431)

        crew = _crew()

        class _dialogs(DynAccessor):
            __slots__ = ()
            default_dialog = DynAccessor(432)
            pro_boost_switch_dialog = DynAccessor(433)
            research_confirm_dialog = DynAccessor(434)
            wot_plus_activated_dialog = DynAccessor(435)

        dialogs = _dialogs()

        class _hangar(DynAccessor):
            __slots__ = ()
            footer = DynAccessor(436)
            header = DynAccessor(437)
            main = DynAccessor(438)

            class _overlays(DynAccessor):
                __slots__ = ()
                playlist = DynAccessor(439)

            overlays = _overlays()
            tooltips = DynAccessor(440)
            vehicle_tooltip = DynAccessor(441)

        hangar = _hangar()

        class _integrated_auction(DynAccessor):
            __slots__ = ()

            class _tooltips(DynAccessor):
                __slots__ = ()
                auction_event_banner_tooltip = DynAccessor(442)

            tooltips = _tooltips()

        integrated_auction = _integrated_auction()

        class _lobby(DynAccessor):
            __slots__ = ()
            collector20_reward = DynAccessor(443)
            elite_window = DynAccessor(444)
            select_vehicle = DynAccessor(445)

            class _veh_skill_tree(DynAccessor):
                __slots__ = ()
                comparison = DynAccessor(446)

                class _dialogs(DynAccessor):
                    __slots__ = ()
                    alternate_configuration = DynAccessor(447)

                dialogs = _dialogs()
                intro_page = DynAccessor(448)

                class _notifications(DynAccessor):
                    __slots__ = ()
                    perk_available = DynAccessor(449)

                notifications = _notifications()
                rarity_reward_screen = DynAccessor(450)
                reward_screen = DynAccessor(451)

            veh_skill_tree = _veh_skill_tree()

        lobby = _lobby()

        class _lootbox(DynAccessor):
            __slots__ = ()
            auto_open = DynAccessor(452)
            info_page = DynAccessor(453)
            main = DynAccessor(454)

            class _tooltips(DynAccessor):
                __slots__ = ()
                box_compensation = DynAccessor(455)
                box_tooltip = DynAccessor(456)
                entry_point = DynAccessor(457)
                guaranteed_reward_info = DynAccessor(458)
                random_national_bonus = DynAccessor(459)
                statistics_category = DynAccessor(460)

            tooltips = _tooltips()

        lootbox = _lootbox()

        class _maps_training(DynAccessor):
            __slots__ = ()
            maps_training_page = DynAccessor(461)
            maps_training_queue = DynAccessor(462)
            maps_training_result = DynAccessor(463)
            scenario_tooltip = DynAccessor(464)

        maps_training = _maps_training()

        class _personal_missions_30(DynAccessor):
            __slots__ = ()
            assembling_video = DynAccessor(465)
            campaign_selector = DynAccessor(466)
            intro_screen = DynAccessor(467)
            main = DynAccessor(468)
            rewards = DynAccessor(469)

            class _tooltips(DynAccessor):
                __slots__ = ()
                missions_category_tooltip = DynAccessor(470)
                mission_progress_tooltip = DynAccessor(471)
                param_tooltip = DynAccessor(472)

            tooltips = _tooltips()

        personal_missions_30 = _personal_missions_30()

        class _pet_system(DynAccessor):
            __slots__ = ()
            event_view = DynAccessor(473)
            fullscreen_event_view = DynAccessor(474)
            info_page = DynAccessor(475)
            pet_house_marker = DynAccessor(476)
            pet_storage = DynAccessor(477)

            class _tooltips(DynAccessor):
                __slots__ = ()
                pet_storage_tooltip = DynAccessor(478)
                pet_tooltip = DynAccessor(479)
                synergy_tooltip = DynAccessor(480)

            tooltips = _tooltips()

        pet_system = _pet_system()

        class _post_battle(DynAccessor):
            __slots__ = ()
            flag = DynAccessor(481)
            random = DynAccessor(482)

            class _tooltips(DynAccessor):
                __slots__ = ()
                critical_damage = DynAccessor(483)

            tooltips = _tooltips()

        post_battle = _post_battle()

        class _seniority_awards(DynAccessor):
            __slots__ = ()

            class _notifications(DynAccessor):
                __slots__ = ()
                manual_claim = DynAccessor(484)
                tokens = DynAccessor(485)
                vehicles = DynAccessor(486)

            notifications = _notifications()
            rewards = DynAccessor(487)

            class _tooltips(DynAccessor):
                __slots__ = ()
                seniority_tooltip = DynAccessor(488)

            tooltips = _tooltips()
            vehicle_rewards = DynAccessor(489)

        seniority_awards = _seniority_awards()

        class _stronghold_event(DynAccessor):
            __slots__ = ()

            class _tooltips(DynAccessor):
                __slots__ = ()
                event_banner_tooltip = DynAccessor(490)

            tooltips = _tooltips()

        stronghold_event = _stronghold_event()

        class _tech_tree(DynAccessor):
            __slots__ = ()
            main = DynAccessor(491)

        tech_tree = _tech_tree()

        class _template(DynAccessor):
            __slots__ = ()
            main = DynAccessor(492)

        template = _template()

        class _tooltips(DynAccessor):
            __slots__ = ()
            tooltips = DynAccessor(493)

        tooltips = _tooltips()

        class _user_missions(DynAccessor):
            __slots__ = ()

            class _hub(DynAccessor):
                __slots__ = ()
                mission_hub_intro_view = DynAccessor(495)

            hub = _hub(494)
            info_page = DynAccessor(496)

            class _notifications(DynAccessor):
                __slots__ = ()
                complete_notification = DynAccessor(497)
                fail_notification = DynAccessor(498)
                mission_complete_notification = DynAccessor(499)
                shield_notification = DynAccessor(500)
                start_notification = DynAccessor(501)

            notifications = _notifications()

            class _tooltips(DynAccessor):
                __slots__ = ()
                all_quests_done_tooltip = DynAccessor(502)
                challenges_banner_tooltip = DynAccessor(503)
                challenges_restart_tooltip = DynAccessor(504)
                challenges_shields_tooltip = DynAccessor(505)
                daily_quest_tooltip = DynAccessor(506)
                daily_reroll_tooltip = DynAccessor(507)
                param_tooltip = DynAccessor(508)
                pm3_banner_tooltip = DynAccessor(509)
                weekly_quest_tooltip = DynAccessor(510)

            tooltips = _tooltips()

        user_missions = _user_missions()

        class _vehicle_hub(DynAccessor):
            __slots__ = ()
            main = DynAccessor(511)

            class _tooltips(DynAccessor):
                __slots__ = ()
                armor_tooltip = DynAccessor(512)
                back_to_main_progression_tooltip = DynAccessor(513)
                minor_short_tooltip = DynAccessor(514)
                minor_tooltip = DynAccessor(515)
                perk_tooltip = DynAccessor(516)
                prestige_reward_tooltip = DynAccessor(517)
                vanity_entry_point_tooltip = DynAccessor(518)

            tooltips = _tooltips()

        vehicle_hub = _vehicle_hub()

        class _demos(DynAccessor):
            __slots__ = ()
            blend_mode_custom = DynAccessor(730)
            blend_mode_gf = DynAccessor(731)
            data_layer = DynAccessor(732)

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
                                tooltips = DynAccessor(734)

                            param_tooltip = _param_tooltip()

                        pages = _pages()

                    tech_ui = _tech_ui()

                pages = _pages()

            entry = _entry(733)

            class _notifications(DynAccessor):
                __slots__ = ()
                test_notification = DynAccessor(735)

            notifications = _notifications()

        demos = _demos()

    mono = _mono()

    class _battle_modifiers(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()

            class _tooltips(DynAccessor):
                __slots__ = ()
                ModifiersDomainTooltipView = DynAccessor(519)

            tooltips = _tooltips()

        lobby = _lobby()

    battle_modifiers = _battle_modifiers()

    class _battle_royale(DynAccessor):
        __slots__ = ()

        class _battle(DynAccessor):
            __slots__ = ()

            class _views(DynAccessor):
                __slots__ = ()
                LeaveBattleView = DynAccessor(520)

            views = _views()

        battle = _battle()

        class _lobby(DynAccessor):
            __slots__ = ()
            BattleRoyaleBattleCard = DynAccessor(521)

            class _views(DynAccessor):
                __slots__ = ()
                PreBattleView = DynAccessor(522)

            views = _views()

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _lobby(DynAccessor):
                __slots__ = ()
                battle_quest_awards_view = DynAccessor(523)
                battle_results = DynAccessor(524)
                hangar = DynAccessor(525)
                info_page = DynAccessor(526)
                progression_main_view = DynAccessor(527)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    ability = DynAccessor(528)
                    all_quests_done_tooltip = DynAccessor(529)
                    banner = DynAccessor(530)
                    battle_selector = DynAccessor(531)
                    ceasefire = DynAccessor(532)
                    commander = DynAccessor(533)
                    leaderboard_reward_tooltip_view = DynAccessor(534)
                    progression_quest = DynAccessor(535)
                    progression_widget = DynAccessor(536)
                    proxy_currency_tooltip = DynAccessor(537)
                    respawn = DynAccessor(538)
                    reward_currency_tooltip = DynAccessor(539)
                    shop_button = DynAccessor(540)
                    upgrades_button = DynAccessor(541)
                    vehicle = DynAccessor(542)

                tooltips = _tooltips()

            lobby = _lobby()

        mono = _mono()

    battle_royale = _battle_royale()

    class _comp7(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()
            Comp7BattleCard = DynAccessor(543)
            MembersWindow = DynAccessor(544)
            PlatoonDropdown = DynAccessor(545)
            RewardsSelectionScreen = DynAccessor(546)

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _battle(DynAccessor):
                __slots__ = ()
                ban_progression = DynAccessor(547)
                ban_view = DynAccessor(548)
                ban_widget = DynAccessor(549)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    ban_show_tooltip = DynAccessor(550)

                tooltips = _tooltips()

            battle = _battle()

            class _lobby(DynAccessor):
                __slots__ = ()

                class _dialogs(DynAccessor):
                    __slots__ = ()
                    purchase_dialog = DynAccessor(551)

                dialogs = _dialogs()
                flag = DynAccessor(552)
                hangar = DynAccessor(553)
                intro_screen = DynAccessor(554)
                meta_root_view = DynAccessor(555)
                no_vehicles_screen = DynAccessor(556)
                post_battle_results_view = DynAccessor(557)
                rewards_screen = DynAccessor(558)
                season_statistics = DynAccessor(559)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    battles_indicator_tooltip = DynAccessor(560)
                    crew_members_tooltip = DynAccessor(561)
                    damage_indicator_tooltip = DynAccessor(562)
                    day_tooltip = DynAccessor(563)
                    division_tooltip = DynAccessor(564)
                    entry_point_tooltip = DynAccessor(565)
                    fifth_rank_tooltip = DynAccessor(566)
                    general_rank_tooltip = DynAccessor(567)
                    last_update_tooltip = DynAccessor(568)
                    prestige_indicator_tooltip = DynAccessor(569)
                    prestige_points_info_tooltip = DynAccessor(570)
                    progression_table_tooltip = DynAccessor(571)
                    progression_tooltip = DynAccessor(572)
                    rank_compatibility_tooltip = DynAccessor(573)
                    rank_inactivity_tooltip = DynAccessor(574)
                    rank_indicator_tooltip = DynAccessor(575)
                    season_point_tooltip = DynAccessor(576)
                    sixth_rank_tooltip = DynAccessor(577)
                    style3d_tooltip = DynAccessor(578)
                    tournament_entry_point_tooltip = DynAccessor(579)
                    weekly_quest_widget_tooltip = DynAccessor(580)
                    wins_indicator_tooltip = DynAccessor(581)

                tooltips = _tooltips()

                class _tournaments(DynAccessor):
                    __slots__ = ()
                    ols_view = DynAccessor(582)
                    wci_view = DynAccessor(583)

                tournaments = _tournaments()
                whats_new_view = DynAccessor(584)

            lobby = _lobby()

        mono = _mono()

    comp7 = _comp7()

    class _comp7_light(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()
            Comp7LightBattleCard = DynAccessor(585)
            MembersWindow = DynAccessor(586)
            PlatoonDropdown = DynAccessor(587)

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _lobby(DynAccessor):
                __slots__ = ()
                battle_quest_awards_view = DynAccessor(588)
                entry_point_tooltip = DynAccessor(589)
                flag = DynAccessor(590)
                hangar = DynAccessor(591)
                intro_screen = DynAccessor(592)
                leaderboard_reward_tooltip_view = DynAccessor(593)
                no_vehicles_screen = DynAccessor(594)
                post_battle_results_view = DynAccessor(595)
                progression_main_view = DynAccessor(596)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    all_quests_done_tooltip = DynAccessor(597)
                    battle_quest_tooltip = DynAccessor(598)
                    prestige_points_info_tooltip = DynAccessor(599)

                tooltips = _tooltips()

            lobby = _lobby()

        mono = _mono()

    comp7_light = _comp7_light()

    class _frontline(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()
            RewardsSelectionView = DynAccessor(600)
            WelcomeView = DynAccessor(601)

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _lobby(DynAccessor):
                __slots__ = ()

                class _dialogs(DynAccessor):
                    __slots__ = ()
                    battle_abilities_confirm_dialog = DynAccessor(602)

                dialogs = _dialogs()
                hangar = DynAccessor(603)
                info_view = DynAccessor(604)
                post_battle_results_view = DynAccessor(605)
                post_battle_rewards_view = DynAccessor(606)
                progression_screen = DynAccessor(607)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    banner_tooltip = DynAccessor(608)
                    battle_ability_alt_tooltip = DynAccessor(609)
                    battle_ability_tooltip = DynAccessor(610)
                    level_reserves_tooltip = DynAccessor(611)
                    skill_order_tooltip = DynAccessor(612)

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
                FunRandomModeSubSelector = DynAccessor(613)

            feature = _feature()

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _lobby(DynAccessor):
                __slots__ = ()
                battle_results = DynAccessor(614)
                hangar = DynAccessor(615)
                progression = DynAccessor(616)
                rewards = DynAccessor(617)
                tier_list = DynAccessor(618)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    battle_results_economic_tooltip = DynAccessor(619)
                    entry_point_tooltip = DynAccessor(620)
                    loot_box_tooltip = DynAccessor(621)
                    no_quests_tooltip = DynAccessor(622)
                    progression_quest_tooltip = DynAccessor(623)
                    progression_tooltip = DynAccessor(624)

                tooltips = _tooltips()

            lobby = _lobby()

        mono = _mono()

    fun_random = _fun_random()

    class _last_stand(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()
            MembersWindow = DynAccessor(625)
            PlatoonDropdown = DynAccessor(626)
            SearchingDropdown = DynAccessor(627)

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _battle(DynAccessor):
                __slots__ = ()
                battle_loading = DynAccessor(628)
                help_view = DynAccessor(629)
                tab_screen = DynAccessor(630)

            battle = _battle()

            class _lobby(DynAccessor):
                __slots__ = ()
                attachments_reward_view = DynAccessor(631)
                battle_result_view = DynAccessor(632)

                class _dialogs(DynAccessor):
                    __slots__ = ()
                    abilities_incomplete_confirm = DynAccessor(633)

                dialogs = _dialogs()
                difficulty_congratulation_view = DynAccessor(634)
                hangar = DynAccessor(635)
                meta_intro = DynAccessor(636)
                narration_view = DynAccessor(637)
                prebattle_queue_view = DynAccessor(638)
                promo_view = DynAccessor(639)
                reward_path_view = DynAccessor(640)
                stage_reward_view = DynAccessor(641)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    additional_data_tooltip = DynAccessor(642)
                    banner_tooltip = DynAccessor(643)
                    battle_pass_tooltip = DynAccessor(644)
                    booster_tooltip = DynAccessor(645)
                    daily_quests_tooltip = DynAccessor(646)
                    difficulty_tooltip = DynAccessor(647)
                    points_tooltip = DynAccessor(648)
                    reward_path_tooltip = DynAccessor(649)
                    simple_format_tooltip = DynAccessor(650)
                    vehicle_tooltip = DynAccessor(651)

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
                attachments_preview = DynAccessor(652)
                confirmation = DynAccessor(653)
                intro = DynAccessor(654)
                main = DynAccessor(655)

                class _notifications(DynAccessor):
                    __slots__ = ()
                    special_rewards_notification = DynAccessor(656)
                    start_notification = DynAccessor(657)

                notifications = _notifications()

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    event_banner = DynAccessor(658)
                    fixed_rewards = DynAccessor(659)

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
                award_view = DynAccessor(660)
                completed_progression_view = DynAccessor(661)
                no_serial_vehicles_confirm = DynAccessor(662)
                no_vehicles_confirm = DynAccessor(663)
                progression_view = DynAccessor(664)
                resources_loading_confirm = DynAccessor(665)
                resources_loading_view = DynAccessor(666)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    event_banner_tooltip = DynAccessor(667)
                    max_progress_tooltip = DynAccessor(668)
                    progress_tooltip = DynAccessor(669)
                    serial_number_tooltip = DynAccessor(670)
                    simple_tooltip = DynAccessor(671)

                tooltips = _tooltips()
                vehicle_preview_bottom_panel = DynAccessor(672)

            lobby = _lobby()

        mono = _mono()

    resource_well = _resource_well()

    class _server_side_replay(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()
            MetaReplaysView = DynAccessor(673)

            class _popovers(DynAccessor):
                __slots__ = ()
                ReplaysFilterPopover = DynAccessor(674)

            popovers = _popovers()

        lobby = _lobby()

    server_side_replay = _server_side_replay()

    class _story_mode(DynAccessor):
        __slots__ = ()

        class _mono(DynAccessor):
            __slots__ = ()

            class _battle(DynAccessor):
                __slots__ = ()
                epilogue_window = DynAccessor(675)
                onboarding_battle_result_view = DynAccessor(676)
                prebattle_window = DynAccessor(677)

            battle = _battle()

            class _lobby(DynAccessor):
                __slots__ = ()
                battle_result_view = DynAccessor(678)
                congratulations_window = DynAccessor(679)
                event_welcome_view = DynAccessor(680)
                mission_selection_view = DynAccessor(681)
                newbie_advertising_view = DynAccessor(682)
                onboarding_queue_view = DynAccessor(683)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    badge_tooltip = DynAccessor(684)
                    battle_result_stat_tooltip = DynAccessor(685)
                    difficulty_tooltip = DynAccessor(686)
                    event_banner_tooltip = DynAccessor(687)
                    medal_tooltip = DynAccessor(688)
                    mission_tooltip = DynAccessor(689)
                    newbie_banner_tooltip = DynAccessor(690)

                tooltips = _tooltips()

            lobby = _lobby()

        mono = _mono()

    story_mode = _story_mode()
    Anchor = DynAccessor(691)

    class _child_views_demo(DynAccessor):
        __slots__ = ()
        ChildDemoView = DynAccessor(692)
        MainView = DynAccessor(693)

    child_views_demo = _child_views_demo()
    Comp7DemoPageView = DynAccessor(694)
    ComponentsDemo = DynAccessor(695)
    CustomMixBlendModes = DynAccessor(696)
    DataLayerDemoView = DynAccessor(697)
    DataTrackerDemo = DynAccessor(698)
    DeathCamDemoView = DynAccessor(699)
    DemoContextMenu = DynAccessor(700)
    Easings = DynAccessor(701)
    GameLoadingDebugView = DynAccessor(702)
    GFCharset = DynAccessor(703)
    GFComponents = DynAccessor(704)
    GFDemoPopover = DynAccessor(705)
    GFDemoRichTooltipWindow = DynAccessor(706)
    GFDemoWindow = DynAccessor(707)
    GFHooksDemo = DynAccessor(708)
    GFInjectView = DynAccessor(709)
    GFInputCases = DynAccessor(710)
    GFMixBlendModes = DynAccessor(711)
    GFSimpleTooltipWindow = DynAccessor(712)
    GFWebSubDemoWindow = DynAccessor(713)

    class _gf_dialogs_demo(DynAccessor):
        __slots__ = ()
        DefaultDialogProxy = DynAccessor(714)
        GFDialogsDemo = DynAccessor(715)

        class _sub_views(DynAccessor):
            __slots__ = ()
            DummyContent = DynAccessor(716)
            DummyFooter = DynAccessor(717)
            DummyIcon = DynAccessor(718)
            DummyStepper = DynAccessor(719)
            DummyTitle = DynAccessor(720)
            DummyTopRight = DynAccessor(721)

        sub_views = _sub_views()

    gf_dialogs_demo = _gf_dialogs_demo()

    class _gf_viewer(DynAccessor):
        __slots__ = ()
        GFViewerWindow = DynAccessor(722)

    gf_viewer = _gf_viewer()

    class _igb_demo(DynAccessor):
        __slots__ = ()
        BrowserFullscreenWindow = DynAccessor(723)
        BrowserWindow = DynAccessor(724)
        MainView = DynAccessor(725)

    igb_demo = _igb_demo()
    LocaleDemo = DynAccessor(726)
    MediaWrapperDemo = DynAccessor(727)
    ModeSelectorDemo = DynAccessor(728)
    ModeSelectorToolsetView = DynAccessor(729)
    ParallaxExample = DynAccessor(736)
    ParallaxViewer = DynAccessor(737)
    PluralLocView = DynAccessor(738)
    PropsSupportDemo = DynAccessor(739)
    ReactSpringVizualizer = DynAccessor(740)
    SelectableRewardDemoView = DynAccessor(741)
    StructuralDataBindDemo = DynAccessor(742)

    class _sub_views_demo(DynAccessor):
        __slots__ = ()
        GFSubViewsDemo = DynAccessor(743)

        class _sub_views(DynAccessor):
            __slots__ = ()
            CustomizationCartProxy = DynAccessor(744)
            ProgressiveItemsViewProxy = DynAccessor(745)

        sub_views = _sub_views()

    sub_views_demo = _sub_views_demo()
    UILoggerDemo = DynAccessor(746)
    VideoSupportView = DynAccessor(747)
    W2CTestPageWindow = DynAccessor(748)
    WgcgMockView = DynAccessor(749)

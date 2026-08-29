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
            attachments_preview = DynAccessor(394)

        attachments_preview = _attachments_preview()

        class _battle_pass(DynAccessor):
            __slots__ = ()

            class _dialogs(DynAccessor):
                __slots__ = ()
                chapter_confirm = DynAccessor(395)

            dialogs = _dialogs()
            full_screen_video = DynAccessor(396)
            how_to_earn_points = DynAccessor(397)
            intro = DynAccessor(398)
            main = DynAccessor(399)
            rewards_screen = DynAccessor(400)
            rewards_selection = DynAccessor(401)
            tankmen_screen = DynAccessor(402)

            class _tooltips(DynAccessor):
                __slots__ = ()
                bpcoin = DynAccessor(403)
                bptaler = DynAccessor(404)
                bp_points = DynAccessor(405)
                completed = DynAccessor(406)
                crew_member_skill = DynAccessor(407)
                gold_mission = DynAccessor(408)
                in_progress = DynAccessor(409)
                lock_icon = DynAccessor(410)
                no_chapter = DynAccessor(411)
                on_pause = DynAccessor(412)
                quest_chain = DynAccessor(413)
                random_quest = DynAccessor(414)
                reward_compensation = DynAccessor(415)
                upgrade_style = DynAccessor(416)
                vehicle_bp_points = DynAccessor(417)

            tooltips = _tooltips()
            vehicle_cap_award = DynAccessor(418)

        battle_pass = _battle_pass()

        class _challenges(DynAccessor):
            __slots__ = ()
            awards_view = DynAccessor(419)

            class _dialogs(DynAccessor):
                __slots__ = ()
                challenge_dialog = DynAccessor(420)

            dialogs = _dialogs()
            main = DynAccessor(421)

        challenges = _challenges()

        class _crew(DynAccessor):
            __slots__ = ()
            welcome_screen = DynAccessor(422)

        crew = _crew()

        class _dialogs(DynAccessor):
            __slots__ = ()
            default_dialog = DynAccessor(423)
            pro_boost_switch_dialog = DynAccessor(424)
            research_confirm_dialog = DynAccessor(425)
            wot_plus_activated_dialog = DynAccessor(426)

        dialogs = _dialogs()

        class _hangar(DynAccessor):
            __slots__ = ()
            footer = DynAccessor(427)
            header = DynAccessor(428)
            main = DynAccessor(429)

            class _overlays(DynAccessor):
                __slots__ = ()
                playlist = DynAccessor(430)

            overlays = _overlays()
            tooltips = DynAccessor(431)
            vehicle_tooltip = DynAccessor(432)

        hangar = _hangar()

        class _integrated_auction(DynAccessor):
            __slots__ = ()

            class _tooltips(DynAccessor):
                __slots__ = ()
                auction_event_banner_tooltip = DynAccessor(433)

            tooltips = _tooltips()

        integrated_auction = _integrated_auction()

        class _lobby(DynAccessor):
            __slots__ = ()
            collector20_reward = DynAccessor(434)
            elite_window = DynAccessor(435)
            select_vehicle = DynAccessor(436)

            class _veh_skill_tree(DynAccessor):
                __slots__ = ()
                comparison = DynAccessor(437)

                class _dialogs(DynAccessor):
                    __slots__ = ()
                    alternate_configuration = DynAccessor(438)

                dialogs = _dialogs()
                intro_page = DynAccessor(439)

                class _notifications(DynAccessor):
                    __slots__ = ()
                    perk_available = DynAccessor(440)

                notifications = _notifications()
                rarity_reward_screen = DynAccessor(441)
                reward_screen = DynAccessor(442)

            veh_skill_tree = _veh_skill_tree()

        lobby = _lobby()

        class _lootbox(DynAccessor):
            __slots__ = ()
            auto_open = DynAccessor(443)

            class _dialogs(DynAccessor):
                __slots__ = ()
                reroll_dialog = DynAccessor(444)

            dialogs = _dialogs()
            info_page = DynAccessor(445)
            main = DynAccessor(446)

            class _tooltips(DynAccessor):
                __slots__ = ()
                box_compensation = DynAccessor(447)
                box_tooltip = DynAccessor(448)
                entry_point = DynAccessor(449)
                guaranteed_reward_info = DynAccessor(450)
                random_national_bonus = DynAccessor(451)
                reroll = DynAccessor(452)
                statistics_category = DynAccessor(453)

            tooltips = _tooltips()

        lootbox = _lootbox()

        class _maps_training(DynAccessor):
            __slots__ = ()
            maps_training_page = DynAccessor(454)
            maps_training_queue = DynAccessor(455)
            maps_training_result = DynAccessor(456)
            scenario_tooltip = DynAccessor(457)

        maps_training = _maps_training()

        class _personal_missions_30(DynAccessor):
            __slots__ = ()
            assembling_video = DynAccessor(458)
            campaign_selector = DynAccessor(459)
            intro_screen = DynAccessor(460)
            main = DynAccessor(461)
            rewards = DynAccessor(462)

            class _tooltips(DynAccessor):
                __slots__ = ()
                missions_category_tooltip = DynAccessor(463)
                mission_progress_tooltip = DynAccessor(464)
                param_tooltip = DynAccessor(465)
                umg_tooltip = DynAccessor(466)

            tooltips = _tooltips()

        personal_missions_30 = _personal_missions_30()

        class _pet_system(DynAccessor):
            __slots__ = ()
            event_view = DynAccessor(467)
            fullscreen_event_view = DynAccessor(468)
            info_page = DynAccessor(469)
            pet_house_marker = DynAccessor(470)
            pet_storage = DynAccessor(471)

            class _tooltips(DynAccessor):
                __slots__ = ()
                pet_storage_tooltip = DynAccessor(472)
                pet_tooltip = DynAccessor(473)
                synergy_tooltip = DynAccessor(474)

            tooltips = _tooltips()

        pet_system = _pet_system()

        class _post_battle(DynAccessor):
            __slots__ = ()
            flag = DynAccessor(475)
            random = DynAccessor(476)

            class _tooltips(DynAccessor):
                __slots__ = ()
                critical_damage = DynAccessor(477)

            tooltips = _tooltips()

        post_battle = _post_battle()

        class _prebattle_highlights(DynAccessor):
            __slots__ = ()
            main = DynAccessor(478)

        prebattle_highlights = _prebattle_highlights()

        class _rest_bonus(DynAccessor):
            __slots__ = ()

            class _tooltips(DynAccessor):
                __slots__ = ()
                rest_bonus_tooltip = DynAccessor(479)

            tooltips = _tooltips()

        rest_bonus = _rest_bonus()

        class _seniority_awards(DynAccessor):
            __slots__ = ()

            class _notifications(DynAccessor):
                __slots__ = ()
                manual_claim = DynAccessor(480)
                tokens = DynAccessor(481)
                vehicles = DynAccessor(482)

            notifications = _notifications()
            rewards = DynAccessor(483)

            class _tooltips(DynAccessor):
                __slots__ = ()
                seniority_tooltip = DynAccessor(484)

            tooltips = _tooltips()
            vehicle_rewards = DynAccessor(485)

        seniority_awards = _seniority_awards()

        class _stronghold_event(DynAccessor):
            __slots__ = ()

            class _tooltips(DynAccessor):
                __slots__ = ()
                event_banner_tooltip = DynAccessor(486)

            tooltips = _tooltips()

        stronghold_event = _stronghold_event()

        class _tech_tree(DynAccessor):
            __slots__ = ()
            main = DynAccessor(487)

        tech_tree = _tech_tree()

        class _template(DynAccessor):
            __slots__ = ()
            main = DynAccessor(488)

        template = _template()

        class _tooltips(DynAccessor):
            __slots__ = ()
            tooltips = DynAccessor(489)

        tooltips = _tooltips()

        class _user_missions(DynAccessor):
            __slots__ = ()

            class _hub(DynAccessor):
                __slots__ = ()
                mission_hub_intro_view = DynAccessor(491)

            hub = _hub(490)
            info_page = DynAccessor(492)

            class _notifications(DynAccessor):
                __slots__ = ()
                complete_notification = DynAccessor(493)
                fail_notification = DynAccessor(494)
                mission_complete_notification = DynAccessor(495)
                shield_notification = DynAccessor(496)
                start_notification = DynAccessor(497)

            notifications = _notifications()

            class _tooltips(DynAccessor):
                __slots__ = ()
                all_quests_done_tooltip = DynAccessor(498)
                challenges_banner_tooltip = DynAccessor(499)
                challenges_restart_tooltip = DynAccessor(500)
                challenges_shields_tooltip = DynAccessor(501)
                daily_quest_tooltip = DynAccessor(502)
                daily_reroll_tooltip = DynAccessor(503)
                param_tooltip = DynAccessor(504)
                pm4_banner_tooltip = DynAccessor(505)
                weekly_quest_tooltip = DynAccessor(506)

            tooltips = _tooltips()

        user_missions = _user_missions()

        class _vehicle_hub(DynAccessor):
            __slots__ = ()
            main = DynAccessor(507)

            class _tooltips(DynAccessor):
                __slots__ = ()
                armor_tooltip = DynAccessor(508)
                back_to_main_progression_tooltip = DynAccessor(509)
                minor_short_tooltip = DynAccessor(510)
                minor_tooltip = DynAccessor(511)
                perk_tooltip = DynAccessor(512)
                prestige_reward_tooltip = DynAccessor(513)
                vanity_entry_point_tooltip = DynAccessor(514)

            tooltips = _tooltips()

        vehicle_hub = _vehicle_hub()

        class _winback(DynAccessor):
            __slots__ = ()

            class _popovers(DynAccessor):
                __slots__ = ()
                winback_leave_mode_popover_view = DynAccessor(515)

            popovers = _popovers()

            class _tooltips(DynAccessor):
                __slots__ = ()
                main_reward_tooltip = DynAccessor(516)
                mode_info_tooltip = DynAccessor(517)
                selectable_reward_tooltip = DynAccessor(518)
                selected_rewards_tooltip = DynAccessor(519)

            tooltips = _tooltips()
            winback_leave_mode_dialog_view = DynAccessor(520)
            winback_reward_view = DynAccessor(521)
            winback_selectable_reward_view = DynAccessor(522)
            winback_umg_intro_view = DynAccessor(523)

        winback = _winback()

        class _demos(DynAccessor):
            __slots__ = ()
            blend_mode_custom = DynAccessor(757)
            blend_mode_gf = DynAccessor(758)
            data_layer = DynAccessor(759)

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
                                tooltips = DynAccessor(761)

                            param_tooltip = _param_tooltip()

                        pages = _pages()

                    tech_ui = _tech_ui()

                pages = _pages()

            entry = _entry(760)

            class _notifications(DynAccessor):
                __slots__ = ()
                test_notification = DynAccessor(762)

            notifications = _notifications()

        demos = _demos()

    mono = _mono()

    class _battle_modifiers(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()

            class _tooltips(DynAccessor):
                __slots__ = ()
                ModifiersDomainTooltipView = DynAccessor(524)

            tooltips = _tooltips()

        lobby = _lobby()

    battle_modifiers = _battle_modifiers()

    class _battle_royale(DynAccessor):
        __slots__ = ()

        class _battle(DynAccessor):
            __slots__ = ()

            class _views(DynAccessor):
                __slots__ = ()
                LeaveBattleView = DynAccessor(525)

            views = _views()

        battle = _battle()

        class _lobby(DynAccessor):
            __slots__ = ()
            BattleRoyaleBattleCard = DynAccessor(526)

            class _views(DynAccessor):
                __slots__ = ()
                PreBattleView = DynAccessor(527)

            views = _views()

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _lobby(DynAccessor):
                __slots__ = ()
                battle_quest_awards_view = DynAccessor(528)
                battle_results = DynAccessor(529)
                hangar = DynAccessor(530)
                info_page = DynAccessor(531)
                progression_main_view = DynAccessor(532)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    ability = DynAccessor(533)
                    all_quests_done_tooltip = DynAccessor(534)
                    banner = DynAccessor(535)
                    battle_selector = DynAccessor(536)
                    ceasefire = DynAccessor(537)
                    commander = DynAccessor(538)
                    leaderboard_reward_tooltip_view = DynAccessor(539)
                    progression_quest = DynAccessor(540)
                    progression_widget = DynAccessor(541)
                    proxy_currency_tooltip = DynAccessor(542)
                    respawn = DynAccessor(543)
                    reward_currency_tooltip = DynAccessor(544)
                    shop_button = DynAccessor(545)
                    upgrades_button = DynAccessor(546)
                    vehicle = DynAccessor(547)

                tooltips = _tooltips()

            lobby = _lobby()

        mono = _mono()

    battle_royale = _battle_royale()

    class _comp7(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()
            Comp7BattleCard = DynAccessor(548)
            MembersWindow = DynAccessor(549)
            PlatoonDropdown = DynAccessor(550)
            RewardsSelectionScreen = DynAccessor(551)

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _battle(DynAccessor):
                __slots__ = ()
                ban_progression = DynAccessor(552)
                ban_view = DynAccessor(553)
                ban_widget = DynAccessor(554)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    ban_show_tooltip = DynAccessor(555)

                tooltips = _tooltips()

            battle = _battle()

            class _lobby(DynAccessor):
                __slots__ = ()

                class _dialogs(DynAccessor):
                    __slots__ = ()
                    purchase_dialog = DynAccessor(556)

                dialogs = _dialogs()
                flag = DynAccessor(557)
                hangar = DynAccessor(558)
                intro_screen = DynAccessor(559)
                meta_root_view = DynAccessor(560)
                no_vehicles_screen = DynAccessor(561)
                post_battle_results_view = DynAccessor(562)
                rewards_screen = DynAccessor(563)
                season_statistics = DynAccessor(564)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    battles_indicator_tooltip = DynAccessor(565)
                    crew_members_tooltip = DynAccessor(566)
                    damage_indicator_tooltip = DynAccessor(567)
                    day_tooltip = DynAccessor(568)
                    division_tooltip = DynAccessor(569)
                    entry_point_tooltip = DynAccessor(570)
                    fifth_rank_tooltip = DynAccessor(571)
                    general_rank_tooltip = DynAccessor(572)
                    last_update_tooltip = DynAccessor(573)
                    prestige_indicator_tooltip = DynAccessor(574)
                    prestige_points_info_tooltip = DynAccessor(575)
                    progression_table_tooltip = DynAccessor(576)
                    progression_tooltip = DynAccessor(577)
                    rank_compatibility_tooltip = DynAccessor(578)
                    rank_inactivity_tooltip = DynAccessor(579)
                    rank_indicator_tooltip = DynAccessor(580)
                    season_point_tooltip = DynAccessor(581)
                    sixth_rank_tooltip = DynAccessor(582)
                    style3d_tooltip = DynAccessor(583)
                    tournament_entry_point_tooltip = DynAccessor(584)
                    weekly_quest_widget_tooltip = DynAccessor(585)
                    wins_indicator_tooltip = DynAccessor(586)

                tooltips = _tooltips()

                class _tournaments(DynAccessor):
                    __slots__ = ()
                    ols_view = DynAccessor(587)
                    wci_view = DynAccessor(588)

                tournaments = _tournaments()
                whats_new_view = DynAccessor(589)

            lobby = _lobby()

        mono = _mono()

    comp7 = _comp7()

    class _comp7_core(DynAccessor):
        __slots__ = ()

        class _mono(DynAccessor):
            __slots__ = ()

            class _lobby(DynAccessor):
                __slots__ = ()

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    modifiers_domain_tooltip = DynAccessor(590)

                tooltips = _tooltips()

            lobby = _lobby()

        mono = _mono()

    comp7_core = _comp7_core()

    class _comp7_light(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()
            Comp7LightBattleCard = DynAccessor(591)
            MembersWindow = DynAccessor(592)
            PlatoonDropdown = DynAccessor(593)

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _lobby(DynAccessor):
                __slots__ = ()
                battle_quest_awards_view = DynAccessor(594)
                entry_point_tooltip = DynAccessor(595)
                flag = DynAccessor(596)
                hangar = DynAccessor(597)
                intro_screen = DynAccessor(598)
                leaderboard_reward_tooltip_view = DynAccessor(599)
                no_vehicles_screen = DynAccessor(600)
                post_battle_results_view = DynAccessor(601)
                progression_main_view = DynAccessor(602)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    all_quests_done_tooltip = DynAccessor(603)
                    battle_quest_tooltip = DynAccessor(604)
                    prestige_points_info_tooltip = DynAccessor(605)

                tooltips = _tooltips()

            lobby = _lobby()

        mono = _mono()

    comp7_light = _comp7_light()

    class _fall_tanks(DynAccessor):
        __slots__ = ()

        class _battle(DynAccessor):
            __slots__ = ()
            FallTanksBattleWidgetView = DynAccessor(606)
            FallTanksPostmortemInfoView = DynAccessor(607)

        battle = _battle()

    fall_tanks = _fall_tanks()

    class _frontline(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()
            RewardsSelectionView = DynAccessor(608)
            WelcomeView = DynAccessor(609)

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _lobby(DynAccessor):
                __slots__ = ()

                class _dialogs(DynAccessor):
                    __slots__ = ()
                    battle_abilities_confirm_dialog = DynAccessor(610)

                dialogs = _dialogs()
                hangar = DynAccessor(611)
                info_view = DynAccessor(612)
                post_battle_results_view = DynAccessor(613)
                post_battle_rewards_view = DynAccessor(614)
                progression_screen = DynAccessor(615)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    banner_tooltip = DynAccessor(616)
                    battle_ability_alt_tooltip = DynAccessor(617)
                    battle_ability_tooltip = DynAccessor(618)
                    level_reserves_tooltip = DynAccessor(619)
                    skill_order_tooltip = DynAccessor(620)

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
                FunRandomModeSubSelector = DynAccessor(621)

            feature = _feature()

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _lobby(DynAccessor):
                __slots__ = ()
                battle_results = DynAccessor(622)
                hangar = DynAccessor(623)
                progression = DynAccessor(624)
                rewards = DynAccessor(625)
                tier_list = DynAccessor(626)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    battle_results_economic_tooltip = DynAccessor(627)
                    entry_point_tooltip = DynAccessor(628)
                    loot_box_tooltip = DynAccessor(629)
                    no_quests_tooltip = DynAccessor(630)
                    progression_quest_tooltip = DynAccessor(631)
                    progression_tooltip = DynAccessor(632)

                tooltips = _tooltips()

            lobby = _lobby()

        mono = _mono()

    fun_random = _fun_random()

    class _last_stand(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()
            MembersWindow = DynAccessor(633)
            PlatoonDropdown = DynAccessor(634)
            SearchingDropdown = DynAccessor(635)

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _battle(DynAccessor):
                __slots__ = ()
                battle_loading = DynAccessor(636)
                help_view = DynAccessor(637)
                tab_screen = DynAccessor(638)

            battle = _battle()

            class _lobby(DynAccessor):
                __slots__ = ()
                attachments_reward_view = DynAccessor(639)
                battle_result_view = DynAccessor(640)

                class _dialogs(DynAccessor):
                    __slots__ = ()
                    abilities_incomplete_confirm = DynAccessor(641)

                dialogs = _dialogs()
                difficulty_congratulation_view = DynAccessor(642)
                hangar = DynAccessor(643)
                meta_intro = DynAccessor(644)
                narration_view = DynAccessor(645)
                prebattle_queue_view = DynAccessor(646)
                promo_view = DynAccessor(647)
                reward_path_view = DynAccessor(648)
                stage_reward_view = DynAccessor(649)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    additional_data_tooltip = DynAccessor(650)
                    banner_tooltip = DynAccessor(651)
                    battle_pass_tooltip = DynAccessor(652)
                    booster_tooltip = DynAccessor(653)
                    daily_quests_tooltip = DynAccessor(654)
                    difficulty_tooltip = DynAccessor(655)
                    points_tooltip = DynAccessor(656)
                    reward_path_tooltip = DynAccessor(657)
                    simple_format_tooltip = DynAccessor(658)
                    vehicle_tooltip = DynAccessor(659)

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
                attachments_preview = DynAccessor(660)
                confirmation = DynAccessor(661)
                intro = DynAccessor(662)
                main = DynAccessor(663)

                class _notifications(DynAccessor):
                    __slots__ = ()
                    special_rewards_notification = DynAccessor(664)
                    start_notification = DynAccessor(665)

                notifications = _notifications()

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    event_banner = DynAccessor(666)
                    fixed_rewards = DynAccessor(667)

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
                award_view = DynAccessor(668)
                completed_progression_view = DynAccessor(669)
                no_serial_vehicles_confirm = DynAccessor(670)
                no_vehicles_confirm = DynAccessor(671)
                progression_view = DynAccessor(672)
                resources_loading_confirm = DynAccessor(673)
                resources_loading_view = DynAccessor(674)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    event_banner_tooltip = DynAccessor(675)
                    max_progress_tooltip = DynAccessor(676)
                    progress_tooltip = DynAccessor(677)
                    serial_number_tooltip = DynAccessor(678)
                    simple_tooltip = DynAccessor(679)

                tooltips = _tooltips()
                vehicle_preview_bottom_panel = DynAccessor(680)

            lobby = _lobby()

        mono = _mono()

    resource_well = _resource_well()

    class _server_side_replay(DynAccessor):
        __slots__ = ()

        class _lobby(DynAccessor):
            __slots__ = ()
            MetaReplaysView = DynAccessor(681)

            class _popovers(DynAccessor):
                __slots__ = ()
                ReplaysFilterPopover = DynAccessor(682)

            popovers = _popovers()

        lobby = _lobby()

    server_side_replay = _server_side_replay()

    class _story_mode(DynAccessor):
        __slots__ = ()

        class _mono(DynAccessor):
            __slots__ = ()

            class _battle(DynAccessor):
                __slots__ = ()
                epilogue_window = DynAccessor(683)
                onboarding_battle_result_view = DynAccessor(684)
                prebattle_window = DynAccessor(685)

            battle = _battle()

            class _lobby(DynAccessor):
                __slots__ = ()
                battle_result_view = DynAccessor(686)
                congratulations_window = DynAccessor(687)
                event_welcome_view = DynAccessor(688)
                mission_selection_view = DynAccessor(689)
                newbie_advertising_view = DynAccessor(690)
                onboarding_queue_view = DynAccessor(691)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    badge_tooltip = DynAccessor(692)
                    battle_result_stat_tooltip = DynAccessor(693)
                    difficulty_tooltip = DynAccessor(694)
                    event_banner_tooltip = DynAccessor(695)
                    medal_tooltip = DynAccessor(696)
                    mission_tooltip = DynAccessor(697)
                    newbie_banner_tooltip = DynAccessor(698)

                tooltips = _tooltips()

            lobby = _lobby()

        mono = _mono()

    story_mode = _story_mode()

    class _white_tiger(DynAccessor):
        __slots__ = ()

        class _battle(DynAccessor):
            __slots__ = ()
            WhiteTigerBattleLoading = DynAccessor(699)
            WhiteTigerHudView = DynAccessor(700)

        battle = _battle()

        class _lobby(DynAccessor):
            __slots__ = ()
            BattleCard = DynAccessor(701)

            class _platoon(DynAccessor):
                __slots__ = ()
                MembersWindow = DynAccessor(702)

            platoon = _platoon()

        lobby = _lobby()

        class _mono(DynAccessor):
            __slots__ = ()

            class _lobby(DynAccessor):
                __slots__ = ()
                battle_results_screen = DynAccessor(703)
                main = DynAccessor(704)
                narrative_screen = DynAccessor(705)

                class _notifications(DynAccessor):
                    __slots__ = ()
                    special_mission_completed_notification = DynAccessor(706)

                notifications = _notifications()
                reward_screen = DynAccessor(707)

                class _tooltips(DynAccessor):
                    __slots__ = ()
                    ammunition_panel_tooltip = DynAccessor(708)
                    banner_tooltip = DynAccessor(709)
                    battle_results_economic_tooltip = DynAccessor(710)
                    carousel_vehicle_tooltip = DynAccessor(711)
                    crew_info_tooltip = DynAccessor(712)
                    progression_widget_tooltip = DynAccessor(713)
                    stamp_tooltip = DynAccessor(714)
                    tank_info_tooltip = DynAccessor(715)
                    ticket_tooltip = DynAccessor(716)

                tooltips = _tooltips()
                welcome_screen = DynAccessor(717)

            lobby = _lobby()

        mono = _mono()

    white_tiger = _white_tiger()
    Anchor = DynAccessor(718)

    class _child_views_demo(DynAccessor):
        __slots__ = ()
        ChildDemoView = DynAccessor(719)
        MainView = DynAccessor(720)

    child_views_demo = _child_views_demo()
    Comp7DemoPageView = DynAccessor(721)
    ComponentsDemo = DynAccessor(722)
    CustomMixBlendModes = DynAccessor(723)
    DataLayerDemoView = DynAccessor(724)
    DataTrackerDemo = DynAccessor(725)
    DeathCamDemoView = DynAccessor(726)
    DemoContextMenu = DynAccessor(727)
    Easings = DynAccessor(728)
    GameLoadingDebugView = DynAccessor(729)
    GFCharset = DynAccessor(730)
    GFComponents = DynAccessor(731)
    GFDemoPopover = DynAccessor(732)
    GFDemoRichTooltipWindow = DynAccessor(733)
    GFDemoWindow = DynAccessor(734)
    GFHooksDemo = DynAccessor(735)
    GFInjectView = DynAccessor(736)
    GFInputCases = DynAccessor(737)
    GFMixBlendModes = DynAccessor(738)
    GFSimpleTooltipWindow = DynAccessor(739)
    GFWebSubDemoWindow = DynAccessor(740)

    class _gf_dialogs_demo(DynAccessor):
        __slots__ = ()
        DefaultDialogProxy = DynAccessor(741)
        GFDialogsDemo = DynAccessor(742)

        class _sub_views(DynAccessor):
            __slots__ = ()
            DummyContent = DynAccessor(743)
            DummyFooter = DynAccessor(744)
            DummyIcon = DynAccessor(745)
            DummyStepper = DynAccessor(746)
            DummyTitle = DynAccessor(747)
            DummyTopRight = DynAccessor(748)

        sub_views = _sub_views()

    gf_dialogs_demo = _gf_dialogs_demo()

    class _gf_viewer(DynAccessor):
        __slots__ = ()
        GFViewerWindow = DynAccessor(749)

    gf_viewer = _gf_viewer()

    class _igb_demo(DynAccessor):
        __slots__ = ()
        BrowserFullscreenWindow = DynAccessor(750)
        BrowserWindow = DynAccessor(751)
        MainView = DynAccessor(752)

    igb_demo = _igb_demo()
    LocaleDemo = DynAccessor(753)
    MediaWrapperDemo = DynAccessor(754)
    ModeSelectorDemo = DynAccessor(755)
    ModeSelectorToolsetView = DynAccessor(756)
    ParallaxExample = DynAccessor(763)
    ParallaxViewer = DynAccessor(764)
    PluralLocView = DynAccessor(765)
    PropsSupportDemo = DynAccessor(766)
    ReactSpringVizualizer = DynAccessor(767)
    SelectableRewardDemoView = DynAccessor(768)
    StructuralDataBindDemo = DynAccessor(769)

    class _sub_views_demo(DynAccessor):
        __slots__ = ()
        GFSubViewsDemo = DynAccessor(770)

        class _sub_views(DynAccessor):
            __slots__ = ()
            CustomizationCartProxy = DynAccessor(771)
            ProgressiveItemsViewProxy = DynAccessor(772)

        sub_views = _sub_views()

    sub_views_demo = _sub_views_demo()
    UILoggerDemo = DynAccessor(773)
    VideoSupportView = DynAccessor(774)
    W2CTestPageWindow = DynAccessor(775)
    WgcgMockView = DynAccessor(776)

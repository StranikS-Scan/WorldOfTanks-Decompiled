# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/views.py
from gui.impl.gen_utils import DynAccessor

class Views(DynAccessor):
    __slots__ = ()

    class _common(DynAccessor):
        __slots__ = ()

        class _context_menu_window(DynAccessor):
            __slots__ = ()

            class _context_menu_content(DynAccessor):
                __slots__ = ()
                ContextMenuContent = DynAccessor(8)

            context_menu_content = _context_menu_content()

            class _context_menu_window(DynAccessor):
                __slots__ = ()
                ContextMenuWindow = DynAccessor(9)

            context_menu_window = _context_menu_window()

        context_menu_window = _context_menu_window()

        class _dialog_view(DynAccessor):
            __slots__ = ()

            class _dialog_window(DynAccessor):
                __slots__ = ()
                DialogWindow = DynAccessor(10)

            dialog_window = _dialog_window()

            class _simple_dialog_content(DynAccessor):
                __slots__ = ()
                SimpleDialogContent = DynAccessor(11)

            simple_dialog_content = _simple_dialog_content()

            class _components(DynAccessor):
                __slots__ = ()

                class _balance_contents(DynAccessor):
                    __slots__ = ()
                    CommonBalanceContent = DynAccessor(12)

                balance_contents = _balance_contents()

                class _dialog_prices_content(DynAccessor):
                    __slots__ = ()
                    DialogPricesContent = DynAccessor(13)

                dialog_prices_content = _dialog_prices_content()

                class _dialog_prices_tooltip(DynAccessor):
                    __slots__ = ()
                    DialogPricesTooltip = DynAccessor(14)

                dialog_prices_tooltip = _dialog_prices_tooltip()

            components = _components()

        dialog_view = _dialog_view()

        class _drop_down_menu_window(DynAccessor):
            __slots__ = ()

            class _drop_down_menu_content(DynAccessor):
                __slots__ = ()
                DropDownMenuContent = DynAccessor(15)

            drop_down_menu_content = _drop_down_menu_content()

            class _drop_down_menu_window(DynAccessor):
                __slots__ = ()
                DropDownMenuWindow = DynAccessor(16)

            drop_down_menu_window = _drop_down_menu_window()

        drop_down_menu_window = _drop_down_menu_window()

        class _pop_over_window(DynAccessor):
            __slots__ = ()

            class _pop_over_window(DynAccessor):
                __slots__ = ()
                PopOverWindow = DynAccessor(17)

            pop_over_window = _pop_over_window()

        pop_over_window = _pop_over_window()

        class _standard_window(DynAccessor):
            __slots__ = ()

            class _standard_window(DynAccessor):
                __slots__ = ()
                StandardWindow = DynAccessor(18)

            standard_window = _standard_window()

        standard_window = _standard_window()

        class _tooltip_window(DynAccessor):
            __slots__ = ()

            class _advanced_tooltip_content(DynAccessor):
                __slots__ = ()
                AdvandcedTooltipContent = DynAccessor(19)
                AdvandcedAnimatedTooltipContent = DynAccessor(20)

            advanced_tooltip_content = _advanced_tooltip_content()

            class _backport_tooltip_content(DynAccessor):
                __slots__ = ()
                BackportTooltipContent = DynAccessor(21)

            backport_tooltip_content = _backport_tooltip_content()

            class _loot_box_compensation_tooltip(DynAccessor):
                __slots__ = ()
                LootBoxCompensationTooltipContent = DynAccessor(22)
                CrewSkinsCompensationTooltipContent = DynAccessor(23)
                LootBoxVehicleCompensationTooltipContent = DynAccessor(24)

            loot_box_compensation_tooltip = _loot_box_compensation_tooltip()

            class _simple_tooltip_content(DynAccessor):
                __slots__ = ()
                SimpleTooltipContent = DynAccessor(25)
                SimpleTooltipHtmlContent = DynAccessor(26)

            simple_tooltip_content = _simple_tooltip_content()

            class _tooltip_window(DynAccessor):
                __slots__ = ()
                TooltipWindow = DynAccessor(27)

            tooltip_window = _tooltip_window()

        tooltip_window = _tooltip_window()

    common = _common()

    class _lobby(DynAccessor):
        __slots__ = ()

        class _battle_pass(DynAccessor):
            __slots__ = ()

            class _trophy_device_confirm_dialog(DynAccessor):
                __slots__ = ()
                TrophyDeviceConfirmDialogContent = DynAccessor(28)

            trophy_device_confirm_dialog = _trophy_device_confirm_dialog()
            BattlePassAwardsView = DynAccessor(86)
            BattlePassBuyView = DynAccessor(87)
            BattlePassEntryPointView = DynAccessor(88)
            BattlePassProgressionsView = DynAccessor(89)
            BattlePassVehicleAwardView = DynAccessor(90)
            BattlePassVotingConfirmView = DynAccessor(91)
            BattlePassVotingResultView = DynAccessor(92)

            class _sharedComponents(DynAccessor):
                __slots__ = ()
                Emblem = DynAccessor(93)
                Header = DynAccessor(94)

            sharedComponents = _sharedComponents()

            class _tooltips(DynAccessor):
                __slots__ = ()
                BattlePassChoseWinnerTooltipView = DynAccessor(95)
                BattlePassCompletedTooltipView = DynAccessor(96)
                BattlePassInProgressTooltipView = DynAccessor(97)
                BattlePassLockIconTooltipView = DynAccessor(98)
                BattlePassNotStartedTooltipView = DynAccessor(99)
                BattlePassPointsView = DynAccessor(100)
                BattlePassUndefinedStyleView = DynAccessor(101)
                BattlePassUndefinedTankmanView = DynAccessor(102)

                class _sharedComponents(DynAccessor):
                    __slots__ = ()
                    BlockCompleted = DynAccessor(103)
                    Chose = DynAccessor(104)
                    FinalLevel = DynAccessor(105)
                    PerBattlePointsTable = DynAccessor(106)
                    Point = DynAccessor(107)
                    VehicleInfo = DynAccessor(108)

                sharedComponents = _sharedComponents()
                VehiclePointsTooltipView = DynAccessor(109)

            tooltips = _tooltips()

        battle_pass = _battle_pass()

        class _blueprints(DynAccessor):
            __slots__ = ()

            class _fragments_balance_content(DynAccessor):
                __slots__ = ()
                FragmentsBalanceContent = DynAccessor(29)

            fragments_balance_content = _fragments_balance_content()

            class _blueprint_screen(DynAccessor):
                __slots__ = ()

                class _blueprint_screen(DynAccessor):
                    __slots__ = ()
                    BlueprintScreen = DynAccessor(30)

                blueprint_screen = _blueprint_screen()

            blueprint_screen = _blueprint_screen()

        blueprints = _blueprints()

        class _crew_books(DynAccessor):
            __slots__ = ()

            class _crew_books_buy_dialog(DynAccessor):
                __slots__ = ()
                CrewBooksBuyDialog = DynAccessor(31)

            crew_books_buy_dialog = _crew_books_buy_dialog()

            class _crew_books_dialog_content(DynAccessor):
                __slots__ = ()
                CrewBooksDialogContent = DynAccessor(32)

            crew_books_dialog_content = _crew_books_dialog_content()

            class _crew_books_lack_view(DynAccessor):
                __slots__ = ()
                CrewBooksLackView = DynAccessor(33)

            crew_books_lack_view = _crew_books_lack_view()

            class _crew_books_view(DynAccessor):
                __slots__ = ()
                CrewBooksView = DynAccessor(34)

            crew_books_view = _crew_books_view()

            class _crew_book_item_view(DynAccessor):
                __slots__ = ()
                CrewBookItemView = DynAccessor(35)

            crew_book_item_view = _crew_book_item_view()

        crew_books = _crew_books()

        class _marathon(DynAccessor):
            __slots__ = ()

            class _marathon_reward_view(DynAccessor):
                __slots__ = ()
                MarathonRewardView = DynAccessor(36)

            marathon_reward_view = _marathon_reward_view()

        marathon = _marathon()

        class _missions(DynAccessor):
            __slots__ = ()

            class _missions_tab_bar_view(DynAccessor):
                __slots__ = ()
                MissionsTabBarView = DynAccessor(37)

            missions_tab_bar_view = _missions_tab_bar_view()
            Daily = DynAccessor(117)
            DailyQuestsTooltip = DynAccessor(118)
            DailyQuestsWidget = DynAccessor(119)
            RerollTooltip = DynAccessor(120)
            RerollTooltipWithCountdown = DynAccessor(121)

        missions = _missions()

        class _nation_change(DynAccessor):
            __slots__ = ()

            class _nation_change_screen(DynAccessor):
                __slots__ = ()
                NationChangeScreen = DynAccessor(38)

            nation_change_screen = _nation_change_screen()

        nation_change = _nation_change()

        class _premacc(DynAccessor):
            __slots__ = ()

            class _daily_experience_view(DynAccessor):
                __slots__ = ()
                DailyExperiencePage = DynAccessor(39)

            daily_experience_view = _daily_experience_view()

            class _maps_blacklist_view(DynAccessor):
                __slots__ = ()
                MapsBlacklistView = DynAccessor(40)

            maps_blacklist_view = _maps_blacklist_view()

            class _piggybank(DynAccessor):
                __slots__ = ()
                Piggybank = DynAccessor(41)

            piggybank = _piggybank()

            class _prem_dashboard_view(DynAccessor):
                __slots__ = ()
                PremDashboardView = DynAccessor(42)

            prem_dashboard_view = _prem_dashboard_view()

            class _squad_bonus_tooltip_content(DynAccessor):
                __slots__ = ()
                SquadBonusTooltipContent = DynAccessor(43)

            squad_bonus_tooltip_content = _squad_bonus_tooltip_content()

            class _dashboard(DynAccessor):
                __slots__ = ()

                class _dashboard_premium_card(DynAccessor):
                    __slots__ = ()
                    DashboardPremiumCard = DynAccessor(44)

                dashboard_premium_card = _dashboard_premium_card()

                class _prem_dashboard_double_experience_card(DynAccessor):
                    __slots__ = ()
                    PremDashboardDoubleExperienceCard = DynAccessor(45)

                prem_dashboard_double_experience_card = _prem_dashboard_double_experience_card()

                class _prem_dashboard_header(DynAccessor):
                    __slots__ = ()
                    PremDashboardHeader = DynAccessor(46)

                prem_dashboard_header = _prem_dashboard_header()

                class _prem_dashboard_maps_blacklist_card(DynAccessor):
                    __slots__ = ()
                    PremDashboardMapsBlacklistCard = DynAccessor(47)

                prem_dashboard_maps_blacklist_card = _prem_dashboard_maps_blacklist_card()

                class _prem_dashboard_piggy_bank_card(DynAccessor):
                    __slots__ = ()
                    PremDashboardPiggyBankCard = DynAccessor(48)

                prem_dashboard_piggy_bank_card = _prem_dashboard_piggy_bank_card()

                class _prem_dashboard_quests_card(DynAccessor):
                    __slots__ = ()
                    PremDashboardQuestsCard = DynAccessor(49)

                prem_dashboard_quests_card = _prem_dashboard_quests_card()

            dashboard = _dashboard()

            class _maps_blacklist(DynAccessor):
                __slots__ = ()

                class _maps_blacklist_confirm_dialog(DynAccessor):
                    __slots__ = ()
                    MapsBlacklistConfirmDialogContent = DynAccessor(50)

                maps_blacklist_confirm_dialog = _maps_blacklist_confirm_dialog()

                class _maps_blacklist_tooltips(DynAccessor):
                    __slots__ = ()
                    MapsBlacklistInfoTooltipContent = DynAccessor(51)

                maps_blacklist_tooltips = _maps_blacklist_tooltips()

            maps_blacklist = _maps_blacklist()

        premacc = _premacc()

        class _progressive_reward(DynAccessor):
            __slots__ = ()

            class _progressive_reward_award(DynAccessor):
                __slots__ = ()
                ProgressiveRewardAward = DynAccessor(52)

            progressive_reward_award = _progressive_reward_award()

            class _progressive_reward_view(DynAccessor):
                __slots__ = ()
                ProgressiveRewardView = DynAccessor(53)

            progressive_reward_view = _progressive_reward_view()

        progressive_reward = _progressive_reward()

        class _ranked(DynAccessor):
            __slots__ = ()

            class _ranked_year_award(DynAccessor):
                __slots__ = ()
                RankedYearAward = DynAccessor(54)

            ranked_year_award = _ranked_year_award()

        ranked = _ranked()

        class _reward_window(DynAccessor):
            __slots__ = ()

            class _piggy_bank_reward_window_content(DynAccessor):
                __slots__ = ()
                PiggyBankRewardWindowContent = DynAccessor(55)

            piggy_bank_reward_window_content = _piggy_bank_reward_window_content()

            class _reward_window_content(DynAccessor):
                __slots__ = ()
                RewardWindowContent = DynAccessor(56)

            reward_window_content = _reward_window_content()

            class _twitch_reward_window_content(DynAccessor):
                __slots__ = ()
                TwitchRewardWindowContent = DynAccessor(57)

            twitch_reward_window_content = _twitch_reward_window_content()

        reward_window = _reward_window()

        class _seniority_awards(DynAccessor):
            __slots__ = ()

            class _seniority_awards_multi_open_view(DynAccessor):
                __slots__ = ()
                SeniorityAwardsMultiOpenView = DynAccessor(58)

            seniority_awards_multi_open_view = _seniority_awards_multi_open_view()

            class _seniority_reward_view(DynAccessor):
                __slots__ = ()
                SeniorityRewardView = DynAccessor(59)

            seniority_reward_view = _seniority_reward_view()

            class _seniority_reward_award(DynAccessor):
                __slots__ = ()

                class _seniority_reward_award_view(DynAccessor):
                    __slots__ = ()
                    SeniorityRewardAwardView = DynAccessor(60)

                seniority_reward_award_view = _seniority_reward_award_view()

            seniority_reward_award = _seniority_reward_award()

        seniority_awards = _seniority_awards()

        class _shop(DynAccessor):
            __slots__ = ()

            class _buy_vehicle_view(DynAccessor):
                __slots__ = ()
                BuyVehicleView = DynAccessor(61)

            buy_vehicle_view = _buy_vehicle_view()

        shop = _shop()

        class _ten_years_countdown(DynAccessor):
            __slots__ = ()

            class _ten_years_countdown_award(DynAccessor):
                __slots__ = ()
                TenYearsCountdownAward = DynAccessor(62)

            ten_years_countdown_award = _ten_years_countdown_award()
            TenYearsCountdownEntryPoint = DynAccessor(123)
            TenYearsOnboardingView = DynAccessor(124)

        ten_years_countdown = _ten_years_countdown()

        class _tooltips(DynAccessor):
            __slots__ = ()

            class _clans(DynAccessor):
                __slots__ = ()
                ClanShortInfoTooltipContent = DynAccessor(63)

            clans = _clans()

        tooltips = _tooltips()

        class _video(DynAccessor):
            __slots__ = ()

            class _video_view(DynAccessor):
                __slots__ = ()
                VideoView = DynAccessor(64)

            video_view = _video_view()

        video = _video()

        class _customization(DynAccessor):
            __slots__ = ()
            CustomizationCart = DynAccessor(110)

        customization = _customization()

        class _demountkit(DynAccessor):
            __slots__ = ()
            CommonWindow = DynAccessor(111)
            DemountWindow = DynAccessor(112)

        demountkit = _demountkit()

        class _epic(DynAccessor):
            __slots__ = ()
            PostbattleQuestProgress = DynAccessor(113)

            class _tooltips(DynAccessor):
                __slots__ = ()
                QuestProgressTooltip = DynAccessor(114)

            tooltips = _tooltips()

        epic = _epic()

        class _instructions(DynAccessor):
            __slots__ = ()
            BuyWindow = DynAccessor(115)
            SellWindow = DynAccessor(116)

        instructions = _instructions()

        class _techtree(DynAccessor):
            __slots__ = ()
            TechTreeIntro = DynAccessor(122)

        techtree = _techtree()

    lobby = _lobby()

    class _test_check_box_view(DynAccessor):
        __slots__ = ()
        TestCheckBoxView = DynAccessor(65)

    test_check_box_view = _test_check_box_view()

    class _test_text_button_view(DynAccessor):
        __slots__ = ()
        TestTextButtonView = DynAccessor(66)

    test_text_button_view = _test_text_button_view()

    class _windows_layout_view(DynAccessor):
        __slots__ = ()
        WindowsLayountView = DynAccessor(67)

    windows_layout_view = _windows_layout_view()

    class _demo_view(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _demo_window_content(DynAccessor):
                __slots__ = ()
                DemoWindowContent = DynAccessor(68)
                ImageProps = DynAccessor(69)

            demo_window_content = _demo_window_content()

            class _demo_window_details_panel(DynAccessor):
                __slots__ = ()
                DemoWindowDetailsPanel = DynAccessor(70)

            demo_window_details_panel = _demo_window_details_panel()

            class _demo_window_image_panel(DynAccessor):
                __slots__ = ()
                DemoWindowImagePanel = DynAccessor(71)

            demo_window_image_panel = _demo_window_image_panel()

            class _image_preview_window_content(DynAccessor):
                __slots__ = ()
                ImagePreviewWindowContent = DynAccessor(72)

            image_preview_window_content = _image_preview_window_content()

        views = _views()

    demo_view = _demo_view()

    class _examples(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _test_dialogs_view(DynAccessor):
                __slots__ = ()
                TestDialogsView = DynAccessor(73)

            test_dialogs_view = _test_dialogs_view()

            class _test_expr_functions_view(DynAccessor):
                __slots__ = ()
                TestExprFunctionsView = DynAccessor(74)

            test_expr_functions_view = _test_expr_functions_view()

            class _test_sub_view(DynAccessor):
                __slots__ = ()
                TestSubView = DynAccessor(75)

            test_sub_view = _test_sub_view()

            class _test_view(DynAccessor):
                __slots__ = ()
                TestView = DynAccessor(76)

            test_view = _test_view()

            class _unbound_example(DynAccessor):
                __slots__ = ()
                UnboundExample = DynAccessor(77)

            unbound_example = _unbound_example()

        views = _views()

    examples = _examples()

    class _list_examples(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _list_examples_empty_render_window_content(DynAccessor):
                __slots__ = ()
                ListExamplesEmptyRenderWindowContent = DynAccessor(78)

            list_examples_empty_render_window_content = _list_examples_empty_render_window_content()

            class _list_examples_window_content(DynAccessor):
                __slots__ = ()
                ListExamplesWindowContent = DynAccessor(79)

            list_examples_window_content = _list_examples_window_content()

        views = _views()

    list_examples = _list_examples()

    class _rotation_pivot_view(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _rotation_pivot_view(DynAccessor):
                __slots__ = ()
                RotationAndPivotTestView = DynAccessor(80)

            rotation_pivot_view = _rotation_pivot_view()

        views = _views()

    rotation_pivot_view = _rotation_pivot_view()

    class _rotation_view(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _rotation_view(DynAccessor):
                __slots__ = ()
                RotationTestView = DynAccessor(81)

            rotation_view = _rotation_view()

        views = _views()

    rotation_view = _rotation_view()

    class _scale_view(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _scale_view(DynAccessor):
                __slots__ = ()
                ScaleTestView = DynAccessor(82)

            scale_view = _scale_view()

        views = _views()

    scale_view = _scale_view()

    class _test_uikit_buttons_view(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _test_uikit_buttons_view(DynAccessor):
                __slots__ = ()
                TestUikitButtonsView = DynAccessor(83)

            test_uikit_buttons_view = _test_uikit_buttons_view()

        views = _views()

    test_uikit_buttons_view = _test_uikit_buttons_view()

    class _test_uikit_view(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _test_uikit_view(DynAccessor):
                __slots__ = ()
                TestUikitView = DynAccessor(84)

            test_uikit_view = _test_uikit_view()

        views = _views()

    test_uikit_view = _test_uikit_view()

    class _wtypes_view(DynAccessor):
        __slots__ = ()

        class _views(DynAccessor):
            __slots__ = ()

            class _wtypes_demo_window_content(DynAccessor):
                __slots__ = ()
                WtypesDemoWindowContent = DynAccessor(85)

            wtypes_demo_window_content = _wtypes_demo_window_content()

        views = _views()

    wtypes_view = _wtypes_view()
    Anchor = DynAccessor(125)
    ComplexListView = DynAccessor(126)
    ComponentsDemo = DynAccessor(127)
    DataTrackerDemo = DynAccessor(128)
    DemoContextMenu = DynAccessor(129)
    Easings = DynAccessor(130)
    GFDemoPopover = DynAccessor(131)
    GFDemoRichTooltipWindow = DynAccessor(132)
    GFDemoWindow = DynAccessor(133)
    GFInjectView = DynAccessor(134)
    GFSimpleTooltipWindow = DynAccessor(135)
    LocaleDemo = DynAccessor(136)
    MixBlendModeAnimation = DynAccessor(137)
    PropsSupportDemo = DynAccessor(138)
    StructuralDataBindDemo = DynAccessor(139)
    TextFormat = DynAccessor(140)
    VideoSupportView = DynAccessor(141)

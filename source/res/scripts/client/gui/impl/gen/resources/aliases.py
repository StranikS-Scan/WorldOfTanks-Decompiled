# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/aliases.py
from gui.impl.gen_utils import DynAccessor

class battle_modifiers(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Modifiers = DynAccessor(130446)

    shared = _shared(130447)


class battle_pass(DynAccessor):
    __slots__ = ()
    ChapterChoice = DynAccessor(130449)
    Progression = DynAccessor(130450)
    PostProgression = DynAccessor(130451)
    BuyPass = DynAccessor(130452)
    BuyPassRewards = DynAccessor(130453)
    BuyLevels = DynAccessor(130454)
    BuyLevelsRewards = DynAccessor(130455)
    HolidayFinal = DynAccessor(130456)
    FinalRewardPreview = DynAccessor(130457)
    TankmenScreen = DynAccessor(130458)


class battle_result(DynAccessor):
    __slots__ = ()
    none = DynAccessor(130460)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        User = DynAccessor(130461)
        Vehicle = DynAccessor(130462)

    contextMenu = _contextMenu(130463)


class battle_results(DynAccessor):
    __slots__ = ()

    class _progression(DynAccessor):
        __slots__ = ()
        DailyMissions = DynAccessor(130465)
        WeeklyMissions = DynAccessor(130466)
        PersonalMissions = DynAccessor(130467)
        BattlePass = DynAccessor(130468)
        Prestige = DynAccessor(130469)
        BattleMatters = DynAccessor(130470)
        ModuleVehicleUnlocks = DynAccessor(130471)
        CommonQuests = DynAccessor(130472)
        Challenges = DynAccessor(130473)

    progression = _progression(130474)


class common(DynAccessor):
    __slots__ = ()
    none = DynAccessor(130476)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(130477)

    contextMenu = _contextMenu(130478)

    class _tooltip(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(130479)
        Wulf = DynAccessor(130480)
        Param = DynAccessor(130481)

    tooltip = _tooltip(130482)

    class _popOver(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(130483)

    popOver = _popOver(130484)

    class _shared(DynAccessor):
        __slots__ = ()
        DynamicEconomics = DynAccessor(130485)

    shared = _shared(130486)


class hangar(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        VehiclesInfo = DynAccessor(130488)
        VehiclesStatistics = DynAccessor(130489)
        Consumables = DynAccessor(130490)
        Equipments = DynAccessor(130491)
        Instructions = DynAccessor(130492)
        Shells = DynAccessor(130493)
        Loadout = DynAccessor(130494)
        Crew = DynAccessor(130495)
        VehicleParams = DynAccessor(130496)
        ETEVehicleParams = DynAccessor(130497)
        CurrentVehicle = DynAccessor(130498)
        VehiclesInventory = DynAccessor(130499)
        MainMenu = DynAccessor(130500)
        VehicleMenu = DynAccessor(130501)
        LootboxEntryPoint = DynAccessor(130502)
        VehicleFilters = DynAccessor(130503)
        VehiclePlaylists = DynAccessor(130504)
        Teaser = DynAccessor(130505)
        OptionalDevicesAssistant = DynAccessor(130506)
        SpaceInteraction = DynAccessor(130507)
        HeroTank = DynAccessor(130508)
        UserMissions = DynAccessor(130509)
        ModeState = DynAccessor(130510)
        EasyTankEquip = DynAccessor(130511)
        PetEvent = DynAccessor(130512)
        PetObjectTooltip = DynAccessor(130513)
        Settings = DynAccessor(130514)
        KeyBindings = DynAccessor(130515)
        ManageableVehiclePlaylists = DynAccessor(130516)

    shared = _shared(130517)


class lobby_footer(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        Platoon = DynAccessor(130519)
        ContactsList = DynAccessor(130520)
        SessionStats = DynAccessor(130521)
        VehicleCompare = DynAccessor(130522)
        NotificationsCenter = DynAccessor(130523)
        Chats = DynAccessor(130524)
        ReferralProgram = DynAccessor(130525)
        ServerInfo = DynAccessor(130526)

    default = _default(130527)


class lobby_header(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        FightStart = DynAccessor(130529)
        NavigationBar = DynAccessor(130530)
        Prebattle = DynAccessor(130531)
        Wallet = DynAccessor(130532)
        AccountDashboard = DynAccessor(130533)
        HeaderState = DynAccessor(130534)
        UserAccount = DynAccessor(130535)
        ReservesEntryPoint = DynAccessor(130536)
        PremShop = DynAccessor(130537)
        CurrentVehicle = DynAccessor(130538)

    default = _default(130539)


class select_vehicle(DynAccessor):
    __slots__ = ()

    class _select_vehicle(DynAccessor):
        __slots__ = ()
        VehiclesInfo = DynAccessor(130541)
        VehiclesInventory = DynAccessor(130542)
        VehiclesStatistics = DynAccessor(130543)
        VehicleFilters = DynAccessor(130544)
        VehiclePlaylists = DynAccessor(130545)

    select_vehicle = _select_vehicle(130546)


class states(DynAccessor):
    __slots__ = ()

    class _Hangar(DynAccessor):
        __slots__ = ()

        class _Loadout(DynAccessor):
            __slots__ = ()
            Equipment = DynAccessor(130548)
            Instructions = DynAccessor(130549)
            Shells = DynAccessor(130550)
            Consumables = DynAccessor(130551)

        Loadout = _Loadout(130552)
        Vehicles = DynAccessor(130553)

    Hangar = _Hangar(130554)


class user_missions(DynAccessor):
    __slots__ = ()

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        BattlePass = DynAccessor(130556)
        Events = DynAccessor(130557)
        Quests = DynAccessor(130558)
        EventMainInfoTip = DynAccessor(130559)

    hangarWidget = _hangarWidget(130560)

    class _hub(DynAccessor):
        __slots__ = ()

        class _basicMissions(DynAccessor):
            __slots__ = ()
            MainView = DynAccessor(130561)

            class _DailyMissionsSection(DynAccessor):
                __slots__ = ()
                MainView = DynAccessor(130562)
                DailyBlock = DynAccessor(130563)
                PremiumBlock = DynAccessor(130564)
                RewardProgressBlock = DynAccessor(130565)

            DailyMissionsSection = _DailyMissionsSection(130566)
            WeeklyMissions = DynAccessor(130567)
            PersonalMissions = DynAccessor(130568)

        basicMissions = _basicMissions(130569)

        class _challengeMissions(DynAccessor):
            __slots__ = ()
            MainView = DynAccessor(130570)

        challengeMissions = _challengeMissions(130571)

    hub = _hub(130572)


class vehicle_hub(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        VehicleParams = DynAccessor(130574)
        Wallet = DynAccessor(130575)
        VehicleInfo = DynAccessor(130576)
        ManageableVehiclePlaylists = DynAccessor(130577)
        VehiclesInfo = DynAccessor(130578)
        VehiclesStatistics = DynAccessor(130579)
        VehicleFilters = DynAccessor(130580)
        VehiclePlaylists = DynAccessor(130581)
        VehiclesInventory = DynAccessor(130582)

    default = _default(130583)


class vehicle_menu(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        Customization = DynAccessor(130585)
        CrewAutoReturn = DynAccessor(130586)
        CrewRetrain = DynAccessor(130587)
        QuickTraining = DynAccessor(130588)
        CrewOut = DynAccessor(130589)
        CrewBack = DynAccessor(130590)
        EasyEquip = DynAccessor(130591)
        ArmorInspector = DynAccessor(130592)
        FieldModification = DynAccessor(130593)
        NationChange = DynAccessor(130594)
        Research = DynAccessor(130595)
        AboutVehicle = DynAccessor(130596)
        Compare = DynAccessor(130597)
        Repairs = DynAccessor(130598)
        VehSkillTree = DynAccessor(130599)
        ProBoost = DynAccessor(130600)

    default = _default(130601)


class white_tiger(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Carousel = DynAccessor(130603)
        ConsumablesPanel = DynAccessor(130604)
        Progression = DynAccessor(130605)
        Crewman = DynAccessor(130606)
        VehicleStats = DynAccessor(130607)
        ProgressionContent = DynAccessor(130608)
        ProgressionQuests = DynAccessor(130609)
        LootboxEntryPoint = DynAccessor(130610)

    shared = _shared(130611)


class battle_royale(DynAccessor):
    __slots__ = ()
    BattleSelector = DynAccessor(130613)
    UserMissions = DynAccessor(130614)
    VehiclesInventory = DynAccessor(130615)
    VehiclesFilter = DynAccessor(130616)
    AlertMessage = DynAccessor(130617)
    Header = DynAccessor(130618)
    LoadoutPanelContainer = DynAccessor(130619)
    Events = DynAccessor(130620)

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        Progression = DynAccessor(130621)
        EventShop = DynAccessor(130622)

    hangarWidget = _hangarWidget(130623)

    class _loadoutPanelContainer(DynAccessor):
        __slots__ = ()
        Loadout = DynAccessor(130624)
        Commander = DynAccessor(130625)

    loadoutPanelContainer = _loadoutPanelContainer(130626)


class comp7(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(130628)
        Schedule = DynAccessor(130629)
        SeasonModifier = DynAccessor(130630)
        RoleSkillSlot = DynAccessor(130631)
        UserMissions = DynAccessor(130632)
        EntryPoint = DynAccessor(130633)
        WeeklyQuestsWidget = DynAccessor(130634)
        BattleResultsWeeklyQuests = DynAccessor(130635)
        BattleResultsCustomizationQuests = DynAccessor(130636)

    shared = _shared(130637)


class comp7_light(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(130639)
        SeasonModifier = DynAccessor(130640)
        RoleSkillSlot = DynAccessor(130641)
        UserMissions = DynAccessor(130642)
        EntryPoint = DynAccessor(130643)
        Quests = DynAccessor(130644)
        BattleResultsProgressionQuests = DynAccessor(130645)

    shared = _shared(130646)


class frontline(DynAccessor):
    __slots__ = ()

    class _loadout(DynAccessor):
        __slots__ = ()
        BattleAbilities = DynAccessor(130648)

    loadout = _loadout(130649)

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(130650)
        AlertMessage = DynAccessor(130651)

    shared = _shared(130652)


class fun_random(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(130654)
        ProgressionEntryPoint = DynAccessor(130655)
        ProgressionQuests = DynAccessor(130656)

    shared = _shared(130657)


class last_stand(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Carousel = DynAccessor(130659)
        Difficulty = DynAccessor(130660)
        MoneyBalance = DynAccessor(130661)
        TeamStats = DynAccessor(130662)
        Meta = DynAccessor(130663)
        Keys = DynAccessor(130664)
        Quests = DynAccessor(130665)
        RewardPath = DynAccessor(130666)
        Shop = DynAccessor(130667)
        Gsw = DynAccessor(130668)
        Switcher = DynAccessor(130669)
        PresetsSwitcher = DynAccessor(130670)
        VehiclesDaily = DynAccessor(130671)
        BundleCard = DynAccessor(130672)
        DailyCard = DynAccessor(130673)
        Parallax = DynAccessor(130674)

    shared = _shared(130675)


class Aliases(DynAccessor):
    __slots__ = ()
    battle_modifiers = battle_modifiers()
    battle_pass = battle_pass()
    battle_result = battle_result()
    battle_results = battle_results()
    common = common()
    hangar = hangar()
    lobby_footer = lobby_footer()
    lobby_header = lobby_header()
    select_vehicle = select_vehicle()
    states = states()
    user_missions = user_missions()
    vehicle_hub = vehicle_hub()
    vehicle_menu = vehicle_menu()
    white_tiger = white_tiger()
    battle_royale = battle_royale()
    comp7 = comp7()
    comp7_light = comp7_light()
    frontline = frontline()
    fun_random = fun_random()
    last_stand = last_stand()

# Embedded file name: scripts/client/gui/Scaleform/locale/FORTIFICATIONS.py
from debug_utils import LOG_WARNING

class FORTIFICATIONS(object):
    TIME_TIMEVALUE = '#fortifications:Time/timeValue'
    BUILDINGDIRECTION_TOOLTIP = '#fortifications:BuildingDirection/tooltip'
    FORTINTELLIGENCE_HEADERBLOCK = '#fortifications:FortIntelligence/headerBlock'
    FORTINTELLIGENCE_TOPBLOCK = '#fortifications:FortIntelligence/topBlock'
    FORTINTELLIGENCE_MIDDLEBLOCK = '#fortifications:FortIntelligence/middleBlock'
    FORTINTELLIGENCE_BOTTOMBLOCK = '#fortifications:FortIntelligence/bottomBlock'
    TIME_TIMEVALUE_DAYS = TIME_TIMEVALUE + '/days'
    TIME_TIMEVALUE_HOURS = TIME_TIMEVALUE + '/hours'
    TIME_TIMEVALUE_MIN = TIME_TIMEVALUE + '/min'
    TIME_TIMEVALUE_LESSMIN = TIME_TIMEVALUE + '/lessMin'
    GENERAL_DIRECTION = '#fortifications:General/direction'
    GENERAL_DIRECTIONNAME1 = '#fortifications:General/directionName1'
    GENERAL_DIRECTIONNAME2 = '#fortifications:General/directionName2'
    GENERAL_DIRECTIONNAME3 = '#fortifications:General/directionName3'
    GENERAL_DIRECTIONNAME4 = '#fortifications:General/directionName4'
    GENERAL_ORDERTYPE_BATTLEPAYMENTS = '#fortifications:General/orderType/battlePayments'
    GENERAL_ORDERTYPE_REQUISITION = '#fortifications:General/orderType/requisition'
    GENERAL_ORDERTYPE_EVACUATION = '#fortifications:General/orderType/evacuation'
    GENERAL_ORDERTYPE_HEAVYTRUCKS = '#fortifications:General/orderType/heavyTrucks'
    GENERAL_ORDERTYPE_MILITARYMANEUVERS = '#fortifications:General/orderType/militaryManeuvers'
    GENERAL_ORDERTYPE_ADDITIONALBRIEFING = '#fortifications:General/orderType/additionalBriefing'
    GENERAL_ORDERTYPE_TACTICALTRAINING = '#fortifications:General/orderType/tacticalTraining'
    FORTWELCOMEVIEW_CREATEFORTBTN = '#fortifications:FortWelcomeView/createFortBtn'
    FORTWELCOMEVIEW_TITLE = '#fortifications:FortWelcomeView/title'
    FORTWELCOMEVIEW_BUILDINGANDUPGRADING_TITLE = '#fortifications:FortWelcomeView/buildingAndUpgrading/title'
    FORTWELCOMEVIEW_BUILDINGANDUPGRADING_BODY = '#fortifications:FortWelcomeView/buildingAndUpgrading/body'
    FORTWELCOMEVIEW_BONUSES_TITLE = '#fortifications:FortWelcomeView/bonuses/title'
    FORTWELCOMEVIEW_BONUSES_BODY = '#fortifications:FortWelcomeView/bonuses/body'
    FORTWELCOMEVIEW_WARFORRESOURCES_TITLE = '#fortifications:FortWelcomeView/warForResources/title'
    FORTWELCOMEVIEW_WARFORRESOURCES_BODY = '#fortifications:FortWelcomeView/warForResources/body'
    FORTWELCOMEVIEW_HYPERLINK_MORE = '#fortifications:FortWelcomeView/hyperlink/more'
    FORTWELCOMEVIEW_WARNING = '#fortifications:FortWelcomeView/warning'
    FORTWELCOMEVIEW_REQUIREMENTCOMMANDER = '#fortifications:FortWelcomeView/requirementCommander'
    FORTWELCOMEVIEW_REQUIREMENTCLAN = '#fortifications:FortWelcomeView/requirementClan'
    FORTWELCOMEVIEW_CLANSEARCH = '#fortifications:FortWelcomeView/clanSearch'
    FORTWELCOMEVIEW_CLANCREATE = '#fortifications:FortWelcomeView/clanCreate'
    FORTWELCOMECOMMANDERVIEW_TITLE = '#fortifications:FortWelcomeCommanderView/title'
    FORTWELCOMECOMMANDERVIEW_BUTTON_LABEL = '#fortifications:FortWelcomeCommanderView/button/label'
    FORTWELCOMECOMMANDERVIEW_OPTION1_TITLE = '#fortifications:FortWelcomeCommanderView/option1/title'
    FORTWELCOMECOMMANDERVIEW_OPTION1_DESCR = '#fortifications:FortWelcomeCommanderView/option1/descr'
    FORTWELCOMECOMMANDERVIEW_OPTION2_TITLE = '#fortifications:FortWelcomeCommanderView/option2/title'
    FORTWELCOMECOMMANDERVIEW_OPTION2_DESCR = '#fortifications:FortWelcomeCommanderView/option2/descr'
    FORTWELCOMECOMMANDERVIEW_OPTION3_TITLE = '#fortifications:FortWelcomeCommanderView/option3/title'
    FORTWELCOMECOMMANDERVIEW_OPTION3_DESCR = '#fortifications:FortWelcomeCommanderView/option3/descr'
    FORTMAINVIEW_COMMON_TOTALDEPOTQUANTITYTEXT = '#fortifications:FortMainView/common/totalDepotQuantityText'
    FORTMAINVIEW_COMMON_TITLE = '#fortifications:FortMainView/common/title'
    FORTMAINVIEW_DIRECTIONS_TITLE = '#fortifications:FortMainView/directions/title'
    FORTMAINVIEW_DIRECTIONS_SELECTINGSTATUS = '#fortifications:FortMainView/directions/selectingStatus'
    FORTMAINVIEW_TRANSPORTING_TITLE = '#fortifications:FortMainView/transporting/title'
    FORTMAINVIEW_TRANSPORTING_EXPORTINGSTATUS = '#fortifications:FortMainView/transporting/exportingStatus'
    FORTMAINVIEW_TRANSPORTING_IMPORTINGSTATUS = '#fortifications:FortMainView/transporting/importingStatus'
    FORTMAINVIEW_TRANSPORTING_TUTORIALDESCR = '#fortifications:FortMainView/transporting/tutorialDescr'
    FORTMAINVIEW_TRANSPORTING_TUTORIALDESCRDISABLED = '#fortifications:FortMainView/transporting/tutorialDescrDisabled'
    FORTMAINVIEW_SORTIEBUTTON_TITLE = '#fortifications:FortMainView/sortieButton/title'
    FORTMAINVIEW_INTELLIGENCEBUTTON_TITLE = '#fortifications:FortMainView/intelligenceButton/title'
    FORTMAINVIEW_HEADER_LEVELSLBL = '#fortifications:FortMainView/header/levelsLbl'
    FORTMAINVIEW_LEAVE_BUTTON_LABEL = '#fortifications:FortMainView/leave/button/label'
    FORTDIRECTIONSWINDOW_TITLE = '#fortifications:FortDirectionsWindow/title'
    FORTDIRECTIONSWINDOW_BUTTON_NEWDIRECTION = '#fortifications:FortDirectionsWindow/button/newDirection'
    FORTDIRECTIONSWINDOW_BUTTON_NEWDIRECTION_TOOLTIP_ENABLED = '#fortifications:FortDirectionsWindow/button/newDirection/tooltip/enabled'
    FORTDIRECTIONSWINDOW_BUTTON_NEWDIRECTION_TOOLTIP_ENABLED_DESCR = '#fortifications:FortDirectionsWindow/button/newDirection/tooltip/enabled/descr'
    FORTDIRECTIONSWINDOW_BUTTON_NEWDIRECTION_TOOLTIP_DISABLED = '#fortifications:FortDirectionsWindow/button/newDirection/tooltip/disabled'
    FORTDIRECTIONSWINDOW_BUTTON_NEWDIRECTION_TOOLTIP_DISABLED_DESCR = '#fortifications:FortDirectionsWindow/button/newDirection/tooltip/disabled/descr'
    FORTDIRECTIONSWINDOW_BUTTON_CLOSEDIRECTION = '#fortifications:FortDirectionsWindow/button/closeDirection'
    FORTDIRECTIONSWINDOW_DESCR_REQUIREMENTS = '#fortifications:FortDirectionsWindow/descr/requirements'
    FORTDIRECTIONSWINDOW_DESCR_COMPLETED = '#fortifications:FortDirectionsWindow/descr/completed'
    FORTDIRECTIONSWINDOW_LABEL_OPENEDDIRECTIONS = '#fortifications:FortDirectionsWindow/label/openedDirections'
    FORTDIRECTIONSWINDOW_LABEL_NOTOPENED = '#fortifications:FortDirectionsWindow/label/notOpened'
    FORTDIRECTIONSWINDOW_LABEL_NOBUILDINGS = '#fortifications:FortDirectionsWindow/label/noBuildings'
    BUILDINGDIRECTION_TOOLTIP_HEADER = BUILDINGDIRECTION_TOOLTIP + '/header'
    BUILDINGDIRECTION_TOOLTIP_BODY = BUILDINGDIRECTION_TOOLTIP + '/body'
    BUILDINGDIRECTION_LABEL1 = '#fortifications:BuildingDirection/label1'
    BUILDINGDIRECTION_LABEL2 = '#fortifications:BuildingDirection/label2'
    BUILDINGDIRECTION_LABEL3 = '#fortifications:BuildingDirection/label3'
    BUILDINGDIRECTION_LABEL4 = '#fortifications:BuildingDirection/label4'
    FORTCLANLISTWINDOW_TITLE = '#fortifications:FortClanListWindow/title'
    FORTCLANSTATISTICSWINDOW_TITLE = '#fortifications:FortClanStatisticsWindow/title'
    FORTCLANSTATISTICSWINDOW_SORTIE_BATTLESHEADER = '#fortifications:FortClanStatisticsWindow/sortie/battlesHeader'
    CLANSTATS_PARAMS_SORTIE_BATTLESCOUNT_LABEL = '#fortifications:clanStats/params/sortie/battlesCount/label'
    CLANSTATS_PARAMS_SORTIE_BATTLESCOUNT_TOOLTIP_HEADER = '#fortifications:clanStats/params/sortie/battlesCount/tooltip/header'
    CLANSTATS_PARAMS_SORTIE_BATTLESCOUNT_TOOLTIP_BODY = '#fortifications:clanStats/params/sortie/battlesCount/tooltip/body'
    CLANSTATS_PARAMS_SORTIE_WINS_LABEL = '#fortifications:clanStats/params/sortie/wins/label'
    CLANSTATS_PARAMS_SORTIE_WINS_TOOLTIP_HEADER = '#fortifications:clanStats/params/sortie/wins/tooltip/header'
    CLANSTATS_PARAMS_SORTIE_WINS_TOOLTIP_BODY = '#fortifications:clanStats/params/sortie/wins/tooltip/body'
    CLANSTATS_PARAMS_SORTIE_AVGDEFRES_LABEL = '#fortifications:clanStats/params/sortie/avgDefres/label'
    CLANSTATS_PARAMS_SORTIE_AVGDEFRES_TOOLTIP_HEADER = '#fortifications:clanStats/params/sortie/avgDefres/tooltip/header'
    CLANSTATS_PARAMS_SORTIE_AVGDEFRES_TOOLTIP_BODY = '#fortifications:clanStats/params/sortie/avgDefres/tooltip/body'
    CLANSTATS_PARAMS_SORTIE_BATTLES_MIDDLEBATTLESCOUNT_LABEL = '#fortifications:clanStats/params/sortie/battles/middleBattlesCount/label'
    CLANSTATS_PARAMS_SORTIE_BATTLES_CHAMPIONBATTLESCOUNT_LABEL = '#fortifications:clanStats/params/sortie/battles/championBattlesCount/label'
    CLANSTATS_PARAMS_SORTIE_BATTLES_ABSOLUTEBATTLESCOUNT_LABEL = '#fortifications:clanStats/params/sortie/battles/absoluteBattlesCount/label'
    CLANSTATS_PARAMS_SORTIE_DEFRES_LOOTINSORTIES_LABEL = '#fortifications:clanStats/params/sortie/defres/lootInSorties/label'
    FORTTRANSPORTCONFIRMATIONWINDOW_TITLE = '#fortifications:FortTransportConfirmationWindow/title'
    FORTTRANSPORTCONFIRMATIONWINDOW_MAXTRANSPORTINGSIZELABEL = '#fortifications:FortTransportConfirmationWindow/maxTransportingSizeLabel'
    FORTTRANSPORTCONFIRMATIONWINDOW_TRANSPORTINGTEXT = '#fortifications:FortTransportConfirmationWindow/transportingText'
    FORTTRANSPORTCONFIRMATIONWINDOW_TRANSPORTINGFOOTERTEXT = '#fortifications:FortTransportConfirmationWindow/transportingFooterText'
    FORTTRANSPORTCONFIRMATIONWINDOW_TRANSPORTBUTTON = '#fortifications:FortTransportConfirmationWindow/transportButton'
    FORTTRANSPORTCONFIRMATIONWINDOW_CANCELBUTTON = '#fortifications:FortTransportConfirmationWindow/cancelButton'
    BUILDINGS_BUILDINGTOOLTIP_STRENGTH = '#fortifications:Buildings/buildingTooltip/strength'
    BUILDINGS_BUILDINGTOOLTIP_STORE = '#fortifications:Buildings/buildingTooltip/store'
    BUILDINGS_BUILDINGTOOLTIP_ORDER = '#fortifications:Buildings/buildingTooltip/order'
    BUILDINGS_TROWELLABEL = '#fortifications:Buildings/trowelLabel'
    BUILDINGS_BUILDINGNAME_BASE_BUILDING = '#fortifications:Buildings/buildingName/base_building'
    BUILDINGS_BUILDINGNAME_WARSCHOOL_BUILDING = '#fortifications:Buildings/buildingName/warSchool_building'
    BUILDINGS_BUILDINGNAME_TROPHY_BUILDING = '#fortifications:Buildings/buildingName/trophy_building'
    BUILDINGS_BUILDINGNAME_TRAINING_BUILDING = '#fortifications:Buildings/buildingName/training_building'
    BUILDINGS_BUILDINGNAME_TANKODROM_BUILDING = '#fortifications:Buildings/buildingName/tankodrom_building'
    BUILDINGS_BUILDINGNAME_INTENDANCY_BUILDING = '#fortifications:Buildings/buildingName/intendancy_building'
    BUILDINGS_BUILDINGNAME_FINANCE_BUILDING = '#fortifications:Buildings/buildingName/finance_building'
    BUILDINGS_BUILDINGNAME_CAR_BUILDING = '#fortifications:Buildings/buildingName/car_building'
    CONGRATULATIONWINDOW_BUTTONLBL = '#fortifications:CongratulationWindow/buttonLbl'
    CONGRATULATIONWINDOW_TITLELBL = '#fortifications:CongratulationWindow/titleLbl'
    CONGRATULATIONWINDOW_TEXTTITLE = '#fortifications:CongratulationWindow/textTitle'
    CONGRATULATIONWINDOW_TEXTBODY = '#fortifications:CongratulationWindow/textBody'
    BUILDINGPOPOVER_HEADER_LEVELSLBL = '#fortifications:BuildingPopover/header/levelsLbl'
    BUILDINGPOPOVER_HEADER_TITLESTATUS_FOUNDATION = '#fortifications:BuildingPopover/header/titleStatus/foundation'
    BUILDINGPOPOVER_HEADER_TITLESTATUS_MODERNIZATION = '#fortifications:BuildingPopover/header/titleStatus/modernization'
    BUILDINGPOPOVER_HEADER_TITLESTATUS_HALFDESTROY = '#fortifications:BuildingPopover/header/titleStatus/halfDestroy'
    BUILDINGPOPOVER_HEADER_TITLESTATUS_CONGRATULATION = '#fortifications:BuildingPopover/header/titleStatus/congratulation'
    BUILDINGPOPOVER_HEADER_TITLESTATUS_FREEZE = '#fortifications:BuildingPopover/header/titleStatus/freeze'
    BUILDINGPOPOVER_COMMANDERSTATUS_BODYSTATUS_FOUNDATION = '#fortifications:BuildingPopover/commanderStatus/bodyStatus/foundation'
    BUILDINGPOPOVER_SOLDIERSTATUS_BODYSTATUS_FOUNDATION = '#fortifications:BuildingPopover/soldierStatus/bodyStatus/foundation'
    BUILDINGPOPOVER_COMMANDERSTATUS_BODYSTATUS_HALFDESTROY = '#fortifications:BuildingPopover/commanderStatus/bodyStatus/halfDestroy'
    BUILDINGPOPOVER_SOLDIERSTATUS_BODYSTATUS_HALFDESTROY = '#fortifications:BuildingPopover/soldierStatus/bodyStatus/halfDestroy'
    BUILDINGPOPOVER_COMMANDERSTATUS_BODYSTATUS_MODERNIZATION = '#fortifications:BuildingPopover/commanderStatus/bodyStatus/modernization'
    BUILDINGPOPOVER_COMMANDERSTATUS_BODYSTATUS_CONGRATULATION = '#fortifications:BuildingPopover/commanderStatus/bodyStatus/congratulation'
    BUILDINGPOPOVER_INDICATORS_HPLBL = '#fortifications:BuildingPopover/indicators/hpLbl'
    BUILDINGPOPOVER_INDICATORS_DEFRESLBL = '#fortifications:BuildingPopover/indicators/defResLbl'
    BUILDINGPOPOVER_DEFRESINFO_DEFRESBUILDINGTITLE = '#fortifications:BuildingPopover/defResInfo/defResBuildingTitle'
    BUILDINGPOPOVER_DEFRESINFO_BASEBUILDINGTITLE = '#fortifications:BuildingPopover/defResInfo/baseBuildingTitle'
    BUILDINGPOPOVER_HEADER_MESSAGESTATUS = '#fortifications:BuildingPopover/header/messageStatus'
    BUILDINGPOPOVER_DEFRESACTIONS_PREPARINGDEFRES = '#fortifications:BuildingPopover/defResActions/preparingDefRes'
    BUILDINGPOPOVER_DEFRESACTIONS_PREPAREDDEFRES = '#fortifications:BuildingPopover/defResActions/preparedDefRes'
    BUILDINGPOPOVER_DEFRESACTIONS_PREPARETIMEOVER = '#fortifications:BuildingPopover/defResActions/prepareTimeOver'
    BUILDINGPOPOVER_DEFRESACTIONS_DIRECTIONOPENED = '#fortifications:BuildingPopover/defResActions/directionOpened'
    BUILDINGPOPOVER_DEFRESACTIONS_REQUESTDEFRES = '#fortifications:BuildingPopover/defResActions/requestDefRes'
    BUILDINGPOPOVER_DEFRESACTIONS_MANAGEMENT = '#fortifications:BuildingPopover/defResActions/management'
    BUILDINGPOPOVER_ASSIGNPLAYERS = '#fortifications:BuildingPopover/assignPlayers'
    BUILDINGS_MODERNIZATIONDESCR_BASE_BUILDING = '#fortifications:Buildings/modernizationDescr/base_building'
    BUILDINGS_DEFRESINFO_BASE_BUILDING = '#fortifications:Buildings/defResInfo/base_building'
    BUILDINGS_DEFRESINFO_WARSCHOOL_BUILDING = '#fortifications:Buildings/defResInfo/warSchool_building'
    BUILDINGS_DEFRESINFO_TROPHY_BUILDING = '#fortifications:Buildings/defResInfo/trophy_building'
    BUILDINGS_DEFRESINFO_TRAINING_BUILDING = '#fortifications:Buildings/defResInfo/training_building'
    BUILDINGS_DEFRESINFO_TANKODROM_BUILDING = '#fortifications:Buildings/defResInfo/tankodrom_building'
    BUILDINGS_DEFRESINFO_INTENDANCY_BUILDING = '#fortifications:Buildings/defResInfo/intendancy_building'
    BUILDINGS_DEFRESINFO_FINANCE_BUILDING = '#fortifications:Buildings/defResInfo/finance_building'
    BUILDINGS_DEFRESINFO_CAR_BUILDING = '#fortifications:Buildings/defResInfo/car_building'
    BUILDINGS_PROCESSORDERINFO_WARSCHOOL_BUILDING = '#fortifications:Buildings/processOrderInfo/warSchool_building'
    BUILDINGS_PROCESSORDERINFO_TROPHY_BUILDING = '#fortifications:Buildings/processOrderInfo/trophy_building'
    BUILDINGS_PROCESSORDERINFO_TRAINING_BUILDING = '#fortifications:Buildings/processOrderInfo/training_building'
    BUILDINGS_PROCESSORDERINFO_TANKODROM_BUILDING = '#fortifications:Buildings/processOrderInfo/tankodrom_building'
    BUILDINGS_PROCESSORDERINFO_INTENDANCY_BUILDING = '#fortifications:Buildings/processOrderInfo/intendancy_building'
    BUILDINGS_PROCESSORDERINFO_FINANCE_BUILDING = '#fortifications:Buildings/processOrderInfo/finance_building'
    BUILDINGS_PROCESSORDERINFO_CAR_BUILDING = '#fortifications:Buildings/processOrderInfo/car_building'
    ORDERS_ORDERPOPOVER_DURATIONTIME = '#fortifications:Orders/orderPopover/durationTime'
    ORDERS_ORDERPOPOVER_LEVELSLBL = '#fortifications:Orders/orderPopover/levelsLbl'
    ORDERS_ORDERPOPOVER_PRODUCTIONTIME = '#fortifications:Orders/orderPopover/productionTime'
    ORDERS_ORDERPOPOVER_PRODUCTIONBUILDING = '#fortifications:Orders/orderPopover/productionBuilding'
    ORDERS_ORDERPOPOVER_ORDERPRICE = '#fortifications:Orders/orderPopover/orderPrice'
    ORDERS_ORDERPOPOVER_PRODUCEDAMOUNT = '#fortifications:Orders/orderPopover/producedAmount'
    ORDERS_ORDERPOPOVER_USEORDER = '#fortifications:Orders/orderPopover/useOrder'
    ORDERS_ORDERPOPOVER_NOTAVAILABLE = '#fortifications:Orders/orderPopover/notAvailable'
    ORDERS_ORDERPOPOVER_ORDERTYPE_BATTLEPAYMENTS = '#fortifications:Orders/orderPopover/orderType/battlePayments'
    ORDERS_ORDERPOPOVER_ORDERTYPE_REQUISITION = '#fortifications:Orders/orderPopover/orderType/requisition'
    ORDERS_ORDERPOPOVER_ORDERTYPE_EVACUATION = '#fortifications:Orders/orderPopover/orderType/evacuation'
    ORDERS_ORDERPOPOVER_ORDERTYPE_HEAVYTRUCKS = '#fortifications:Orders/orderPopover/orderType/heavyTrucks'
    ORDERS_ORDERPOPOVER_ORDERTYPE_MILITARYMANEUVERS = '#fortifications:Orders/orderPopover/orderType/militaryManeuvers'
    ORDERS_ORDERPOPOVER_ORDERTYPE_ADDITIONALBRIEFING = '#fortifications:Orders/orderPopover/orderType/additionalBriefing'
    ORDERS_ORDERPOPOVER_ORDERTYPE_TACTICALTRAINING = '#fortifications:Orders/orderPopover/orderType/tacticalTraining'
    ORDERS_ORDERPOPOVER_ORDERNOTREADY = '#fortifications:Orders/orderPopover/orderNotReady'
    ORDERS_ORDERPOPOVER_INDEFENSIVE = '#fortifications:Orders/orderPopover/inDefensive'
    FORTIFICATION_CLAN_POSITION_LEADER = '#fortifications:fortification/clan/position/leader'
    FORTIFICATION_CLAN_POSITION_VICE_LEADER = '#fortifications:fortification/clan/position/vice_leader'
    FORTIFICATION_CLAN_POSITION_RECRUITER = '#fortifications:fortification/clan/position/recruiter'
    FORTIFICATION_CLAN_POSITION_TREASURER = '#fortifications:fortification/clan/position/treasurer'
    FORTIFICATION_CLAN_POSITION_DIPLOMAT = '#fortifications:fortification/clan/position/diplomat'
    FORTIFICATION_CLAN_POSITION_COMMANDER = '#fortifications:fortification/clan/position/commander'
    FORTIFICATION_CLAN_POSITION_PRIVATE = '#fortifications:fortification/clan/position/private'
    FORTIFICATION_CLAN_POSITION_RECRUIT = '#fortifications:fortification/clan/position/recruit'
    ORDERS_ORDERCONFIRMATIONWINDOW_PREPARATIONTIME = '#fortifications:Orders/orderConfirmationWindow/preparationTime'
    ORDERS_ORDERCONFIRMATIONWINDOW_COST = '#fortifications:Orders/orderConfirmationWindow/cost'
    MODERNIZATION_APPLYBUTTON_LABEL = '#fortifications:Modernization/applyButton/label'
    MODERNIZATION_CANCELBUTTON_LABEL = '#fortifications:Modernization/cancelButton/label'
    MODERNIZATION_WINDOWTITLE = '#fortifications:Modernization/windowTitle'
    MODERNIZATION_MODERNIZATIONINFO_BEFORELABEL = '#fortifications:Modernization/modernizationInfo/beforeLabel'
    MODERNIZATION_MODERNIZATIONINFO_AFTERLABEL = '#fortifications:Modernization/modernizationInfo/afterLabel'
    MODERNIZATION_MODERNIZATIONINFO_COUNTCOST = '#fortifications:Modernization/modernizationInfo/countCost'
    MODERNIZATION_CONDITIONS_GENERALCONDITION = '#fortifications:Modernization/conditions/generalCondition'
    MODERNIZATION_CONDITIONS_DEFENCEPERIOD = '#fortifications:Modernization/conditions/defencePeriod'
    MODERNIZATION_CONDITIONS_NOTFULFILLED = '#fortifications:Modernization/conditions/notFulfilled'
    MODERNIZATION_CONDITIONS_FORTMAXLEVEL = '#fortifications:Modernization/conditions/fortMaxLevel'
    FIXEDPLAYERS_LISTHEADER_FIELDNAME = '#fortifications:FixedPlayers/listHeader/fieldName'
    FIXEDPLAYERS_LISTHEADER_FIELDROLE = '#fortifications:FixedPlayers/listHeader/fieldRole'
    FIXEDPLAYERS_LISTHEADER_FIELDWEEK = '#fortifications:FixedPlayers/listHeader/fieldWeek'
    FIXEDPLAYERS_LISTHEADER_FIELDALLTIME = '#fortifications:FixedPlayers/listHeader/fieldAllTime'
    FIXEDPLAYERS_HEADER_BTNLBL = '#fortifications:FixedPlayers/header/btnLbl'
    FIXEDPLAYERS_HEADER_ISASSIGNED = '#fortifications:FixedPlayers/header/isAssigned'
    FIXEDPLAYERS_WINDOWTITLE = '#fortifications:FixedPlayers/windowTitle'
    SORTIE_INTROVIEW_TITLE = '#fortifications:sortie/introView/title'
    SORTIE_INTROVIEW_DESCR = '#fortifications:sortie/introView/descr'
    SORTIE_INTROVIEW_FORTBATTLES_TITLE = '#fortifications:sortie/introView/fortBattles/title'
    SORTIE_INTROVIEW_FORTBATTLES_DESCR = '#fortifications:sortie/introView/fortBattles/descr'
    SORTIE_INTROVIEW_FORTBATTLES_BTNTITLE = '#fortifications:sortie/introView/fortBattles/btnTitle'
    SORTIE_INTROVIEW_FORTBATTLES_BTNLABEL = '#fortifications:sortie/introView/fortBattles/btnLabel'
    SORTIE_INTROVIEW_SORTIE_TITLE = '#fortifications:sortie/introView/sortie/title'
    SORTIE_INTROVIEW_SORTIE_DESCR = '#fortifications:sortie/introView/sortie/descr'
    SORTIE_INTROVIEW_SORTIE_BTNTITLE = '#fortifications:sortie/introView/sortie/btnTitle'
    SORTIE_DIVISION_NAME_ALL = '#fortifications:sortie/division_name/ALL'
    SORTIE_DIVISION_NAME_ABSOLUTE = '#fortifications:sortie/division_name/ABSOLUTE'
    SORTIE_DIVISION_NAME_CHAMPION = '#fortifications:sortie/division_name/CHAMPION'
    SORTIE_DIVISION_NAME_MIDDLE = '#fortifications:sortie/division_name/MIDDLE'
    SORTIE_LISTVIEW_TITLE = '#fortifications:sortie/listView/title'
    SORTIE_LISTVIEW_DESCRIPTION = '#fortifications:sortie/listView/description'
    SORTIE_LISTVIEW_CREATE = '#fortifications:sortie/listView/create'
    SORTIE_LISTVIEW_LISTTITLE = '#fortifications:sortie/listView/listTitle'
    SORTIE_LISTVIEW_FILTER = '#fortifications:sortie/listView/filter'
    SORTIE_LISTVIEW_LISTCOLUMNS_NAME = '#fortifications:sortie/listView/listColumns/name'
    SORTIE_LISTVIEW_LISTCOLUMNS_DIVISION = '#fortifications:sortie/listView/listColumns/division'
    SORTIE_LISTVIEW_LISTCOLUMNS_MEMBERSCOUNT = '#fortifications:sortie/listView/listColumns/membersCount'
    SORTIE_LISTVIEW_SELECTEDTEAM = '#fortifications:sortie/listView/selectedTeam'
    SORTIE_LISTVIEW_TEAMMEMBERS = '#fortifications:sortie/listView/teamMembers'
    SORTIE_LISTVIEW_TEAMVEHICLESSTUB = '#fortifications:sortie/listView/teamVehiclesStub'
    SORTIE_LISTVIEW_TEAMVEHICLES = '#fortifications:sortie/listView/teamVehicles'
    SORTIE_LISTVIEW_NOTSELECTED = '#fortifications:sortie/listView/notSelected'
    SORTIE_LISTVIEW_ENTERBTN = '#fortifications:sortie/listView/enterBtn'
    SORTIE_LISTVIEW_ENTERTEXT = '#fortifications:sortie/listView/enterText'
    SORTIE_LISTVIEW_SLOT_CLOSED = '#fortifications:sortie/listView/slot/closed'
    SORTIE_ROOM_CANDIDATES = '#fortifications:sortie/room/candidates'
    SORTIE_ROOM_INVITEFRIENDS = '#fortifications:sortie/room/inviteFriends'
    SORTIE_ROOM_MEMBERS = '#fortifications:sortie/room/members'
    SORTIE_ROOM_VEHICLES = '#fortifications:sortie/room/vehicles'
    SORTIE_ROOM_ROSTERLISTTITLE = '#fortifications:sortie/room/rosterListTitle'
    SORTIE_SLOT_TAKEPLACE = '#fortifications:sortie/slot/takePlace'
    SORTIE_SLOT_EMPTYSLOT = '#fortifications:sortie/slot/emptySlot'
    SORTIE_ROOM_CHAT = '#fortifications:sortie/room/chat'
    SORTIE_ROOM_LEAVEBTN = '#fortifications:sortie/room/leaveBtn'
    SORTIE_ROOM_CHANGEDIVISION = '#fortifications:sortie/room/changeDivision'
    SORTIE_ROOM_DIVISION = '#fortifications:sortie/room/division'
    SORTIE_ROOM_TITLE = '#fortifications:sortie/room/title'
    SORTIE_ROOM_DESCRIPTION = '#fortifications:sortie/room/description'
    SORTIE_ROOM_INVITEBTN = '#fortifications:sortie/room/inviteBtn'
    SORTIE_ROOM_MESSAGE_CANDIDATE = '#fortifications:sortie/room/message/candidate'
    SORTIE_ROOM_MESSAGE_CANDIDATE_LOCKEDUNITS = '#fortifications:sortie/room/message/candidate/lockedUnits'
    SORTIE_ROOM_MESSAGE_CANDIDATE_INVALIDVEHICLES = '#fortifications:sortie/room/message/candidate/invalidVehicles'
    SORTIE_ROOM_MESSAGE_CANDIDATE_UNITISFULL = '#fortifications:sortie/room/message/candidate/unitIsFull'
    SORTIE_ROOM_MESSAGE_NOVEHICLE = '#fortifications:sortie/room/message/noVehicle'
    SORTIE_ROOM_MESSAGE_VEHICLEINNOTREADY = '#fortifications:sortie/room/message/vehicleInNotReady'
    SORTIE_ROOM_MESSAGE_GETREADY = '#fortifications:sortie/room/message/getReady'
    SORTIE_ROOM_MESSAGE_WAITING = '#fortifications:sortie/room/message/waiting'
    SORTIE_ROOM_MESSAGE_NOTFULLUNIT = '#fortifications:sortie/room/message/notFullUnit'
    SORTIE_ROOM_MESSAGE_READY = '#fortifications:sortie/room/message/ready'
    SORTIE_ROOM_MESSAGE_LEVELERROR = '#fortifications:sortie/room/message/levelError'
    SORTIE_ROOM_MESSAGE_OPENSLOTS_LEVELERROR = '#fortifications:sortie/room/message/openSlots/levelError'
    SORTIE_ROOM_READY = '#fortifications:sortie/room/ready'
    SORTIE_ROOM_NOTREADY = '#fortifications:sortie/room/notReady'
    SORTIE_ROOM_FIGHT = '#fortifications:sortie/room/fight'
    SORTIE_VEHICLESELECTOR_DESCRIPTION = '#fortifications:sortie/vehicleSelector/description'
    BUILDINGSPROCESS_SHORTDESCR_WARSCHOOL_BUILDING = '#fortifications:BuildingsProcess/shortDescr/warSchool_building'
    BUILDINGSPROCESS_SHORTDESCR_TROPHY_BUILDING = '#fortifications:BuildingsProcess/shortDescr/trophy_building'
    BUILDINGSPROCESS_SHORTDESCR_TRAINING_BUILDING = '#fortifications:BuildingsProcess/shortDescr/training_building'
    BUILDINGSPROCESS_SHORTDESCR_TANKODROM_BUILDING = '#fortifications:BuildingsProcess/shortDescr/tankodrom_building'
    BUILDINGSPROCESS_SHORTDESCR_INTENDANCY_BUILDING = '#fortifications:BuildingsProcess/shortDescr/intendancy_building'
    BUILDINGSPROCESS_SHORTDESCR_FINANCE_BUILDING = '#fortifications:BuildingsProcess/shortDescr/finance_building'
    BUILDINGSPROCESS_SHORTDESCR_CAR_BUILDING = '#fortifications:BuildingsProcess/shortDescr/car_building'
    BUILDINGSPROCESS_STATUSMSG_NOTAVAILABLE = '#fortifications:BuildingsProcess/statusMsg/notAvailable'
    BUILDINGSPROCESS_STATUSMSG_BUILT = '#fortifications:BuildingsProcess/statusMsg/built'
    BUILDINGSPROCESS_MAINLABEL_ACCESSCOUNT = '#fortifications:BuildingsProcess/mainLabel/accessCount'
    BUILDINGSPROCESS_TEXTINFO = '#fortifications:BuildingsProcess/textInfo'
    BUILDINGSPROCESS_WINDOWTITLE = '#fortifications:BuildingsProcess/windowTitle'
    BUILDINGSPROCESS_LONGDESCR_WARSCHOOL_BUILDING = '#fortifications:BuildingsProcess/longDescr/warSchool_building'
    BUILDINGSPROCESS_LONGDESCR_TROPHY_BUILDING = '#fortifications:BuildingsProcess/longDescr/trophy_building'
    BUILDINGSPROCESS_LONGDESCR_TRAINING_BUILDING = '#fortifications:BuildingsProcess/longDescr/training_building'
    BUILDINGSPROCESS_LONGDESCR_TANKODROM_BUILDING = '#fortifications:BuildingsProcess/longDescr/tankodrom_building'
    BUILDINGSPROCESS_LONGDESCR_INTENDANCY_BUILDING = '#fortifications:BuildingsProcess/longDescr/intendancy_building'
    BUILDINGSPROCESS_LONGDESCR_FINANCE_BUILDING = '#fortifications:BuildingsProcess/longDescr/finance_building'
    BUILDINGSPROCESS_LONGDESCR_CAR_BUILDING = '#fortifications:BuildingsProcess/longDescr/car_building'
    BUILDINGSPROCESS_BUTTONLBL = '#fortifications:BuildingsProcess/buttonLbl'
    BUILDINGSPROCESS_BUTTONLBLBUILT = '#fortifications:BuildingsProcess/buttonLblBuilt'
    BUILDINGSPROCESS_ORDERINFO_HEADER = '#fortifications:BuildingsProcess/orderInfo/header'
    BUILDINGSPROCESS_ORDERINFO_DESCRIPTIONPREFIX = '#fortifications:BuildingsProcess/orderInfo/descriptionPrefix'
    BUILDINGSPROCESS_BUILDINGINFO_STATUSMESSAGE = '#fortifications:BuildingsProcess/buildingInfo/statusMessage'
    BUILDINGSPROCESS_BUILDINGINFO_BOTTOMMESSAGE = '#fortifications:BuildingsProcess/buildingInfo/bottomMessage'
    CLANLISTWINDOW_TABLE_MEMBERNAME = '#fortifications:ClanListWindow/table/memberName'
    CLANLISTWINDOW_TABLE_ROLE = '#fortifications:ClanListWindow/table/role'
    CLANLISTWINDOW_TABLE_WEEKMINING = '#fortifications:ClanListWindow/table/weekMining'
    CLANLISTWINDOW_TABLE_MONTHMINING = '#fortifications:ClanListWindow/table/monthMining'
    FORTMAINVIEW_DIRECTIONSTUTOR_TITLE = '#fortifications:FortMainView/directionsTutor/title'
    FORTMAINVIEW_COMMONTUTOR_TITLE = '#fortifications:FortMainView/commonTutor/title'
    FORTMAINVIEW_TRANSPORTINGTUTOR_TITLE = '#fortifications:FortMainView/transportingTutor/title'
    FORTINTELLIGENCE_WINDOWTITLE = '#fortifications:FortIntelligence/windowTitle'
    FORTINTELLIGENCE_HEADERBLOCK_HEADER = FORTINTELLIGENCE_HEADERBLOCK + '/header'
    FORTINTELLIGENCE_HEADERBLOCK_BODY = FORTINTELLIGENCE_HEADERBLOCK + '/body'
    FORTINTELLIGENCE_TOPBLOCK_HEADER = FORTINTELLIGENCE_TOPBLOCK + '/header'
    FORTINTELLIGENCE_TOPBLOCK_BODY = FORTINTELLIGENCE_TOPBLOCK + '/body'
    FORTINTELLIGENCE_MIDDLEBLOCK_HEADER = FORTINTELLIGENCE_MIDDLEBLOCK + '/header'
    FORTINTELLIGENCE_MIDDLEBLOCK_BODY = FORTINTELLIGENCE_MIDDLEBLOCK + '/body'
    FORTINTELLIGENCE_BOTTOMBLOCK_HEADER = FORTINTELLIGENCE_BOTTOMBLOCK + '/header'
    FORTINTELLIGENCE_BOTTOMBLOCK_BODY = FORTINTELLIGENCE_BOTTOMBLOCK + '/body'
    FORTINTELLIGENCE_ADDITIONALTEXT_COMINGSOON = '#fortifications:FortIntelligence/additionalText/comingSoon'
    DEMOUNTBUILDING_WINDOWTITLE = '#fortifications:DemountBuilding/windowTitle'
    DEMOUNTBUILDING_GENERALTEXT_TITLE = '#fortifications:DemountBuilding/generalText/title'
    DEMOUNTBUILDING_GENERALTEXT_BODY = '#fortifications:DemountBuilding/generalText/body'
    DEMOUNTBUILDING_GENERALTEXT_BODYINNERTEXT = '#fortifications:DemountBuilding/generalText/bodyInnerText'
    DEMOUNTBUILDING_QUESTION_TITLE = '#fortifications:DemountBuilding/question/title'
    DEMOUNTBUILDING_QUESTION_BODY = '#fortifications:DemountBuilding/question/body'
    DEMOUNTBUILDING_ERRORMESSAGE = '#fortifications:DemountBuilding/errorMessage'
    DEMOUNTBUILDING_APPLYBUTTON_LABEL = '#fortifications:DemountBuilding/applyButton/label'
    DEMOUNTBUILDING_CANCELBUTTON_LABEL = '#fortifications:DemountBuilding/cancelButton/label'
    CHOICEDIVISION_WINDOWTITLE = '#fortifications:ChoiceDivision/windowTitle'
    CHOICEDIVISION_APPLYBTNLBL = '#fortifications:ChoiceDivision/applyBtnLbl'
    CHOICEDIVISION_CANCELBTNLBL = '#fortifications:ChoiceDivision/cancelBtnLbl'
    CHOICEDIVISION_DESCRIPTION = '#fortifications:ChoiceDivision/description'
    CHOICEDIVISION_DIVISIONFULLNAME = '#fortifications:ChoiceDivision/divisionFullName'
    CHOICEDIVISION_DIVISIONTYPE_MIDDLEDIVISION = '#fortifications:ChoiceDivision/divisionType/middleDivision'
    CHOICEDIVISION_DIVISIONTYPE_CHAMPIONDIVISION = '#fortifications:ChoiceDivision/divisionType/championDivision'
    CHOICEDIVISION_DIVISIONTYPE_ABSOLUTEDIVISION = '#fortifications:ChoiceDivision/divisionType/absoluteDivision'
    CHOICEDIVISION_DIVISIONPROFIT = '#fortifications:ChoiceDivision/divisionProfit'
    CHOICEDIVISION_VEHICLELEVEL = '#fortifications:ChoiceDivision/vehicleLevel'
    DISCONNECTED_WARNING = '#fortifications:disconnected/Warning'
    DISCONNECTED_WARNINGDESCRIPTIONROAMING = '#fortifications:disconnected/WarningDescriptionRoaming'
    DISCONNECTED_WARNINGDESCRIPTIONCENTERUNAVAILABLE = '#fortifications:disconnected/WarningDescriptionCenterUnavailable'
    SORTIE_DIVISION_NAME_ENUM = (SORTIE_DIVISION_NAME_ALL,
     SORTIE_DIVISION_NAME_ABSOLUTE,
     SORTIE_DIVISION_NAME_CHAMPION,
     SORTIE_DIVISION_NAME_MIDDLE)
    BUILDINGS_DEFRESINFO_ENUM = (BUILDINGS_DEFRESINFO_BASE_BUILDING,
     BUILDINGS_DEFRESINFO_WARSCHOOL_BUILDING,
     BUILDINGS_DEFRESINFO_TROPHY_BUILDING,
     BUILDINGS_DEFRESINFO_TRAINING_BUILDING,
     BUILDINGS_DEFRESINFO_TANKODROM_BUILDING,
     BUILDINGS_DEFRESINFO_INTENDANCY_BUILDING,
     BUILDINGS_DEFRESINFO_FINANCE_BUILDING,
     BUILDINGS_DEFRESINFO_CAR_BUILDING)
    BUILDINGSPROCESS_LONGDESCR_ENUM = (BUILDINGSPROCESS_LONGDESCR_WARSCHOOL_BUILDING,
     BUILDINGSPROCESS_LONGDESCR_TROPHY_BUILDING,
     BUILDINGSPROCESS_LONGDESCR_TRAINING_BUILDING,
     BUILDINGSPROCESS_LONGDESCR_TANKODROM_BUILDING,
     BUILDINGSPROCESS_LONGDESCR_INTENDANCY_BUILDING,
     BUILDINGSPROCESS_LONGDESCR_FINANCE_BUILDING,
     BUILDINGSPROCESS_LONGDESCR_CAR_BUILDING)
    BUILDINGPOPOVER_SOLDIERSTATUS_BODYSTATUS_ENUM = (BUILDINGPOPOVER_SOLDIERSTATUS_BODYSTATUS_FOUNDATION, BUILDINGPOPOVER_SOLDIERSTATUS_BODYSTATUS_HALFDESTROY)
    BUILDINGPOPOVER_HEADER_TITLESTATUS_ENUM = (BUILDINGPOPOVER_HEADER_TITLESTATUS_FOUNDATION,
     BUILDINGPOPOVER_HEADER_TITLESTATUS_MODERNIZATION,
     BUILDINGPOPOVER_HEADER_TITLESTATUS_HALFDESTROY,
     BUILDINGPOPOVER_HEADER_TITLESTATUS_CONGRATULATION,
     BUILDINGPOPOVER_HEADER_TITLESTATUS_FREEZE)
    BUILDINGPOPOVER_COMMANDERSTATUS_BODYSTATUS_ENUM = (BUILDINGPOPOVER_COMMANDERSTATUS_BODYSTATUS_FOUNDATION,
     BUILDINGPOPOVER_COMMANDERSTATUS_BODYSTATUS_HALFDESTROY,
     BUILDINGPOPOVER_COMMANDERSTATUS_BODYSTATUS_MODERNIZATION,
     BUILDINGPOPOVER_COMMANDERSTATUS_BODYSTATUS_CONGRATULATION)
    BUILDINGSPROCESS_SHORTDESCR_ENUM = (BUILDINGSPROCESS_SHORTDESCR_WARSCHOOL_BUILDING,
     BUILDINGSPROCESS_SHORTDESCR_TROPHY_BUILDING,
     BUILDINGSPROCESS_SHORTDESCR_TRAINING_BUILDING,
     BUILDINGSPROCESS_SHORTDESCR_TANKODROM_BUILDING,
     BUILDINGSPROCESS_SHORTDESCR_INTENDANCY_BUILDING,
     BUILDINGSPROCESS_SHORTDESCR_FINANCE_BUILDING,
     BUILDINGSPROCESS_SHORTDESCR_CAR_BUILDING)
    BUILDINGS_BUILDINGNAME_ENUM = (BUILDINGS_BUILDINGNAME_BASE_BUILDING,
     BUILDINGS_BUILDINGNAME_WARSCHOOL_BUILDING,
     BUILDINGS_BUILDINGNAME_TROPHY_BUILDING,
     BUILDINGS_BUILDINGNAME_TRAINING_BUILDING,
     BUILDINGS_BUILDINGNAME_TANKODROM_BUILDING,
     BUILDINGS_BUILDINGNAME_INTENDANCY_BUILDING,
     BUILDINGS_BUILDINGNAME_FINANCE_BUILDING,
     BUILDINGS_BUILDINGNAME_CAR_BUILDING)
    CHOICEDIVISION_DIVISIONTYPE_ENUM = (CHOICEDIVISION_DIVISIONTYPE_MIDDLEDIVISION, CHOICEDIVISION_DIVISIONTYPE_CHAMPIONDIVISION, CHOICEDIVISION_DIVISIONTYPE_ABSOLUTEDIVISION)
    ORDERS_ORDERPOPOVER_ORDERTYPE_ENUM = (ORDERS_ORDERPOPOVER_ORDERTYPE_BATTLEPAYMENTS,
     ORDERS_ORDERPOPOVER_ORDERTYPE_REQUISITION,
     ORDERS_ORDERPOPOVER_ORDERTYPE_EVACUATION,
     ORDERS_ORDERPOPOVER_ORDERTYPE_HEAVYTRUCKS,
     ORDERS_ORDERPOPOVER_ORDERTYPE_MILITARYMANEUVERS,
     ORDERS_ORDERPOPOVER_ORDERTYPE_ADDITIONALBRIEFING,
     ORDERS_ORDERPOPOVER_ORDERTYPE_TACTICALTRAINING)
    BUILDINGS_PROCESSORDERINFO_ENUM = (BUILDINGS_PROCESSORDERINFO_WARSCHOOL_BUILDING,
     BUILDINGS_PROCESSORDERINFO_TROPHY_BUILDING,
     BUILDINGS_PROCESSORDERINFO_TRAINING_BUILDING,
     BUILDINGS_PROCESSORDERINFO_TANKODROM_BUILDING,
     BUILDINGS_PROCESSORDERINFO_INTENDANCY_BUILDING,
     BUILDINGS_PROCESSORDERINFO_FINANCE_BUILDING,
     BUILDINGS_PROCESSORDERINFO_CAR_BUILDING)
    FORTMAINVIEW_ENUM = (FORTMAINVIEW_COMMON_TOTALDEPOTQUANTITYTEXT,
     FORTMAINVIEW_COMMON_TITLE,
     FORTMAINVIEW_DIRECTIONS_TITLE,
     FORTMAINVIEW_DIRECTIONS_SELECTINGSTATUS,
     FORTMAINVIEW_TRANSPORTING_TITLE,
     FORTMAINVIEW_TRANSPORTING_EXPORTINGSTATUS,
     FORTMAINVIEW_TRANSPORTING_IMPORTINGSTATUS,
     FORTMAINVIEW_TRANSPORTING_TUTORIALDESCR,
     FORTMAINVIEW_TRANSPORTING_TUTORIALDESCRDISABLED,
     FORTMAINVIEW_SORTIEBUTTON_TITLE,
     FORTMAINVIEW_INTELLIGENCEBUTTON_TITLE,
     FORTMAINVIEW_HEADER_LEVELSLBL,
     FORTMAINVIEW_LEAVE_BUTTON_LABEL,
     FORTMAINVIEW_DIRECTIONSTUTOR_TITLE,
     FORTMAINVIEW_COMMONTUTOR_TITLE,
     FORTMAINVIEW_TRANSPORTINGTUTOR_TITLE)

    @staticmethod
    def sortie_division_name(key):
        outcome = '#fortifications:sortie/division_name/%s' % key
        if outcome not in FORTIFICATIONS.SORTIE_DIVISION_NAME_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome

    @staticmethod
    def buildings_defresinfo(key):
        outcome = '#fortifications:Buildings/defResInfo/%s' % key
        if outcome not in FORTIFICATIONS.BUILDINGS_DEFRESINFO_ENUM:
            raise Exception, 'locale key "' + outcome + '" was not found'
        return outcome

    @staticmethod
    def buildingsprocess_longdescr(key):
        outcome = '#fortifications:BuildingsProcess/longDescr/%s' % key
        if outcome not in FORTIFICATIONS.BUILDINGSPROCESS_LONGDESCR_ENUM:
            raise Exception, 'locale key "' + outcome + '" was not found'
        return outcome

    @staticmethod
    def buildingpopover_soldierstatus_bodystatus(key):
        outcome = '#fortifications:BuildingPopover/soldierStatus/bodyStatus/%s' % key
        if outcome not in FORTIFICATIONS.BUILDINGPOPOVER_SOLDIERSTATUS_BODYSTATUS_ENUM:
            raise Exception, 'locale key "' + outcome + '" was not found'
        return outcome

    @staticmethod
    def buildingpopover_header_titlestatus(key):
        outcome = '#fortifications:BuildingPopover/header/titleStatus/%s' % key
        if outcome not in FORTIFICATIONS.BUILDINGPOPOVER_HEADER_TITLESTATUS_ENUM:
            raise Exception, 'locale key "' + outcome + '" was not found'
        return outcome

    @staticmethod
    def buildingpopover_commanderstatus_bodystatus(key):
        outcome = '#fortifications:BuildingPopover/commanderStatus/bodyStatus/%s' % key
        if outcome not in FORTIFICATIONS.BUILDINGPOPOVER_COMMANDERSTATUS_BODYSTATUS_ENUM:
            raise Exception, 'locale key "' + outcome + '" was not found'
        return outcome

    @staticmethod
    def buildingsprocess_shortdescr(key):
        outcome = '#fortifications:BuildingsProcess/shortDescr/%s' % key
        if outcome not in FORTIFICATIONS.BUILDINGSPROCESS_SHORTDESCR_ENUM:
            raise Exception, 'locale key "' + outcome + '" was not found'
        return outcome

    @staticmethod
    def buildings_buildingname(key):
        outcome = '#fortifications:Buildings/buildingName/%s' % key
        if outcome not in FORTIFICATIONS.BUILDINGS_BUILDINGNAME_ENUM:
            raise Exception, 'locale key "' + outcome + '" was not found'
        return outcome

    @staticmethod
    def choicedivision_divisiontype(key):
        outcome = '#fortifications:ChoiceDivision/divisionType/%s' % key
        if outcome not in FORTIFICATIONS.CHOICEDIVISION_DIVISIONTYPE_ENUM:
            raise Exception, 'locale key "' + outcome + '" was not found'
        return outcome

    @staticmethod
    def orders_orderpopover_ordertype(key):
        outcome = '#fortifications:Orders/orderPopover/orderType/%s' % key
        if outcome not in FORTIFICATIONS.ORDERS_ORDERPOPOVER_ORDERTYPE_ENUM:
            raise Exception, 'locale key "' + outcome + '" was not found'
        return outcome

    @staticmethod
    def buildings_processorderinfo(key):
        outcome = '#fortifications:Buildings/processOrderInfo/%s' % key
        if outcome not in FORTIFICATIONS.BUILDINGS_PROCESSORDERINFO_ENUM:
            raise Exception, 'locale key "' + outcome + '" was not found'
        return outcome

    @staticmethod
    def fortmainview(key):
        outcome = '#fortifications:FortMainView/%s' % key
        if outcome not in FORTIFICATIONS.FORTMAINVIEW_ENUM:
            raise Exception, 'locale key "' + outcome + '" was not found'
        return outcome

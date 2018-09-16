# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/strings_entries/ingame_gui.py
from gui.impl.gen_utils import DynAccessor

class IngameGui(DynAccessor):
    __slots__ = ()

    class aim(DynAccessor):
        __slots__ = ()
        zoom = 1588

    class attackReason(DynAccessor):
        __slots__ = ()
        artilleryProtection = 1622
        artillery_sector = 1623
        bombers = 1624

    class battleEndWarning(DynAccessor):
        __slots__ = ()
        text = 1593

    class battleMessenger(DynAccessor):
        __slots__ = ()

        class toxic(DynAccessor):
            __slots__ = ()

            class blackList(DynAccessor):
                __slots__ = ()

                class ADD_IN_BLACKLIST(DynAccessor):
                    __slots__ = ()
                    body = 1599
                    header = 1598

                class CANT_ADD_IN_BLACKLIST(DynAccessor):
                    __slots__ = ()
                    body = 1601
                    header = 1600

                class REMOVE_FROM_BLACKLIST(DynAccessor):
                    __slots__ = ()
                    body = 1603
                    header = 1602

    class battleProgress(DynAccessor):
        __slots__ = ()

        class hint(DynAccessor):
            __slots__ = ()
            description = 1631
            noBindingKey = 1638
            press = 1630

    class chat_example(DynAccessor):
        __slots__ = ()
        attack = 1158
        attack_enemy = 1163
        attention_to_cell = 1162
        back_to_base = 1159
        follow_me = 1157

        class global_msg(DynAccessor):
            __slots__ = ()

            class atk(DynAccessor):
                __slots__ = ()
                focus_hq = 1145
                save_tanks = 1139
                time = 1140

            class c_def(DynAccessor):
                __slots__ = ()
                focus_hq = 1146
                save_tanks = 1137
                time = 1141

            class lane(DynAccessor):
                __slots__ = ()
                center = 1143
                east = 1144
                west = 1142

        help_me = 1155
        help_me_ex = 1156
        negative = 1161
        positive = 1160
        reloading_cassette = 1149
        reloading_gun = 1148
        reloading_ready = 1150
        reloading_ready_cassette = 1152
        reloading_unavailable = 1153
        spg_aim_area = 1164
        stop = 1154
        support_me_with_fire = 1147
        turn_back = 1151

    class chat_shortcuts(DynAccessor):
        __slots__ = ()
        attack = 1114
        attack_enemy = 1135
        attack_enemy_reloading = 1136
        attention_to_base_atk = 1124
        attention_to_base_def = 1125
        attention_to_cell = 1118
        attention_to_objective_atk = 1122
        attention_to_objective_def = 1123
        attention_to_position = 1121
        back_to_base = 1115
        follow_me = 1113

        class global_msg(DynAccessor):
            __slots__ = ()

            class atk(DynAccessor):
                __slots__ = ()
                focus_hq = 1133
                save_tanks = 1126
                time = 1128

            class c_def(DynAccessor):
                __slots__ = ()
                focus_hq = 1134
                save_tanks = 1127
                time = 1129

            class lane(DynAccessor):
                __slots__ = ()
                center = 1131
                east = 1132
                west = 1130

        help_me = 1111
        help_me_ex = 1112
        negative = 1117
        positive = 1116
        reloading_cassette = 1106
        reloading_gun = 1105
        reloading_ready = 1107
        reloading_ready_cassette = 1108
        reloading_unavailable = 1109
        spg_aim_area = 1119
        spg_aim_area_reloading = 1120
        stop = 1110
        support_me_with_fire = 1104
        turn_back = 1103

    class colorSettingsTipPanel(DynAccessor):
        __slots__ = ()
        btnLabel = 1632

    class consumables_panel(DynAccessor):
        __slots__ = ()

        class equipment(DynAccessor):
            __slots__ = ()
            cooldownSeconds = 1272

            class tooltip(DynAccessor):
                __slots__ = ()
                empty = 1271

    class countRibbons(DynAccessor):
        __slots__ = ()
        multiSeparator = 1533

    class cruise_ctrl(DynAccessor):
        __slots__ = ()
        speedMetric = 1270

    class damageIndicator(DynAccessor):
        __slots__ = ()
        multiplier = 1594

    class damageLog(DynAccessor):
        __slots__ = ()
        multiplier = 1557

        class shellType(DynAccessor):
            __slots__ = ()
            ARMOR_PIERCING = 1552
            ARMOR_PIERCING_CR = 1555
            ARMOR_PIERCING_HE = 1554
            HIGH_EXPLOSIVE = 1553
            HOLLOW_CHARGE = 1556

    class damage_panel(DynAccessor):
        __slots__ = ()

        class crew(DynAccessor):
            __slots__ = ()

            class commander(DynAccessor):
                __slots__ = ()
                destroyed = 1255
                normal = 1254

            class driver(DynAccessor):
                __slots__ = ()
                destroyed = 1257
                normal = 1256

            class gunner1(DynAccessor):
                __slots__ = ()
                destroyed = 1263
                normal = 1262

            class gunner2(DynAccessor):
                __slots__ = ()
                destroyed = 1265
                normal = 1264

            class loader1(DynAccessor):
                __slots__ = ()
                destroyed = 1267
                normal = 1266

            class loader2(DynAccessor):
                __slots__ = ()
                destroyed = 1269
                normal = 1268

            class radioman1(DynAccessor):
                __slots__ = ()
                destroyed = 1259
                normal = 1258

            class radioman2(DynAccessor):
                __slots__ = ()
                destroyed = 1261
                normal = 1260

        class devices(DynAccessor):
            __slots__ = ()

            class ammoBay(DynAccessor):
                __slots__ = ()
                critical = 1237
                destroyed = 1238
                normal = 1236

            class chassis(DynAccessor):
                __slots__ = ()
                critical = 1243
                destroyed = 1244
                normal = 1242

            class engine(DynAccessor):
                __slots__ = ()
                critical = 1231
                destroyed = 1232
                normal = 1230

            class fuelTank(DynAccessor):
                __slots__ = ()
                critical = 1249
                destroyed = 1250
                normal = 1248

            class gun(DynAccessor):
                __slots__ = ()
                critical = 1234
                destroyed = 1235
                normal = 1233

            class radio(DynAccessor):
                __slots__ = ()
                critical = 1246
                destroyed = 1247
                normal = 1245

            class surveyingDevice(DynAccessor):
                __slots__ = ()
                critical = 1252
                destroyed = 1253
                normal = 1251

            class track(DynAccessor):
                __slots__ = ()
                critical = 1240
                destroyed = 1241
                normal = 1239

            class turretRotator(DynAccessor):
                __slots__ = ()
                critical = 1228
                destroyed = 1229
                normal = 1227

    class devices(DynAccessor):
        __slots__ = ()
        ammo_bay = 1036
        chassis = 1044
        engine = 1035
        fuel_tank = 1037
        gun = 1041
        left_track = 1039
        radio = 1038
        right_track = 1040
        surveing_device = 1043
        turret_rotator = 1042

    class distance(DynAccessor):
        __slots__ = ()
        meters = 1589

    class dynamicSquad(DynAccessor):
        __slots__ = ()

        class ally(DynAccessor):
            __slots__ = ()
            add = 1579
            disabled = 1581
            received = 1586
            wasSent = 1583

        class enemy(DynAccessor):
            __slots__ = ()
            add = 1580
            disabled = 1582
            received = 1587
            wasSent = 1584

        invite = 1585

    class efficiencyRibbons(DynAccessor):
        __slots__ = ()
        armor = 1534
        assistByAbility = 1618
        assistSpot = 1543
        assistTrack = 1542
        burn = 1538
        capture = 1535
        crits = 1544
        damage = 1536
        defence = 1539
        defenderBonus = 1617
        destructibleDamaged = 1614
        destructibleDestroyed = 1615
        destructiblesDefended = 1616
        enemySectorCaptured = 1613
        kill = 1540
        ram = 1537
        receivedBurn = 1548
        receivedCrits = 1546
        receivedDamage = 1547
        receivedRam = 1549
        receivedWorldCollision = 1550
        spotted = 1541
        stun = 1558
        vehicleRecovery = 1551
        worldCollision = 1545

    class epic_players_panel(DynAccessor):
        __slots__ = ()

        class state(DynAccessor):
            __slots__ = ()

            class hidden(DynAccessor):
                __slots__ = ()
                body = 1302
                header = 1301
                note = 1303

            class medium_player(DynAccessor):
                __slots__ = ()
                body = 1308
                header = 1307
                note = 1309

            class medium_tank(DynAccessor):
                __slots__ = ()
                body = 1311
                header = 1310
                note = 1312

            class short(DynAccessor):
                __slots__ = ()
                body = 1305
                header = 1304
                note = 1306

            class toggle(DynAccessor):
                __slots__ = ()
                body = 1314
                header = 1313
                note = 1315

    class flagNotification(DynAccessor):
        __slots__ = ()
        flagAbsorbed = 1575
        flagCaptured = 1572
        flagDelivered = 1574
        flagInbase = 1573

    class flags(DynAccessor):
        __slots__ = ()
        timer = 1532

    class fortConsumables(DynAccessor):
        __slots__ = ()

        class timer(DynAccessor):
            __slots__ = ()
            postfix = 1531

    class hitMarker(DynAccessor):
        __slots__ = ()
        blocked = 1559
        critical = 1561
        ricochet = 1560

    class marker(DynAccessor):
        __slots__ = ()
        meters = 1138

    class personalMissions(DynAccessor):
        __slots__ = ()

        class tip(DynAccessor):
            __slots__ = ()
            additionalHeader = 1528
            mainHeader = 1527

            class noQuests(DynAccessor):
                __slots__ = ()
                battleType = 1530
                vehicleType = 1529

    class player_errors(DynAccessor):
        __slots__ = ()

        class cant_move(DynAccessor):
            __slots__ = ()
            chassis_damaged = 1052
            crew_inactive = 1050
            engine_damaged = 1051

        class cant_shoot(DynAccessor):
            __slots__ = ()
            crew_inactive = 1054
            gun_damaged = 1056
            gun_locked = 1058
            gun_reload = 1057
            no_ammo = 1055
            vehicle_destroyed = 1053

        class cant_switch(DynAccessor):
            __slots__ = ()
            engine_destroyed = 1059

        class equipment(DynAccessor):
            __slots__ = ()
            alreadyActivated = 1060

            class extinguisher(DynAccessor):
                __slots__ = ()
                doesNotActivated = 1066

            isInCooldown = 1061

            class medkit(DynAccessor):
                __slots__ = ()
                allTankmenAreSafe = 1063
                tankmanIsSafe = 1062

            class order(DynAccessor):
                __slots__ = ()
                notReady = 1067

            class repairkit(DynAccessor):
                __slots__ = ()
                allDevicesAreNotDamaged = 1065
                deviceIsNotDamaged = 1064

    class player_messages(DynAccessor):
        __slots__ = ()
        ALLY_HIT = 1080
        COMBAT_EQUIPMENT_READY_ARTILLERY = 1428
        COMBAT_EQUIPMENT_READY_BOMBER = 1429
        COMBAT_EQUIPMENT_READY_INSPIRE = 1432
        COMBAT_EQUIPMENT_READY_RECON = 1430
        COMBAT_EQUIPMENT_READY_SMOKE = 1431
        COMBAT_EQUIPMENT_USED_ARTILLERY = 1433
        COMBAT_EQUIPMENT_USED_BOMBER = 1434
        COMBAT_EQUIPMENT_USED_INSPIRE = 1437
        COMBAT_EQUIPMENT_USED_RECON = 1435
        COMBAT_EQUIPMENT_USED_SMOKE = 1436
        DEATH_FROM_ARTILLERY_ALLY_ALLY = 1390
        DEATH_FROM_ARTILLERY_ALLY_ENEMY = 1391
        DEATH_FROM_ARTILLERY_ALLY_SUICIDE = 1387
        DEATH_FROM_ARTILLERY_ENEMY_ALLY = 1393
        DEATH_FROM_ARTILLERY_ENEMY_ENEMY = 1392
        DEATH_FROM_ARTILLERY_ENEMY_SUICIDE = 1386
        DEATH_FROM_ARTILLERY_PROTECTION_UNKNOWN_ALLY = 1397
        DEATH_FROM_ARTILLERY_PROTECTION_UNKNOWN_ENEMY = 1396
        DEATH_FROM_BOMBER_ALLY_SUICIDE = 1389
        DEATH_FROM_BOMBER_ENEMY_SUICIDE = 1388
        DEATH_FROM_DEATH_ZONE_ALLY_ALLY = 1485
        DEATH_FROM_DEATH_ZONE_ALLY_ENEMY = 1486
        DEATH_FROM_DEATH_ZONE_ALLY_SELF = 1484
        DEATH_FROM_DEATH_ZONE_ALLY_SUICIDE = 1483
        DEATH_FROM_DEATH_ZONE_ENEMY_ALLY = 1489
        DEATH_FROM_DEATH_ZONE_ENEMY_ENEMY = 1490
        DEATH_FROM_DEATH_ZONE_ENEMY_SELF = 1488
        DEATH_FROM_DEATH_ZONE_ENEMY_SUICIDE = 1487
        DEATH_FROM_DEATH_ZONE_SELF_ALLY = 1481
        DEATH_FROM_DEATH_ZONE_SELF_ENEMY = 1482
        DEATH_FROM_DEATH_ZONE_SELF_SUICIDE = 1480
        DEATH_FROM_DEVICE_EXPLOSION_AT_FIRE = 1409
        DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT = 1407
        DEATH_FROM_DROWNING_ALLY_ALLY = 1422
        DEATH_FROM_DROWNING_ALLY_ENEMY = 1423
        DEATH_FROM_DROWNING_ALLY_SELF = 1421
        DEATH_FROM_DROWNING_ALLY_SUICIDE = 1420
        DEATH_FROM_DROWNING_ENEMY_ALLY = 1426
        DEATH_FROM_DROWNING_ENEMY_ENEMY = 1427
        DEATH_FROM_DROWNING_ENEMY_SELF = 1425
        DEATH_FROM_DROWNING_ENEMY_SUICIDE = 1424
        DEATH_FROM_DROWNING_SELF_ALLY = 1418
        DEATH_FROM_DROWNING_SELF_ENEMY = 1419
        DEATH_FROM_DROWNING_SELF_SUICIDE = 1417
        DEATH_FROM_GAS_ATTACK_ALLY_ALLY = 1494
        DEATH_FROM_GAS_ATTACK_ALLY_ENEMY = 1495
        DEATH_FROM_GAS_ATTACK_ALLY_SELF = 1493
        DEATH_FROM_GAS_ATTACK_ENEMY_ALLY = 1497
        DEATH_FROM_GAS_ATTACK_ENEMY_ENEMY = 1498
        DEATH_FROM_GAS_ATTACK_ENEMY_SELF = 1496
        DEATH_FROM_GAS_ATTACK_SELF_ALLY = 1491
        DEATH_FROM_GAS_ATTACK_SELF_ENEMY = 1492
        DEATH_FROM_INACTIVE_CREW = 1406
        DEATH_FROM_INACTIVE_CREW_AT_SHOT = 1404
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_ALLY = 1466
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_ENEMY = 1467
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF = 1465
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SUICIDE = 1464
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_ALLY = 1470
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_ENEMY = 1471
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF = 1469
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SUICIDE = 1468
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_ALLY = 1462
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_ENEMY = 1463
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE = 1461
        DEATH_FROM_OVERTURN_ALLY_ALLY = 1517
        DEATH_FROM_OVERTURN_ALLY_ENEMY = 1518
        DEATH_FROM_OVERTURN_ALLY_SELF = 1516
        DEATH_FROM_OVERTURN_ALLY_SUICIDE = 1515
        DEATH_FROM_OVERTURN_ENEMY_ALLY = 1521
        DEATH_FROM_OVERTURN_ENEMY_ENEMY = 1522
        DEATH_FROM_OVERTURN_ENEMY_SELF = 1520
        DEATH_FROM_OVERTURN_ENEMY_SUICIDE = 1519
        DEATH_FROM_OVERTURN_SELF_ALLY = 1513
        DEATH_FROM_OVERTURN_SELF_ENEMY = 1514
        DEATH_FROM_OVERTURN_SELF_SUICIDE = 1512
        DEATH_FROM_RAMMING_ALLY_ALLY = 1510
        DEATH_FROM_RAMMING_ALLY_ENEMY = 1511
        DEATH_FROM_RAMMING_ALLY_SELF = 1509
        DEATH_FROM_RAMMING_ALLY_SUICIDE = 1508
        DEATH_FROM_RAMMING_ENEMY_ALLY = 1525
        DEATH_FROM_RAMMING_ENEMY_ENEMY = 1526
        DEATH_FROM_RAMMING_ENEMY_SELF = 1524
        DEATH_FROM_RAMMING_ENEMY_SUICIDE = 1523
        DEATH_FROM_RAMMING_SELF_ALLY = 1506
        DEATH_FROM_RAMMING_SELF_ENEMY = 1507
        DEATH_FROM_RAMMING_SELF_SUICIDE = 1505
        DEATH_FROM_RECOVERY_ALLY_SUICIDE = 1395
        DEATH_FROM_RECOVERY_ENEMY_SUICIDE = 1394
        DEATH_FROM_SECTOR_BOMBERS_UNKNOWN_ALLY = 1401
        DEATH_FROM_SECTOR_BOMBERS_UNKNOWN_ENEMY = 1400
        DEATH_FROM_SECTOR_PROTECTION_UNKNOWN_ALLY = 1399
        DEATH_FROM_SECTOR_PROTECTION_UNKNOWN_ENEMY = 1398
        DEATH_FROM_SHOT_ALLY_ALLY = 1368
        DEATH_FROM_SHOT_ALLY_ALLY_ARTILLERY = 1369
        DEATH_FROM_SHOT_ALLY_ALLY_BOMBER = 1370
        DEATH_FROM_SHOT_ALLY_ENEMY = 1371
        DEATH_FROM_SHOT_ALLY_ENEMY_ARTILLERY = 1372
        DEATH_FROM_SHOT_ALLY_ENEMY_BOMBER = 1373
        DEATH_FROM_SHOT_ALLY_SUICIDE = 1374
        DEATH_FROM_SHOT_ALLY_SUICIDE_ARTILLERY = 1375
        DEATH_FROM_SHOT_ALLY_SUICIDE_BOMBER = 1376
        DEATH_FROM_SHOT_ENEMY_ALLY = 1380
        DEATH_FROM_SHOT_ENEMY_ALLY_ARTILLERY = 1381
        DEATH_FROM_SHOT_ENEMY_ALLY_BOMBER = 1382
        DEATH_FROM_SHOT_ENEMY_ENEMY = 1383
        DEATH_FROM_SHOT_ENEMY_ENEMY_ARTILLERY = 1384
        DEATH_FROM_SHOT_ENEMY_ENEMY_BOMBER = 1385
        DEATH_FROM_SHOT_ENEMY_SUICIDE = 1377
        DEATH_FROM_SHOT_ENEMY_SUICIDE_ARTILLERY = 1378
        DEATH_FROM_SHOT_ENEMY_SUICIDE_BOMBER = 1379
        DEATH_FROM_SHOT_SELF_ALLY = 1362
        DEATH_FROM_SHOT_SELF_ALLY_ARTILLERY = 1363
        DEATH_FROM_SHOT_SELF_ALLY_BOMBER = 1364
        DEATH_FROM_SHOT_SELF_ENEMY = 1365
        DEATH_FROM_SHOT_SELF_ENEMY_ARTILLERY = 1366
        DEATH_FROM_SHOT_SELF_ENEMY_BOMBER = 1367
        DEATH_FROM_WORLD_COLLISION_ALLY_ALLY = 1449
        DEATH_FROM_WORLD_COLLISION_ALLY_ENEMY = 1450
        DEATH_FROM_WORLD_COLLISION_ALLY_SELF = 1448
        DEATH_FROM_WORLD_COLLISION_ALLY_SUICIDE = 1447
        DEATH_FROM_WORLD_COLLISION_ENEMY_ALLY = 1453
        DEATH_FROM_WORLD_COLLISION_ENEMY_ENEMY = 1454
        DEATH_FROM_WORLD_COLLISION_ENEMY_SELF = 1452
        DEATH_FROM_WORLD_COLLISION_ENEMY_SUICIDE = 1451
        DEATH_FROM_WORLD_COLLISION_SELF_ALLY = 1445
        DEATH_FROM_WORLD_COLLISION_SELF_ENEMY = 1446
        DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE = 1444
        DESTRUCTIBLE_DESTROYED_ALLY = 1605
        DESTRUCTIBLE_DESTROYED_ENEMY = 1606
        DESTRUCTIBLE_DESTROYED_SELF = 1604
        DEVICE_CRITICAL_AT_FIRE = 1072
        DEVICE_CRITICAL_AT_SHOT = 1068
        DEVICE_DESTROYED_AT_FIRE = 1075
        DEVICE_DESTROYED_AT_SHOT = 1069
        DEVICE_REPAIRED = 1079
        DEVICE_REPAIRED_TO_CRITICAL = 1076
        DEVICE_STARTED_FIRE_AT_SHOT = 1070
        ENGINE_CRITICAL_AT_UNLIMITED_RPM = 1073
        ENGINE_DESTROYED_AT_UNLIMITED_RPM = 1074
        FIRE_STOPPED = 1077
        TANKMAN_HIT_AT_SHOT = 1071
        TANKMAN_RESTORED = 1078
        allied_team_name = 1088
        ally_base_captured_by_notification = 1084
        ally_base_captured_notification = 1081
        base_capture_blocked = 1087
        base_captured_by_notification = 1086
        base_captured_notification = 1083
        enemy_base_captured_by_notification = 1085
        enemy_base_captured_notification = 1082
        enemy_team_name = 1089
        loader_intuition_was_used = 1102

        class postmortem_caption(DynAccessor):
            __slots__ = ()
            other = 1092
            self = 1091

        postmortem_caption_ = 1090
        postmortem_userNoHasAmmo = 1093
        replayControlsHelp1 = 1099
        replayControlsHelp2 = 1100
        replayControlsHelp3 = 1101
        replayFreeCameraActivated = 1095
        replayPaused = 1098
        replaySavedCameraActivated = 1096
        replaySpeedChange = 1097
        tank_in_fire = 1094

    class players_panel(DynAccessor):
        __slots__ = ()

        class state(DynAccessor):
            __slots__ = ()

            class large(DynAccessor):
                __slots__ = ()
                body = 1294
                header = 1293
                note = 1295

            class medium(DynAccessor):
                __slots__ = ()
                body = 1288
                header = 1287
                note = 1289

            class medium2(DynAccessor):
                __slots__ = ()
                body = 1291
                header = 1290
                note = 1292

            class none(DynAccessor):
                __slots__ = ()
                body = 1282
                header = 1281
                note = 1283

            class short(DynAccessor):
                __slots__ = ()
                body = 1285
                header = 1284
                note = 1286

        unknown_clan = 1300
        unknown_frags = 1298
        unknown_name = 1296
        unknown_vehicle = 1297
        unknown_vehicleState = 1299

    class postmortem(DynAccessor):
        __slots__ = ()

        class tips(DynAccessor):
            __slots__ = ()

            class exitHangar(DynAccessor):
                __slots__ = ()
                label = 1279
                text = 1280

            class observerMode(DynAccessor):
                __slots__ = ()
                label = 1277
                text = 1278

    class postmortem_messages(DynAccessor):
        __slots__ = ()
        DEATH_FROM_DEATH_ZONE_ALLY_SELF = 1477
        DEATH_FROM_DEATH_ZONE_ENEMY_SELF = 1475
        DEATH_FROM_DEATH_ZONE_SELF_SUICIDE = 1473
        DEATH_FROM_DEVICE_EXPLOSION_AT_FIRE = 1410
        DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT = 1408
        DEATH_FROM_DROWNING_ALLY_SELF = 1416
        DEATH_FROM_DROWNING_ENEMY_SELF = 1414
        DEATH_FROM_DROWNING_SELF_SUICIDE = 1412
        DEATH_FROM_FIRE = 1403
        DEATH_FROM_INACTIVE_CREW_AT_SHOT = 1405
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF = 1460
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF = 1458
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE = 1456
        DEATH_FROM_OVERTURN_ALLY_SELF = 1361
        DEATH_FROM_OVERTURN_ENEMY_SELF = 1360
        DEATH_FROM_OVERTURN_SELF_SUICIDE = 1359
        DEATH_FROM_RAMMING_ALLY_SELF = 1504
        DEATH_FROM_RAMMING_ENEMY_SELF = 1502
        DEATH_FROM_RAMMING_SELF_SUICIDE = 1500
        DEATH_FROM_SHOT = 1353
        DEATH_FROM_SHOT_ARTILLERY = 1357
        DEATH_FROM_SHOT_BOMBER = 1358
        DEATH_FROM_WORLD_COLLISION_ALLY_SELF = 1443
        DEATH_FROM_WORLD_COLLISION_ENEMY_SELF = 1441
        DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE = 1439
        DEATH_UNKNOWN = 1354

    class recovery(DynAccessor):
        __slots__ = ()
        cooldown = 1621
        hint1 = 1619
        hint2 = 1620

    class repairPoint(DynAccessor):
        __slots__ = ()
        title = 1591
        unavailable = 1592

    class respawnView(DynAccessor):
        __slots__ = ()
        additionalTip = 1563
        additionalTipLimited = 1564
        classNotAvailable = 1571
        cooldownLbl = 1565
        destroyedLbl = 1566
        disabledLbl = 1567
        emptySlotInfo = 1569
        emptySlotInfoTooltip = 1570
        nextVehicleName = 1568
        title = 1562

    class rewardWindow(DynAccessor):
        __slots__ = ()

        class base(DynAccessor):
            __slots__ = ()
            btnLabel = 1637
            descText = 1636
            headerText = 1635
            subHeaderText = 1634

        winHeaderText = 1633

    class scorePanel(DynAccessor):
        __slots__ = ()
        mySquadLbl = 1577
        playerScore = 1578
        squadLbl = 1576

    class shells_kinds(DynAccessor):
        __slots__ = ()
        ARMOR_PIERCING = 1222
        ARMOR_PIERCING_CR = 1224
        ARMOR_PIERCING_HE = 1223
        HIGH_EXPLOSIVE = 1221
        HOLLOW_CHARGE = 1220
        params = 1225
        stunParams = 1226

    class siegeMode(DynAccessor):
        __slots__ = ()

        class hint(DynAccessor):
            __slots__ = ()

            class forMode(DynAccessor):
                __slots__ = ()
                c_0 = 1608
                c_1 = 1609
                c_2 = 1610
                c_3 = 1611

            noBinding = 1612
            press = 1607

    class statistics(DynAccessor):
        __slots__ = ()
        exit = 1189

        class final(DynAccessor):
            __slots__ = ()
            heroes = 1212

            class lifeInfo(DynAccessor):
                __slots__ = ()
                alive = 1213
                dead = 1214

            class personal(DynAccessor):
                __slots__ = ()
                capturePoints = 1210
                damaged = 1205
                directHits = 1208
                directHitsReceived = 1209
                droppedCapturePoints = 1211
                killed = 1204
                postmortem = 1203
                shots = 1207
                spotted = 1206

            class reasons(DynAccessor):
                __slots__ = ()
                reason0 = 1193
                reason1lose = 1195
                reason1tie = 1196
                reason1win = 1194
                reason2 = 1197
                reason3 = 1198

            class stats(DynAccessor):
                __slots__ = ()
                credits = 1201
                experience = 1200
                multipliedExp = 1199
                repair = 1202

            class status(DynAccessor):
                __slots__ = ()
                lose = 1192
                tie = 1190
                win = 1191

        header = 1177

        class headers(DynAccessor):
            __slots__ = ()
            header0 = 1181
            header1 = 1182
            header2 = 1183
            header3 = 1184
            header4 = 1185

        class playerState(DynAccessor):
            __slots__ = ()
            c_0 = 1215
            c_1 = 1217
            c_2 = 1216
            c_3 = 1218
            c_4 = 1219

        class tab(DynAccessor):
            __slots__ = ()

            class line_up(DynAccessor):
                __slots__ = ()
                header = 1165
                title = 1166

            class progressTracing(DynAccessor):
                __slots__ = ()
                notAvailable = 1178

            class quests(DynAccessor):
                __slots__ = ()
                header = 1167

                class notAvailable(DynAccessor):
                    __slots__ = ()
                    title = 1176

                class nothingToPerform(DynAccessor):
                    __slots__ = ()
                    descr = 1174
                    title = 1173

                class status(DynAccessor):
                    __slots__ = ()
                    done = 1171
                    fullDone = 1172
                    inProgress = 1168
                    increaseResult = 1170
                    onPause = 1169

                class switchOff(DynAccessor):
                    __slots__ = ()
                    title = 1175

        class tabs(DynAccessor):
            __slots__ = ()
            group = 1186
            heroes = 1188
            personal = 1187

        team1title = 1179
        team2title = 1180

    class stun(DynAccessor):
        __slots__ = ()
        indicator = 1628
        seconds = 1629

    tabStatsHint = 1590

    class tankmen(DynAccessor):
        __slots__ = ()
        commander = 1045
        driver = 1046
        gunner = 1048
        loader = 1049
        radioman = 1047

    class timer(DynAccessor):
        __slots__ = ()
        battlePeriod = 1276
        started = 1275
        starting = 1274
        waiting = 1273

    class trajectoryView(DynAccessor):
        __slots__ = ()

        class hint(DynAccessor):
            __slots__ = ()
            alternateModeLeft = 1626
            alternateModeRight = 1627
            noBindingKey = 1625

    class vehicle_messages(DynAccessor):
        __slots__ = ()
        DEATH_FROM_DEATH_ZONE_ALLY_SELF = 1476
        DEATH_FROM_DEATH_ZONE_ENEMY_SELF = 1474
        DEATH_FROM_DEATH_ZONE_SELF_SUICIDE = 1472
        DEATH_FROM_DROWNING_ALLY_SELF = 1415
        DEATH_FROM_DROWNING_ENEMY_SELF = 1413
        DEATH_FROM_DROWNING_SELF_SUICIDE = 1411
        DEATH_FROM_FIRE = 1402
        DEATH_FROM_GAS_ATTACK_ALLY_SELF = 1479
        DEATH_FROM_GAS_ATTACK_ENEMY_SELF = 1478
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF = 1459
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF = 1457
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE = 1455
        DEATH_FROM_OVERTURN_ALLY_SELF = 1597
        DEATH_FROM_OVERTURN_ENEMY_SELF = 1596
        DEATH_FROM_OVERTURN_SELF_SUICIDE = 1595
        DEATH_FROM_RAMMING_ALLY_SELF = 1503
        DEATH_FROM_RAMMING_ENEMY_SELF = 1501
        DEATH_FROM_RAMMING_SELF_SUICIDE = 1499
        DEATH_FROM_SHOT = 1352
        DEATH_FROM_SHOT_ARTILLERY = 1355
        DEATH_FROM_SHOT_BOMBER = 1356
        DEATH_FROM_WORLD_COLLISION_ALLY_SELF = 1442
        DEATH_FROM_WORLD_COLLISION_ENEMY_SELF = 1440
        DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE = 1438
        DEVICE_CRITICAL_AT_RAMMING_ALLY_ALLY = 1333
        DEVICE_CRITICAL_AT_RAMMING_ALLY_SELF = 1330
        DEVICE_CRITICAL_AT_RAMMING_ALLY_SUICIDE = 1331
        DEVICE_CRITICAL_AT_RAMMING_ENEMY_ALLY = 1332
        DEVICE_CRITICAL_AT_RAMMING_ENEMY_SELF = 1329
        DEVICE_CRITICAL_AT_RAMMING_SELF_SUICIDE = 1328
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_ALLY = 1321
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_SELF = 1318
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_SUICIDE = 1319
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ENEMY_ALLY = 1320
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ENEMY_SELF = 1317
        DEVICE_CRITICAL_AT_WORLD_COLLISION_SELF_SUICIDE = 1316
        DEVICE_DESTROYED_AT_RAMMING_ALLY_ALLY = 1339
        DEVICE_DESTROYED_AT_RAMMING_ALLY_SELF = 1336
        DEVICE_DESTROYED_AT_RAMMING_ALLY_SUICIDE = 1337
        DEVICE_DESTROYED_AT_RAMMING_ENEMY_ALLY = 1338
        DEVICE_DESTROYED_AT_RAMMING_ENEMY_SELF = 1335
        DEVICE_DESTROYED_AT_RAMMING_SELF_SUICIDE = 1334
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_ALLY = 1327
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_SELF = 1324
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_SUICIDE = 1325
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ENEMY_ALLY = 1326
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ENEMY_SELF = 1323
        DEVICE_DESTROYED_AT_WORLD_COLLISION_SELF_SUICIDE = 1322
        DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_ALLY = 1345
        DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_SELF = 1342
        DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_SUICIDE = 1343
        DEVICE_STARTED_FIRE_AT_RAMMING_ENEMY_ALLY = 1344
        DEVICE_STARTED_FIRE_AT_RAMMING_ENEMY_SELF = 1341
        DEVICE_STARTED_FIRE_AT_RAMMING_SELF_SUICIDE = 1340
        TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_ALLY = 1351
        TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_SELF = 1348
        TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_SUICIDE = 1349
        TANKMAN_HIT_AT_WORLD_COLLISION_ENEMY_ALLY = 1350
        TANKMAN_HIT_AT_WORLD_COLLISION_ENEMY_SELF = 1347
        TANKMAN_HIT_AT_WORLD_COLLISION_SELF_SUICIDE = 1346

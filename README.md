# WorldOfTanks-Decompiled
Unpacked and decompiled files of **WorldOfTanks**. The base branch contains decompiles of the **EU**-version of the game client. At the same time, other branches can be added - a test client, a supertest or a client from other regions, if there are main differences in them.

Each client has its own [**branch**](https://github.com/StranikS-Scan/WorldOfTanks-Decompiled/branches/all). In the default-branch is the latest version of the client. Micropatches that are released after the first release of the client are added only to branch of released client. This allows you to easily track all the stages of the release of the game.

### Consist
* Python **py**-files since client version **0.9.2**
* Game **xml**-files since version **0.9.12**

### Soft
Using **[PjOrion](https://koreanrandom.com/forum/topic/15280-)**:
* **"Uncompile 6"** decompiler updated by **[R. Bernstein](https://github.com/rocky/python-uncompyle6)** and modified **StranikS_Scan**
* Built-in decompressor of xml-files realized by **[SkepticalFox](https://github.com/ShadowHunterRUS)** and modified **StranikS_Scan**

### Using ###
1. Download commit to PC
2. Run once **"Zip-Unpacker.exe"** to restore the original files from the **zip-archive** with the correct letters case in the file names and symbols codes in texts

### Auto decompilation algorithm (recommendations)
1. Replace old files with new files in the folder **"source"**: paths.xml, version.xml
2. Delete old files and copy new files in the folder **"res"**
3. Run **"WOT-UnDec.exe"** to unpack and decompile the files

### Manual decompilation algorithm
1. Create a folder **"source"** and a subfolder **"res"** in it
2. Copy files **"paths.xml"** and **"version.xml"** from game-root to a folder **"source"**
3. Copy all **xml**-files from game folder **"res"** to the directory **"source\res"**
4. Extract the contents of the archive **"res\packages\scripts.pkg"** to the directory **"source\res"**
5. Decode all **xml**-files using **[PjOrion](https://koreanrandom.com/forum/topic/15280-)**: **"WOT-Client"** -> **"Unpack XML"** -> **"Unpack folder..."** select **"source"**
6. Decompile all **pyc**-files using **"Uncompile6"** in **[PjOrion](https://koreanrandom.com/forum/topic/15280-)**: **"Decompile"** -> **"Decompile pyc-folder..."** select **"source"**
7. Find and delete all **pyc**-files

### Pull requesting to the repository (recommendations)
1. You must clone the commit from the repository from which you want to continue the existing branch or start a new branch
2. If you adding a new client, then create a new branch with the name as client main version **"X.X.X"** (do not use **"CT"** or **"ST"** unless it's a not separate special branch)
3. Clean the existing **"source"** directory and put new files there using the algorithm above
4. Change the name of the archive to the current one in the file **"Zip-Packer.arg"**
5. Create an **zip**-archive by running the console program **Zip-Packer.exe** (required **7z.exe** on your PC)
6. Delete the old **"zip"** archive in the **"zip"** directory
7. Create a commit, named as **"X.X.X: Added/Updated/Release/... #YYY"** or **"X.X.X_CT:..."**
8. Offer a **"Pull request"** in the right branch

### Files with different case of letters
Due to the fact that during the update of the game, the developers changed the case of the letters in the files, there may be duplicate files in the repository. To solve this problem, the **"Zip-Unpacker.exe"** file has been added to the repository. After downloading the repository or after synchronizing your copy of the repository with the GitHub, run this file. It will extract the py-files from the archive as they should be.
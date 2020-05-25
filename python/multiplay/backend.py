'''
    Backends

    Copyright 2018 Jacques Gasselin

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''
import uuid

class Backend(object):
    def __init__(self):
        pass

    def _isLocalPlayerEqualToPlayer(self, connectionUUID, localPlayerUUID, playerID):
        if playerID is None or localPlayerUUID is None:
            return False
        foundPlayerID = self._findPlayerForLocalPlayerAndConnection(localPlayerUUID, connectionUUID)
        return playerID == foundPlayerID

    def open(self):
        pass

    def close(self):
        pass

    def reset(self):
        pass

    def connect(self, client_address, gameUUID):
        if isinstance(gameUUID, str):
            gameUUID = uuid.UUID(gameUUID)
        connectionUUID = uuid.uuid5(gameUUID, client_address)
        self._storeConnection(connectionUUID, gameUUID)
        return connectionUUID

    def login(self, connectionUUID, localDeviceUUID):
        if isinstance(localDeviceUUID, str):
            localDeviceUUID = uuid.UUID(localDeviceUUID)
        if isinstance(connectionUUID, str):
            connectionUUID = uuid.UUID(connectionUUID)
        localPlayerUUID = self._findLocalPlayerForConnection(connectionUUID)
        playerID = self._findPlayerForDevice(localDeviceUUID)
        if self._isLocalPlayerEqualToPlayer(connectionUUID, localDeviceUUID, playerID):
            return localPlayerUUID
        if playerID is None:
            playerID = self._createPlayerForDevice(localDeviceUUID)
        localPlayerUUID = uuid.uuid5(localDeviceUUID, str(playerID))
        self._storeLocalPlayerForConnection(playerID, localPlayerUUID, connectionUUID)
        return localPlayerUUID

    def writePlayerData(self, connectionUUID, localPlayerUUID, data):
        if isinstance(localPlayerUUID, str):
            localPlayerUUID = uuid.UUID(localPlayerUUID)
        if isinstance(connectionUUID, str):
            connectionUUID = uuid.UUID(connectionUUID)
        playerID = self._findPlayerForLocalPlayerAndConnection(localPlayerUUID, connectionUUID)
        gameUUID = self._findGameByConnection(connectionUUID)
        return self._storePlayerData(playerID, gameUUID, data)

    def readPlayerData(self, connectionUUID, localPlayerUUID):
        if isinstance(localPlayerUUID, str):
            localPlayerUUID = uuid.UUID(localPlayerUUID)
        if isinstance(connectionUUID, str):
            connectionUUID = uuid.UUID(connectionUUID)
        playerID = self._findPlayerForLocalPlayerAndConnection(localPlayerUUID, connectionUUID)
        gameUUID = self._findGameByConnection(connectionUUID)
        return self._loadPlayerData(playerID, gameUUID)

class PickleBackend(Backend):
    def __init__(self, dbPath):
        Backend.__init__(self)
        self.__gameByConnection = {}
        self.__localPlayerByConnection = {}
        self.__deviceByConnection = {}
        self.__playerByLocalPlayerAndConnection = {}
        self.__playerByDevice = {}
        self.__dataPerPlayerAndGame = {}
        self.__dbPath = dbPath

    def _storeConnection(self, connectionUUID, gameUUID):
        self.__gameByConnection[connectionUUID] = gameUUID

    def _findGameByConnection(self, connectionUUID):
        return self.__gameByConnection.get(connectionUUID, None)

    def _findLocalPlayerForConnection(self, connectionUUID):
        return self.__localPlayerByConnection.get(connectionUUID, None)

    def _findPlayerForDevice(self, localDeviceUUID):
        return self.__playerByDevice.get(localDeviceUUID, None)

    def _createPlayerForDevice(self, localDeviceUUID):
        playerID = uuid.uuid4()
        self.__playerByDevice[localDeviceUUID] = playerID
        return playerID

    def _storeLocalPlayerForConnection(self, playerID, localPlayerUUID, connectionUUID):
        self.__localPlayerByConnection[connectionUUID] = localPlayerUUID
        self.__playerByLocalPlayerAndConnection[(localPlayerUUID, connectionUUID)] = playerID

    def _findPlayerForLocalPlayerAndConnection(self, localPlayerUUID, connectionUUID):
        if localPlayerUUID is None:
            return None
        return self.__playerByLocalPlayerAndConnection.get((localPlayerUUID, connectionUUID), None)

    def _storePlayerData(self, playerID, gameUUID, data):
        if playerID is None or gameUUID is None:
            return False
        self.__dataPerPlayerAndGame[(playerID, gameUUID)] = data
        return True

    def _loadPlayerData(self, playerID, gameUUID):
        if playerID is None or gameUUID is None:
            return None
        return self.__dataPerPlayerAndGame.get((playerID, gameUUID), None)

    def reset(self):
        self.__gameByConnection = {}
        self.__localPlayerByConnection = {}
        self.__deviceByConnection = {}
        self.__playerByLocalPlayerAndConnection = {}
        self.__playerByDevice = {}
        self.__dataPerPlayerAndGame = {}

    def open(self):
        try:
            with open(self.__dbPath, "rb") as f:
                import pickle
                instance = pickle.load(f)
                self.__dict__ = instance.__dict__
        except EOFError:
            pass
        except FileNotFoundError:
            pass

    def close(self):
        with open(self.__dbPath, "wb") as f:
            import pickle
            pickle.dump(self, f)

class Sqlite3Backend(Backend):
    def __init__(self, dbPath):
        Backend.__init__(self)
        self.__dbPath = dbPath

    def _storeConnection(self, connectionUUID, gameUUID):
        cur = self.__conn.cursor()
        cur.execute('INSERT OR REPLACE INTO connection (connection_uuid, game_uuid) VALUES ("%s", "%s")' % (str(connectionUUID), str(gameUUID)))
        cur.close()

    def _findGameByConnection(self, connectionUUID):
        cur = self.__conn.cursor()
        cur.execute('SELECT game_uuid FROM connection WHERE connection_uuid="%s"' % str(connectionUUID))
        result = cur.fetchone()
        cur.close()
        if result:
            return result[0]
        return None

    def _findLocalPlayerForConnection(self, connectionUUID):
        cur = self.__conn.cursor()
        cur.execute('SELECT local_player_uuid FROM local_player_by_connection WHERE connection_uuid="%s"' % str(connectionUUID))
        result = cur.fetchone()
        if result:
            return result[0]
        return None

    def _findPlayerForDevice(self, localDeviceUUID):
        return None

    def _createPlayerForDevice(self, localDeviceUUID):
        cur = self.__conn.cursor()
        cur.execute('INSERT INTO player (display_name) VALUES ("none")')
        playerID = cur.lastrowid
        cur.close()
        return playerID

    def _storeLocalPlayerForConnection(self, playerID, localPlayerUUID, connectionUUID):
        cur = self.__conn.cursor()
        cur.execute('INSERT OR REPLACE INTO local_player_by_connection VALUES ("%s", "%s", %i)' % (str(localPlayerUUID), str(connectionUUID), playerID))
        cur.close()

    def _findPlayerForLocalPlayerAndConnection(self, localPlayerUUID, connectionUUID):
        if localPlayerUUID is None:
            return None
        cur = self.__conn.cursor()
        cur.execute('SELECT player_id FROM local_player_by_connection WHERE connection_uuid="%s" AND local_player_uuid="%s"' % (str(connectionUUID), str(localPlayerUUID)))
        result = cur.fetchone()
        cur.close()
        if result:
            return result[0]
        return None

    def _storePlayerData(self, playerID, gameUUID, data):
        if playerID is None or gameUUID is None:
            return False
        cur = self.__conn.cursor()
        cur.execute('INSERT INTO player_data (player_id, game_uuid, data) VALUES (%i, "%s", "%s")' % (playerID, str(gameUUID), str(data)))
        cur.close()
        return True

    def _loadPlayerData(self, playerID, gameUUID):
        if playerID is None or gameUUID is None:
            return None
        cur = self.__conn.cursor()
        cur.execute('SELECT data FROM player_data WHERE player_id=%i AND game_uuid="%s"' % (playerID, str(gameUUID)))
        result = cur.fetchone()
        cur.close()
        if result:
            return result[0]
        return None

    def open(self):
        import sqlite3
        self.__conn = sqlite3.connect(self.__dbPath)
        cur = self.__conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS connection (connection_id INTEGER PRIMARY KEY, connection_uuid TEXT, game_uuid TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS player (player_id INTEGER PRIMARY KEY, display_name TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS local_player_by_connection (local_player_uuid TEXT, connection_uuid TEXT, player_id INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS player_data (player_id INTEGER, game_uuid TEXT, data TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS player_by_device (device_uuid text, player_id INTEGER)")
        cur.close()

    def close(self):
        self.__conn.close()
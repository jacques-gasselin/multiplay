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
import random

class Backend(object):
    def __init__(self):
        self.__isLogging = False

    def _isLocalPlayerEqualToPlayer(self, connectionUUID, localPlayerUUID, playerID):
        if self.logging:
            print("_isLocalPlayerEqualToPlayer(%s, %s, %s)" % (connectionUUID, localPlayerUUID, str(playerID)))
        if playerID is None or localPlayerUUID is None:
            return False
        foundPlayerID = self._findPlayerForLocalPlayerAndConnection(localPlayerUUID, connectionUUID)
        return playerID == foundPlayerID

    def _createDisplayName(self):
        first = ["Super", "Mega", "Blaster", "Thunder", "Points", "Game"]
        second = ["Killer", "Player", "Lord", "Pants", "Suit", "Flame", "Angel"]
        numbers = "0123456789"
        parts = [random.choice(first), random.choice(second), random.choice(numbers), random.choice(numbers)]
        return "".join(parts)

    def _createSessionDisplayName(self):
        first = ["Session", "Game", "Match"]
        numbers = "0123456789"
        parts = [random.choice(first), random.choice(numbers), random.choice(numbers), random.choice(numbers), random.choice(numbers)]
        return "".join(parts)

    def _createFriendCode(self):
        set = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        length = 8
        return "".join([random.choice(set) for i in range(length)])

    def _createSessionShareCode(self):
        set = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        length = 8
        return "".join([random.choice(set) for i in range(length)])

    def isLogging(self):
        try:
            return self.__isLogging
        except AttributeError:
            return False

    def setIsLogging(self, TrueOrFalse):
        self.__isLogging = TrueOrFalse

    logging = property(isLogging, setIsLogging)

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
        if self.logging:
            print("login(%s, %s)" % (connectionUUID, localDeviceUUID))
        if isinstance(localDeviceUUID, str):
            localDeviceUUID = uuid.UUID(localDeviceUUID)
        if isinstance(connectionUUID, str):
            connectionUUID = uuid.UUID(connectionUUID)
        localPlayerUUID = self._findLocalPlayerForConnection(connectionUUID)
        playerID = self._findPlayerForDevice(localDeviceUUID)
        if self._isLocalPlayerEqualToPlayer(connectionUUID, localDeviceUUID, playerID):
            if self.logging:
                print("[local found] -> ", localPlayerUUID)
            return localPlayerUUID
        if playerID is None:
            playerID = self._createPlayerForDevice(localDeviceUUID)
            assert(playerID is not None)
        localPlayerUUID = uuid.uuid5(localDeviceUUID, str(playerID))
        self._storeLocalPlayerForConnection(playerID, localPlayerUUID, connectionUUID)
        if self.logging:
            print("[created] -> ", localPlayerUUID)
        return localPlayerUUID

    ### Player Management

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

    def setPlayerDisplayName(self, connectionUUID, localPlayerUUID, name):
        if isinstance(localPlayerUUID, str):
            localPlayerUUID = uuid.UUID(localPlayerUUID)
        if isinstance(connectionUUID, str):
            connectionUUID = uuid.UUID(connectionUUID)
        playerID = self._findPlayerForLocalPlayerAndConnection(localPlayerUUID, connectionUUID)
        return self._setPlayerDisplayName(playerID, name)

    def setSessionDisplayName(self, connectionUUID, localSessionUUID, name):
        if isinstance(localSessionUUID, str):
            localSessionUUID = uuid.UUID(localSessionUUID)
        if isinstance(connectionUUID, str):
            connectionUUID = uuid.UUID(connectionUUID)
        sessionID = self._findSessionForLocalSessionAndConnection(localSessionUUID, connectionUUID)
        return self._setSessionDisplayName(sessionID, name)

    def getPlayerDisplayName(self, connectionUUID, localPlayerUUID):
        if isinstance(localPlayerUUID, str):
            localPlayerUUID = uuid.UUID(localPlayerUUID)
        if isinstance(connectionUUID, str):
            connectionUUID = uuid.UUID(connectionUUID)
        playerID = self._findPlayerForLocalPlayerAndConnection(localPlayerUUID, connectionUUID)
        return self._getPlayerDisplayName(playerID)

    def getSessionDisplayName(self, connectionUUID, localSessionUUID):
        if isinstance(localSessionUUID, str):
            localSessionUUID = uuid.UUID(localSessionUUID)
        if isinstance(connectionUUID, str):
            connectionUUID = uuid.UUID(connectionUUID)
        sessionID = self._findSessionForLocalSessionAndConnection(localSessionUUID, connectionUUID)
        return self._getSessionDisplayName(sessionID)

    def getPlayerFriendCode(self, connectionUUID, localPlayerUUID):
        if isinstance(localPlayerUUID, str):
            localPlayerUUID = uuid.UUID(localPlayerUUID)
        if isinstance(connectionUUID, str):
            connectionUUID = uuid.UUID(connectionUUID)
        playerID = self._findPlayerForLocalPlayerAndConnection(localPlayerUUID, connectionUUID)
        return self._getPlayerFriendCode(playerID)

    def getSessionShareCode(self, connectionUUID, localSessionUUID):
        if isinstance(localSessionUUID, str):
            localSessionUUID = uuid.UUID(localSessionUUID)
        if isinstance(connectionUUID, str):
            connectionUUID = uuid.UUID(connectionUUID)
        sessionID = self._findSessionForLocalSessionAndConnection(localSessionUUID, connectionUUID)
        return self._getSessionShareCode(sessionID)

    def addFriendToLocalPlayer(self, connectionUUID, localPlayerUUID, friendCode):
        if isinstance(localPlayerUUID, str):
            localPlayerUUID = uuid.UUID(localPlayerUUID)
        if isinstance(connectionUUID, str):
            connectionUUID = uuid.UUID(connectionUUID)
        playerID = self._findPlayerForLocalPlayerAndConnection(localPlayerUUID, connectionUUID)
        friendID = self._findPlayerForFriendCode(friendCode)
        return self._addFriendToPlayer(playerID, friendID)

    def authenticateLocalPlayer(self, connectionUUID, localPlayerUUID, auth_token_type, auth_token):
        if isinstance(localPlayerUUID, str):
            localPlayerUUID = uuid.UUID(localPlayerUUID)
        if isinstance(connectionUUID, str):
            connectionUUID = uuid.UUID(connectionUUID)
        playerID = self._findPlayerForLocalPlayerAndConnection(localPlayerUUID, connectionUUID)
        authedPlayerID = self._findAuthenticatedPlayerForAuthToken(auth_token_type, auth_token)
        if not authedPlayerID:
            # if the auth token is not in our table of auth tokens we migrate the current player
            # to be authorized and now other connections can get the same underlying player id
            # as long as their auth token matches
            self._authenticatePlayerForAuthToken(auth_token_type, auth_token, playerID)
        else:
            # if it is then we need to migrate the local player to the authed player unless they are
            # already the same
            if playerID != authedPlayerID:
                #TODO migrate
                self._storeLocalPlayerForConnection(authedPlayerID, localPlayerUUID, connectionUUID)

    #### Session Management

    def createSession(self, connectionUUID, localPlayerUUID):
        if isinstance(localPlayerUUID, str):
            localPlayerUUID = uuid.UUID(localPlayerUUID)
        if isinstance(connectionUUID, str):
            connectionUUID = uuid.UUID(connectionUUID)
        playerID = self._findPlayerForLocalPlayerAndConnection(localPlayerUUID, connectionUUID)
        gameUUID = self._findGameByConnection(connectionUUID)
        sessionID = self._createSession(gameUUID, playerID)
        assert(sessionID is not None)
        localSessionUUID = uuid.uuid5(localPlayerUUID, str(sessionID))
        self._storeLocalSessionForConnection(sessionID, localSessionUUID, connectionUUID)
        return localSessionUUID

class PickleBackend(Backend):
    def __init__(self, dbPath):
        Backend.__init__(self)
        self.__gameByConnection = {}
        self.__localPlayerByConnection = {}
        self.__localSessionByConnection = {}
        self.__deviceByConnection = {}
        self.__playerByLocalPlayerAndConnection = {}
        self.__sessionByLocalSessionAndConnection = {}
        self.__friendByPlayer = {}
        self.__playerByAuthToken = {}
        self.__playerByDevice = {}
        self.__playerDisplayName = {}
        self.__playerFriendCode = {}
        self.__dataPerPlayerAndGame = {}
        self.__sessionByGame = {}
        self.__sessionDisplayName = {}
        self.__sessionShareCode = {}
        self.__dbPath = dbPath

    def _storeConnection(self, connectionUUID, gameUUID):
        self.__gameByConnection[connectionUUID] = gameUUID

    def _findGameByConnection(self, connectionUUID):
        return self.__gameByConnection.get(connectionUUID, None)

    def _findLocalPlayerForConnection(self, connectionUUID):
        return self.__localPlayerByConnection.get(connectionUUID, None)

    def _findPlayerForDevice(self, localDeviceUUID):
        return self.__playerByDevice.get(localDeviceUUID, None)

    def _findAuthenticatedPlayerForAuthToken(self, auth_token_type, auth_token):
        return self.__playerByAuthToken.get((auth_token_type, auth_token), None)

    def _authenticatePlayerForAuthToken(self, auth_token_type, auth_token, playerID):
        self.__playerByAuthToken[(auth_token_type, auth_token)] = playerID

    def _createPlayerForDevice(self, localDeviceUUID):
        displayName = self._createDisplayName()
        friendCode = self._createFriendCode()
        playerID = uuid.uuid4()
        self.__playerByDevice[localDeviceUUID] = playerID
        self.__playerDisplayName[playerID] = displayName
        self.__playerFriendCode[playerID] = friendCode
        return playerID

    def _createSession(self, gameUUID, playerID):
        displayName = self._createSessionDisplayName()
        shareCode = self._createSessionShareCode()
        sessionID = uuid.uuid4()
        self.__sessionByGame[gameUUID] = sessionID
        self.__sessionDisplayName[sessionID] = displayName
        self.__sessionShareCode[sessionID] = shareCode
        return sessionID

    def _storeLocalPlayerForConnection(self, playerID, localPlayerUUID, connectionUUID):
        self.__localPlayerByConnection[connectionUUID] = localPlayerUUID
        self.__playerByLocalPlayerAndConnection[(localPlayerUUID, connectionUUID)] = playerID

    def _storeLocalSessionForConnection(self, sessionID, localSessionUUID, connectionUUID):
        self.__localSessionByConnection[connectionUUID] = localSessionUUID
        self.__sessionByLocalSessionAndConnection[(localSessionUUID, connectionUUID)] = sessionID

    def _findPlayerForFriendCode(self, friendCode):
        if self.logging:
            print("_findPlayerForFriendCode(%s)" % (friendCode))
        if friendCode is None:
            return None
        result = None
        for playerID, code in self.__playerFriendCode.items():
            if code == friendCode:
                result = playerID
                break
        if self.logging:
            print("-> ", result)
        return result

    def _findSessionForShareCode(self, shareCode):
        if self.logging:
            print("_findSessionForShareCode(%s)" % (shareCode))
        if shareCode is None:
            return None
        result = None
        for sessionID, code in self.__sessionShareCode.items():
            if code == shareCode:
                result = sessionID
                break
        if self.logging:
            print("-> ", result)
        return result

    def _findPlayerForLocalPlayerAndConnection(self, localPlayerUUID, connectionUUID):
        if self.logging:
            print("_findPlayerForLocalPlayerAndConnection(%s, %s)" % (localPlayerUUID, connectionUUID))
        if localPlayerUUID is None:
            return None
        result = self.__playerByLocalPlayerAndConnection.get((localPlayerUUID, connectionUUID), None)
        if self.logging:
            print("-> ", result)
        return result

    def _findSessionForLocalSessionAndConnection(self, localSessionUUID, connectionUUID):
        if self.logging:
            print("_findSessionForLocalSessionAndConnection(%s, %s)" % (localSessionUUID, connectionUUID))
        if localSessionUUID is None:
            return None
        result = self.__sessionByLocalSessionAndConnection.get((localSessionUUID, connectionUUID), None)
        if self.logging:
            print("-> ", result)
        return result

    def _storePlayerData(self, playerID, gameUUID, data):
        if playerID is None or gameUUID is None:
            return False
        self.__dataPerPlayerAndGame[(playerID, gameUUID)] = data
        return True

    def _loadPlayerData(self, playerID, gameUUID):
        if playerID is None or gameUUID is None:
            return None
        return self.__dataPerPlayerAndGame.get((playerID, gameUUID), None)

    def _setPlayerDisplayName(self, playerID, name):
        if playerID is None or name is None:
            return False
        try:
            self.__playerDisplayName[playerID] = name
        except AttributeError:
            self.__playerDisplayName = { playerID : name }
        return True

    def _setSessionDisplayName(self, sessionID, name):
        if sessionID is None or name is None:
            return False
        try:
            self.__sessionDisplayName[sessionID] = name
        except AttributeError:
            self.__sessionDisplayName = { sessionID : name }
        return True

    def _getPlayerDisplayName(self, playerID):
        if playerID is None:
            return None
        return self.__playerDisplayName[playerID]

    def _getSessionDisplayName(self, sessionID):
        if sessionID is None:
            return None
        return self.__sessionDisplayName[sessionID]

    def _getPlayerFriendCode(self, playerID):
        if playerID is None:
            return None
        return self.__playerFriendCode[playerID]

    def _getSessionShareCode(self, sessionID):
        if sessionID is None:
            return None
        return self.__sessionShareCode[sessionID]

    def _addFriendToPlayer(self, playerID, friendID):
        if playerID is None or friendID is None:
            return False
        self.__friendByPlayer[playerID] = friendID
        return True

    def reset(self):
        self.__gameByConnection = {}
        self.__localPlayerByConnection = {}
        self.__deviceByConnection = {}
        self.__playerByLocalPlayerAndConnection = {}
        self.__playerByDevice = {}
        self.__playerDisplayName = {}
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

    def _executeQuery(self, query):
        if self.logging:
            print(query)
        cur = self.__conn.cursor()
        cur.execute(query)
        cur.close()

    def _executeQueryAndFetchOne(self, query):
        if self.logging:
            print(query)
        cur = self.__conn.cursor()
        cur.execute(query)
        result = cur.fetchone()
        if self.logging:
            print(result)
        cur.close()
        return result

    def _executeQueryAndReturnRowId(self, query):
        if self.logging:
            print(query)
        cur = self.__conn.cursor()
        cur.execute(query)
        result = cur.lastrowid
        if self.logging:
            print(result)
        cur.close()
        return result

    def _storeConnection(self, connectionUUID, gameUUID):
        deleteQuery = 'DELETE FROM connection WHERE connection_uuid="%s" AND game_uuid="%s"' % (str(connectionUUID), str(gameUUID))
        selectQuery = 'INSERT OR REPLACE INTO connection (connection_uuid, game_uuid) VALUES ("%s", "%s")' % (str(connectionUUID), str(gameUUID))
        self._executeQuery(deleteQuery)
        self._executeQuery(selectQuery)

    def _findGameByConnection(self, connectionUUID):
        selectQuery = 'SELECT game_uuid FROM connection WHERE connection_uuid="%s"' % str(connectionUUID)
        result = self._executeQueryAndFetchOne(selectQuery)
        if result:
            return result[0]
        return None

    def _findLocalPlayerForConnection(self, connectionUUID):
        selectQuery = 'SELECT local_player_uuid FROM local_player_by_connection WHERE connection_uuid="%s"' % str(connectionUUID)
        result = self._executeQueryAndFetchOne(selectQuery)
        if result:
            return result[0]
        return None

    def _findPlayerForDevice(self, localDeviceUUID):
        selectQuery = 'SELECT player_id FROM player_by_device WHERE device_uuid="%s"' % str(localDeviceUUID)
        result = self._executeQueryAndFetchOne(selectQuery)
        if result:
            return result[0]
        return None

    def _findAuthenticatedPlayerForAuthToken(self, auth_token_type, auth_token):
        selectQuery = 'SELECT player_id FROM authenticated_players WHERE auth_token_type="%s" AND auth_token="%s"' % (str(auth_token_type), str(auth_token))
        result = self._executeQueryAndFetchOne(selectQuery)
        if result:
            return result[0]
        return None

    def _authenticatePlayerForAuthToken(self, auth_token_type, auth_token, playerID):
        if self.logging:
            print("_authenticatePlayerForAuthToken(%s, %s, %i)" % (auth_token_type, auth_token, playerID))
        assert(playerID is not None)
        if playerID is None or auth_token_type is None or auth_token is None:
            return False
        insertQuery = 'INSERT OR REPLACE INTO authenticated_players VALUES (%i, "%s", "%s")' % (playerID, str(auth_token_type), str(auth_token))
        self._executeQuery(insertQuery)
        return True

    def _createPlayerForDevice(self, localDeviceUUID):
        displayName = self._createDisplayName()
        friendCode = self._createFriendCode()
        insertQuery = 'INSERT INTO player (display_name, friend_code) VALUES ("%s", "%s")' % (displayName, friendCode)
        playerID = self._executeQueryAndReturnRowId(insertQuery)
        insertQuery = 'INSERT INTO player_by_device (device_uuid, player_id) VALUES ("%s", %i)' % (str(localDeviceUUID), playerID)
        self._executeQuery(insertQuery)
        return playerID

    def _createSession(self, gameUUID, playerID):
        displayName = self._createSessionDisplayName()
        shareCode = self._createSessionShareCode()
        insertQuery = 'INSERT INTO session (game_uuid, display_name, share_code, min_players, max_players) VALUES ("%s", "%s", "%s", 2, 16)' % (str(gameUUID), displayName, shareCode)
        sessionID = self._executeQueryAndReturnRowId(insertQuery)
        insertQuery = 'INSERT INTO player_by_session (session_id, player_id) VALUES (%i, %i)' % (sessionID, playerID)
        self._executeQuery(insertQuery)
        return sessionID

    def _storeLocalPlayerForConnection(self, playerID, localPlayerUUID, connectionUUID):
        assert(playerID is not None)
        if self.logging:
            print("_storeLocalPlayerForConnection(%s, %s, %s):" % (str(playerID), localPlayerUUID, connectionUUID))
        if playerID is None or localPlayerUUID is None or connectionUUID is None:
            return False
        deleteQuery = 'DELETE FROM local_player_by_connection WHERE connection_uuid="%s" AND local_player_uuid="%s"' % (str(connectionUUID), str(localPlayerUUID))
        insertQuery = 'INSERT OR REPLACE INTO local_player_by_connection VALUES ("%s", "%s", %i)' % (str(localPlayerUUID), str(connectionUUID), playerID)
        self._executeQuery(deleteQuery)
        self._executeQuery(insertQuery)
        return True

    def _storeLocalSessionForConnection(self, sessionID, localSessionUUID, connectionUUID):
        assert(sessionID is not None)
        if self.logging:
            print("_storeLocalSessionForConnection(%s, %s, %s):" % (str(sessionID), localSessionUUID, connectionUUID))
        if sessionID is None or localSessionUUID is None or connectionUUID is None:
            return False
        deleteQuery = 'DELETE FROM local_session_by_connection WHERE connection_uuid="%s" AND local_session_uuid="%s"' % (str(connectionUUID), str(localSessionUUID))
        insertQuery = 'INSERT OR REPLACE INTO local_session_by_connection VALUES ("%s", "%s", %i)' % (str(localSessionUUID), str(connectionUUID), sessionID)
        self._executeQuery(deleteQuery)
        self._executeQuery(insertQuery)
        return True

    def _findPlayerForFriendCode(self, friendCode):
        if self.logging:
            print("_findPlayerForFriendCode(%s)" % (friendCode))
        if friendCode is None:
            return None
        result = None
        selectQuery = 'SELECT player_id FROM player WHERE friend_code="%s"' % (str(friendCode))
        result = self._executeQueryAndFetchOne(selectQuery)
        if result:
            return result[0]
        return None

    def _findSessionForShareCode(self, shareCode):
        if self.logging:
            print("_findSessionForShareCode(%s)" % (shareCode))
        if shareCode is None:
            return None
        result = None
        selectQuery = 'SELECT session_id FROM session WHERE share_code="%s"' % (str(shareCode))
        result = self._executeQueryAndFetchOne(selectQuery)
        if result:
            return result[0]
        return None

    def _findPlayerForLocalPlayerAndConnection(self, localPlayerUUID, connectionUUID):
        if self.logging:
            print("_findPlayerForLocalPlayerAndConnection(%s, %s)" % (localPlayerUUID, connectionUUID))
        if localPlayerUUID is None or connectionUUID is None:
            return None
        selectQuery = 'SELECT player_id FROM local_player_by_connection WHERE connection_uuid="%s" AND local_player_uuid="%s"' % (str(connectionUUID), str(localPlayerUUID))
        result = self._executeQueryAndFetchOne(selectQuery)
        if result:
            return result[0]
        return None

    def _findSessionForLocalSessionAndConnection(self, localSessionUUID, connectionUUID):
        if self.logging:
            print("_findSessionForLocalSessionAndConnection(%s, %s)" % (localSessionUUID, connectionUUID))
        if localSessionUUID is None or connectionUUID is None:
            return None
        selectQuery = 'SELECT session_id FROM local_session_by_connection WHERE connection_uuid="%s" AND local_session_uuid="%s"' % (str(connectionUUID), str(localSessionUUID))
        result = self._executeQueryAndFetchOne(selectQuery)
        if result:
            return result[0]
        return None

    def _storePlayerData(self, playerID, gameUUID, data):
        if playerID is None or gameUUID is None:
            return False
        deleteQuery = 'DELETE FROM player_data WHERE player_id=%i AND game_uuid="%s"' % (playerID, str(gameUUID))
        insertQuery = 'INSERT INTO player_data (player_id, game_uuid, data) VALUES (%i, "%s", "%s")' % (playerID, str(gameUUID), str(data))
        self._executeQuery(deleteQuery)
        self._executeQuery(insertQuery)
        return True

    def _loadPlayerData(self, playerID, gameUUID):
        if playerID is None or gameUUID is None:
            return None
        selectQuery = 'SELECT data FROM player_data WHERE player_id=%i AND game_uuid="%s"' % (playerID, str(gameUUID))
        result = self._executeQueryAndFetchOne(selectQuery)
        if result:
            return result[0]
        return None

    def _setPlayerDisplayName(self, playerID, name):
        if playerID is None or name is None:
            return False
        updateQuery = 'UPDATE player SET display_name="%s" WHERE player_id=%i' % (name, playerID)
        self._executeQuery(updateQuery)
        return True

    def _setSessionDisplayName(self, sessionID, name):
        if sessionID is None or name is None:
            return False
        updateQuery = 'UPDATE session SET display_name="%s" WHERE session_id=%i' % (name, sessionID)
        self._executeQuery(updateQuery)
        return True

    def _getPlayerDisplayName(self, playerID):
        if playerID is None:
            return None
        selectQuery = 'SELECT display_name FROM player WHERE player_id=%i' % (playerID)
        result = self._executeQueryAndFetchOne(selectQuery)
        if result:
            return result[0]
        return None

    def _getSessionDisplayName(self, sessionID):
        if sessionID is None:
            return None
        selectQuery = 'SELECT display_name FROM session WHERE session_id=%i' % (sessionID)
        result = self._executeQueryAndFetchOne(selectQuery)
        if result:
            return result[0]
        return None

    def _getPlayerFriendCode(self, playerID):
        if playerID is None:
            return None
        selectQuery = 'SELECT friend_code FROM player WHERE player_id=%i' % (playerID)
        result = self._executeQueryAndFetchOne(selectQuery)
        if result:
            return result[0]
        return None

    def _getSessionShareCode(self, sessionID):
        if sessionID is None:
            return None
        selectQuery = 'SELECT share_code FROM session WHERE session_id=%i' % (sessionID)
        result = self._executeQueryAndFetchOne(selectQuery)
        if result:
            return result[0]
        return None

    def _addFriendToPlayer(self, playerID, friendID):
        if playerID is None or friendID is None:
            return False
        insertQuery = 'INSERT INTO player_friends (player_id, friend_id) VALUES (%i, %i)' % (playerID, friendID)
        self._executeQuery(insertQuery)
        return True

    def open(self):
        import sqlite3
        self.__conn = sqlite3.connect(self.__dbPath)
        cur = self.__conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS connection (connection_id INTEGER PRIMARY KEY, connection_uuid TEXT, game_uuid TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS player (player_id INTEGER PRIMARY KEY, display_name TEXT, friend_code TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS authenticated_players (player_id INTEGER, auth_token_type TEXT, auth_token TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS local_player_by_connection (local_player_uuid TEXT, connection_uuid TEXT, player_id INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS player_data (player_id INTEGER, game_uuid TEXT, data TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS player_friends (player_id INTEGER, friend_id INTEGER, alias TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS player_by_device (device_uuid text, player_id INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS session (session_id INTEGER PRIMARY KEY, game_uuid TEXT, display_name TEXT, creation_date DATE, expiry_date DATE, share_code TEXT, min_players INTEGER, max_players INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS player_by_session (session_id INTEGER, player_id INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS local_session_by_connection (local_session_uuid TEXT, connection_uuid TEXT, session_id INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS session_data (session_id INTEGER, data TEXT)")
        cur.close()

    def close(self):
        self.__conn.commit()
        self.__conn.close()
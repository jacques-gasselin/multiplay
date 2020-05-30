'''
    Client-Server API and Connection Tests (with JSON formatted responses)

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

import pathfix
pathfix.fix_sys_path()

import unittest
from multiplay import backend

class TestBackend(object):
    def test_open(self):
        db = self._createInstance()
        db.open()

    def test_close(self):
        db = self._createInstance()
        db.open()
        db.close()

    def test_connect(self):
        db = self._createInstance()
        db.open()
        token = db.connect("0.0.0.0:1234", "12345678-1234-5678-1234-567812345678")
        self.assertTrue(token is not None)
        token2 = db.connect("0.0.0.0:1234", "12345678-1234-5678-1234-567812345678")
        self.assertEqual(token, token2)
        token3 = db.connect("0.0.0.1:1234", "12345678-1234-5678-1234-567812345678")
        self.assertNotEqual(token, token3)

    def test_login(self):
        db = self._createInstance()
        db.open()
        conn = db.connect("0.0.0.0:1234", "12345678-1234-5678-1234-567812345678")
        self.assertTrue(conn is not None)
        localPlayer = db.login(conn, "00000000-0000-0000-0000-000000000000")
        self.assertTrue(localPlayer is not None)
        # differing device should not return same player, we can't rely on IP addresses only
        localPlayer2 = db.login(conn, "10000000-0000-0000-0000-000000000001")
        self.assertTrue(localPlayer2 is not None)
        self.assertNotEqual(localPlayer, localPlayer2)

    def test_writePlayerData(self):
        db = self._createInstance()
        db.open()
        conn = db.connect("0.0.0.0:1234", "12345678-1234-5678-1234-567812345678")
        self.assertTrue(conn is not None)
        localPlayer = db.login(conn, "00000000-0000-0000-0000-000000000000")
        self.assertTrue(localPlayer is not None)
        result = db.writePlayerData(conn, localPlayer, "testing")
        self.assertTrue(result)

    def test_readPlayerData(self):
        db = self._createInstance()
        db.open()
        conn = db.connect("0.0.0.0:1234", "12345678-1234-5678-1234-567812345678")
        self.assertTrue(conn is not None)
        localPlayer = db.login(conn, "00000000-0000-0000-0000-000000000000")
        self.assertTrue(localPlayer is not None)
        result = db.writePlayerData(conn, localPlayer, "testing")
        self.assertTrue(result)
        result = db.readPlayerData(conn, localPlayer)
        self.assertEqual(result, "testing")

    def test_modifyPlayerData(self):
        db = self._createInstance()
        db.open()
        db.logging = True
        conn = db.connect("0.0.0.0:1234", "12345678-1234-5678-1234-567812345678")
        self.assertTrue(conn is not None)
        localPlayer = db.login(conn, "00000000-0000-0000-0000-000000000000")
        self.assertTrue(localPlayer is not None)
        result = db.writePlayerData(conn, localPlayer, "testing")
        self.assertTrue(result)
        result = db.readPlayerData(conn, localPlayer)
        self.assertEqual(result, "testing")
        result = result + "2"
        self.assertEqual(result, "testing2")
        result = db.writePlayerData(conn, localPlayer, result)
        self.assertTrue(result)
        result = db.readPlayerData(conn, localPlayer)
        self.assertEqual(result, "testing2")

    def test_setDisplayName(self):
        db = self._createInstance()
        db.open()
        conn = db.connect("0.0.0.0:1234", "12345678-1234-5678-1234-567812345678")
        self.assertTrue(conn is not None)
        localPlayer = db.login(conn, "00000000-0000-0000-0000-000000000000")
        self.assertTrue(localPlayer is not None)
        result = db.setPlayerDisplayName(conn, localPlayer, "player 1")
        self.assertTrue(result)
        result = db.getPlayerDisplayName(conn, localPlayer)
        self.assertEqual(result, "player 1")

class TestPickleBackend(unittest.TestCase, TestBackend):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        self.__dbPath = ".pickle_backend.test"

    def _createInstance(self):
        return backend.PickleBackend(self.__dbPath)

class TestSqlite3Backend(unittest.TestCase, TestBackend):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        self.__dbPath = ".sqlite3_backend.test.db"

    def _createInstance(self):
        return backend.Sqlite3Backend(self.__dbPath)

if __name__ == '__main__':
    unittest.main()

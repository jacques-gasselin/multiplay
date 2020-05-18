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

import json
import uuid
import urllib.request
import urllib.parse

import unittest

gameUUID = uuid.UUID("12345678-1234-5678-1234-567812345678")
localDeviceUUID = uuid.uuid1(clock_seq=0)
#host = "multiplay.ludo.digital"
host = "localhost"
port = 12345

def _get_json_server_response(command, args):
    argsStr = urllib.parse.urlencode(args)
    r = urllib.request.urlopen("http://%s:%s/%s?%s" % (host, port, command, argsStr))
    response = r.read()
    return json.loads(response.decode())

class TestServerConnection(unittest.TestCase):
    
    def test_connect(self):
        response = _get_json_server_response("connect", { 'game' : gameUUID })
        self.assertTrue('connectionToken' in response)

    def test_login(self):
        connectionUUID = _get_json_server_response("connect", { 'game' : gameUUID })['connectionToken']
        response = _get_json_server_response("login", { 'connection' : connectionUUID, 'localDevice' : localDeviceUUID })
        self.assertTrue('localPlayerToken' in response)

    def test_writePlayerData(self):
        connectionUUID = _get_json_server_response("connect", { 'game' : gameUUID })['connectionToken']
        localPlayerUUID = _get_json_server_response("login", { 'connection' : connectionUUID, 'localDevice' : localDeviceUUID })['localPlayerToken']
        response = _get_json_server_response("writePlayerData", { 'connection' : connectionUUID, 'localPlayer' : localPlayerUUID, 'data' : "test" })
        self.assertFalse('error' in response)
        self.assertTrue('status' in response)

    def test_readPlayerData(self):
        connectionUUID = _get_json_server_response("connect", { 'game' : gameUUID })['connectionToken']
        localPlayerUUID = _get_json_server_response("login", { 'connection' : connectionUUID, 'localDevice' : localDeviceUUID })['localPlayerToken']
        _get_json_server_response("writePlayerData", { 'connection' : connectionUUID, 'localPlayer' : localPlayerUUID, 'data' : "test" })
        response = _get_json_server_response("readPlayerData", { 'connection' : connectionUUID, 'localPlayer' : localPlayerUUID})
        self.assertTrue('data' in response)
        self.assertEqual("test", response['data'])

    def test_erasePlayerData(self):
        connectionUUID = _get_json_server_response("connect", { 'game' : gameUUID })['connectionToken']
        localPlayerUUID = _get_json_server_response("login", { 'connection' : connectionUUID, 'localDevice' : localDeviceUUID })['localPlayerToken']
        _get_json_server_response("writePlayerData", { 'connection' : connectionUUID, 'localPlayer' : localPlayerUUID, 'data' : "" })
        response = _get_json_server_response("readPlayerData", { 'connection' : connectionUUID, 'localPlayer' : localPlayerUUID})
        self.assertTrue('data' in response)
        self.assertEqual("", response['data'])

    def test_incrementPlayerScore(self):
        connectionUUID = _get_json_server_response("connect", { 'game' : gameUUID })['connectionToken']
        localPlayerUUID = _get_json_server_response("login", { 'connection' : connectionUUID, 'localDevice' : localDeviceUUID })['localPlayerToken']
        playerData = { "score" : 0 }
        _get_json_server_response("writePlayerData", { 'connection' : connectionUUID, 'localPlayer' : localPlayerUUID, 'data' : json.dumps(playerData)})
        response = _get_json_server_response("readPlayerData", { 'connection' : connectionUUID, 'localPlayer' : localPlayerUUID})
        self.assertTrue('data' in response)
        data = json.loads(response['data'])
        score = int(data['score'])
        data['score'] = str(score + 1)
        response = _get_json_server_response("writePlayerData", { 'connection' : connectionUUID, 'localPlayer' : localPlayerUUID, 'data' : json.dumps(data) })
        response = _get_json_server_response("readPlayerData", { 'connection' : connectionUUID, 'localPlayer' : localPlayerUUID})
        data = json.loads(response['data'])
        self.assertEqual(1, int(data['score']))

if __name__ == '__main__':
    unittest.main()

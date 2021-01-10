                **multiplay**
                **Framework for multiplayer games**
                Jacques Gasselin,
                Copyright 2018


Design
======

Each platform defines its own API and ecosystem for managing Players and Games. Most of them are incompatible and have severe platform bugs. This framework move the responsibility of fixing the bugs to the community and to allow cross platform gaming.

Types
=====

The Client - Server connection is based on a few base types

 Name       | Range    | Description
------------|----------|-----------------
 Boolean    |  [0, 1]  | 0=False, !0=True
 String     |  char[]  | A variable length array of unicode characters.
 Data       |  byte[]  | A variable length array of bytes.
 UUID       |  Base16  | 128bit UUID, represented as 32 hexadecimals in URLs, or 8 bytes when connected via a socket
 List<UUID> |   N/A    | A comma separated list of UUIDs.
 IPAddress  |  IPv6    | 128bit unsigned number, as 32 hexadecimals grouped in to 4 digits separated by colons, or 8 bytes when connected via a socket
 Port       | [0,2^32] | A port number to combine with an IPAddress for a socket connection
  [Client-Server types]

Response Formats
================

All URL requests support an option argument *response* (encoded as the suffix of the endpoint). If the format is omitted the type is assumed to be binary and
the response is pure bytes.

Supported formats:

- `.json`
- `.plist`

### Examples

For a JSON response you would add the `.json` suffix to the endpoint.
> /connect.json?game=gameUUID

For a plist response you would add the `.plist` suffix to the endpoint. 
> /connect.plist?game=gameUUID

For a pure bytes response you would omit a suffix for the endpoint.
> /connect?game=gameUUID

HTTP Request Methods
====================

The following request methods are supported. Each has a specific purpose and should only be used for that express purpose.

Method      | Use
------------|---------------------------
GET         |  Reads an entry from an endpoint
POST        |  Appends or adds to an entry at an endpoint
PUT         |  Replaces an entry at an endpoint
DELETE      |  Removes an entry at an endpoint
CONNECT     |  For session P2P connection only.  


Connect the Game
=================

Call the API with the game server URL and the game UUID. The UUID is purely a token that the server and client has agreed upon. GameConnectionToken is returned that is used for all communication between the game and the server from this point onward.

```
***********************************************
* .--------.                        .--------.
* |        +----connect:gameUUID--->|        |
* |  Game  |                        | Server |
* |        |<----connectionUUID-----+        |
* '--------'                        '--------'
*
***********************************************
```

Client Side:

   *URL Request*

~~~ http
GET /connect?game=$gameUUID HTTP/1.0
~~~

   *Response*:

   connectionToken : UUID
   
   json
~~~ json
{ "connectionToken" : UUID }
~~~

   plist
~~~ xml
<dict>
  <key>connectionToken</key>
  <string>UUID</string>
</dict>
~~~

Server Side:

 1. Lookup game UUID in database
 1. If not found return an empty UUID
 1. If found generate a connection UUID, that does not clash with other current or stale connnections, with a timeout
 1. Clear out all stale connections for the game UUID
 1. Return the connection UUID

This handshake allows the server to manage load and by assigning tokens
it can ensure that only active connections are serviced in case of
rogue clients.

A server may choose to allow connections for games that are not already registered. This is great for development of games or for learning focused platforms that want to offer multiplayer services.

Connect the Local Player
========================

Use the GameConnectionToken to create a player, or fetch the last used player, with the localDeviceUUID.
For iOS this would be the same as [[UIDevice currentDevice].identifierForVendor UUIDString]

```
****************************************************************
*   .---------.                                    .--------.
*   |         +----login:connection,localDevice--->|        |
*   |  Game   |                                    | Server |
*   |         |<-----localplayerTokenUUID----------+        |
*   '---------'                                    '--------'
*        ^
*        |
*  localDeviceUUID
*        |
*        |
*    .---+----.
*   |          |                                    
*   |  Device  |                                    
*   |          |                                    
*    '--------'                                    
*
****************************************************************
```

Client Side:

   *URL Request*

~~~ http
GET /login?connection=$connectionToken&localDevice=$localDeviceUUID HTTP/1.0
~~~

   *Response*:
   
   localPlayerToken : UUID
   
   json
~~~ json
{
  "localPlayerToken" : UUID,
  "displayName" : String,
  "friendCode" : String
}
~~~
   
   plist
~~~ xml
<dict>
  <key>localPlayerToken</key>
  <string></string>
  <key>displayName</key>
  <string></string>
  <key>friendCode</key>
  <string></string>
</dict>
~~~

Server Side:

~~~ sql
   SELECT P.localPlayerToken, P.connectionTime, P.deviceUUID
   FROM playerTokenConnectionTimeAndDeviceUUIDByConnectionToken AS P
   WHERE P.connectionToken = $connectionToken
~~~
   1. Resolve if there are stale connections based on the connection time being stale.
      Remove the stale connections from the table so that no more requests are serviced on
      a stale connection
   1. If there are multiple connections invalidate all that are not for the given device id
   1. If there is a valid connection for the given device return that and refresh the connection time.
   1. If there are no connections insert a new unique one into the table and return that playerToken.
      This involves selecting from the playerByDevice Table and returning a token for the last used
      player for that device.
      Or if there are no players associated with that device returning a new one.

>    There may be multiple tokens for a single player. Such that play can begin under one
>    anonymous player and then be merged by some authenticated login to another existing player.
>    This is a common game affordance to avoid locking a player into a login flow when they first start a game.

This flow relies on the game being able to provide a stable UUID for the device. If a user has chose to forget settings on the device the UUID should have been regenerated and a new anonymous login would occurr.

Write Data for the Local Player
================================

A game will often want to write data for the local player in the cloud.
With a valid connectionToken and localPlayerToken we should be abe to save a binary blob of data.
This completely replaces the data that was there before.

Client Side:

   *URL Request*:

PUT
~~~ http
PUT /playerData HTTP/1.0
Content-Type: application/x-www-form-urlencoded

connection=$connectionToken&localPlayer=$localPlayerToken&data=$data
~~~

   *Reponse*
  
   status : Boolean
   
   binary
~~~ binary
   0 | 1
~~~
   
   json
~~~ json
{ "status" : (0|1) }
~~~

   plist  
~~~ xml
<dict>
  <key>status</key>
  <true|false />
</dict>
~~~

Append Data for the Local Player
================================

A game will often want to just modify or append some data for the local player in the cloud.
With a valid connectionToken and localPlayerToken we should be abe to save a binary blob of data.
This appends or composes with the data that was there before.

Client Side:

*URL Request*:

POST
~~~ http
POST /playerData HTTP/1.0
Content-Type: application/x-www-form-urlencoded

connection=$connectionToken&localPlayer=$localPlayerToken&data=$data
~~~

*Reponse*

status : Boolean

binary
~~~ binary
   0 | 1
~~~

json
~~~ json
{ "status" : (0|1) }
~~~

plist
~~~ xml
<dict>
  <key>status</key>
  <true|false />
</dict>
~~~

Read Data for the Local Player
=================================

Retrieve a blob of local player data for the game.

Client Side:

   *URL Request*:

~~~ http
GET /playerData?connection=$connectionToken&localPlayer=$localPlayerToken HTTP/1.0
~~~

   *Response*
   
   data : Data

   binary
~~~ binary
   Data
~~~

   json
~~~ json
{ "data" : Data }
~~~

   plist
~~~ xml
<dict>
  <key>data</key>
  <data>Data</data>
</dict>
~~~

The returned data will be empty if there was no data to retrieve. The potential for an error in the connection may be needed too to have a status.

Delete Data for the Local Player
================================

Removes local player data for the game.

Client Side:

*URL Request*:

~~~ http
DELETE /playerData?connection=$connectionToken&localPlayer=$localPlayerToken HTTP/1.0
~~~

*Reponse*

status : Boolean

binary
~~~ binary
   0 | 1
~~~

json
~~~ json
{ "status" : (0|1) }
~~~

plist
~~~ xml
<dict>
  <key>status</key>
  <true|false />
</dict>
~~~

Starting a Session
==================

A session is a server state instance than can be shared among players. This is used for saving data in a shared game. As this is possibly shared among players the easiest way to manage atomicity is to treat it like a key value store. There exists a binary blob for each key. There is no merging of data, and last in wins if two connections write to the same key.

Client Side:

   *URL Request*
   
~~~ http
POST /sessions HTTP/1.0
Content-Type: application/x-www-form-urlencoded

connection=$connection&localPlayer=$localPlayer&displayName=$displayName
~~~
   
   *Response*
   
   localSessionToken : UUID

   json
~~~ json
{ 
  "localSessionToken" : UUID,
  "displayName" : String,
  "shareCode" : String
}
~~~
   
   plist
~~~ xml
<dict>
  <key>localSessionToken</key>
  <string></string>
  <key>displayName</key>
  <string></string>
  <key>shareCode</key>
  <string></string>
</dict>
~~~

Server Side:

   1. Create a new session for the player.


Get List of Sessions for the Local Player
=========================================

Get the sessions that the player is in currently.
This may be session the player created or another player created and then added the local the player to.

Client Side:

   *URL Request*
   
~~~ http
GET /sessions?connection=$connectionToken&localPlayer=$localPlayerToken HTTP/1.0
~~~

   *Response*

   sessionTokens : List<UUID>

Leave a session and destroy if empty
====================================

Leave a session that the local player is in. If that session is
now empty; remove it from the server.

Client Side:

   *URL Request*

~~~ http
DELETE /sessions?connection=$connectionToken&localPlayer=$localPlayerToken&session=$sessionToken HTTP/1.0
~~~

   *Response*

   status : Boolean

Write State to a Session
========================

Write data to a key for the session.

The `key` argument is optional. If `key` is missing an empty key is used.

An empty key is a valid and can be used for session wide state.

Client Side:

   *URL Request*
    
~~~ http
PUT /sessionData HTTP/1.0
Content-Type: application/x-www-form-urlencoded

connection=$connectionToken&session=$sessionToken&key=$key&data=$data
~~~

   *Response*

   status : Boolean

Append State to a Session
=========================

Appends data to the session data for `key`. 

Client Side:

   *URL Request*

~~~ http
POST /sessionData HTTP/1.0
Content-Type: application/x-www-form-urlencoded

connection=$connectionToken&session=$sessionToken&key=$key&data=$data
~~~

   *Response*

   status : Boolean


Read State from a Session
=========================

Read data from a key for the session.

The `key` argument is optional. If `key` is missing an empty key is used.

An empty key is a valid and can be used for session wide state.

Client Side:

   *URL Request*

~~~ http
GET /sessionData?connection=$connectionToken&session=$sessionToken&key=$key HTTP/1.0
~~~

   *Response*

   data : Data

Add a player to a session
=========================

A session is created with only one player, the only way to add players is to invite them.

Client Side:

   *URL Request*

~~~ http
POST /sessionPlayers HTTP/1.0
Content-Type: application/x-www-form-urlencoded

connection=$connectionToken&session=$sessionToken&player=$remotePlayerToken
~~~
   *Response*
   
   status : Boolean

>   `remotePlayerToken` is the token of a player other than the local player to add to the session.

Remove a player from a session
==============================

Client Side:

   *URL Request*

~~~ http
DELETE /sessionPlayers?connection=$connectionToken&session=$sessionToken&player=$remotePlayerToken
~~~

   *Response*

   status : Boolean

>   `remotePlayerToken` is the token of a player other than the local player to remove from the session.


Create Peer-to-Peer Connection with Player in Session
=====================================================

Client Side:

   *URL Request*
   
~~~ http
CONNECT /sessionPlayers?connection=$connectionToken&session=$sessionToken&player=$remotePlayerToken
~~~
   
   *Response*
   
   address : IPAddress
   port : Port
   INETADDR

>   `remotePlayerToken` is the token of a player other than the local player to directy connect to.

This connection may be truly peer-to-peer but if reachability is an issue it may be tunneled through a STUN or TURN server. An implementation detail the client does not need to worry about.


<!-- Markdeep: -->
<style class="fallback">body{visibility:hidden;white-space:pre;font-family:monospace}</style>
<script src="markdeep.min.js"></script>
<script src="https://casual-effects.com/markdeep/latest/markdeep.min.js?"></script>
<script>window.alreadyProcessedMarkdeep||(document.body.style.visibility="visible")</script>

multiplay
=========

Framework for multiplayer games

- Client API language bindings
  - Java
  - JavaScript
  - Python
  - Swift
- Server implementations for you to host your own server.

See DESIGN.md for more details on the overall design.

Go to each language binding folder's README.md for detailed information on that language binding. 

----

To quickly test how the server works

> python3 python/multiplay/simple_http_server.py

You can then browse to http://localhost:12345/application/chat.html

Try logging in a user, creating a session and chatting. 

Or run the tests

> python3 python/test/test_json_responses.py

----

Swift Package Manager
---------------------

To test out the Swift bindings you can run the following at the project root.

> swift run


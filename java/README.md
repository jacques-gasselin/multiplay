Abstract
========

Java bindings to multiplay should:
- abstract away all network requests.
- take and return Java objects rather than buffers whenever possible
- use java.nio objects for all buffer objects
- use java.concurrent objects for all async behaviors

Building
========

Ant
---

Simply run `ant` from the command line.
> ant

The `build.xml` file in this directory contains all the instructions for building, testing and deploying the project

Targets:
- `build` - builds the project and puts the .jar files in the `dist` folder
- `test` - runs the tests and puts the reports in `test_reports`
- `clean`
- `javadoc` - compiles the documentation in  the `docs` folder
- `run-chat` - runs the Chat client demo.

This command will list all public targets that you can run
> ant -p


Testing
=======

JUnit
-----

Run the JUnits in the `test` folder.

Using ant
> ant test

Demos
-----

All the demos can run against a local server or a remote server.

The default serverURL is `http://localhost:12345`

If you want to test against another server just specify the server protocol, host and port on the command line.

Commandline
-----------

Options:
- `-v,--verbose`  Enable verbose logging.
- `--protocol` One of `http`, `https`. Default is `http`
- `-h,--host`  Hostname of the server. Default is `localhost`
- `-p,--port`  Port to use. Default is `12345`

Example:

> java -cp demo_build:build org.multiplay.chat.Chat --verbose

Ant
---

Properties:
- `demo.protocol`
- `demo.host`
- `demo.port`

Example:

> ant -Ddemo.host=multiplay.my.domain run-chat


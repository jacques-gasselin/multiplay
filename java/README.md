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
> `> ant`

The `build.xml` file in this directory contains all the instructions for building, testing and deploying the project

Targets:
- `build` - builds the project and puts the .jar files in the `dist` folder
- `test` - runs the tests and puts the reports in `test_reports`
- `clean`
- `javadoc` - compiles the documentation in  the `docs` folder

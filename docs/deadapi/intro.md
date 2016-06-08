Introduction
============

`deadapi` provides the HTTP API used by the web management and monitoring interface, and the provided commandline interface. Thereby bridges the outside world and the database via a simple CRUD REST API.

It supports pushing events via a streamed long-running HTTP response, in accordance with the [Server-sent events/Eventsource specification](http://www.w3.org/TR/eventsource). Events are triggered via [the LISTEN/NOTIFY pub/sub mechanism in Postgres](https://www.postgresql.org/docs/9.5/static/libpq-notify.html), and the database in turn contains triggers that send a NOTIFY on certain table row changes. Therefore data changes can bubble all the way to clients, which can use the standard Eventsource API to subscribe to these.

It provides a quick way to stage firmware updates: a firmware image together with a list of controller IDs can be uploaded, and `deadapi` simply drops (or links) the file into subfolders dedicated to the given controllers (see [Common files](../cfiles)).

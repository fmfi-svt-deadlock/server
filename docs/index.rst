Deadlock server: centralized "manager" of the system
====================================================


The server performs the following functions:

- holds the authoritative version of the access rules
  - also generates the offline database for controllers
- collects access logs
- provides software updates and time synchronization for the other devices
- monitors system state (and reports it to the management UIs)
- provides an API for the outside world (and all our tools).

Except for the contents of the database, it is entirely stateless. This simplifies the code and makes replication and failover trivial.

The server is separated into 3 independent modules: ``deadserver`` (communicates with controllers), ``deadapi`` (API for the outside world), and ``deadaux`` (auxiliary jobs).

Contents:

Concepts and common abstractions:
---------------------------------

.. toctree::
   :maxdepth: 2
   :caption: Start here

   intro
   cfiles


Communication with controllers:
-------------------------------

.. toctree::
   :maxdepth: 2
   :caption: deadserver

   deadserver/index


HTTP API for the outside world:
-------------------------------

.. toctree::
   :maxdepth: 2
   :caption: deadapi

   deadapi/index


Auxiliary jobs supporting the other components:
-----------------------------------------------

.. toctree::
   :maxdepth: 2
   :caption: deadaux

   deadaux/index


.. Indices and tables
.. ==================
..
.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`


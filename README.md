Nullboard-Backups-Server
========================

Simple [Nullboard](https://nullboard.io/preview)
[Backups](https://nullboard.io/backups) Server in Python3 (using
[Flask](https://flask.palletsprojects.com/)).

Installation
------------

To install, simply download, configure (see below), and run `nbbkps.py`.

```sh
$ wget https://raw.githubusercontent.com/7heo/nullboard-backups-server/master/nbbkps.py
$ ./nbbkps.py
```

Proper deployment
-----------------

It is possible to deploy this software by following the [Official Flask
Documentation on Deployments to
Production](https://flask.palletsprojects.com/en/2.3.x/deploying/).

Configuration
-------------

The configuration happens directly in the source of `nbbkps.py`, at the
beginning of the file. Once these options are properly set (make sure you set
the backup directory in a place that isn't world-readable, especially not in
the `www` root), you can start administering the server.

Administration
--------------

TBD.

Backups structure
-----------------

Nullboard-Backups-Server tried as much as possible to take inspiration from the
[Nullboard Agent](https://github.com/apankrat/nullboard-agent) in its
functionality and structure.

Therefore Nullboard-Backups-Server creates the same structure under the
location of the backup directory (configured in "Configuration").

Connecting to the Nullboard.io instance
---------------------------------------

To connect to the Nullboard.io instance of your choice, follow the steps
described in the [Official Nullboard backups page for local
backups](https://nullboard.io/backups#setup), but use the endpoints of your
nbbkps instance in the `URL` field, and any token you want (tokens aren't
implemented yet) in the `Access token` field.

FAQ
---

### Does Nullboard-Backups-Server support synchronization?

No, because Nullboard.io does not support synchronization. However, there are
[plans](https://github.com/apankrat/nullboard/issues/2#issuecomment-498276772)
for such a feature, so it might happen in the future.

### Can it support multiple users?

No, it is not implemented yet. In a future version, this will be possible.

### Is this secure?

There was some effort to write this software in a way that wouldn't encourage
abuse (especially wrt user input), but there was no effort made, yet, to ensure
the absence of exlpoits/vulnerabilities.

In addition, this software allows the users (anyone, currently, as tokens
aren't implemented!) to upload arbitrary content (but not with arbitrary file
names) to your server, so it is best to place the backup directory **outside**
of the `www` root.

In short, this can be relatively safely deployed in your LAN, but I would
personally audit it and report & correct bugs before deploying it publicly.

There are plans in the future to audit and correct any vulnerabilities found.

Contributing
------------

Feel free to open PRs against this repository, but do not expect them to be
merged unconditionally.

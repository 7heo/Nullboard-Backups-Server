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
beginning of the file. Once these options are properly set (make sure you
**change the secrets** and set the backup directory in a place that isn't
world-readable, especially not in the `www` root), you can start administering
the server.

Administration
--------------

To administer the server, you can use the following endpoints under the
`/admin` endpoint with parameters `x-www-form-urlencoded`:

- `/admin/new-token`: To create a new token. The required parameters are
		      `login`, `password` and `user`. The `user` parameter is
		      the name of the user to create a token for. It must be
                      unique.
- `/admin/get-token`: To get an existing token for a known user name. The
                      required parameters are `login`, `password` and `user`.
		      The `user` parameter is the name of the user for whom to
                      get the token. It must exist in the token list.
- `/admin/list-tokens`: To get the entire list of tokens, without user names.
                        The required parameters are `login` and `password`.
- `/admin/del-token`: To delete an existing token. The required parameters are
		      `login`, `password`, `user` and `token`. The `user`
		      parameter is the name of the user for whom to delete the
                      token, and the `token` parameter is the token to delete.
		      The both the `user` and the `token` must exist in the
		      token list, and `token` paramter *must* match the listed
                      token for the `user` passed in parameters.

*Note: All the `/admin` endpoints require the `login` and `password`
parameters. The must always match what is configured in the server script.*

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
nbbkps instance in the `URL` field, and the token you created via the admin
endpoint in the `Access token` field.

FAQ
---

### Does Nullboard-Backups-Server support synchronization?

No, because Nullboard.io does not support synchronization. However, there are
[plans](https://github.com/apankrat/nullboard/issues/2#issuecomment-498276772)
for such a feature, so it might happen in the future.

### Can it support multiple users?

Yes! Different users have to use different tokens, and they will write their
backups in different directories.

### Is this secure?

There was some effort to write this software in a way that wouldn't encourage
abuse (especially wrt user input), but there was no effort made, yet, to ensure
the absence of exlpoits/vulnerabilities.

In addition, this software allows the users (anyone with a valid token) to
upload arbitrary content (but not with arbitrary file names) to your server, so
it is best to place the backup directory **outside** of the `www` root.

In short, this can be relatively safely deployed in your LAN, but I would
personally audit it and report & correct bugs before deploying it publicly.

There are plans in the future to audit and correct any vulnerabilities found.

Contributing
------------

Feel free to open PRs against this repository, but do not expect them to be
merged unconditionally.

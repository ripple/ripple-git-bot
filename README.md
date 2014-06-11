Ripple Git Bot
==============

Handles basic build management for ripple development. When this script is run it will merge all pull requests that meet Ripple guidelines.

The script can also set up hooks to a server that will be sent information whenever this script needs to be called.

### Dependencies:

* Python 2.7 branch
* https://github.com/jacquev6/PyGithub
* Flask + gunicorn web API

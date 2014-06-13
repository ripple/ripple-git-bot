Ripple Git Bot
==============

Handles basic build management for ripple development. When this script is run it will merge all pull requests that meet Ripple guidelines.

The script can also set up hooks to a server that will be sent information whenever this script needs to be called.

### Dependencies:

* Python 2.7.X
* https://github.com/jacquev6/PyGithub
* https://pypi.python.org/pypi/Flask
* https://pypi.python.org/pypi/gunicorn/

### Setup Instructions:

1. Create an account on heroku
2. Download and install the heroku command line toolkit
3. Fork and clone this repository to your computer
4. Open up a command prompt and login to heroku:

		$ heroku login

5. Go to your cloned repository and set it up on heroku:

		$ cd Checkout/ripple-git-bot
		$ heroku create

6. Edit the config variables in your new repository:
	* Set "hookurl" to the url you just got from running "heroku create"
	* Set "orgname" to the name of the organization the bot will check (note that the bot must have access to this organization)
	* Set "cibotnames" to a list containing the usernames of the CI bots that update the status of the repositories
7. Create a GitHub account for the bot
8. Create a token for the bot with access to:
	* repo
	* public\_repo
	* write:org
	* write:repo\_hook
	* repo:status
	* read:org
	* read:repo\_hook
	* user
	* admin:org
	* admin:repo\_hook
9. Set the environment variable BOT_TOKEN in heroku to the token you just created
10. Push your cloned repository to your heroku server:

		$ git push heroku master

11. Visit the url of your heroku server to get the bot to add the initial hooks. You should see the message "GitHub pull requests succesfully analyzed."
12. You're done! The bot should now automatically manage your pull requests.

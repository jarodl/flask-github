flask-github
============

Flask-github is an extension for authenticating Flask applications with Github. It also provides support for various other requests to the Github API.

Installation
------------

	pip install flask-github

Usage
-------

An example application is provided. Getting it up and running should be pretty straightforward:

1. Create a new application on Github (or use an existing one)
2. Add the `client_id` and `client_secret` to `config.json`
3. Start the server:

		python example/example.py

Example App URLs
----------------

Redirect the user to authenticate with Github:

	http://localhost:5000/login

Check if the user is a member of an organization:

	http://localhost:5000/orgs/<organization_name>

Check if the user belongs to a certain team:

	http://localhost:5000/teams/<team_id>

API Requests
------------

After authenticating, this extension also provides methods for doing GET requests to the Github API as the authenticated user.

	github = GithubAuth(
    	client_id='123456789',
    	client_secret='987654321',
    	session_key='user_id'
	)

	# returns the authenticated user
	github.get_github_user()
	
	# returns true if the authenticated user is a member of the organization
	github.has_org_access('mindsnacks')

Options
-------

* `session_key` -- Key for the value stored in the session to determine if a user is logged in
* `client_id` -- Given by Github when creating an application
* `client_secret` -- Given by Github when creating an application

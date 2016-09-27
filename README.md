This repo has all the code necessary to run an instance of rabbitlol locally or in Google App Engine.

## Requirements

1. [Google App Engine SDK for Python](https://cloud.google.com/appengine/docs/python/download)
2. virtualenv-2.7
3. make

## Running Locally

Go to repo's root directory and run `make run`. You should be able to visit rabbitlol homepage at <http://localhost:8080> once all the necessary packages are fetched.

## Running on Google App Engine

Go to <https://console.cloud.google.com/appengine> and create yourself a project, save your project ID. Go to repo's root directory and run `PROJECT_ID=<your-project-id> make deploy`. Once all the packages are installed and you are authenticated, app will be uploaded to App Engine and you should be able to visit rabbitlol homepage at `https://<your-project-id>.appspot.com`

## How to make sign in work?

1. Update `rabbitlol_url` variable in `app/oauth.py` with your app's url (e.g. if you are running the app locally, update it to `http://localhost:8080`)
2. Create a Facebook/GitHub/Google/Twitter app. Set the callback URL for OAuth as `<your-app-url>/oauth/callback/<lower-case-service-name>`. For example, if you are running the app locally, the callback URL for GitHub is <http://localhost:8080/oauth/callback/github>.
3. Update the variables in `app/secrets.py` with the secrets you obtained in step 2.
4. If you are running the app in the App Engine, re-deploy the app.

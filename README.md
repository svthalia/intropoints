# Intropoints
Welcome to the Intropoints repository. This repository includes the application that can be used to set up an
online scavenger hunt. The application can be used to create Tournaments and Teams of Users for these Tournaments. 
Challenges can be created for each Tournament. The Challenges can be solved by the Teams by uploading a photo after
which an administrator needs to approve (or decline) a Submission for a Challenge. If a Submission is approved, the
Challenge is closed for that Team and points are awarded.

## Setup
This project is built using both [Django](https://www.djangoproject.com) (for the backend) and 
[VueJS](https://vuejs.org) (for the frontend). Both need to be set up (and connected) for development to work.

### Setup backend
1. First install at least [Python](https://www.python.org) 3.11 on your system.
2. If `pip3` is not installed on your system, execute `apt install python3-pip` to install it.
3. Also make sure `python3-dev` is installed on your system, execute `apt install python3-dev`.
4. Install Poetry by following the steps on
[their website](https://python-poetry.org/docs/#installing-with-the-official-installer). Make sure `poetry` is added 
to `PATH` before continuing.
5. Clone this repository.
6. Go to the `backend` directory.
7. Run `poetry install` to install the backend dependencies.
8. Run `poetry shell` to start a shell with the dependencies loaded. This command needs to be run every time you open
a new shell and want to run the development server.
9. Go to the `website` directory.
10. Run `./manage.py migrate` to initialize the database and load all migrations.
11. Run `./manage.py createsuperuser` to create an administrator user.
12. Run `./manage.py runserver` to start the development server locally.

Now your backend server is set up and running on `localhost:8000`. The administrator interface can be accessed by going
to `localhost:8000/admin`.

### Setup frontend
1. Install at least version 17 of [NodeJS](https://nodejs.org/en).
2. Clone this repository (or if you have done that in the previous steps, skip this step).
3. Go to the `frontend` directory.
4. Use `npm install` to install the required packages.
5. Use `npm run dev` to run the development server.

### Connecting the frontend to the backend
Now that both the frontend and the backend server are up and running, we need to supply the frontend with credentials
such that it can connect to the backend service.

1. Log in on the administrator dashboard of the backend by going to `localhost:8000/admin` and logging in with your
administrator account.
2. Under `Django OAuth Toolkit`, add an `Application`.
3. Provide the following settings: 
- Redirect uris: http://localhost:5173/auth/callback
- Client type: Public
- Authorization grant type: Implicit
- Name: VueJS Frontend
- Skip Authorization: True
4. Before saving the application, make sure to copy over the Client ID and Client Secret to some other location.
5. Now save the application.
6. Create a `.env` file in the `frontend` folder of the repository. The `.env` file should have the following content:
```
VITE_API_BASE_URI=http://localhost:8000
VITE_API_AUTHORIZATION_ENDPOINT=/oauth/authorize/
VITE_API_ACCESS_TOKEN_ENDPOINT=/oauth/token/
VITE_API_OAUTH_CLIENT_ID=[Client ID you copied over]
VITE_API_OAUTH_CLIENT_SECRET=[Client Secret you copied over]
VITE_API_OAUTH_REDIRECT_URI=http://localhost:5173/auth/callback
VITE_API_LOGOUT_URL=/users/logout
VITE_DEBUG=true
```
7. Reload the development server (`npm run dev`) and you are good to go :)!




# mclauncher

## Getting started

### Use Docker image

You can quickly start with pre-built docker image.

```bash
docker pull ghcr.io/nownabe-dev/mclauncher:latest
```

### Run on Google Cloud

You can run mclauncher on [Cloud Run](https://cloud.google.com/run) by clicking this button.

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)

* You should add `roles/compute.instanceAdmin.v1` for your Minecraft server instance to the service account used for the Cloud Run service. If you want to minimize permissions, you can create your own custom role.
* Firestore and Firebase Authentication must be initialized. For now, mclauncher supports only Google provider for Firebase Authentication.

### Configurations

Environment variables:

* `PORT` (required)
* `INSTANCE_ZONE` (required)
* `INSTANCE_NAME` (required)
* `SHUTTER_AUTHORIZED_EMAIL` (required) - email of service account which calls `/shutter`.
* `FIREBASE_CREDENTIALS_JSON` (required) - used for Firebase Authentication and Firestore.
* `FIREBASE_CONFIG_JSON` (required)
* `TITLE` (optional) - default is `mclauncher`.
* `WEB_CONCURRENCY` (optional) - default is `4`.
* `SHUTTER_COUNT_TO_SHUTDOWN` (optional) - If the count of consecutive vacant of the server counted by `/shutter` exceeds this count, `/shutter` shuts down the instance.

## Development on Codespaces

Install dependencies with [poetry](https://python-poetry.org/).

```bash
poetry install
```

Run Firestore emulator.

```bash
firebase emulators:start
```

Set environment variables.

```bash
export FIREBASE_CONFIG_JSON='{"apiKey":"...", ...}'
export FIREBASE_CREDENTIALS_JSON="$(cat firebase.credentials.json)"
export FIRESTORE_EMULATOR_HOST="localhost:8080"
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/gcpproject.credentials.json"
export INSTANCE_ZONE="asia-northeast1-a"
export INSTANCE_NAME="minecraft-instance"
export SHUTTER_AUTHORIZED_EMAIL="mclauncher@example.com"
```

If you haven't added your email as an authorized user, run `tools/add_authorized_users.py`.

```bash
poetry run python tools/add_authorized_users.py you@example.com
```

Run the development server.

```bash
poetry run uvicorn main:app --reload
```

Or you can run and debug with `Ctrl + Shift + D`.

You can forward ports. See the detail: [Forwarding ports in your codespace - GitHub Docs](https://docs.github.com/en/codespaces/developing-in-codespaces/forwarding-ports-in-your-codespace).

Test.

```bash
poetry run pytest
```

# mclauncher

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
export FIREBASE_CREDENTIALS_JSON="$(cat firebase.credentials.json)"
export FIRESTORE_EMULATOR_HOST="localhost:8080"
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/gcpproject.credentials.json"
export INSTANCE_ZONE="asia-northeast1-a"
export INSTANCE_NAME="minecraft-instance"
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

## Deploy

### Configurations

Environment variables:

* `PORT` (required)
* `INSTANCE_ZONE` (required)
* `INSTANCE_NAME` (required)
* `FIREBASE_CREDENTIALS_JSON` (required) - used for Firebase Authentication and Firestore.
* `TITLE` (optional) - default is `mclauncher`.
* `WEB_CONCURRENCY` (optional) - default is `4`.

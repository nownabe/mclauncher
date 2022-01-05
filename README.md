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

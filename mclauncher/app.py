'''Create app'''

from os import path
from typing import Callable

from fastapi import FastAPI, Request
from firebase_admin.auth import InvalidIdTokenError, CertificateFetchError, ExpiredIdTokenError, RevokedIdTokenError, UserDisabledError
from starlette.templating import Jinja2Templates
from starlette.responses import JSONResponse, HTMLResponse

from .api.v1 import app as v1

_AUTH_SCHEME = "Bearer"


def _authorize(app, verify_id_token: Callable, is_authorized_user: Callable[[str], bool]):
    """Create a middleware to authorize requests."""
    @app.middleware("http")
    async def _authorize(request: Request, call_next):
        id_token = request.headers["Authorization"][len(_AUTH_SCHEME)+1:]
        try:
            token = verify_id_token(id_token)
        except (ValueError, InvalidIdTokenError) as error:
            return JSONResponse(
                content={'error': f'invalid token: {error}'},
                status_code=400,
            )
        except (ExpiredIdTokenError, RevokedIdTokenError) as error:
            return JSONResponse(
                content={'error': f'invalid token: {error}'},
                status_code=403,
            )
        except (UserDisabledError, ) as error:
            return JSONResponse(
                content={'error': f'invalid user: {error}'},
                status_code=403,
            )
        except (CertificateFetchError,) as error:
            return JSONResponse(
                content={'error': f'internal server error: {error}'},
                status_code=500,
            )
        else:
            if is_authorized_user(token['email']):
                return await call_next(request)
            else:
                return JSONResponse(
                    content={'error': 'forbidden'},
                    status_code=403,
                )


def create_app(
        verify_id_token: Callable,
        is_authorized_user: Callable[[str], bool],
):
    app = FastAPI()
    templates = Jinja2Templates(
        directory=path.join(path.dirname(__file__), 'templates')
    )

    _authorize(
        app=v1,
        verify_id_token=verify_id_token,
        is_authorized_user=is_authorized_user
    )
    app.mount("/api/v1", v1)

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """
        The index page returns index.html.
        """
        return templates.TemplateResponse(
            "index.html",
            context={"request": request}
        )

    return app

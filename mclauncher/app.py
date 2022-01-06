'''Create app'''

from os import path
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from firebase_admin.auth import InvalidIdTokenError, CertificateFetchError, ExpiredIdTokenError, RevokedIdTokenError, UserDisabledError
from starlette import status
from starlette.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from mclauncher.instance import Instance

from mclauncher.minecraft import MinecraftProtocol

from .api.v1 import create_app as create_v1

_AUTH_SCHEME = "Bearer"


def _authorize(app, verify_id_token: Callable, is_authorized_user: Callable[[str], bool]):
    """Create a middleware to authorize requests."""
    @app.middleware("http")
    async def _authorize(request: Request, call_next):
        id_token = request.headers["Authorization"][len(_AUTH_SCHEME)+1:]
        try:
            token = verify_id_token(id_token)
        except (ValueError, InvalidIdTokenError) as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'invalid token: {error}',
            ) from error
        except (ExpiredIdTokenError, RevokedIdTokenError) as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'invalid token: {error}',
            ) from error
        except (UserDisabledError,) as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'invalid user: {error}',
            ) from error
        except (CertificateFetchError,) as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'internal server error: {error}',
            ) from error
        else:
            if is_authorized_user(token['email']):
                return await call_next(request)
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f'forbidden',
                )


def create_app(
        verify_id_token: Callable,
        is_authorized_user: Callable[[str], bool],
        connect_minecraft: Callable[[str], MinecraftProtocol],
        get_instance: Callable[[], Instance],
        start_instance: Callable[[], None],
):
    app = FastAPI()
    templates = Jinja2Templates(
        directory=path.join(path.dirname(__file__), 'templates')
    )

    v1 = create_v1(
        connect_minecraft=connect_minecraft,
        get_instance=get_instance,
        start_instance=start_instance,
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

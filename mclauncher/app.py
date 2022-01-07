'''Create app'''

from logging import getLogger
from os import path
from typing import Callable, Optional

from fastapi import FastAPI, Request, status, Header
from fastapi.exceptions import HTTPException
from firebase_admin.auth import InvalidIdTokenError, CertificateFetchError, ExpiredIdTokenError, RevokedIdTokenError, UserDisabledError
from starlette.templating import Jinja2Templates
from starlette.responses import HTMLResponse, JSONResponse
from mclauncher.instance import Instance

from mclauncher.minecraft import MinecraftProtocol

from .api.v1 import create_app as create_v1

_AUTH_SCHEME = "Bearer"
logger = getLogger('uvicorn')


def _authorize(app, verify_id_token: Callable, is_authorized_user: Callable[[str], bool]):
    """Create a middleware to authorize requests."""
    @app.middleware("http")
    async def _authorize(request: Request, call_next):
        try:
            id_token = request.headers["Authorization"][len(_AUTH_SCHEME)+1:]
            token = verify_id_token(id_token)
        except (KeyError,) as error:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={'detail': f'invalid header: {error}'}
            )
        except (ExpiredIdTokenError, RevokedIdTokenError) as error:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={'detail': f'invalid token: {error}'},
            )
        except (ValueError, InvalidIdTokenError) as error:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={'detail': f'invalid token: {error}'}
            )
        except (UserDisabledError,) as error:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={'detail': f'invalid user: {error}'},
            )
        except (CertificateFetchError,) as error:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={'detail': f'internal server error: {error}'},
            )
        else:
            if is_authorized_user(token['email']):
                return await call_next(request)
            else:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={'detail': 'forbidden'},
                )


def create_app(
        title: str,
        verify_id_token: Callable,
        is_authorized_user: Callable[[str], bool],
        connect_minecraft: Callable[[str], MinecraftProtocol],
        get_instance: Callable[[], Instance],
        start_instance: Callable[[], None],
        shutter_authorize: Callable[[str], bool],
        shutdown: Callable[[], None],
):
    app = FastAPI()
    templates = Jinja2Templates(
        directory=path.join(path.dirname(__file__), 'templates'),
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
            context={"request": request, "title": title}
        )

    @app.post("/shutter", status_code=status.HTTP_204_NO_CONTENT)
    async def _shutter(authorization: Optional[str] = Header(None)):
        if authorization is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="not authorized",
            )

        try:
            ok = shutter_authorize(authorization)
        except Exception as error:
            logger.error('shutter_authorize() in /shutter: %r', error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="internal server error"
            ) from error

        if not ok:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="forbidden",
            )

        try:
            await shutdown()
        except Exception as error:
            logger.error('shutdown() in /shutter: %r', error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="internal server error"
            ) from error

        return None

    return app

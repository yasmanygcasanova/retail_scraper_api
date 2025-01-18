import os
import time

import sentry_sdk
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from api.api import api_router
from auth.dependency.authorizer import AuthorizerDependency

load_dotenv()
DSN_SENTRY = os.getenv('DSN_SENTRY')

sentry_sdk.init(
    dsn=DSN_SENTRY,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0,
)

authorizer = AuthorizerDependency(key_pattern="API_KEY")
app = FastAPI(
    title="Cnovatech Scraper API",
    version="0.0.1",
    description="API para consultar o sortimento de produtos",
    contact={
        "name": "Support",
        "email": "contato@cnovatech.com.br",
    },
    dependencies=[Depends(authorizer)]
)
origins = ["service-scraping-kc2ppxkdgq-uc.a.run.app"]


@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f'{process_time:0.4f} sec')
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=[
        "localhost",
        "service-scraping-kc2ppxkdgq-uc.a.run.app",
        "service-database-kc2ppxkdgq-uc.a.run.app",
        "*.cnovatech.com.br"
    ]
)

app.include_router(api_router, prefix="/api/v1")

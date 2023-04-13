import motor
from azure.moitor.opentelemetry.exporter import AzureMonitorTraceExporter
from benie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
import os
from pathlib import Path

# CORS Origins
apiUrl = os.environ.get("REACT_APP_WEB_BASE_URL")
if apiUrl is not None:
    origins = ["https://portal.azure.com",
               "https://ms.azure.com",
                "https://localhost:3000",
                apiUrl]
    print("CORS Origins: ", origins[2], "is allowed for local host debugging. If you want to change pin number. go to, " ,Path(__file__))
else:
    origins = ["*"]
    print("Setting CORS to allow all origins because env var REACT_APP_WEB_BASE_URL is not set")

from .models import Settings, __beanie_models__

settings = Settings()

app = FastAPI(
    description="Todo API",
    version = "1.0.0",
    title="Todo API",
    docs_url="/"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

from . import routes

@app.on_event("startup")
async def startup_event():
    if settings.APPLICAIONINSIGHTS_CONNECTION_STRING:
        exporter = AzureMonitorTraceExporter.from_connection_string(
            settings.APPLICAIONINSIGHTS_CONNECTION_STRING
        )
        tracer = TracerProvider(
            resource=Resource.create({SERVICE_NAME: settings.APPLICATIONINSIGHTS_ROLENAME})
        )
        tracer.add_span_processor(BatchExportSpanProcessor(exporter))
        FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)

    client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.AZURE_COSMOS_CONNECTION_STRING
    )

    await init_beanie(
            database = client[settings.AZURE_COSMOS_DATABASE_NAME],
            document_models = __beanie_models__
    )

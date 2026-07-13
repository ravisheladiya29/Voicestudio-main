import asyncio
import secrets
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, status
from loguru import logger
from pydantic import BaseModel

from api.routes.agent_stream import router as agent_stream_router
from api.routes.auth import router as auth_router
from api.routes.campaign import router as campaign_router
from api.routes.credentials import router as credentials_router
from api.routes.folder import router as folder_router
from api.routes.knowledge_base import router as knowledge_base_router
from api.routes.node_types import router as node_types_router
from api.routes.organization import router as organization_router
from api.routes.organization_usage import router as organization_usage_router
from api.routes.public_agent import router as public_agent_router
from api.routes.public_download import router as public_download_router
from api.routes.public_embed import router as public_embed_router
from api.routes.reports import router as reports_router
from api.routes.s3_signed_url import router as s3_router
from api.routes.service_keys import router as service_keys_router
from api.routes.superuser import router as superuser_router
from api.routes.telephony import router as telephony_router
from api.routes.tool import router as tool_router
from api.routes.turn_credentials import router as turn_credentials_router
from api.routes.user import router as user_router
from api.routes.webrtc_signaling import router as webrtc_signaling_router
from api.routes.workflow import router as workflow_router
from api.routes.workflow_embed import router as workflow_embed_router
from api.routes.workflow_recording import router as workflow_recording_router
from api.routes.workflow_text_chat import router as workflow_text_chat_router
from api.services.integrations import all_routers

router = APIRouter(
    tags=["main"],
    responses={404: {"description": "Not found"}},
)

router.include_router(telephony_router)
router.include_router(superuser_router)
router.include_router(workflow_router)
router.include_router(workflow_text_chat_router)
router.include_router(user_router)
router.include_router(campaign_router)
router.include_router(credentials_router)
router.include_router(tool_router)
router.include_router(organization_router)
router.include_router(s3_router)
router.include_router(service_keys_router)
router.include_router(organization_usage_router)
router.include_router(reports_router)
router.include_router(webrtc_signaling_router)
router.include_router(turn_credentials_router)
router.include_router(public_embed_router)
router.include_router(public_agent_router)
router.include_router(public_download_router)
router.include_router(workflow_embed_router)
router.include_router(knowledge_base_router)
router.include_router(workflow_recording_router)
router.include_router(folder_router)
router.include_router(auth_router)
router.include_router(node_types_router)
router.include_router(agent_stream_router)

for _integration_router in all_routers():
    router.include_router(_integration_router)


class HealthResponse(BaseModel):
    status: str
    version: str
    backend_api_endpoint: str
    # Public URL the deployment is reachable at when it sits behind a Cloudflare
    # tunnel (the host has no public IP). null for a directly-reachable deployment.
    # The UI shows this so operators know the URL telephony providers should call.
    tunnel_url: str | None = None
    deployment_mode: str
    auth_provider: str
    turn_enabled: bool
    force_turn_relay: bool
    # Public Stack Auth client config — only populated when auth_provider == "stack".
    # The UI reads these at runtime to initialize Stack, so they no longer need to
    # be baked into the browser bundle at build time. Both are public values.
    stack_project_id: str | None = None
    stack_publishable_client_key: str | None = None
    # True when MPS_API_URL is set — Managed AI tab / Service Keys can reach a backend.
    managed_ai_enabled: bool = False


DEVOPS_SECRET_HEADER = "X-Devops-Secret"

HEALTH_TUNNEL_LOOKUP_TIMEOUT_SEC = 1.0


async def _resolve_tunnel_url_for_health() -> str | None:
    """Best-effort tunnel URL for /health without blocking on cloudflared."""
    from api.constants import BACKEND_API_ENDPOINT
    from api.utils.common import is_local_or_private_url
    from api.utils.tunnel import TunnelURLProvider

    if not is_local_or_private_url(BACKEND_API_ENDPOINT):
        return None

    try:
        tunnel_urls = await asyncio.wait_for(
            TunnelURLProvider.get_tunnel_urls(),
            timeout=HEALTH_TUNNEL_LOOKUP_TIMEOUT_SEC,
        )
    except Exception:
        return None

    if not tunnel_urls:
        return None

    resolved = tunnel_urls[0]
    if is_local_or_private_url(resolved):
        return None
    return resolved


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    from api.constants import (
        APP_VERSION,
        AUTH_PROVIDER,
        BACKEND_API_ENDPOINT,
        DEPLOYMENT_MODE,
        FORCE_TURN_RELAY,
        MPS_API_URL,
        STACK_AUTH_PROJECT_ID,
        STACK_PUBLISHABLE_CLIENT_KEY,
        TURN_SECRET,
    )

    logger.debug("Health endpoint called")
    tunnel_url = await _resolve_tunnel_url_for_health()
    is_stack = AUTH_PROVIDER == "stack"
    return HealthResponse(
        status="ok",
        version=APP_VERSION,
        backend_api_endpoint=BACKEND_API_ENDPOINT,
        tunnel_url=tunnel_url,
        deployment_mode=DEPLOYMENT_MODE,
        auth_provider=AUTH_PROVIDER,
        turn_enabled=bool(TURN_SECRET),
        force_turn_relay=FORCE_TURN_RELAY,
        stack_project_id=STACK_AUTH_PROJECT_ID if is_stack else None,
        stack_publishable_client_key=(
            STACK_PUBLISHABLE_CLIENT_KEY if is_stack else None
        ),
        managed_ai_enabled=bool(MPS_API_URL and MPS_API_URL.strip()),
    )


class ActiveCallsResponse(BaseModel):
    active_calls: int


def _verify_devops_secret(
    configured_secret: str | None,
    provided_secret: str | None,
) -> None:
    if not configured_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Devops secret is not configured",
        )
    if not provided_secret or not secrets.compare_digest(
        provided_secret,
        configured_secret,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )


@router.get("/health/active-calls", response_model=ActiveCallsResponse)
async def active_calls(
    x_devops_secret: Annotated[
        str | None,
        Header(alias=DEVOPS_SECRET_HEADER),
    ] = None,
) -> ActiveCallsResponse:
    """In-flight call count for THIS worker — the drain signal for deploys.

    A deploy orchestrator polls this per worker and waits for zero before
    sending SIGTERM, because uvicorn force-closes live call WebSockets (close
    code 1012) on SIGTERM and would cut calls mid-conversation otherwise. The
    count is per-process: one uvicorn per VM port (scripts/rolling_update.sh)
    or per Kubernetes pod (preStop hook). See api/services/pipecat/active_calls.py.
    """
    from api.constants import DEVOPS_SECRET
    from api.services.pipecat.active_calls import active_call_count

    _verify_devops_secret(DEVOPS_SECRET, x_devops_secret)
    return ActiveCallsResponse(active_calls=active_call_count())

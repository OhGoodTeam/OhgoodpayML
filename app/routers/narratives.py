# # routers/narratives.py
# import os
# from datetime import datetime, timezone
# from typing import Optional

# from fastapi import APIRouter, Header, HTTPException, Request
# from fastapi.responses import StreamingResponse

# from app.services.narratives.sse import sse, SSE_HEADERS
# from services.narratives.chat_intro import ChatIntroService
# from app.services.narratives.dashboard_advice import DashboardAdvisor
# from app.schemas.narratives import Snapshot, MetaPayload

# API_PREFIX = os.getenv("API_AI_PREFIX", "")
# INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN")

# router = APIRouter(prefix=f"{API_PREFIX}/v1/narratives", tags=["narratives"])

# def _check_token(x_internal_token: Optional[str]):
#     if INTERNAL_TOKEN and (not x_internal_token or x_internal_token != INTERNAL_TOKEN):
#         raise HTTPException(status_code=401, detail="invalid internal token")

# # @router.get("/intro/stream", response_class=StreamingResponse)
# # def intro_stream(
# #     request: Request,
# #     x_internal_token: Optional[str] = Header(default=None, alias="X-Internal-Token"),
# #     x_trace_id: Optional[str] = Header(default=None, alias="X-Trace-Id"),
# # ):
# #     _check_token(x_internal_token)

# #     def gen():
# #         meta = MetaPayload(
# #             traceId=x_trace_id,
# #             model=ChatIntroService.MODEL,
# #             context="chat",
# #             startedAt=datetime.now(timezone.utc).isoformat(),
# #         ).model_dump(exclude_none=True)
# #         yield sse(meta, event="meta")
# #         # 토큰 스트림
# #         for frame in ChatIntroService.stream_intro():
# #             yield frame
# #         yield sse({}, event="done")

# #     return StreamingResponse(gen(), media_type="text/event-stream", headers=SSE_HEADERS)

# @router.post("/advice/stream", response_class=StreamingResponse)
# def advice_stream(
#     snapshot: Snapshot,
#     request: Request,
#     x_internal_token: Optional[str] = Header(default=None, alias="X-Internal-Token"),
#     x_trace_id: Optional[str] = Header(default=None, alias="X-Trace-Id"),
#     x_snapshot_hash: Optional[str] = Header(default=None, alias="X-Snapshot-Hash"),
# ):
#     _check_token(x_internal_token)

#     def gen():
#         meta = MetaPayload(
#             traceId=x_trace_id,
#             model=DashboardAdvisor.MODEL,
#             context="dashboard",
#             startedAt=datetime.now(timezone.utc).isoformat(),
#             snapshot_hash=x_snapshot_hash,
#         ).model_dump(exclude_none=True)
#         yield sse(meta, event="meta")

#         # 비스트리밍으로 생성 → payload 이벤트로 한 번에 송출
#         payload = DashboardAdvisor.build_payload(snapshot, x_trace_id, x_snapshot_hash)
#         yield sse(payload.model_dump(), event="payload")

#         yield sse({}, event="done")

#     return StreamingResponse(gen(), media_type="text/event-stream", headers=SSE_HEADERS)

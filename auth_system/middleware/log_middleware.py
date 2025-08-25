import uuid
import json
from django.utils.deprecation import MiddlewareMixin
from constants import LOGIN_PORTALS
from auth_system.models import TblUser
from auth_system.models.login_session import LoginSession
import jwt
from django.conf import settings


class APILogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get("Authorization", "")
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
        request._token = token
        session_uuid = None
        if token:
            try:
                session = LoginSession.objects.filter(
                    token=token, is_active=True
                ).first()
                if session:
                    session_uuid = (
                        str(session.session_id)
                        if hasattr(session, "session_id")
                        else str(session.pk)
                    )
            except Exception as e:
                print(f"[Middleware] Error fetching session by token: {e}")
        if session_uuid:
            request.uniqid = session_uuid
            request.session["session_uuid"] = session_uuid
            request.session.modified = True
        else:
            new_uuid = str(uuid.uuid4())
            request.uniqid = new_uuid
            request.session["session_uuid"] = new_uuid
            request.session.modified = True
        try:
            if request.body:
                request._body_data = json.loads(request.body.decode("utf-8"))
            else:
                request._body_data = {}
        except Exception:
            request._body_data = {}
        request._query_params = _flatten_querydict(
            request.GET,
            exclude_keys=[
                "page",
                "page_size",
                "limit",
                "offset",
            ],
        )

    def process_response(self, request, response):
        try:
            path = request.path_info
            method = request.method
            user = getattr(request, "user", None)
            user_obj = user if user and user.is_authenticated else None
            app_name = None
            if path == "/api/auth_system/login/":
                if (
                    response.status_code == 200
                    and hasattr(response, "content")
                    and response.get("Content-Type", "").startswith("application/json")
                ):
                    try:
                        data = json.loads(response.content.decode("utf-8"))
                        new_uuid = data.get("session_uuid")
                        if new_uuid:
                            request.uniqid = new_uuid
                            request.session["session_uuid"] = new_uuid
                            request.session.modified = True
                    except Exception as e:
                        print(f"[Middleware] Failed to parse login response UUID: {e}")
                portal_id = int(request._body_data.get("portal_id", 1))
                app_name = next(
                    (
                        key.lower()
                        for key, val in LOGIN_PORTALS.items()
                        if val == portal_id
                    ),
                    "auth_system",
                )
                if not user_obj:
                    username = request._body_data.get("username")
                    if username:
                        try:
                            if username.isdigit() and len(username) == 10:
                                user_obj = TblUser.objects.filter(
                                    mobile_number=username
                                ).first()
                            elif "@" in username:
                                user_obj = TblUser.objects.filter(
                                    email=username
                                ).first()
                            else:
                                user_obj = TblUser.objects.filter(
                                    username=username
                                ).first()
                        except Exception:
                            user_obj = None
            elif path == "/api/auth_system/logout/":
                token = request._token
                portal_id = None
                if token:
                    try:
                        decoded = jwt.decode(token, options={"verify_signature": False})
                        # portal_id = decoded.get("portal_id")
                        portal_id = int(decoded.get("portal_id") or 0)

                        app_name = next(
                            (
                                key.lower()
                                for key, val in LOGIN_PORTALS.items()
                                if val == portal_id
                            ),
                            "auth_system",
                        )
                        session = LoginSession.objects.filter(
                            token=token, is_active=True
                        ).first()
                        if not user_obj and session and hasattr(session, "user"):
                            user_obj = session.user
                    except Exception as e:
                        print(
                            f"[Middleware] Error decoding token or fetching session: {e}"
                        )
                        app_name = "auth_system"
                else:
                    app_name = "auth_system"
            else:
                if path.startswith("/api/ems/"):
                    app_name = "ems"
                elif path.startswith("/api/cms/"):
                    app_name = "cms"
                elif path.startswith("/api/lead/"):
                    app_name = "lead"
                elif path.startswith("/api/code_of_conduct/"):
                    app_name = "code_of_conduct"
                elif path.startswith("/api/auth_system/"):
                    app_name = "auth_system"

            if not app_name:
                return response
            APILog = self._import_apilog_model(app_name)
            if not APILog:
                return response
            query_params = getattr(request, "_query_params", {})
            body_data = getattr(request, "_body_data", {})
            if method == "GET" and not query_params:
                request_data = {"message": "Full data fetched "}
            else:
                request_data = (
                    {
                        **getattr(request, "_body_data", {}),
                        **getattr(request, "_query_params", {}),
                    },
                )
            log_entry = APILog(
                uniqid=request.uniqid,
                user=user_obj,
                method=method,
                endpoint=path,
                request_data=request_data,
                response_status=response.status_code,
            )
            try:
                if hasattr(response, "content") and response.get(
                    "Content-Type", ""
                ).startswith("application/json"):
                    log_entry.response_data = json.loads(
                        response.content.decode("utf-8")
                    )
                else:
                    log_entry.response_data = None
            except Exception:
                log_entry.response_data = None
            log_entry.save()
        except Exception as e:
            print(f"[Middleware] APILog error: {e}")
        return response

    def _import_apilog_model(self, app_name):
        try:
            module = __import__(f"{app_name}.models", fromlist=["APILog"])
            return getattr(module, "APILog")
        except (ImportError, AttributeError) as e:
            print(f"[Middleware] Could not import APILog from {app_name}.models: {e}")
            return None


def _flatten_querydict(querydict, exclude_keys=None):
    exclude_keys = exclude_keys or []
    return {
        key: (value[0] if len(value) == 1 else value)
        for key, value in querydict.lists()
        if key not in exclude_keys
    }

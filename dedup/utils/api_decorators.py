import uuid
from functools import wraps
from dedup.models.apilog import APILog


def log_api_call():
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            user = getattr(request, "user", None)
            method = request.method
            endpoint = request.path

            
            session_uniqid = (
                request.session.get("api_session_id")
                or request.headers.get("X-Session-Log-Id")
                or request.query_params.get("session_log_id")
            )

            
            call_uniqid = uuid.uuid4()

            try:
                if method in ["POST", "PUT", "PATCH"]:
                    request_data = request.data
                else:
                    request_data = request.query_params

                if hasattr(request_data, "dict"):
                    request_data = request_data.dict()
            except Exception:
                request_data = {}

            response = func(self, request, *args, **kwargs)

            try:
                if hasattr(response, "data") and isinstance(response.data, dict):
                    response.data["log_id"] = str(call_uniqid)
                    response.data["session_log_id"] = (
                        str(session_uniqid) if session_uniqid else None
                    )
            except Exception:
                pass  

            try:
                APILog.objects.create(
                    uniqid=call_uniqid,
                    session_id=session_uniqid,
                    user=user if user and user.is_authenticated else None,
                    method=method,
                    endpoint=endpoint,
                    request_data=request_data,
                    response_data=(
                        response.data if hasattr(response, "data") else str(response)
                    ),
                    response_status=getattr(response, "status_code", None),
                )
            except Exception as e:
                print(f"Error saving API log: {e}")

            return response

        return wrapper

    return decorator

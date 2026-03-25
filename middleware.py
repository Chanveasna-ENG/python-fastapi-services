from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Fixes: X-Content-Type-Options Header Missing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Fixes: Cross-Origin-Resource-Policy Header Missing
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        # Fixes: Storable and Cacheable Content (for sensitive API data)
        response.headers["Cache-Control"] = "no-store, max-age=0"
        return response
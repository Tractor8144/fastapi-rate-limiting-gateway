from fastapi.requests import Request
from app.routes.admin import IdentifierType


class RequestParser:
    @staticmethod
    def extract_identifiers(request: Request) -> dict:
        identifiers = dict()

        # extract API key -> Priority-1
        if api_key := request.headers.get('X-API-KEY'):
            identifiers[IdentifierType.IDENTIFIER_API_KEY] = api_key

        # extract user_id from bearer token if available
        if auth_header := request.headers.get('Authorization'):
            if auth_header.startswith("Bearer "):
                user_id = auth_header.split(' ')[1]
                identifiers[IdentifierType.IDENTIFIER_USER_ID] = user_id

        # extract Organization ID from
        if org_id := request.headers.get('X-ORG-ID'):
            identifiers[IdentifierType.IDENTIFIER_ORG_ID] = org_id

        # Extract the route path
        if request.url.path:
            identifiers[IdentifierType.IDENTIFIER_ROUTE] = request.url.path

        # Extract client IP address
        identifiers[IdentifierType.IDENTIFIER_IP] = request.client.host

        return identifiers

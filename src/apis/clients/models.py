from base64 import b64encode

from django.db import models

from ..base import models as base_repo_models


class Client(base_repo_models.BaseModel):
    id = models.CharField(primary_key=True, db_index=True, max_length=100, editable=False)
    client_id = models.CharField(max_length=150)
    client_secret = models.TextField()
    name = models.CharField(max_length=100)
    response_type = models.CharField(max_length=200)
    scope = models.CharField(max_length=200)
    grant_types = models.CharField(max_length=200)
    redirect_uris = models.CharField(max_length=200)

    def validate_secret(self, secret: str) -> bool:
        encode_secret = Client.encode_client_secret(secret)
        return encode_secret == self.client_secret

    def validate_scope(self, scope: str) -> bool:
        scopes = scope.split(' ')
        for scp in scopes:
            if scp not in self.scope.split(' '):
                return False
        return True

    def validate_grant_type(self, grant_type: str) -> bool:
        grant_types = grant_type.split(' ')
        for g_type in grant_types:
            if g_type not in self.grant_types.split(' '):
                return False
        return True

    def validate_redirect_uri(self, redirect_uri: str) -> bool:
        redirect_uris = redirect_uri.split(' ')
        for uri in redirect_uris:
            if uri not in self.redirect_uris.split(' '):
                return False
        return True

    @staticmethod
    def encode_client_secret(secret: str) -> str:
        return b64encode(secret.encode('utf-8')).decode()

    @staticmethod
    def create(payload: dict) -> "Client":
        base64_encoded_secret = Client.encode_client_secret(payload['client_secret'])
        return Client.objects.create(
            id=payload['client_id'],
            client_id=payload['client_id'],
            client_secret=base64_encoded_secret,
            name=payload['client_id'],
            response_type=payload['response_type'],
            scope=payload['scope'],
            grant_types=payload['grant_types'],
            redirect_uris=payload['redirect_uris']
        )

    @staticmethod
    def get_by_id(client_id: str):
        try:
            return Client.objects.get(id=client_id)
        except (Exception, Client.DoesNotExist):
            return None

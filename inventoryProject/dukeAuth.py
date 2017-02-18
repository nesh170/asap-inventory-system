from urllib.parse import urljoin

from social_core.backends.oauth import BaseOAuth2


class DukeOAuth2(BaseOAuth2):
    """Duke OAuth2 authentication backend"""

    def auth_html(self):
        pass

    name = 'duke'
    API_URL = "https://api.colab.duke.edu/"
    AUTHORIZATION_URL = 'https://oauth.oit.duke.edu/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://oauth.oit.duke.edu/oauth/token'
    ACCESS_TOKEN_METHOD = 'POST'
    ID_KEY = 'netid'
    REDIRECT_STATE = False
    EXTRA_DATA = [
        ('expires_in', 'expires_in')
    ]

    def get_user_details(self, response):
        """Return user details from Duke account"""
        return {'username': response.get('netid'),
                'email': response.get('mail'),
                'first_name': response.get('firstName'),
                'last_name': response.get('lastName')}

    def user_data(self, access_token, *args, **kwargs):
        data = self._user_data(access_token)
        return data

    def _user_data(self, access_token, path=None):
        url = urljoin(self.API_URL, 'identity/v1/')
        client_id, client_secret = self.get_key_and_secret()
        return self.get_json(url, headers={'x-api-key': client_id, 'Authorization': 'Bearer ' + access_token})
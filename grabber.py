import os
import json

from conjur.api import Api
from datetime import datetime, timedelta
from time import sleep

url = os.getenv('CONJUR_APPLIANCE_URL', default=None)
cert_path = os.getenv('CONJUR_SSL_CERTIFICATE_PATH', default=None)
account = os.getenv('CONJUR_ACCOUNT', default=None)
token_file = os.getenv('CONJUR_AUTHN_TOKEN_FILE', default=None)
secrets_file = os.getenv('SECRETS_FILE', default=None)
timeout = int(os.getenv('FETCH_TIMEOUT', default=None))

if any([url, cert_path, account, token_file, secrets_file, timeout]) is None:
    raise Exception(
        "Need all of the following env: CONJUR_APPLIANCE_URL,"
        "CONJUR_SSL_CERTIFICATE_PATH, CONJUR_ACCOUNT, CONJUR_AUTHN_TOKEN_FILE,"
        "SECRETS_FILE, and FETCH_TIMEOUT"
        )

if not os.path.exists(secrets_file):
    raise Exception("No SECRETS_FILE in " + secrets_file)

with open(secrets_file, 'r') as f:
    secrets = json.load(f)
    if type(secrets) is not dict:
        raise Exception("Secrets file should be dict not " \
            + type(secrets))

while True:
    # if there is no token file wait for 5 seconds and run new cycle
    if not os.path.exists(token_file):
        sleep(5)
        continue

    with open(token_file, 'r') as f:
        api_token = f.read()
        # if there is no token wait for 5 seconds and run new cycle
        if api_token == '':
            sleep(5)
            continue

    # Small hack
    # We don't use Client here, because it requires login_id and 
    # tries to authenticate by itself (what already done by k8s 
    # authenticator)
    # Instead, we use the API library directly
    # But it also tries to authenticate by itself, so we put token
    # inside _api_token variable, and renew api_token_expiration time
    # to avoid unnecessary authentication
    client = Api(url=url,
                 account=account,
                 ca_bundle=cert_path)
    client._api_token = api_token
    client.api_token_expiration = datetime.now() + timedelta(minutes=client.API_TOKEN_DURATION)

    for secret in secrets:
        value = client.get_variable(secret)
        with open(secrets[secret], 'w') as f:
            f.write(value.decode("utf-8"))
        print("Value %s has written" % secrets[secret])

    sleep(timeout)
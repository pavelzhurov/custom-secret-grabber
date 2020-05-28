# custom-secret-grabber

This is the demo of custom secret grabber written with [Conjur Python 3 SDK](https://github.com/cyberark/conjur-api-python3).
This grabber works according to the following schema and needs [conjur-k8s-authenticator](https://github.com/cyberark/conjur-authn-k8s-client) running aside.
1. Authenticator requests access to secrets:
    1. Sends a CSR with SAN containing pod and namespace
    2. Conjur generates a certificate and adds it to the particular pod in a particular namespace (indicated in CSR's SAN)
    3. Openshift injects certificate in that pod
2. The authenticator uses the certificate to obtain a temporal token
3. Authenticator puts the token into emptyDir Token
4. Custom secret grabber (CSG) obtains it from emptyDir Token
5. CSG using Python SDK grabs secrets from Conjur
6. CSG puts secrets into emptyDir secrets
7. The application uses secrets from emptyDir Secrets

Currently, Python SDK (0.0.5) doesn't provide kubernetes native authentication, that's why we need to use conjur-k8s-authenticator aside.

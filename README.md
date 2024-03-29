# Setup

# App descriptions

## simple-keycloak-auth-app

This app uses public access type

## lib-keycloak-auth-app

This app uses confidential access type

## oauth2proxy + app

This app uses public access type

## Keycloak Setup

## simple-keycloak-auth-app 

Uses the master realm with no additional configuration needed.

## lib-keycloak-auth-app

### Create a new realm

    * General: Enabled, OpenID Endpoint Configuration
    * Login: User registration enabled

### Create a new client

    * Settings: Enabled, Direct Access Granted, Service Accounts Enabled, Authorization Enabled
    * Scope: Full Scope Allowed (Will automatically grant all available roles to all users using this client, you may want to disable this and assign the roles to the client manually)
    * Valid Redirect URIs: http://localhost:8081/callback (Or whatever you configure in your python app)

### Modify the admin-cli client

    * Settings: Service Accounts Enabled
    * Scope: Full Scope Allowed
    * Service Account Roles: Select all Client Roles available for account and realm_management

### Setting credentials

*Important*

The first time this is run and keycloak is configurured, the client secret needs
to be obtained from the lib-keycloak-app > credentials and admin-cli >
credentials pages and imported into the docker-compose file (or via .env) in app2 section.


# Useful reading on Access Types

https://stackoverflow.com/questions/58911507/keycloak-bearer-only-clients-why-do-they-exist

* Public - web app - will be forced to login
* Confidential - backend that hold secrets
* Bearer-only - api used by web app, same token can be used 



# Keycloak Tokens

Get an Access token from Keycloak API

    ADMIN_NAME=admin
    ADMIN_PASSWORD=password
    KEYCLOAK_DOMAIN=localhost:8180
    REALM=master

For client app use (as set in the client id field in the clients menu)

    CLIENT_ID=login-app-name

For admin access use the following

    CLIENT_ID=admin-cli

Then call the URL and obtain the access token (here using jq to make it simpler)

    curl    --request POST \
            --header 'Content-Type: application/x-www-form-urlencoded' \
            --data-urlencode "client_id=${CLIENT_ID}" \
            --data-urlencode "username=${ADMIN_NAME}" \
            --data-urlencode "password=${ADMIN_PASSWORD}" \
            --data-urlencode "grant_type=password" \
            "http://${KEYCLOAK_DOMAIN}/auth/realms/${REALM}/protocol/openid-connect/token" | jq .access_token

Set the access token variable for future use

    ACCESS_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2l...."

If you see no output then remove the pipe to jq amd you see no output then
remove the jq arg and check the error message.

# Setup Keycloak

We are creating client for testing and getting JWT tokens.

* Go to http://localhost:8180/auth/
* Login with admin/password
* Go to Clients section on sidebar
* Click Create button
* Fill Client ID as 'login-app'
* Click Save button

# Testing the App

Without a session token

    curl http://localhost:8280/users/me/items/
    {"detail":"Not authenticated"}

With an expired or invalid session token

    curl http://localhost:8280/users/me/items/  --header "Authorization: Bearer ${ACCESS_TOKEN}"
    {"detail":"Could not validate credentials"}
    
With a valid session token as shown above, set CLIENT_ID to login-app

    curl http://localhost:8280/users/me/items/ --header "Authorization: Bearer ${ACCESS_TOKEN}"
    [{"item_id":"Foo","owner":"admin"}]
    

# Keycloak Admin Usage

## Get a user

Once the access token is set, to get details about a user use 

    USER=user1

    curl --request GET \
         --header "Content-Type: application/json" \
         --header "Authorization: Bearer ${ACCESS_TOKEN}" \
        "http://${KEYCLOAK_DOMAIN}/auth/admin/realms/${REALM}/users/?username=${USER}"

or to list all users in the realm use

    curl --request GET \
         --header "Content-Type: application/json" \
         --header "Authorization: Bearer ${ACCESS_TOKEN}" \
        "http://${KEYCLOAK_DOMAIN}/auth/admin/realms/${REALM}/users" | jq .

Again piping the output to jq makes it easier to read. 

## Delete a user

From the Get a user section, obtain the value from the user 'id' field.

    USER_ID="4b2aa64a-bace-4db5-b556-e3334c829a48"

    curl --request DELETE \
         --header "Content-Type: application/json" \
         --header "Authorization: Bearer ${ACCESS_TOKEN}" \
        "http://${KEYCLOAK_DOMAIN}/auth/admin/realms/${REALM}/users/${USER_ID}"

Nothing is return apart from 200 OK so to verify its deleted run the Get a user
request again.

## Create a user 

TODO

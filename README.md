
# Get an Access token from Keycloak API

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


# Get a user

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

# Delete a user

From the Get a user section, obtain the value from the user 'id' field.

    USER_ID="4b2aa64a-bace-4db5-b556-e3334c829a48"

    curl --request DELETE \
         --header "Content-Type: application/json" \
         --header "Authorization: Bearer ${ACCESS_TOKEN}" \
        "http://${KEYCLOAK_DOMAIN}/auth/admin/realms/${REALM}/users/${USER_ID}"

Nothing is return apart from 200 OK so to verify its deleted run the Get a user
request again.

# Creat a user

This is not required as creation is performed via Active Directory.
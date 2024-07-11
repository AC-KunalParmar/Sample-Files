#!/bin/bash

############
# requires 'bash, 'jq' and 'curl'
# set your Service Account credentials below
############

API_TOKEN=$(curl -s -X POST https://auth.app.wiz.io/oauth/token \
-H "Content-Type: application/x-www-form-urlencoded" \
-H "encoding: UTF-8" \
--data-urlencode 'grant_type=client_credentials' \
--data-urlencode 'client_id=SERVICE_ACCOUNT_CLIENT_ID' \
--data-urlencode 'client_secret=SERVICE_ACCOUNT_CLIENT_SECRET' \
--data-urlencode 'audience=wiz-api' | jq -r '.access_token')

QUERY_VARS=$(cat <<EOF
{"first":20,"filterBy":{"project":["53bb8fe3-ef74-5d0d-9f47-641d1ad0051c"],"search":"02ec6916-371f-4a99-b1bb-a68a11788aca","status":["OPEN"],"relatedEntity":{"tag":null}},"orderBy":{"field":"SEVERITY","direction":"DESC"}}
EOF
)

function callAPI {
    curl -s -X POST https://api.us5.app.wiz.io/graphql \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${API_TOKEN}" \
    -d '{
    "variables": '"$QUERY_VARS"',
    "query": "query IssuesTable($filterBy: IssueFilters, $first: Int, $after: String, $orderBy: IssueOrder) { issues(filterBy: $filterBy, first: $first, after: $after, orderBy: $orderBy) { nodes { ...IssueDetails } pageInfo { hasNextPage endCursor } totalCount }} fragment IssueDetails on Issue { id control { id name query securitySubCategories { id category { id } } } createdAt updatedAt projects { id name slug businessUnit riskProfile { businessImpact } } status severity entity { id name type } entitySnapshot { id type name cloudPlatform region subscriptionName subscriptionId subscriptionExternalId subscriptionTags nativeType } note serviceTickets { externalId name url action { id type } }}"}'
}

RESULT=$(callAPI)
echo "${RESULT}" # your data is here!

# If paginating on a Graph Query, then use <'quick': false> in the query variables.
# Uncomment the following section to paginate over all the results:
# while true; do
#     PAGE_INFO=$(echo "${RESULT}" | jq -r '.data | .undefined | .pageInfo')
#     HAS_NEXT_PAGE=$(echo "${PAGE_INFO}" | jq -r '.hasNextPage')
#     if [ "$HAS_NEXT_PAGE" = true ]; then
#         END_CURSOR=$(echo "${PAGE_INFO}" | jq -r '.endCursor')
#         QUERY_VARS=$(echo "$QUERY_VARS" | jq --arg foo "$END_CURSOR" '. + {after: $foo}')
#     else
#         break
#     fi
#     RESULT=$(callAPI)
#     echo "${RESULT}"
#  done
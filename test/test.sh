#!/usr/bin/env bash

# Insert stay
echo -e "Insert Stay "
curl -s -d "{\"datein\": \"2021-04-20\", \"dateout\": \"2021-04-22\", \"email\":\"myemail@email.com\"}" \
-H "Content-Type: application/json" http://localhost:8000/stayData | jq .

# Return the stayID
echo -e "Return the stayID "
curl -s -X GET "http://localhost:8000/getStayId?email=myemail@email.com&datein=2021-04-20&dateout=2021-04-22" | jq .

#List stays
echo -e "List stays"
curl -s -X GET http://localhost:8000/allStays?email=myemail@email.com | jq .

# Remove stay
echo -e "Remove stay"
curl -d "{\"datein\": \"2021-04-20\", \"dateout\": \"2021-04-22\", \"email\":\"myemail@email.com\"}" \
-H "Content-Type: application/json" \
http://localhost:8000/removeStay


# List stays
echo -e "List stays"
curl -X GET http://localhost:8000/allStays?email=myemail@email.com | jq -s .


# Test consent policy

echo -e "Add new stay to test the policy consent function"
curl -d "{\"datein\": \"2021-04-20\", \"dateout\": \"2021-04-22\", \"email\":\"myemail@email.com\"}" \
-H "Content-Type: application/json" \
http://localhost:8000/stayData

# Insert policy consent

echo -e "Insert policy consent"
curl -d "{\"policyid\": \"14\", \"consent\": \"True\", \"email\":\"myemail@email.com\", \"timestamp\":\"2021-04-22\"}" \
-H "Content-Type: application/json" \
http://localhost:8000/consentInformation


curl -d "{\"policyid\": \"14\", \"consent\": \"True\", \"email\":\"myemail@email.com\", \"timestamp\":\"2021-05-22\"}" \
-H "Content-Type: application/json" \
http://localhost:8000/consentInformation
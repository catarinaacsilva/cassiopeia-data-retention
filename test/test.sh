#!/usr/bin/env bash

# Insert stay

curl -d "{\"datein\": \"2021-04-20\", \"dateout\": \"2021-04-22\", \"email\":\"myemail@email.com\"}" \
-H "Content-Type: application/json" \
http://localhost:8000/stayData

#List stays

curl -X GET http://localhost:8000/allStays?email=myemail@email.com | jq .

# Remove stay

curl -d "{\"datein\": \"2021-04-20\", \"dateout\": \"2021-04-22\", \"email\":\"myemail@email.com\"}" \
-H "Content-Type: application/json" \
http://localhost:8000/removeStay


# List stays

curl -X GET http://localhost:8000/allStays?email=myemail@email.com | jq .


# Store information about consent information

curl -d "{\"policyid\": \"14\", \"consent\": \"True\", \"email\":\"myemail@email.com\", \"timestamp\": \"2021-04-20\"}" \
-H "Content-Type: application/json" \
http://localhost:8000/consentInformation


# List consent information

curl -X GET http://localhost:8000/listConsent?email=myemail@email.com | jq .
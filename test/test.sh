#!/usr/bin/env bash

# Insert stay

curl -d "{\"datein\": \"2021-04-20\", \"dateout\": \"2021-04-22\", \"email\":\"myemail@email.com\"}" \
-H "Content-Type: application/json" \
http://localhost:8000/stayData


curl -X GET http://localhost:8000/allStays?email=myemail@email.com | jq .


curl -d "{\"datein\": \"2021-04-20\", \"dateout\": \"2021-04-22\", \"email\":\"myemail@email.com\"}" \
-H "Content-Type: application/json" \
http://localhost:8000/removeStay


curl -X GET http://localhost:8000/allStays?email=myemail@email.com | jq .


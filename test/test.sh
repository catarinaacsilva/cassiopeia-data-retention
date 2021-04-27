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


# Test consent policy - Add new stay to test the policy consent function

echo -e "Add new stay to test the policy consent function"
content=$(curl -d "{\"datein\": \"2021-04-20\", \"dateout\": \"2021-04-22\", \"email\":\"myemail@email.com\"}" \
-H "Content-Type: application/json" \
http://localhost:8000/stayData) 
stay_id=$( jq -r  '.stay_id' <<< "${content}" ) 
echo "${stay_id}"

# Insert policy consent

echo -e "Insert policy consent"
curl -d "{\"policyid\": 14, \"consent\": true, \"timestamp\":\"2021-04-22\", \"stay_id\": $stay_id}" \
-H "Content-Type: application/json" \
http://localhost:8000/consentInformation


# List policy consent
echo -e "List policy consent"
curl -X GET http://localhost:8000/listConsent?stay_id=$stay_id | jq -s .


##############################################################################################################################

#                                    TEST INFLUX

##############################################################################################################################


# Add new user to test next function

echo -e "Add new stay to test the policy consent function"
content=$(curl -d "{\"datein\": \"2021-04-21\", \"dateout\": \"2021-04-22\", \"email\":\"testinflux@email.com\"}" \
-H "Content-Type: application/json" \
http://localhost:8000/stayData) 
stay_id=$( jq -r  '.stay_id' <<< "${content}" ) 
echo "${stay_id}"

# Correlate devices data and user

echo -e "Correlate devices data and user"
curl -s -X GET "http://localhost:8000/userData?email=testinflux@email.com&stay_id=$stay_id" | jq .


# Export data to csv

echo -e "Export data to csv"
curl -s -X GET "http://localhost:8000/exportCsv?stay_id=$stay_id" > data.csv


# Return entity ids od the sensors that collected data

echo -e "Return entity ids of the sensors that collected data"
curl -s -X GET "http://localhost:8000/entityData?email=testinflux@email.com&stay_id=$stay_id" | jq .


# Remove user data of the influxdb by stay and the email

echo -e "Remove user data of the influxdb by stay and the email"
curl -s -X GET "http://localhost:8000/removeDataUser?email=testinflux@email.com&stay_id=$stay_id" | jq .



#Insert receipt
echo -e "Insert receipt"
uuid=$(uuidgen)
echo -e "uuid=$uuid"
curl -d "{\"email\":\"testinflux@email.com\", \"id_receipt\":\"$uuid\", \"stay_id\": $stay_id}" \
-H "Content-Type: application/json" \
http://localhost:8000/receiptInformation | jq .



#Get receipt id given the stay and the email
echo -e "Get receipt id given the stay and the email"
curl -s -X GET "http://localhost:8000/receiptsByStay?email=testinflux@email.com&stay_id=$stay_id" | jq .


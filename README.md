# hotel-vacancy

This is an experimental and private-use application that periodically retrieves availability information on my favorite hotels from hotel reservation sites and notifies me via Slack when a reservation is available based on conditions I specify in advance.

## Architecture

This application is built on AWS with the following components.

- EventBridge Scheduler: Executes Lambda function periodically.
- Lambda: Searches for hotel availability information from reservation sites and stores the information in DynamoDB when found.
- DynamoDB: Stores the availability information.
- Lambda for DynamoDB Stream: Sends a message to Slack if new availability information is found or if existing availability are updated

## Requirements

```console
poetry install
```

## How to deploy

```console
poetry export -f layer/requirements.txt
sam build && sam deploy
```

## TODO

- Write unit tests

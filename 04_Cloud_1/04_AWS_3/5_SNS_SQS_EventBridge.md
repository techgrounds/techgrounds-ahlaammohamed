# SNS, SQS, Event Bridge
## Introduction
SNS (Simple Notification Service) is a notification service.

AWS SNS can publish messages to many different endpoints:
- HTTP and HTTPS
- Email and Email-JSON
- AWS SQS
- Applications
- AWS Lambda
- SMS (depending on region)

SQS: a queuing system, and the receivers have to pull the messages to be processed and deleted from the queue.

SNS and SQS can works well together.

## Exercise
Gain practical experience with SNS, SQS, Event Bridge

## Results
`SNS and Event Bridge`

**Step 1: Create an Amazon SNS topic and an Amazon subscription**
![PrnScr](/00_includes/04_AWS3/15_SNS.png)

**Step 3: Create a rule**
![PrnScr](/00_includes/04_AWS3/11_Review1.png)
![PrnScr](/00_includes/04_AWS3/12_Review2.png)

**Step 4: Send test events**
![PrnScr](/00_includes/04_AWS3/13_Send_events.png)

**Step 5: Check mailbox for the notification**
![PrnScr](/00_includes/04_AWS3/14_AWS_notification.png)


`SQS`

**Step 1: Create a SQS queue**
![PrnScr](/00_includes/04_AWS3/16_SQS.png)

**Step 2: Send a message**
![PrnScr](/00_includes/04_AWS3/17_Received.png)

I used the `poll for message` button to see if I have received the message. 

As you can see in the screenshot below, I have received the "Hello World" message that I have sent.
![PrnScr](/00_includes/04_AWS3/18_SQS_message.png)

**After reading the message, I delete it from the queue. This action serves as a signal to SQS that I have processed the message.**

## Sources
- https://www.w3schools.com/aws/aws_cloudessentials_awssqs.php

- https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-input-transformer-tutorial.html
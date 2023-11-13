# AWS Global infrastructure

## Introduction
AWS has a global infrastructure made up of the following components:

- Regions
- Availability Zones
- Edge Locations


## Exercise
`1. Explain what region, AWS Availability Zone, Edge location are?`

**Regions**: A region refers to a geographical area where a cloud provider, has established and operates a cluster of data centers. 

Within each AWS region, there are multiple availability zones. 

**Availability zones**: Availability zones are essentially separate data centers within the same region, each with its own power, cooling, and networking facilities. These availability zones are interconnected to provide high availability and fault tolerance. Deploying applications across multiple availability zones helps ensure that if one zone experiences an issue, the others can continue to operate, increasing the overall reliability of the system.

**Edge location**: Edge Locations are strategically located data centers that are distributed worldwide to bring content and services closer to end-users. They act as caching points for content, reducing latency and improving the overall performance of web applications and services.

`2. Why would you choose one region over another? (e.g. eu-central-1 (Frankfurt) over us-west-2 (Oregon))`

The best region for your AWS deployment depends on your specific use case, considering factors like performance, compliance, cost, and high availability. 

In this case I would choose the Frankfurt region since I am based in the Netherlands.

## Reference list
- https://docs.aws.amazon.com/index.html

- https://www.youtube.com/watch?v=aHAkDISza24

- https://www.w3schools.com/aws/aws_cloudessentials_awsinfrastructure.php 
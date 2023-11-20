# AWS Global infrastructure
## Introduction
The AWS Global Cloud Infrastructure is the most secure, extensive, and reliable cloud platform, offering over 200 fully featured services from data centers globally. Whether you need to deploy your application workloads across the globe in a single click, or you want to build and deploy specific applications closer to your end-users with single-digit millisecond latency, AWS provides you the cloud infrastructure where and when you need it.

AWS has a global infrastructure made up of the following components:

- Regions
- Availability Zones
- Edge Locations


The AWS Cloud spans 102 Availability Zones within 32 geographic regions around the world, with announced plans for 15 more Availability Zones and 5 more AWS Regions in Canada, Germany, Malaysia, New Zealand, and Thailand.

## Exercise
Study the AWS global infrastructure and answer the questions in Techgrounds's learn world.

## Result
`1. Explain what region, AWS Availability Zone, Edge location are?`

**Regions**: A region refers to a geographical area where a cloud provider, has established and operates a cluster of data centers. 

Within each AWS region, there are multiple availability zones. 

**Availability zones**: Availability zones are essentially separate data centers within the same region, each with its own power, cooling, and networking facilities. These availability zones are interconnected to provide high availability and fault tolerance. Deploying applications across multiple availability zones helps ensure that if one zone experiences an issue, the others can continue to operate, increasing the overall reliability of the system.

**Edge location**: Edge Locations are strategically located data centers that are distributed worldwide to bring content and services closer to end-users. They act as caching points for content, reducing latency and improving the overall performance of web applications and services.

`2. Why would you choose one region over another? (e.g. eu-central-1 (Frankfurt) over us-west-2 (Oregon))`

The best region for your AWS deployment depends on your specific use case, considering factors like performance, compliance, cost, and high availability. 

I am based in the Netherlands and due to cost advantages and regulatory considerations, eu-central-1 (Frankfurt) seems to be a suitable choice.

## Sources
- https://docs.aws.amazon.com/index.html

- https://www.youtube.com/watch?v=aHAkDISza24

- https://www.w3schools.com/aws/aws_cloudessentials_awsinfrastructure.php 
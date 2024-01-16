# ELB & Auto Scaling
## Introduction

## Exercise 
**Exercise 1: Launch an EC2 instance with the following requirements:**
- Region: Frankfurt (eu-central-1)
- AMI: Amazon Linux 2
- Type: t3.micro
- Security Group: Allow HTTP

User data:
```
#!/bin/bash
# Install Apache Web Server and PHP
yum install -y httpd mysql php unzip
# Download Lab files
wget https://aws-tc-largeobjects.s3.amazonaws.com/CUR-TF-100-RESTRT-1/80-lab-vpc-web-server/lab-app.zip
unzip lab-app.zip -d /var/www/html/
# Turn on web server
chkconfig httpd on
service httpd start
```

Create an AMI from your instance with the following requirements:
Image name: Web server AMI

**Exercise 2: Create an application load balancer with the following requirements:**
- Name: LabELB
- Listener: HTTP on port 80
- AZs: eu-central-1a and eu-central-1b
- Subnets: must be public

Security Group:
- Name: ELB SG
- Rules: allow HTTP access

Target Group:
- Name: LabTargetGroup
- Targets: to be registered by Auto Scaling

**Exercise 3: Create a launch configuration for the Auto Scaling group. It has to be identical to the server that is currently running. Create an auto scaling group with the following requirements:**
- Name: Lab ASG
- Launch Configuration: Web server launch configuration
- Subnets: must be in eu-central-1a and eu-central-1b
- Load Balancer: LabELB
- Group metrics collection in CloudWatch must be enabled

Group Size:
- Desired Capacity: 2
- Minimum Capacity: 2
- Maximum Capacity: 4
- Scaling policy: Target tracking with a target of 60% average CPU utilisation

**Exercise 4: Verify that the EC2 instances are online and that they are part of the target group for the load balancer.**

**Access the server via the ELB by using the DNS name of the ELB.**

**Perform a load test on your server(s) using the website on your server to activate auto scaling.**

## Results
**Exercise 1:** 
![PrnScr](/00_includes/04_AWS2/1_Opdracht_EC2.png)

As you can see in the screenshot above I have created my EC2 instance with the requirements that were given. The status checks have also been passed.

In the Action tab I click on the 
![PrnScr](/00_includes/04_AWS2/2_AMI_webserver.png)
import aws_cdk as cdk
from aws_cdk import (
Stack,
aws_ec2 as ec2, 
aws_s3 as s3,
aws_kms as kms,
aws_backup as backup,           
Duration,                       
aws_events as events, 
CfnOutput,
aws_autoscaling as autoscaling,
aws_elasticloadbalancingv2 as elbv2,
aws_certificatemanager as acm, 
aws_cloudwatch as cloudwatch,  
aws_iam as iam     
)

from constructs import Construct
import projectv1_1.config as config

class ProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

# WEBSERVER
        # Create Webserver VPC & subnets:
        webvpc = ec2.Vpc(self, 'vpc-webserver',
            ip_addresses=ec2.IpAddresses.cidr('10.0.1.0/24'),
            vpc_name='vpc-webserver',
            nat_gateways=1,
            max_azs=3,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                subnet_type=ec2.SubnetType.PUBLIC,  
                name='Webserver',
                cidr_mask=28  
                ),
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS, 
                    name="Database",
                ),
            ]
        ) 

        self.webvpc = webvpc # To store the VPC object in a class attribute to make it accessible across methods and make the code more readable.

# ADMIN
        # Create Admin VPC & (1) subnet
        adminvpc = ec2.Vpc(self, 'vpc-adminserver',
            ip_addresses=ec2.IpAddresses.cidr('10.0.2.0/24'),
            vpc_name='vpc-adminserver',
            nat_gateways=0,
            max_azs=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,  
                    name='Adminserver',                 
                    cidr_mask=28                        
                ),
            ]
        )


        self.adminvpc = adminvpc # To store the VPC object in a class attribute to make it accessible across methods and make the code more readable.

        # Create VPC Peering 
        self.vpc_peering = ec2.CfnVPCPeeringConnection(self,"VPC1toVPC2",
            peer_vpc_id=self.webvpc.vpc_id,    
            vpc_id=self.adminvpc.vpc_id,   
            )
        
# ROUTE TABLES
        # Get Subnet Webserver
        self.subnet_webserver = self.webvpc.private_subnets[0]

        # Get Route Table Webserver
        self.rt_sub_webserver = self.subnet_webserver.route_table

        # Create a route in the Webserver subnet's route table and connect with VPC Peering
        self.rt_web_to_peering = ec2.CfnRoute(self, "RT-web-peering",
            route_table_id=self.rt_sub_webserver.route_table_id,
            destination_cidr_block="10.0.2.0/24",
            vpc_peering_connection_id=self.vpc_peering.ref
            )

        # Connect VPC Peering service to Route Table from Adminserver
        # Get Subnet Adminserver
        self.subnet_adminserver = self.adminvpc.public_subnets[0]

        # Get Route Table Adminserver
        self.rt_sub_adminserver = self.subnet_adminserver.route_table

        # Create a route in the Admin subnet's route table and connect with VPC Peering
        self.rt_admin_to_peering = ec2.CfnRoute(self, "RT-admin-peering",
            route_table_id=self.rt_sub_adminserver.route_table_id,
            destination_cidr_block="10.0.1.0/24",
            vpc_peering_connection_id=self.vpc_peering.ref
            )
        
# NACLS AND RULES FOR THE WEBSERVER
        # Create Network ACL for the Webserver
        self.nacl_web = ec2.NetworkAcl(self, 'web-NACL', 
            network_acl_name='nacl-web',
            vpc=self.webvpc,
            subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
            )

        # Inbound rule in Web VPC for Ephemeral ports 
        self.nacl_web.add_entry("Inbound-Ephemeral",
            cidr=ec2.AclCidr.any_ipv4(),
            rule_number=90,
            traffic=ec2.AclTraffic.tcp_port_range(1024, 65535),    
            direction=ec2.TrafficDirection.INGRESS
            )

        # Inbound rule in Web VPC for HTTP traffic
        self.nacl_web.add_entry("Inbound-HTTP",
            cidr=ec2.AclCidr.any_ipv4(),
            rule_number=100,
            traffic=ec2.AclTraffic.tcp_port(80),        
            direction=ec2.TrafficDirection.INGRESS
            )
        

        # Inbound rule in Web VPC for HTTPS traffic:
        self.nacl_web.add_entry("Inbound-HTTPS",
            cidr=ec2.AclCidr.any_ipv4(),
            rule_number=200,
            traffic=ec2.AclTraffic.tcp_port(443),
            direction=ec2.TrafficDirection.INGRESS,
            )


        # Inbound rule in Web VPC for SSH from Admin server 
        self.nacl_web.add_entry("Inbound SSH from Admin",
            cidr=ec2.AclCidr.ipv4('10.0.2.0/24'),
            rule_number=300,
            traffic=ec2.AclTraffic.tcp_port(22),      
            direction=ec2.TrafficDirection.INGRESS,
            )


        # Inbound rule in Web VPC for RDP from Admin server
        self.nacl_web.add_entry("Inbound RDP from Admin",
            cidr=ec2.AclCidr.ipv4('10.0.2.0/24'), 
            rule_number=400,
            traffic=ec2.AclTraffic.tcp_port(3389),  
            rule_action=ec2.Action.ALLOW,      
            direction=ec2.TrafficDirection.INGRESS,
            )

        # Outbound rule all traffic in Web VPC
        self.nacl_web.add_entry("Outbound-All",
            cidr=ec2.AclCidr.any_ipv4(),
            rule_number=700,
            traffic=ec2.AclTraffic.all_traffic(),
            direction=ec2.TrafficDirection.EGRESS
            )


# NACLS AND RULES FOR THE ADMIN 
        # Create Network ACL for the Adminserver:
        self.nacl_admin = ec2.NetworkAcl(self, 'admin-NACL', 
            network_acl_name='nacl-admin',
            vpc=self.adminvpc,
            subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
            )
            
        # Inbound rule in Admin VPC for RDP from the admin IP
        admin_ip = "87.209.147.77/32"   # Change the admin_ip to your own home/admin IP "192.168.1.250/32"

        # Inbound rule in Admin VPC for ephemeral ports 
        self.nacl_admin.add_entry("Inbound-Ephemeral",
            cidr=ec2.AclCidr.any_ipv4(),
            rule_number=250,
            traffic=ec2.AclTraffic.tcp_port_range(49152, 65535),    # Windows ephemeral ports
            direction=ec2.TrafficDirection.INGRESS
            )

        self.nacl_admin.add_entry("Inbound RDP from Admin-ip",
            cidr=ec2.AclCidr.ipv4(admin_ip),
            rule_number=500,
            traffic=ec2.AclTraffic.tcp_port(3389),  
            rule_action=ec2.Action.ALLOW,      
            direction=ec2.TrafficDirection.INGRESS,
            )

        # Outbound rule all traffic in Admin VPC
        self.nacl_admin.add_entry("Outbound-All",
            cidr=ec2.AclCidr.any_ipv4(),
            rule_number=600,
            traffic=ec2.AclTraffic.all_traffic(),
            direction=ec2.TrafficDirection.EGRESS
            )

        
# SECURITY GROUPS
        admin_cidr_sg = ec2.Peer.ipv4("0.0.0.0/0")

        # Create Security Group for Webserver 
        sg_webserver = ec2.SecurityGroup(self,"WebServerSG", 
        vpc = self.webvpc,
        description = "WebserverSG",                                                                  
            )

        sg_webserver.add_ingress_rule(admin_cidr_sg, ec2.Port.tcp(22), "Allow SSH from Admin") 
        sg_webserver.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP from Admin")
        sg_webserver.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), "Allow HTTPS from Admin")

        # Create Security Group for Admin server
        sg_adminserver = ec2.SecurityGroup(self,"AdminSG", 
        vpc = self.adminvpc,
        description = "AdminSG",                                                               
            )

        # Allow inbound RDP traffic from a specific IP 
        sg_adminserver.add_ingress_rule(
            peer=ec2.Peer.ipv4("87.209.147.77/32"),  # Change this to your home/office 
            connection=ec2.Port.tcp(3389),           # RDP port
            description="Allow RDP from only my IP"
            )

# ADDITIONAL CONFIGURATIONS OPTIONS
        # Define user data 
        user_data_webserver = ec2.UserData.for_linux( shebang =  "#!/bin/bash")
        user_data_webserver.add_commands ( 
                                "yum -y install httpd",
                                "systemctl enable httpd",
                                 "systemctl start httpd",
                                """echo '<html><h1> Hi there! </h1>
                                 <b1> What is your task of the day? <b1>                                         
                                </html>' > /var/www/html/index.html"""

            )

        # Keypair for Webserver:
        sleutel_web = ec2.KeyPair.from_key_pair_name(self, "MyWEBKeyPair",
        key_pair_name="sleutel_web",
            )

# EC2 INSTANCE (WEBSERVER)
        # Create Webserver instance
        self.instance_webserver = ec2.Instance(self, "web-instance",
            instance_name="web-instance",
            vpc=webvpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            private_ip_address="10.0.1.70",
            key_pair=sleutel_web,  # Use the key-pair you created
            security_group=sg_webserver,  # Use the security group you created
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T2, ec2.InstanceSize.MICRO),
            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2023),
            block_devices=[ec2.BlockDevice(
                device_name="/dev/xvda",
                volume=ec2.BlockDeviceVolume.ebs(
                    volume_size=15,
                    encrypted=True,
                )
            )],
        user_data=user_data_webserver,  # Use the user data defined for the web server
            )
        
        #  # Output the Webserver (public IP)
        # CfnOutput(self,"Webserver-publicIP",
        #     value=self.instance_webserver.instance_public_ip,
        #     export_name="mypublicIpv4"
        #     )
        
         # Output the Webserver (private IP)
        CfnOutput(self, "Webserver-privateIP",
            value=self.instance_webserver.instance_private_ip,
            export_name="webserver-private-ip"
            )
        
        # Output the Webserver private DNS name 
        CfnOutput(self, "Webserver-privateDNSname", # this is needed for SSH from Admin server
            value=self.instance_webserver.instance_private_dns_name,
            export_name="webserver-private-dns-name"
            )
        
        keypair_adminserver = ec2.KeyPair.from_key_pair_name(self, "MyADMINKeyPair",
        key_pair_name="keypair_adminserver",
            )

# EC2 INSTANCE (ADMIN SERVER)
        # Create Admin server instance
        self.instance_adminserver = ec2.Instance(self,"admin-instance",
            instance_name="admin-instance",
            vpc=adminvpc,                             
            vpc_subnets=ec2.SubnetSelection(                    
                subnet_type=ec2.SubnetType.PUBLIC),
            private_ip_address="10.0.2.10",             
            key_pair=keypair_adminserver,                  
            security_group=sg_adminserver,                
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T2, ec2.InstanceSize.MICRO),  
            machine_image=ec2.WindowsImage(
                ec2.WindowsVersion.WINDOWS_SERVER_2022_ENGLISH_FULL_BASE),  
            block_devices=[ec2.BlockDevice(
                device_name="/dev/sda1",                        
                volume=ec2.BlockDeviceVolume.ebs(
                    volume_size=30,                             
                    encrypted=True,                         # Encryption on root disk
                    )
                ), ec2.BlockDevice(
                device_name="/dev/sdf",                         
                volume=ec2.BlockDeviceVolume.ebs(
                    volume_size=256,                          
                    encrypted=True,                         # Encryption on attached EBS
                    )
                )]
            )
        
        
        # # Output the Admin server public IP
        # CfnOutput(self, "Adminserver-publicIP",
        #     value=self.instance_adminserver.instance_public_ip,
        #     export_name="adminserver-public-ip"
        #     )
        
        # # Output the Admin server private IP
        # CfnOutput(self, "Adminserver-privateIP",
        #     value=self.instance_adminserver.instance_private_ip,
        #     export_name="adminserver-private-ip"
        #     )

# BACKUP
#         # Create a Backup plan
#         self.backup_plan = backup.BackupPlan(self, "backup-plan",
#             backup_plan_name="Backup-plan",
#             backup_plan_rules=[backup.BackupPlanRule(
#                 rule_name="Retain-7-days",
#                 start_window=Duration.hours(1),             # This start the backup within 1 hour of the scheduled start
#                 completion_window=Duration.hours(2),        # This completes the backup within 2 hours of starting
#                 delete_after=Duration.days(7),              # This retains the backups for 7 days
#                 schedule_expression=events.Schedule.cron(
#                     hour="3",    # This backup is scheduled to run every day at 3 AM UTC (= 4 AM CET)
#                     minute="0", )   
#                 )]
#                 )
        
#         # Specify Webserver as a resource to backup
#         self.backup_plan.add_selection("-Resource-WEB-backup", 
#             backup_selection_name="WEB-backup",
#             resources=[
#                 backup.BackupResource.from_ec2_instance(self.instance_webserver)
#                 ]
#                 )
        
# # KMS
#         # Create a KMS key (needed for S3 encryption)
#         kms_key = kms.Key(self, "YourTrustedKey", 
#             enable_key_rotation=True,
#             alias="your-trusted-key"  # KMS key name
#             )         
                        
# # BUCKET
#         # Create the S3 bucket
#         bucket = s3.Bucket(self, "bucket",
#             bucket_name="bucketforcloudproject", 
#             encryption=s3.BucketEncryption.KMS,  # Use KMS encryption
#             encryption_key=kms_key,  # Assigns the KMS key
#             access_control=s3.BucketAccessControl.PRIVATE,  # This sets the bucket to private
#             versioned=True,
#             block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
#             removal_policy=cdk.RemovalPolicy.DESTROY  # This deletes the bucket when the stack is deleted
#             )

#         assert bucket.encryption_key == kms_key  # Assert the bucket's encryption key
        
#         # Grant read/write permissions to the web server instance and admin server instance
#         bucket.grant_read_write(self.instance_webserver.role)
#         bucket.grant_read_write(self.instance_adminserver.role)


#         # Output the bucket name
#         CfnOutput(self, "bucket-name",
#             value=bucket.bucket_name,
#             export_name="bucket-name"
#             )

# # AUTO SCALING GROUP
#          # Create security group for Auto Scaling Group
#         self.sg_autoscaling = ec2.SecurityGroup(self, "SG-ASG-web",
#             vpc=webvpc,
#             description="ASG-SG"
#             )
        
#          # Create Role for webserver instance
#         self.role_web = iam.Role(self, "role-webserv",
#             assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
#         )

#         # Create an Auto Scaling group
#         self.auto_scaling_group = autoscaling.AutoScalingGroup(self, "ASG-web",
#             vpc=webvpc,
#             vpc_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS), 
#             security_group=self.sg_autoscaling,
#             role=self.role_web,
#             instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO), #(ec2.InstanceClass.T2, ec2.InstanceSize.MICRO),
#             machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2023),
#             user_data=user_data_webserver,
#             min_capacity=1,
#             max_capacity=3,
#             desired_capacity=1,
#              health_check=autoscaling.HealthCheck.elb(
#                 grace=Duration.minutes(3) # Instances are marked as unhealthy if they fail to respond to the ELB health check for 3 minutes.
#                 ),
#                 # default_instance_warmup = Duration.seconds(20),
#                 block_devices=[
#                     autoscaling.BlockDevice(
#                         device_name="/dev/xvda",
#                         volume=autoscaling.BlockDeviceVolume.ebs(30, encrypted=True)
#                     )
#                 ]
#             )
        
#        # Get the underlying CfnAutoScalingGroup object (to eliminate the type error in the dependency)
#         cfn_asg = self.auto_scaling_group.node.default_child

#         # Scale up based on CPU utilization
#         cpu_scale_up_policy = autoscaling.CfnScalingPolicy(
#             self,
#             "CpuScaleUpPolicy",
#             policy_type="TargetTrackingScaling",
#             auto_scaling_group_name=self.auto_scaling_group.auto_scaling_group_name,
#             target_tracking_configuration=autoscaling.CfnScalingPolicy.TargetTrackingConfigurationProperty(
#                 target_value=70,
#                 predefined_metric_specification=autoscaling.CfnScalingPolicy.PredefinedMetricSpecificationProperty(
#                     predefined_metric_type="ASGAverageCPUUtilization"
#                 )
#             )
#         )
#         cpu_scale_up_policy.add_dependency(cfn_asg)

#         # Scale down based on CPU utilization
#         cpu_scale_down_policy = autoscaling.CfnScalingPolicy(
#             self,
#             "CpuScaleDownPolicy",
#             policy_type="TargetTrackingScaling",
#             auto_scaling_group_name=self.auto_scaling_group.auto_scaling_group_name,
#             target_tracking_configuration=autoscaling.CfnScalingPolicy.TargetTrackingConfigurationProperty(
#                 target_value=50,
#                 predefined_metric_specification=autoscaling.CfnScalingPolicy.PredefinedMetricSpecificationProperty(
#                     predefined_metric_type="ASGAverageCPUUtilization"
#                 )
#             )
#         )
#         cpu_scale_down_policy.add_dependency(cfn_asg)

#         # Define a single target tracking scaling policy for both scale up and scale down
#         cpu_scale_policy = autoscaling.CfnScalingPolicy(
#             self,
#             "CpuScalePolicy",
#             policy_type="TargetTrackingScaling",
#             auto_scaling_group_name=self.auto_scaling_group.auto_scaling_group_name,
#             target_tracking_configuration=autoscaling.CfnScalingPolicy.TargetTrackingConfigurationProperty(
#                 target_value=70,  # Adjust target values as needed
#                 predefined_metric_specification=autoscaling.CfnScalingPolicy.PredefinedMetricSpecificationProperty(
#                     predefined_metric_type="ASGAverageCPUUtilization"
#                 )
#             )
#         )

#         # Add dependency on the Auto Scaling Group
#         cpu_scale_policy.add_dependency(cfn_asg)

        
#         # # Create Scale policy
#         # self.scale_policy = self.auto_scaling_group.scale_on_cpu_utilization("scale-policy",
#         #     target_utilization_percent=70,  # When CPU usage exceeds 70%, new instances will be launched to bring the average down. If CPU usage drops below 70%, instances will be terminated
#         #    )
        
#         # # Create a custom metric for CPU utilization
#         # cpu_metric = cloudwatch.Metric(
#         #     namespace="AWS/EC2",
#         #     metric_name="CPUUtilization",
#         # )

#         # # Create a step scaling policy
#         # self.scale_policy = autoscaling.StepScalingPolicy(
#         #     self,
#         #     "StepScalingPolicy",
#         #     auto_scaling_group=self.instance_webserver,
#         #     metric=cpu_metric,
#         #     adjustment_type=autoscaling.AdjustmentType.CHANGE_IN_CAPACITY,
#         #     scaling_steps=[
#         #         autoscaling.ScalingInterval(lower=0, upper=40, change=-1),
#         #         autoscaling.ScalingInterval(lower=70, change=1),
#         #     ],
#         # )
        
                                                         
# # APPLICATION LOAD BALANCER
#         # Create security group for the ALB
#         load_balancer_sg = ec2.SecurityGroup(
#             self, "SG_ALB",
#             vpc=webvpc,
#             allow_all_outbound=True,
#             security_group_name="ALB-SG"
#             )

#         # Create an ALB
#         self.alb = elbv2.ApplicationLoadBalancer(self, "ALB",  # This configures a publicly accessible ALB that can distribute traffic across resources in the Web VPC.
#             vpc=webvpc,
#             security_group=load_balancer_sg,
#             internet_facing=True, # This makes the load balancer publically accessable.
#             )
        
#          # Create a Target group for the ALB
#         self.target_group = elbv2.ApplicationTargetGroup(self, "target-group",
#             vpc=webvpc,
#             port=443,
#             targets=[self.auto_scaling_group],
#             )

#          # Import an existing SSL certificate
#         certificate = acm.Certificate.from_certificate_arn(self, "Certificate",
#             certificate_arn="arn:aws:acm:eu-central-1:509994537105:certificate/6523d540-5233-443b-921c-df11bfa99e88",
#         )

#         # Add listener to the ALB for port 443
#         self.https_listener = self.alb.add_listener("https_listener",
#             port=443,
#             ssl_policy=elbv2.SslPolicy.RECOMMENDED_TLS,
#             certificates=[certificate],
#             default_target_groups=[self.target_group]
#             )
        
#         # Add listener to the ALB for port 80 and redirect traffic to port 443
#         self.http_listener = self.alb.add_listener("HTTP-Listener-Redirect",
#              port=80,
#              default_action=elbv2.ListenerAction.redirect(
#                  port="443",
#                  protocol="HTTPS",
#                 )
#             )

#          # Output the ALB DNS name
#         CfnOutput(self, "ALB DNS Name",
#             value=self.alb.load_balancer_dns_name,
#             export_name="alb-dns-name"
#             )
        
#         # Output the EC2 instance ID
#         CfnOutput(self, "Web Server Instance ID",
#             value=self.instance_webserver.instance_id,
#             export_name="web-server-instance-id"
#             )
from aws_cdk import Stack, aws_ec2 as ec2, NestedStack, CfnTag
from constructs import Construct
import cdk_workshop.config as config

class CdkWorkshop(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create VPC 1
        self.ahlaam_vpc = ec2.Vpc(
            self, config.VPC, ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            nat_gateways=0, subnet_configuration=[],
            enable_dns_support=True,
            enable_dns_hostnames=True,
        )

        # Create VPC 2
        self.ahlaam_vpc_2 = ec2.Vpc(
            self, config.VPC_2, ip_addresses=ec2.IpAddresses.cidr("10.1.0.0/16"),
            nat_gateways=0, subnet_configuration=[],
            enable_dns_support=True,
            enable_dns_hostnames=True,
        )    

        # Create a network peering stack which creates peering between the production and management VPCs
        self.peering_stack = NetworkPeeringStack(
            self,
            "NetworkPeeringStack",
            vpc_one=self.ahlaam_vpc,
            vpc_two=self.ahlaam_vpc_2,
        ) 

        self.elastic_ip = ec2.CfnEIP(self, "EIP")
        self.internet_gateway = self.attach_internet_gateway()

        self.subnet_id_to_subnet_map = {}
        self.route_table_id_to_route_table_map = {}
        self.security_group_id_to_group_map = {}
        self.instance_id_to_instance_map = {}

        self.create_route_tables()
        self.create_subnets()
        self.create_subnet_route_table_associations()
        self.nat_gateway = self.attach_nat_gateway()
        self.nat_gateway.add_depends_on(self.elastic_ip)
        self.create_routes()

        # Get the subnets and route tables for the VPC peering connection
        Private_subnet = self.subnet_id_to_subnet_map[config.PRIVATE_SUBNET].ref
        Other_vpc_subnet = self.subnet_id_to_subnet_map[config.PUBLIC_SUBNET].ref
        Private_route_table = self.route_table_id_to_route_table_map[config.PRIVATE_ROUTE_TABLE_2].ref
        Other_vpc_route_table = self.route_table_id_to_route_table_map[config.PUBLIC_ROUTE_TABLE_1].ref

        ec2.CfnRoute(
            self, 'RouteToVPC1',
            route_table_id=Private_route_table,
            destination_cidr_block='10.0.0.0/16',  # The CIDR-block of the public VPC
            vpc_peering_connection_id=self.peering_stack.peerconnection.ref,
        )

        ec2.CfnRoute(
            self, 'RouteToVPC2',
            route_table_id=Other_vpc_route_table,
            destination_cidr_block='10.1.0.0/16',  # The CIDR-block of the private VPC
            vpc_peering_connection_id=self.peering_stack.peerconnection.ref
        )

        # Define NACLs
        nacl_admin = ec2.CfnNetworkAcl(self, "NaclAdmin",
            vpc_id=self.ahlaam_vpc_2.vpc_id,
            tags=[{'key': 'Name', 'value': 'NaclAdmin'}]
        )

        nacl_web = ec2.CfnNetworkAcl(self, "NaclWeb",
            vpc_id=self.ahlaam_vpc.vpc_id,
            tags=[{'key': 'Name', 'value': 'NaclWeb'}]
        ) 

        public_subnet_1 = self.subnet_id_to_subnet_map[config.PUBLIC_SUBNET]
        public_subnet_2 = self.subnet_id_to_subnet_map[config.PUBLIC_SUBNET_2]

        # Associate NACLs with subnets
        ec2.CfnSubnetNetworkAclAssociation(self, "NaclAdminAssociation",
            subnet_id=public_subnet_2.ref,
            network_acl_id=nacl_admin.ref
        ).add_dependency(nacl_admin)

        ec2.CfnSubnetNetworkAclAssociation(self, "NaclWebAssociation",
            subnet_id=public_subnet_1.ref, 
            network_acl_id=nacl_web.ref
        ).add_dependency(nacl_web)

        cidr_block = self.subnet_id_to_subnet_map[config.PUBLIC_SUBNET_2].cidr_block

        # Inbound rule in vpc_web for HTTP traffic
        ec2.CfnNetworkAclEntry(
            self,
            "WebServerNaclInboundHTTP",
            network_acl_id=nacl_web.ref,
            rule_number=100,
            protocol=6,  # TCP
            rule_action="allow",
            egress=False,
            port_range=ec2.CfnNetworkAclEntry.PortRangeProperty(
                from_=80,
                to=80
            ),
            cidr_block="0.0.0.0/0",
        )

        # Outbound rule in vpc_web for HTTP
        ec2.CfnNetworkAclEntry(
            self,
            "WebServerNaclOutboundHTTP",
            network_acl_id=nacl_web.ref,
            rule_number=100,
            protocol=6,  # TCP
            rule_action="allow",
            egress=True,
            port_range=ec2.CfnNetworkAclEntry.PortRangeProperty(
                from_=80,
                to=80
            ),
            cidr_block="0.0.0.0/0",
        )

        # Inbound rule in vpc_web for SSH from admin/management server 
        ec2.CfnNetworkAclEntry(
            self,
            "WebServerNaclInboundSSH",
            network_acl_id=nacl_web.ref,
            rule_number=300,
            protocol=6,  # TCP
            rule_action="allow",
            egress=False,
            port_range=ec2.CfnNetworkAclEntry.PortRangeProperty(
                from_=22,
                to=22
            ),
            cidr_block=cidr_block  # Only inbound traffic for SSH from Admin server
        )

        # Add a new inbound rule in vpc_web for RDP from admin/management server
        ec2.CfnNetworkAclEntry(
            self,
            "ManagementServerNaclInboundRDPFromAdmin",
            network_acl_id=nacl_web.ref,
            rule_number=400,  
            protocol=6,  # TCP
            rule_action="allow",
            egress=False,
            port_range=ec2.CfnNetworkAclEntry.PortRangeProperty(
                from_=3389,
                to=3389
            ),
            cidr_block=cidr_block,  
        )

        admin_ip = "192.168.1.250/32"

        # Add a new inbound rule in vpc_manage for RDP from the admin IP
        ec2.CfnNetworkAclEntry(
            self,
            "ManagementServerNaclInboundRDPFromOwnIPtoAdmin",
            network_acl_id=nacl_admin.ref,
            rule_number=500,  
            protocol=6,  # TCP
            rule_action="allow",
            egress=False,
            port_range=ec2.CfnNetworkAclEntry.PortRangeProperty(
                from_=3389,
                to=3389
            ),
            cidr_block=admin_ip,  # Your admin IP
        )

        self.sg_webserver = ec2.SecurityGroup(self, "sg-webserver",
           vpc=self.ahlaam_vpc,
           allow_all_outbound=True,
           description="Security group for the web server"
        )

        self.sg_webserver.add_ingress_rule(
           peer=ec2.Peer.any_ipv4(),
           connection=ec2.Port.tcp(80),
           description="Allow HTTP traffic"
        )


        # Define user data
        WbS_UD = ec2.UserData.for_linux(shebang="#!/bin/bash")
        WbS_UD.add_commands(
            """#!/bin/bash
            yum -y install httpd
            systemctl enable httpd
            systemctl start httpd
            echo '<h1>Hello From Your Web Server!</h1>' > /var/www/html/index.html
            """
        )

        # # Create a key pair for secure SSH connections
        # keypair_webserver = ec2.KeyPair(self, "keypair_for_WbS",
        #     key_name="key_webserver",
        #     key_type=ec2.KeyPairType.RSA,
        #     key_format="ec2.KeypairFormat.PEM",
        #     tags=[CfnTag(
        #         key="trusted_key_webserver",
        #         value="safety"
        #     )]
        # )


        public_subnet_1 = self.subnet_id_to_subnet_map[config.PUBLIC_SUBNET]

        self.instance_webserver = ec2.Instance(self, "instance-webserver",
            instance_name="instance-webserver",
            vpc=self.ahlaam_vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=[public_subnet_1]),
            private_ip_address="10.0.0.0/16",  # Make sure to use quotes for the IP address
            # key_pair=keypair_webserver,  # Use the key pair you created
            security_group=self.sg_webserver,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T2, ec2.InstanceSize.MICRO),
            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2023),
            block_devices=[ec2.BlockDevice(
            device_name="/dev/xvda",
            volume=ec2.BlockDeviceVolume.ebs(
            volume_size=8,
            encrypted=True,
        )
            )],
    user_data=WbS_UD,  # Use the user data defined for the web server
        )



    def create_route_tables(self):
        # Create Route Tables
        for route_table_id in config.ROUTE_TABLES_ID_TO_ROUTES_MAP_1:
            self.route_table_id_to_route_table_map[route_table_id] = ec2.CfnRouteTable(
                self, route_table_id, vpc_id=self.ahlaam_vpc.vpc_id,
                tags=[{'key': 'Name', 'value': route_table_id}]
            )
        for route_table_id in config.ROUTE_TABLES_ID_TO_ROUTES_MAP_2:
            self.route_table_id_to_route_table_map[route_table_id] = ec2.CfnRouteTable(
                self, route_table_id, vpc_id=self.ahlaam_vpc_2.vpc_id,
                tags=[{'key': 'Name', 'value': route_table_id}]
            )

    def create_routes(self):
        # Create routes of the Route Tables
        for route_table_id, routes in config.ROUTE_TABLES_ID_TO_ROUTES_MAP_1.items():
            for i in range(len(routes)):
                route = routes[i]
                kwargs = {
                    **route,
                    'route_table_id': self.route_table_id_to_route_table_map[route_table_id].ref,
                }
                if route['router_type'] == ec2.RouterType.GATEWAY:
                    kwargs['gateway_id'] = self.internet_gateway.ref
                if route['router_type'] == ec2.RouterType.NAT_GATEWAY:
                    kwargs['nat_gateway_id'] = self.nat_gateway.ref
                del kwargs['router_type']
                ec2.CfnRoute(self, f'{route_table_id}-route-{i}', **kwargs)

    def attach_internet_gateway(self) -> ec2.CfnInternetGateway:
        # Create and attach internet gateway to the VPC
        internet_gateway = ec2.CfnInternetGateway(self, config.INTERNET_GATEWAY)
        ec2.CfnVPCGatewayAttachment(self, 'internet-gateway-attachment',
                                    vpc_id=self.ahlaam_vpc.vpc_id,
                                    internet_gateway_id=internet_gateway.ref)
        return internet_gateway

    def attach_nat_gateway(self) -> ec2.CfnNatGateway:
        # Create and attach nat gateway to the VPC 
        nat_gateway = ec2.CfnNatGateway(self, config.NAT_GATEWAY,
                                        allocation_id=self.elastic_ip.attr_allocation_id,
                                        subnet_id=self.subnet_id_to_subnet_map[config.PUBLIC_SUBNET].ref)
        return nat_gateway

    def create_subnets(self):
        # Create subnets of the VPC
        for subnet_id, subnet_config in config.SUBNET_CONFIGURATION_1.items():
            subnet = ec2.CfnSubnet(
                self, subnet_id, vpc_id=self.ahlaam_vpc.vpc_id,
                cidr_block=subnet_config['cidr_block'],
                availability_zone=subnet_config['availability_zone'],
                tags=[{'key': 'Name', 'value': subnet_id}],
                map_public_ip_on_launch=subnet_config['map_public_ip_on_launch'],
            )
            self.subnet_id_to_subnet_map[subnet_id] = subnet

        for subnet_id, subnet_config in config.SUBNET_CONFIGURATION_2.items():
            subnet = ec2.CfnSubnet(
                self, subnet_id, vpc_id=self.ahlaam_vpc_2.vpc_id,
                cidr_block=subnet_config['cidr_block'],
                availability_zone=subnet_config['availability_zone'],
                tags=[{'key': 'Name', 'value': subnet_id}],
                map_public_ip_on_launch=subnet_config['map_public_ip_on_launch'],
            )
            self.subnet_id_to_subnet_map[subnet_id] = subnet

    def create_subnet_route_table_associations(self):
        # Associate subnets with route tables
        for subnet_id, subnet_config in config.SUBNET_CONFIGURATION_1.items():
            route_table_id = subnet_config['route_table_id']
            ec2.CfnSubnetRouteTableAssociation(
                self, f'{subnet_id}-{route_table_id}',
                subnet_id=self.subnet_id_to_subnet_map[subnet_id].ref,
                route_table_id=self.route_table_id_to_route_table_map[route_table_id].ref
            )
        for subnet_id, subnet_config in config.SUBNET_CONFIGURATION_2.items():
            route_table_id = subnet_config['route_table_id']
            ec2.CfnSubnetRouteTableAssociation(
                self, f'{subnet_id}-{route_table_id}',
                subnet_id=self.subnet_id_to_subnet_map[subnet_id].ref,
                route_table_id=self.route_table_id_to_route_table_map[route_table_id].ref
            )

class NetworkPeeringStack(NestedStack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc_one: ec2.Vpc,
        vpc_two: ec2.Vpc,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)  

        # Create VPC Peering connection in the infrastructure  
        self.peerconnection = ec2.CfnVPCPeeringConnection(
            self,
            "VPC1VPC2Connect",
            vpc_id=vpc_one.vpc_id,
            peer_vpc_id=vpc_two.vpc_id,
        )


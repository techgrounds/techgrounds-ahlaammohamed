from aws_cdk import Stack, aws_ec2 as ec2
from constructs import Construct
import cdk_workshop.config as config

class CdkWorkshop(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # self.subnet_id_to_subnet_map_vpc2 = {}

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

        # Create VPC Peering Connection
        vpc_peering_connection = ec2.CfnVPCPeeringConnection(
            self, "MyCfnVPCPeeringConnection",
            peer_vpc_id=self.ahlaam_vpc_2.vpc_id,
            vpc_id=self.ahlaam_vpc.vpc_id,
        )

        # Accept VPC peering connection from the other VPC
        vpc_peering_connection.status = "active"

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


        # self.create_subnets_for_vpc2()
        # self.create_subnet_route_table_associations_for_vpc2()

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
                                        subnet_id=self.subnet_id_to_subnet_map[config.PUBLIC_SUBNET].ref, )
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
    
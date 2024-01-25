from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)

# Basic VPC configs
VPC = 'custom-vpc'
VPC_2 = 'custom-vpc-2'

INTERNET_GATEWAY = 'internet-gateway'
NAT_GATEWAY = 'nat-gateway'
REGION = 'eu-central-1'

# Route tables
PUBLIC_ROUTE_TABLE_1 = 'public-route-table-1'
PRIVATE_ROUTE_TABLE_1 = 'private-route-table-1'

# Route tables
PUBLIC_ROUTE_TABLE_2 = 'public-route-table-2'
PRIVATE_ROUTE_TABLE_2 = 'private-route-table-2'

ROUTE_TABLES_ID_TO_ROUTES_MAP_1 = {
    PUBLIC_ROUTE_TABLE_1: [
        {
            'destination_cidr_block': '0.0.0.0/0',
            'gateway_id': INTERNET_GATEWAY,
            'router_type': ec2.RouterType.GATEWAY
        }
    ],
    PRIVATE_ROUTE_TABLE_1: [
        {
            'destination_cidr_block': '0.0.0.0/0',
            'nat_gateway_id': NAT_GATEWAY,
            'router_type': ec2.RouterType.NAT_GATEWAY
        }
    ],
}

ROUTE_TABLES_ID_TO_ROUTES_MAP_2 = {
    PUBLIC_ROUTE_TABLE_2: [
        {
            'destination_cidr_block': '0.0.0.0/0',
            'gateway_id': INTERNET_GATEWAY,
            'router_type': ec2.RouterType.GATEWAY
        }
    ],
    PRIVATE_ROUTE_TABLE_2: [
        {
            'destination_cidr_block': '0.0.0.0/0',
            'nat_gateway_id': NAT_GATEWAY,
            'router_type': ec2.RouterType.NAT_GATEWAY
        }
    ],
}


# Instances for VPC 1
PUBLIC_SUBNET = 'public-subnet'
PRIVATE_SUBNET = 'private-subnet'

# Subnets for VPC 1
SUBNET_CONFIGURATION_1 = {
    PUBLIC_SUBNET: {
        'availability_zone': 'eu-central-1a',
        'cidr_block': '10.0.2.0/24',
        'map_public_ip_on_launch': True,
        'route_table_id': PUBLIC_ROUTE_TABLE_1,
    },
    PRIVATE_SUBNET: {
        'availability_zone': 'eu-central-1b',
        'cidr_block': '10.0.3.0/24',
        'map_public_ip_on_launch': False,
        'route_table_id': PRIVATE_ROUTE_TABLE_1,
    },
}

# Instances for VPC 2
PUBLIC_SUBNET_2 = 'public-subnet-2'
PRIVATE_SUBNET_2 = 'private-subnet-2'

# Subnets for VPC 2
SUBNET_CONFIGURATION_2 = {
    PUBLIC_SUBNET_2: {
        'availability_zone': 'eu-central-1c',
        'cidr_block': '10.1.0.0/24',
        'map_public_ip_on_launch': True,
        'route_table_id': PUBLIC_ROUTE_TABLE_2,
    },
    PRIVATE_SUBNET_2: {
        'availability_zone': 'eu-central-1b',
        'cidr_block': '10.1.2.0/24',
        'map_public_ip_on_launch': False,
        'route_table_id': PRIVATE_ROUTE_TABLE_2,
    },
}







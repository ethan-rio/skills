# AWS4 Stencil Lookup Table

Source of truth: `https://github.com/jgraph/drawio/blob/dev/src/main/webapp/js/diagramly/sidebar/Sidebar-AWS4.js`
Last verified: 2026-04-28 (Q1 2025 icon pack).

## Style patterns (memorise both)

### Service icon (99% of cases)

```
sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor={CATEGORY_COLOR};strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.{ICON_NAME};labelPosition=center;
```

Size: **78×78**. Label below icon via `verticalLabelPosition=bottom`.

### Direct shape (7 exceptions) — ALB, NLB, API Gateway, Internet Gateway, NAT Gateway, VPN Gateway, Customer Gateway

```
shape=mxgraph.aws4.{ICON_NAME};...
```

No `resourceIcon` wrapper, no `resIcon=`. Icon has its own aspect ratio — use `aspect=fixed`.

### Group container

```
shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_{KIND};container=1;collapsible=0;recursiveResize=0;strokeColor={ZONE_COLOR};fillColor=none;dashed={0|1};verticalAlign=top|bottom;align=left|center;spacingLeft=30;
```

Kinds: `region`, `vpc`, `az`, `public_subnet`, `private_subnet`, `security_group`, `ecs`, `eks`, `corporate_data_center`, `auto_scaling_group`, `account`, `aws_cloud_alt`.

## Lookup table

### Containers (category: Groups)

| What it is | `grIcon=` | Stroke color | Dashed |
|---|---|---|---|
| AWS Cloud | `group_aws_cloud_alt` | `#232F3E` | 0 |
| Region | `group_region` | `#147EBA` | 1 |
| VPC | `group_vpc` | `#248814` | 0 |
| Availability Zone | `group_az` | `#147EBA` | 1 |
| Public Subnet | `group_public_subnet` | `#7AA116` | 0 |
| Private Subnet | `group_private_subnet` | `#147EBA` | 0 |
| Security Group | `group_security_group` | `#DD3522` | 1 |
| ECS Cluster | `group_ecs` | `#D86613` | 1 |
| EKS Cluster | `group_eks` | `#D86613` | 1 |
| Auto Scaling Group | `group_auto_scaling_group` | `#D86613` | 1 |
| Corporate Data Center | `group_corporate_data_center` | `#545B64` | 1 |
| Account | `group_account` | `#B7CA9D` | 0 |

### Compute

| Service | `resIcon=` | `fillColor=` |
|---|---|---|
| EC2 | `ec2` | `#ED7100` |
| Lambda | `lambda` | `#ED7100` |
| Fargate | `fargate` | `#ED7100` |
| ECS | `elastic_container_service` | `#ED7100` |
| EKS | `elastic_kubernetes_service` | `#ED7100` |
| ECR | `ecr` | `#ED7100` |
| Batch | `batch` | `#ED7100` |

### Networking & Content Delivery (purple `#8C4FFF`)

| Service | name |
|---|---|
| ALB (direct shape) | `application_load_balancer` |
| NLB (direct shape) | `network_load_balancer` |
| API Gateway (direct shape) | `api_gateway` |
| Route 53 | `route_53` |
| CloudFront | `cloudfront` |
| VPC | `vpc` (prefer the group container form) |
| Transit Gateway | `transit_gateway` |
| Direct Connect | `direct_connect` |
| PrivateLink | `privatelink` |
| VPN | `site-to-site_vpn` |

### Storage (green `#7AA116`)

| Service | name |
|---|---|
| S3 | `s3` |
| EFS | `elastic_file_system` |
| EBS | `elastic_block_store` |
| FSx | `fsx` |
| S3 Glacier | `s3_glacier` |
| Backup | `backup` |

### Database (dark purple `#C925D1`)

| Service | name |
|---|---|
| DynamoDB | `dynamodb` |
| RDS | `rds` |
| Aurora | `aurora` |
| DocumentDB | `documentdb` |
| OpenSearch | `opensearch_service` |

### AI / ML (teal `#01A88D`)

| Service | name |
|---|---|
| Bedrock | `bedrock` |
| SageMaker | `sagemaker` |
| Textract | `textract` |
| Comprehend | `comprehend` |

### Security, Identity, Compliance (red `#DD344C`)

| Service | name |
|---|---|
| IAM | `identity_and_access_management` |
| IAM Identity Center (SSO) | `single_sign_on` |
| Cognito | `cognito` |
| Secrets Manager | `secrets_manager` |
| KMS | `key_management_service` |
| Network Firewall | `network_firewall` |
| WAF | `waf` |
| Shield | `shield` |
| Certificate Manager | `certificate_manager_3` |
| GuardDuty | `guardduty` |

### Management & Governance (pink `#E7157B`)

| Service | name |
|---|---|
| CloudWatch | `cloudwatch_2` |
| CloudFormation | `cloudformation` |
| CloudTrail | `cloudtrail` |
| Systems Manager | `systems_manager` |
| Config | `config` |
| Service Catalog | `service_catalog` |

### Application Integration (pink `#E7157B`)

| Service | name |
|---|---|
| EventBridge | `eventbridge` |
| SNS | `simple_notification_service` |
| SQS | `simple_queue_service` |
| Step Functions | `step_functions` |
| AppFlow | `appflow` |
| AppSync | `appsync` |

### Analytics

| Service | name | colour |
|---|---|---|
| Kinesis | `kinesis` | `#8C4FFF` |
| Athena | `athena` | `#8C4FFF` |
| Glue | `glue` | `#8C4FFF` |
| QuickSight | `quicksight` | `#8C4FFF` |
| MSK | `managed_streaming_for_apache_kafka` | `#8C4FFF` |

## Known wrong names (historical mistakes)

| Don't use | Use instead |
|---|---|
| `elastic_container_registry` | `ecr` |
| `identity_and_access_management_iam` | `identity_and_access_management` |
| `cloudwatch` | `cloudwatch_2` |
| `certificate_manager` | `certificate_manager_3` |
| `account` (as resIcon) | `group_account` (as grIcon in a group container) |

## If a service isn't here

Run:
```
WebFetch https://github.com/jgraph/drawio/blob/dev/src/main/webapp/js/diagramly/sidebar/Sidebar-AWS4.js
  grep for the service name (case-insensitive)
```

Then add to this table. Never invent `resIcon` names — the stencil file is authoritative.

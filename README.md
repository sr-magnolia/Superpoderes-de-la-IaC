# Superpoderes de la IaC

Infraestructura como código con AWS CloudFormation: VPC, EC2, ALB con Auto Scaling, DNS con Route 53 y failover multi-región.

## Arquitectura

```
Internet → Route 53 (Failover) → ALB → Auto Scaling Group (1-10 instancias) → Subnets Privadas
```

## Requisitos

- AWS CLI configurado con credenciales válidas
- Permisos para crear recursos de VPC, EC2, ELB y Route 53
- Una Hosted Zone en Route 53 (para los pasos 4 y 5)

## Despliegue

Los stacks se despliegan en orden ya que cada uno depende de los outputs del anterior.

### Opción A: Desde la Consola de AWS

1. Ir a **CloudFormation** → **Create stack** → **With new resources**
2. Seleccionar **Upload a template file** y subir el archivo `.yaml` correspondiente
3. Asignar un nombre al stack y completar los parámetros
4. Hacer clic en **Next** → **Next** → **Submit**
5. Esperar a que el estado sea `CREATE_COMPLETE` antes de pasar al siguiente stack

Seguir este orden y usar estos nombres de stack como referencia:

| Orden | Archivo | Nombre del Stack | Parámetros clave |
|-------|---------|-----------------|------------------|
| 1 | `vpc-network.yaml` | `MiProyecto-VPC-Stack` | `ProjectName`: MiProyecto |
| 2 | `ec2-instance.yaml` | `MiProyecto-EC2-Stack` | `NetworkStackName`: MiProyecto-VPC-Stack |
| 3 | `alb-asg.yaml` | `MiProyecto-Compute-Stack` | `NetworkStackName`: MiProyecto-VPC-Stack |
| 4 | `route53-dns.yaml` | `MiProyecto-DNS-Stack` | `NetworkStackName`, `ComputeStackName`, `HostedZoneId`, `DomainName` |
| 5 | `route53-failover.yaml` | `MiProyecto-Failover-Stack` | `HostedZoneId`, `DomainName`, ALB DNS y Zone IDs de ambas regiones |

Para eliminar, ir a **CloudFormation** → seleccionar el stack → **Delete**, en orden inverso (5 → 1).

### Opción B: Desde la CLI

### 1. VPC y Red

Crea la VPC, subnets públicas/privadas, Internet Gateway y NAT Gateway.

```bash
aws cloudformation deploy \
  --template-file vpc-network.yaml \
  --stack-name MiProyecto-VPC-Stack \
  --parameter-overrides ProjectName=MiProyecto
```

### 2. Instancia EC2

Crea una instancia EC2 en una subnet privada de la VPC.

```bash
aws cloudformation deploy \
  --template-file ec2-instance.yaml \
  --stack-name MiProyecto-EC2-Stack \
  --parameter-overrides NetworkStackName=MiProyecto-VPC-Stack
```

### 3. ALB + Auto Scaling Group

Crea un Application Load Balancer en las subnets públicas y un ASG (1-10 instancias) en las subnets privadas.

```bash
aws cloudformation deploy \
  --template-file alb-asg.yaml \
  --stack-name MiProyecto-Compute-Stack \
  --parameter-overrides NetworkStackName=MiProyecto-VPC-Stack
```

### 4. DNS (Route 53)

Crea registros Alias apuntando al ALB. Requiere una Hosted Zone existente.

```bash
aws cloudformation deploy \
  --template-file route53-dns.yaml \
  --stack-name MiProyecto-DNS-Stack \
  --parameter-overrides \
    NetworkStackName=MiProyecto-VPC-Stack \
    ComputeStackName=MiProyecto-Compute-Stack \
    HostedZoneId=<TU_HOSTED_ZONE_ID> \
    DomainName=<TU_DOMINIO>
```

### 5. DNS Failover

Configura failover entre dos regiones usando registros Alias con Health Checks. Requiere un ALB secundario desplegado en otra región.

```bash
aws cloudformation deploy \
  --template-file route53-failover.yaml \
  --stack-name MiProyecto-Failover-Stack \
  --parameter-overrides \
    HostedZoneId=<TU_HOSTED_ZONE_ID> \
    DomainName=<TU_DOMINIO> \
    PrimaryALBDNS=<DNS_DEL_ALB_PRIMARIO> \
    PrimaryALBHostedZoneId=<ZONE_ID_ALB_PRIMARIO> \
    SecondaryALBDNS=<DNS_DEL_ALB_SECUNDARIO> \
    SecondaryALBHostedZoneId=<ZONE_ID_ALB_SECUNDARIO>
```

## Limpieza

Elimina los stacks en orden inverso para evitar errores de dependencia:

```bash
aws cloudformation delete-stack --stack-name MiProyecto-Failover-Stack
aws cloudformation delete-stack --stack-name MiProyecto-DNS-Stack
aws cloudformation delete-stack --stack-name MiProyecto-EC2-Stack
aws cloudformation delete-stack --stack-name MiProyecto-Compute-Stack
aws cloudformation delete-stack --stack-name MiProyecto-VPC-Stack
```

## Tests de Carga

Consulta [tests/README.md](tests/README.md) para instrucciones de cómo ejecutar pruebas de carga con Locust contra el ALB.

# User stories
## Epic 1: Applicatievereisten
## Exploratie: Verduidelijking van de eisen
## Deliverable: Puntsgewijze omschrijving van alle eisen
Eisen:
- Alle VM disks moeten encrypted zijn.
- De webserver moet dagelijks gebackupt worden. De backups moeten 7 dagen behouden worden.
- De webserver moet op een geautomatiseerde manier geïnstalleerd worden.
- De admin/management server moet bereikbaar zijn met een publiek IP.
- De admin/management server moet alleen bereikbaar zijn van vertrouwde locaties (office/admin’s thuis)
- De volgende IP ranges worden gebruikt: 10.10.10.0/24 & 10.20.20.0/24
- Alle subnets moeten beschermd worden door een firewall op subnet niveau.
- SSH of RDP verbindingen met de webserver mogen alleen tot stand komen vanuit de admin server.
- Wees niet bang om verbeteringen in de architectuur voor te stellen of te implementeren, maar maak wel harde keuzes, zodat je de deadline kan halen.

Omschrijving
- Cloud Provider: AWS
- Development Budget: €10, Production Budget: €150.
- Gebruik AWS Lambda voor lichte workloads en AWS Elastic Beanstalk voor de webserver. Kies voor Amazon RDS voor de SQL database.
- Subnet met 30 Bruikbare IP Adressen: Creëer een Amazon VPC (Virtual Private Cloud) met een subnet dat ten minste 30 bruikbare IP-adressen heeft.
- Verbinding Website naar Database: Configureer de juiste beveiligingsgroepen in AWS om de verbinding tussen de website en database mogelijk te maken zonder het netwerk te openen.
SQL Database en Post Deployment Script: Maak gebruik van Amazon RDS voor de SQL-database. Sla post-deployment scripts op in Amazon S3 (Simple Storage Service).
RPO 24 uur, RTO 1 uur.
- Website 24/7 Online: Gebruik AWS Elastic Beanstalk voor automatische schaalbaarheid en hoge beschikbaarheid. Configureer Amazon CloudWatch-alarms voor monitoring en meldingen.
- Admin Server Beschikbaarheid: Implementeer AWS Auto Scaling om de beschikbaarheid van de admin-server te waarborgen.
- Toegang tot Admin Server: Configureer AWS Identity and Access Management (IAM) voor toegangsbeheer. In productie beperk de toegang tot het IP-adres van de admin.
- Opslag van Scripts: Gebruik Amazon S3 voor de opslag van scripts. Gebruik IAM-rolbeperkingen om alleen autorisatie te verlenen aan admin en machines die scripts aanroepen.
- VM Encryption: Industry Standard: Implementeer AWS Key Management Service (KMS) voor het beheren van encryptiesleutels.
- Backup op Gunstig Moment: Configureer Amazon RDS-backups op een geschikt tijdstip, liefst op een moment waarop weinig klanten actief zijn (bijvoorbeeld 4:00 's nachts).


|| **As a team, we want to have a clear understanding of the requirements of the application.** |
|---|



**Exploration**



You've already received a lot of information. Some requirements are already mentioned in this document, but this list may be incomplete or unclear. It's important to address all uncertainties before undertaking substantial work.

**Deliverable**

A bulleted description of all requirements.

Colons can be used to align columns.

|**Epic**     |**Description**| Cool  |
| ------------- |:-------------:| -----:|
| col 3 is      | right-aligned | $1600 |
| col 2 is      | centered      |   $12 |
| zebra stripes | are neat      |    $1 |

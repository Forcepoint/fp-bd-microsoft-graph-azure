# microsoft-graph-azure
## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)

## General info
Pull authentication events from Azure AD via Graph API and send events to FBA
all the scripts in this project are used only for POC purpose.

azure_fba_installer.sh script installs all services on CentOS machine

## Technologies
* Python Required version is 3 and above
* Python module 'requests' is required
* Python module 'flask' is required
* Python module 'confluent_kafka' is required
* Python module 'PyYAML' is required
* Python module 'pytz' is required
* Python module 'python-dateutil' is required
* Python module 'adal' is required



## Setup
* Copy the azure_fba_installer.tar.gz file into /root folder of the CentOS machine that will host it 
* Decompress the azure_fba_installer.tar.gz file using the command 
```
tar -zxvf azure_fba_installer.tar.gz
```
* Go into the /root/azure_fba_installer folder and edit the setting.yml file so that the parameters
* Make sure the azure_fba_installer.sh file is executable using the command 
```
sudo +x azure_fba_installer.sh
```
Install the Risk Level Manager using the command 
```
sudo ./azure_fba_installer.sh 
```
The installer script will read the settings file, move the services to application_directory and create
all services. The settings.yml file will then be moved to application_directory(defined in settings.yml), do not change the location of this file. 
* Once the installation is completed, reboot the CentOS machine
* After reboot is completed, log into the CentOS machine and verify all 5 services of the Risk Level Manager are
running with the command systemctl list-units | grep azure
the status of all services must be 'loaded active running'
 
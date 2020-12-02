#!/bin/bash

echo "Installing python3"
sudo yum install -y https://centos7.iuscommunity.org/ius-release.rpm
#sudo yum groups install "Development Tools" -y
#sudo yum update -y
sudo yum install -y python36u python36u-libs python36u-devel python36u-pip

# install python modules
sudo pip3 install flask
sudo pip3 install requests
sudo pip3 install confluent-kafka
sudo pip3 install PyYAML
sudo pip3 install pytz
sudo pip3 install python-dateutil
sudo pip3 install adal

echo "INSTALLING JAVA...."
yum install java-1.8.0-openjdk -y
echo 1 | update-alternatives --config java


# check if settings file is exists
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SETTINGS_FILE=${DIR}/settings.yml

if [[ ! -f "$SETTINGS_FILE" ]]; then
    echo "The settings file:$SETTINGS_FILE does not exist"
    exit 1
fi

# create required directories
APPLICATION_DIRECTORY="$(python3 "$DIR"/installer_helper.py "$SETTINGS_FILE")"
echo "**** Moving the application files to $APPLICATION_DIRECTORY ******"
mv "$DIR"/src "$APPLICATION_DIRECTORY"/
mv "$DIR"/scripts "$APPLICATION_DIRECTORY"/
mv "$SETTINGS_FILE" "$APPLICATION_DIRECTORY"/settings.yml
echo "THE SETTINGS FILE IS MOVED TO $APPLICATION_DIRECTORY"
SETTINGS_FILE_P=${APPLICATION_DIRECTORY}/settings.yml

sudo chmod +x "$APPLICATION_DIRECTORY"/scripts/*

sleep 4
echo "CREATING SERVICES...."
"$APPLICATION_DIRECTORY"/scripts/azure_event_service.sh service -c "$SETTINGS_FILE_P"
"$APPLICATION_DIRECTORY"/scripts/azure_risk_level_manager.sh service -c "$SETTINGS_FILE_P"
"$APPLICATION_DIRECTORY"/scripts/azure_user_service.sh service -c "$SETTINGS_FILE_P"
"$APPLICATION_DIRECTORY"/scripts/consumer_service.sh service -c "$SETTINGS_FILE_P"
"$APPLICATION_DIRECTORY"/scripts/fba_service.sh service -c "$SETTINGS_FILE_P"
"$APPLICATION_DIRECTORY"/scripts/kafka_service.sh service -c "$SETTINGS_FILE_P"

sleep 4
#enable all services
echo "ENABLE ALL SERVICES.."
sudo systemctl enable azure_fba_consumer.service
sudo systemctl enable azure_event.service
sudo systemctl enable azure_risk_level.service
sudo systemctl enable azure_user.service
sudo systemctl enable azure_fba.service
sudo systemctl enable zookeeper.service
sudo systemctl enable kafka.service



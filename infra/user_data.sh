#!/bin/bash
exec > >(tee -a /var/log/ec2-init.log|logger -t [ec2-init] -s 2>/dev/console) 2>&1
echo [`date -u +"%Y-%m-%dT%H:%M:%SZ"`] Started User Data
set -x

function s3_website
{
    mkdir /opm
    chdir 755 /opm
    aws s3 cp s3://elasticbeanstalk-us-east-1-422356278867/node_modules.zip /opm
    unzip /opm/node_modules.zip -d /opm
}

function start_nodejs
{
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
    . ~/.nvm/nvm.sh
    nvm install 16.15.1
}

function start_opm_bot
{
    pip3 install discord.py
    pip3 install requests
    pip3 install python-dotenv
    pip3 install urllib3==1.26.6
    sudo python3 /opm/opm-bot/main.py &
}

function gen_cert
{
    name=
    openssl genrsa -out /etc/ssl/private/${name}.pem 2048
    openssl req -new -key /etc/ssl/private/${name}.pem -subj /CN=${name}/ -out /etc/ssl/${name}.csr
    openssl x509 -req -days 3650 -in /etc/ssl/${name}.csr -signkey /etc/ssl/private/${name}.pem -out /etc/ssl/certs/${name}.pem
}

s3_website
start_nodejs
start_opm_bot
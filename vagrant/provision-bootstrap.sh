#!/usr/bin/env bash

echo "Installing and configuring Docker..."
yum install -y yum-utils device-mapper-persistent-data lvm2 nano
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install -y docker-ce docker-ce-cli containerd.io
mkdir /etc/systemd/system/docker.service.d

echo "[Service]
ExecStart=
ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:2375 -H unix://var/run/docker.sock
" > /etc/systemd/system/docker.service.d/docker.conf

systemctl daemon-reload
systemctl start docker
systemctl enable docker
usermod -a -G docker vagrant

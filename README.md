# Dockerhub commandline tool

A simple python module that can fetch docker images from the dockerhub without installing any code from the docker project
on your server/computer/laptop.

This can get a .tgz or an unpacked rootfs for usage with plain LXC, systemd-nspawn or proxmox containers.

## Usage

```bash
# Download alpine image for proxmox
python3 -m dockerhub --tgz alpine /var/lib/vz/templates/alpine

# Download rootfs for systemd-nspawn
python3 -m dockerhub alpine /tmp/example
sudo systemd-nspawn -D /tmp/example

# Download specific version (debian experimental)
python3 -m dockerhub debian:experimental /tmp/deb9

# Download user repository (latest and develop)
python3 -m dockerhub gogs/gogs /tmp/gogs
python3 -m dockerhub gogs/gogs:develop /tmp/gogs-dev
```

Come utilizzare la VM pre-configurata
===

## Pre-requisiti
E' necessario avere installato sul proprio pc:
- Vagrant
- VirtualBox
- l'eseguibile di docker (docker cli)

## Uso della VM
Qui trovate l'elenco di comandi di Vagrant utili per usare la macchina virtuale:

| azione | comando |
|---|---|
| avviare | `vagrant up` |
| fermare | `vagrant halt` |
| rimuovere | `vagrant destroy` |
| verificare lo stato | `vagrant status` |
| collegarsi con ssh | `vagrant ssh` |

## NOTE
Per usare la docker engine presente nella VM è necessario istruire il client docker per connettersi remotamente alla engine.
E' possibile farlo definiendo la seguente variabile di ambiente per il terminale che useremo durante l'esercizio.
```bash
export DOCKER_HOST=tcp://192.168.50.91:2375
```

TDD with Ansible
===

## Prerequisiti
I seguenti pre-requisiti sono necessari per eseguire Ansible a Molecule:
- sistema operativo linux
- docker
- python
- pip

Al fine di testare i Apache, MySQL (o MariaDB) come servizi è necessario che la macchina linux usi **systemd** come gestore di servizi.

## Installazione
Installazione di molecule e delle altre librerie usate:
```bash
pip install --user ansible==2.8.0 testinfra==3.0.5 molecule==2.20.1
```

## Macchina virtuale già configurata - Opzionale
All'interno del repository è presente la definizione di una VM CentOS7 utilizzabile come sistema linux host per eseguire l'esercizio.
La VM è definita tramite Vagrant, quindi per utilizzarla è necessario avere installato sul proprio pc Vagrant e VirtualBox.
[dettagli](./vagrant/README.md)

## Goal
Preparare un server con lo stack LAMP per ospitare siti web e.g. wordpress

Piattaforme target:
- CentOS 7
- Ubuntu LTS 18.04

Cosa ci serve:
- **L**inux (una delle tre piattaforme elencate sopra)
- **A**pache (web server)
- **M**ySQL/**M**ariaDB (database server)
- **P**HP (runtime)

## Live Code
- [ ] brevissima introduzione ad Ansible
- [ ] spiegare lo stack utilizzato (molecule + ansible con docker + testinfra)
- [x] creare il role `molecule init role -d docker -r lamp-live`
- [x] mostrare rapidamente folder e file di ansible
- [x] mostrare molecule boilerplate (molecule.yml and test_default.py)
- [ ] eseguire il test `molecule test`
  - [x] Test matrix
  - [x] errore durante l'esecuzione di _lint_
  - [x] fix meta/main.yml
- [ ] `molecule converge && molecule verify` --> esecuzione più rapida e adatta per TDD
- [x] print distro version - debug msg
- [x] add platform (ubuntu)
- [ ] **Apache2**
  - [x] test_apache_installed
  - [x] install apache
  - [x] test_apache_service_running_and_enabled
  - [x] change platforms using _geerlingguy_ versions
  - [ ] start Apache2 and enables it as a service
- [ ] **index.html** with vars
  - [ ] test presence of index.html
  - [ ] create empty template and deploy it
  - [ ] test content of index.html
  - [ ] create expected index.html
  - [ ] write template and use variables
- [ ] refactor task
  - [ ] remove duplication using distribution specific vars
  - [ ] use of existing variables instead of hard-coded values
  - [ ] removal of conditions in favor of _"distribution dependant"_ imports

## Code Snippets
### print distro version - debug msg
task/main.yml
```yaml
- name: print distro version
  debug: msg="{{ ansible_distribution }} {{ ansible_distribution_version }}"
```

### install on different platforms
meta/main.yml
```yaml
    - name: ubuntu
      versions: 18.04
```
molecule.yml
```yaml
  - name: ubuntu1804
    image: ubuntu:18.04
```

### test package installed
test_default.py
```python
def test_apache_installed(host):
    apache_package_name = _get_apache_package_name(host.system_info.distribution)
    apache_package = host.package(apache_package_name)

    assert apache_package.is_installed
```
Package name is different between distros
```python
def _get_apache_package_name(distribution):
    return {
        "ubuntu": "apache2",
        "centos": "httpd"
    }.get(distribution)
```

### install package
```yaml
- name: Install Apache on Debian-based distros
  block:
    - name: ensure apache is installed on (Debian-based)
      apt:
        name: apache2
        state: present
        update_cache: true
  when: ansible_os_family == 'Debian'

- name: Install Apache on RedHat-based distros
  block:
    - name: ensure apache is installed on (RedHad-based)
      yum:
        name: httpd
        state: present
        update_cache: true
  when: ansible_os_family == 'RedHat'
```

### test package running and enabled
```python
def test_apache_service_running_and_enabled(host):
    apache_package_name = _get_apache_package_name(host.system_info.distribution)
    apache_package = host.service(apache_package_name)

    assert apache_package.is_running
    assert apache_package.is_enabled
```

### Failed to get D-Bus connection: Operation not permitted
molecule.yml
```yaml
  - name: centos7
    image: geerlingguy/docker-centos7-ansible:latest
    command: ""
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
    privileged: true
    pre_build_image: true
  - name: ubuntu1804
    image: geerlingguy/docker-ubuntu1804-ansible:latest
    command: ""
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
    privileged: true
    pre_build_image: true
```

### task running-and-enabled.yml
running-and-enabled.yml
```yaml
- name: ensure Apache is running and enabled
  service:
    name: "{{ apache_service_name }}"
    state: started
    enabled: true
```
main.yml
```yaml
    - import_tasks: running-and-enabled.yml
      vars:
        apache_service_name: httpd
```

### test index.html presence
test_default.py
```python
def test_index_html_exists(host):
    file = host.file("/var/www/html/index.html")

    assert file.is_file
    assert file.exists
```

```yaml
- name: "Ensure index.html is present"
  template:
    src: index.html.j2
    dest: /var/www/html/index.html
```

### test index.html equality
```html
<!DOCTYPE html>
<html>
    <head>
        <title>My Page</title>
    </head>
    <body>
        <h1>Working Software Conference</h1>
        <p>This is just a simple html page</p>
    </body>
</html>
```

```python
def test_index_html_is_equals_to_expected(host):
    file = host.file("/var/www/html/index.html")
    expected = open("expected/index.html",'r')

    assert file.content_string == expected.read()
```

### variables
playbook.yml
```yaml
  vars_files:
    - vars/test.yml
```
vars/test.yml
```yaml
conference_name: "Working Software Conference"
```

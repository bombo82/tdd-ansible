import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_apache2_package(host):
    assert host.package('httpd').is_installed


def test_apache_is_running_and_enabled(host):
    service = host.service('httpd')

    assert service.is_running
    assert service.is_enabled

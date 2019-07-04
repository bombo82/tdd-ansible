import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def _get_apache_package_name(distribution):
    return {
        "ubuntu": "apache2",
        "centos": "httpd"
    }.get(distribution)


def test_apache_is_installed(host):
    package_name = _get_apache_package_name(host.system_info.distribution)
    package = host.package(package_name)

    assert package.is_installed


def test_apache_is_running_and_enabled(host):
    package_name = _get_apache_package_name(host.system_info.distribution)
    service = host.service(package_name)

    assert service.is_running
    assert service.is_enabled

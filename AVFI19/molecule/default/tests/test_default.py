import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_hosts_file(host):
    f = host.file('/etc/hosts')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


def _get_sosreport_package_name(distribution):
    return {
        "ubuntu": "sosreport",
        "centos": "sos"
    }.get(distribution)


def test_sos_report_is_installed(host):
    package_name = _get_sosreport_package_name(host.system_info.distribution)
    package = host.package(package_name)

    assert package.is_installed

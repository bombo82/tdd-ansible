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


def test_index_html_exists(host):
    index_html = host.file("/var/www/html/index.html")

    assert index_html.exists


def test_index_html_is_equals_to_expected(host):
    index_html = host.file("/var/www/html/index.html")
    expected = open("expected/index.html")

    assert index_html.content_string == expected.read()

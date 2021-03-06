
debian_os = ['debian', 'ubuntu']
rhel_os = ['redhat', 'centos']


def test_distribution(host):
    assert host.system_info.distribution.lower() in debian_os + rhel_os


def test_repo_pinning_file(host):
    if host.system_info.distribution.lower() in debian_os:
        f = host.file('/etc/apt/preferences.d/pdns-recursor')
        assert f.exists
        assert f.user == 'root'
        assert f.group == 'root'
        f.contains('Package: pdns-recursor')
        f.contains('Pin: origin repo.powerdns.com')
        f.contains('Pin-Priority: 600')


def test_package(host):
    p = host.package('pdns-recursor')
    assert p.is_installed


def test_service(host):
    # Using Ansible to mitigate some issues with the service test on debian-8
    s = host.ansible('service', 'name=pdns-recursor state=started enabled=yes')
    assert s["changed"] is False


def test_config(host):
    with host.sudo():
        fc = fr = None
        if host.system_info.distribution.lower() in debian_os:
            fc = host.file('/etc/powerdns/recursor.conf')
            fr = host.file('/etc/powerdns/rpz.lua')
        if host.system_info.distribution.lower() in rhel_os:
            fc = host.file('/etc/pdns-recursor/recursor.conf')
            fr = host.file('/etc/pdns-recursor/rpz.lua')

        assert fc.exists
        assert fc.user == 'root'
        assert fc.group == 'root'
        assert 'lua-config-file=' + fr.path in fc.content

        assert fr.exists
        assert fr.user == 'root'
        assert fr.group == 'root'


def systemd_override(host):
    smgr = host.ansible("setup")["ansible_facts"]["ansible_service_mgr"]
    if smgr == 'systemd':
        fname = '/etc/systemd/system/pdns-recursor.service.d/override.conf'
        f = host.file(fname)

        assert f.exists
        assert f.user == 'root'
        assert f.group == 'root'
        assert 'LimitCORE=infinity' in f.content

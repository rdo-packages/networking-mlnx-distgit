%global drv_vendor Mellanox
%global srcname networking_mlnx
%global package_name networking-mlnx
%global docpath doc/build/html
%global service neutron

Name:           python-%{package_name}
Version:        XXX
Release:        XXX
Summary:        %{drv_vendor} OpenStack Neutron driver
Obsoletes:      openstack-%{service}-mellanox

License:        ASL 2.0
URL:            https://pypi.python.org/pypi/%{package_name}
Source0:        https://tarballs.openstack.org/%{package_name}/%{package_name}-%{version}.tar.gz
Source1:        %{service}-mlnx-agent.service
Source2:        eswitchd.service


BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python-mock
BuildRequires:  python-neutron-tests
BuildRequires:  python-oslo-sphinx
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  python-sphinx
BuildRequires:  python-testrepository
BuildRequires:  python-testtools

Requires:       python-babel
Requires:       python-pbr
Requires:       openstack-%{service}-common

%description
This package contains %{drv_vendor} networking driver for OpenStack Neutron.

%prep
%setup -q -n %{package_name}-%{upstream_version}

%build
%{__python2} setup.py build
%{__python2} setup.py build_sphinx
rm %{docpath}/.buildinfo

%install
export PBR_VERSION=%{version}
export SKIP_PIP_INSTALL=1
%{__python2} setup.py install --skip-build --root %{buildroot}

mkdir -p %{buildroot}/%{_sysconfdir}/%{service}/conf.d/%{service}-mlnx-agent
mkdir -p %{buildroot}/%{_sysconfdir}/%{service}/conf.d/eswitchd
mkdir -p %{buildroot}/%{_sysconfdir}/%{service}/rootwrap.d

install -d -m 755 %{buildroot}%{_sysconfdir}/%{service}/plugins/ml2
install -d -m 755 %{buildroot}%{_sysconfdir}/%{service}/plugins/mlnx
install -d -m 755 %{buildroot}%{_sysconfdir}/rootwrap.d/
install -p -D -m 640 etc/%{service}/plugins/ml2/ml2_conf_sdn.ini  %{buildroot}%{_sysconfdir}/%{service}/plugins/ml2
install -p -D -m 640 etc/%{service}/plugins/ml2/eswitchd.conf %{buildroot}%{_sysconfdir}/%{service}/plugins/ml2
install -p -D -m 640 etc/%{service}/plugins/mlnx/mlnx_conf.ini %{buildroot}%{_sysconfdir}/%{service}/plugins/mlnx
install -p -D -m 640 etc/%{service}/rootwrap.d/eswitchd.filters %{buildroot}%{_sysconfdir}/%{service}/rootwrap.d/
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{service}-mlnx-agent.service
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/eswitchd.service


# Remove unused files
rm -rf %{buildroot}%{python_sitelib}/networking_mlnx/hacking


%post
%systemd_post %{service}-mlnx-agent.service
%systemd_post eswitchd.service


%preun
%systemd_preun %{service}-mlnx-agent.service
%systemd_preun eswitchd.service


%postun
%systemd_postun_with_restart %{service}-mlnx-agent.service
%systemd_postun_with_restart eswitchd.service


%files
%license LICENSE
%doc README.rst
%doc %{docpath}
%{python2_sitelib}/%{srcname}
%{python2_sitelib}/%{srcname}-%{version}-py%{python2_version}.egg-info
%config(noreplace) %attr(0640, root, %{service}) %{_sysconfdir}/%{service}/plugins/ml2/*
%config(noreplace) %attr(0640, root, %{service}) %{_sysconfdir}/%{service}/plugins/mlnx/*

%{_bindir}/%{service}-mlnx-agent
%{_unitdir}/%{service}-mlnx-agent.service
%{_bindir}/eswitchd
%{_unitdir}/eswitchd.service
%{_bindir}/ebrctl

%dir %{_sysconfdir}/%{service}/plugins/mlnx
%dir %{_sysconfdir}/%{service}/conf.d/%{service}-mlnx-agent
%dir %{_sysconfdir}/%{service}/conf.d/eswitchd

%attr(0640, root, %{service}) /etc/neutron/rootwrap.d/eswitchd.filters

%changelog

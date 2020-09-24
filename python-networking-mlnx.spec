%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
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
Source0:        https://pypi.io/packages/source/n/%{package_name}/%{package_name}-%{upstream_version}.tar.gz
Source1:        %{service}-mlnx-agent.service
Source2:        eswitchd.service


BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-mock
BuildRequires:  python3-neutron-tests
BuildRequires:  python3-oslo-sphinx
BuildRequires:  python3-pbr
BuildRequires:  python3-setuptools
BuildRequires:  python3-sphinx
BuildRequires:  python3-testrepository
BuildRequires:  python3-testtools
BuildRequires:  systemd
%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

%description
This package contains %{drv_vendor} networking driver for OpenStack Neutron.

%package -n python3-%{package_name}
Summary: Mellanox OpenStack Neutron driver
%{?python_provide:%python_provide python3-%{package_name}}

Requires:       python3-babel >= 1.3
Requires:       python3-eventlet >= 0.18.2
Requires:       python3-netaddr >= 0.7.18
Requires:       python3-neutron-lib >= 2.4.0
Requires:       python3-neutronclient >= 6.7.0
Requires:       python3-oslo-config >= 2:5.2.0
Requires:       python3-openstackclient >= 3.3.0
Requires:       python3-pbr >= 4.0.0
Requires:       python3-six >= 1.10.0
Requires:       python3-sqlalchemy >= 1.2.0
Requires:       python3-defusedxml >= 0.5.0
Requires:       python3-oslo-concurrency >= 3.26.0
Requires:       python3-oslo-privsep >= 1.32.0
Requires:       python3-pyroute2 >= 0.5.7
Requires:       openstack-%{service}-common >= 1:16.0.0

Requires:       python3-zmq

%description -n python3-%{package_name}
This package contains %{drv_vendor} networking driver for OpenStack Neutron.

%prep
%setup -q -n %{package_name}-%{upstream_version}

%build
%{py3_build}
#%{__python3} setup.py build_sphinx
#rm %{docpath}/.buildinfo

%install
export PBR_VERSION=%{version}
%{py3_install}

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
rm -rf %{buildroot}%{python3_sitelib}/networking_mlnx/hacking


%post
%systemd_post %{service}-mlnx-agent.service
%systemd_post eswitchd.service


%preun
%systemd_preun %{service}-mlnx-agent.service
%systemd_preun eswitchd.service


%postun
%systemd_postun_with_restart %{service}-mlnx-agent.service
%systemd_postun_with_restart eswitchd.service


%files -n python3-%{package_name}
%license LICENSE
%doc README.rst
%{python3_sitelib}/%{srcname}
%{python3_sitelib}/%{srcname}-%{version}-*.egg-info
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

# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
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
BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-mock
BuildRequires:  python%{pyver}-neutron-tests
BuildRequires:  python%{pyver}-oslo-sphinx
BuildRequires:  python%{pyver}-pbr
BuildRequires:  python%{pyver}-setuptools
BuildRequires:  python%{pyver}-sphinx
BuildRequires:  python%{pyver}-testrepository
BuildRequires:  python%{pyver}-testtools
BuildRequires:  systemd
%{?systemd_requires}

%description
This package contains %{drv_vendor} networking driver for OpenStack Neutron.

%package -n python%{pyver}-%{package_name}
Summary: Mellanox OpenStack Neutron driver
%{?python_provide:%python_provide python%{pyver}-%{package_name}}

Requires:       python%{pyver}-alembic
Requires:       python%{pyver}-eventlet
Requires:       python%{pyver}-netaddr
Requires:       python%{pyver}-neutron-lib >= 1.7.0
Requires:       python%{pyver}-neutronclient >= 5.1.0
Requires:       python%{pyver}-oslo-config >= 2:3.22.0
Requires:       python%{pyver}-oslo-i18n >= 2.1.0
Requires:       python%{pyver}-oslo-log >= 3.22.0
Requires:       python%{pyver}-oslo-messaging >= 5.19.0
Requires:       python%{pyver}-oslo-serialization >= 1.10.0
Requires:       python%{pyver}-oslo-utils >= 3.20.0
Requires:       python%{pyver}-openstackclient >= 3.3.0
Requires:       python%{pyver}-six
Requires:       python%{pyver}-sqlalchemy
Requires:       python%{pyver}-stevedore
Requires:       openstack-%{service}-common

# Handle python2 exception
%if %{pyver} == 2
Requires:       python-lxml
Requires:       python-zmq
%else
Requires:       python%{pyver}-lxml
Requires:       python%{pyver}-zmq
%endif

%description -n python%{pyver}-%{package_name}
This package contains %{drv_vendor} networking driver for OpenStack Neutron.

%prep
%setup -q -n %{package_name}-%{upstream_version}

%build
%{pyver_build}
%{pyver_bin} setup.py build_sphinx
rm %{docpath}/.buildinfo

%install
export PBR_VERSION=%{version}
%{pyver_install}

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


%files -n python%{pyver}-%{package_name}
%license LICENSE
%doc README.rst
%doc %{docpath}
%{pyver_sitelib}/%{srcname}
%{pyver_sitelib}/%{srcname}-%{version}-*.egg-info
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

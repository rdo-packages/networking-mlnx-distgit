%global drv_vendor Mellanox
%global srcname networking_mlnx
%global package_name networking-mlnx
%global docpath doc/build/html
%global service neutron

Name:           python-%{package_name}
Version:        2016.1.1
Release:        1%{?dist}
Summary:        %{drv_vendor} OpenStack Neutron driver
Obsoletes:      openstack-%{service}-mellanox

License:        ASL 2.0
URL:            https://pypi.python.org/pypi/%{package_name}
Source0:        https://pypi.python.org/packages/source/n/%{package_name}/%{package_name}-%{version}.tar.gz
Source1:         %{service}-mlnx-agent.service

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

install -d -m 755 %{buildroot}%{_sysconfdir}/%{service}/plugins/ml2
mv %{buildroot}/usr/etc/%{service}/plugins/mlnx %{buildroot}%{_sysconfdir}/%{service}/plugins/
mv %{buildroot}/usr/etc/%{service}/plugins/ml2/ml2_conf_sdn.ini %{buildroot}%{_sysconfdir}/%{service}/plugins/ml2

install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{service}-mlnx-agent.service


# Remove unused files
rm -rf %{buildroot}%{python_sitelib}/networking_mlnx/hacking


%post
%systemd_post %{service}-mlnx-agent.service


%preun
%systemd_preun %{service}-mlnx-agent.service


%postun
%systemd_postun_with_restart %{service}-mlnx-agent.service

%files
%license LICENSE
%doc README.rst
%doc %{docpath}
%{python2_sitelib}/%{srcname}
%{python2_sitelib}/%{srcname}-%{version}-py%{python2_version}.egg-info
%config(noreplace) %attr(0640, root, %{service}) %{_sysconfdir}/%{service}/plugins/ml2/ml2_conf_sdn.ini
%{_bindir}/%{service}-mlnx-agent
%{_unitdir}/%{service}-mlnx-agent.service

%dir %{_sysconfdir}/%{service}/plugins/mlnx
%config(noreplace) %attr(0640, root, %{service}) %{_sysconfdir}/%{service}/plugins/mlnx/*.ini
%dir %{_sysconfdir}/%{service}/conf.d/%{service}-mlnx-agent

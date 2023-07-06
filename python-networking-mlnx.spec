%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order
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

License:        Apache-2.0
URL:            https://pypi.python.org/pypi/%{package_name}
Source0:        https://pypi.io/packages/source/n/%{package_name}/%{package_name}-%{upstream_version}.tar.gz
Source1:        %{service}-mlnx-agent.service
Source2:        eswitchd.service


BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-neutron-tests
BuildRequires:  systemd

%{?systemd_ordering}

%description
This package contains %{drv_vendor} networking driver for OpenStack Neutron.

%package -n python3-%{package_name}
Summary: Mellanox OpenStack Neutron driver

Requires:       openstack-%{service}-common >= 1:16.0.0

%description -n python3-%{package_name}
This package contains %{drv_vendor} networking driver for OpenStack Neutron.

%prep
%setup -q -n %{package_name}-%{upstream_version}

sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini
# removing dev envs
sed -i '/^\[testenv\:dev\]/,+5d' tox.ini
sed -i '/^\[testenv\:py3-dev\]/,+4d' tox.ini
sed -i '/^\[testenv\:pep8-dev\]/,+6d' tox.ini
sed -i '/hacking*/d' tox.ini
sed -i '/\# Using neutron master/,+4d' requirements.txt

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

%generate_buildrequires
%pyproject_buildrequires -t -e %{default_toxenv}

%build
%pyproject_wheel

%install
%pyproject_install

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
%{python3_sitelib}/%{srcname}*.dist-info
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

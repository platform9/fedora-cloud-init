%if 0%{?rhel} <= 5
%define __python /usr/bin/python2.6
%endif
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           cloud-init
Version:        0.7.4
Release:        2%{?dist}
Summary:        Cloud instance init scripts

Group:          System Environment/Base
License:        GPLv3
URL:            http://launchpad.net/cloud-init
Source0:        https://github.com/platform9/cloud-init/releases/download/rel-pf9-0.7.4/pf9-cloud-init-0.7.4.tar.gz
Source1:        cloud-init-rhel.cfg
Source2:        cloud-init-README.fedora
Patch0:         cloud-init-0.7.2-fedora.patch

BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if 0%{?rhel} >= 6
BuildRequires:  python-devel
BuildRequires:  python-setuptools-devel
Requires:       e2fsprogs
%else
BuildRequires:  python26-devel
BuildRequires:  python-setuptools
Requires:       e4fsprogs
%endif
Requires:       dmidecode
Requires:       iproute
Requires:       libselinux-python
Requires:       net-tools
Requires:       policycoreutils-python
Requires:       procps
Requires:       python-argparse
%if 0%{?rhel} >= 6
Requires:       PyYAML
Requires:       python-boto >= 2.6.0
Requires:       python-cheetah
Requires:       python-configobj
Requires:       python-jsonpatch
Requires:       python-prettytable
Requires:       python-requests
%else
Requires:       python26-boto >= 2.6.0
Requires:       python26-cheetah
Requires:       python26-configobj
Requires:       python26-PyYAML
%endif
Requires:       rsyslog
Requires:       shadow-utils
Requires:       /usr/bin/run-parts
Requires(post):   chkconfig
Requires(preun):  chkconfig
Requires(postun): initscripts

%description
Cloud-init is a set of init scripts for cloud instances.  Cloud instances
need special scripts to run during initialization to retrieve and install
ssh keys and to let the user run various scripts.


%prep
%setup -q -n %{name}-%{version}
%patch0 -p1

cp -p %{SOURCE2} README.fedora

%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/%{_sharedstatedir}/cloud

# We supply our own config file since our software differs from Ubuntu's.
cp -p %{SOURCE1} $RPM_BUILD_ROOT/%{_sysconfdir}/cloud/cloud.cfg

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/rsyslog.d
cp -p tools/21-cloudinit.conf $RPM_BUILD_ROOT/%{_sysconfdir}/rsyslog.d/21-cloudinit.conf

# Install the init scripts
mkdir -p $RPM_BUILD_ROOT/%{_initrddir}
install -p -m 755 sysvinit/debian/* $RPM_BUILD_ROOT/%{_initrddir}/
install -p -m 755 sysvinit/redhat/* $RPM_BUILD_ROOT/%{_initrddir}/


%clean
rm -rf $RPM_BUILD_ROOT


%post
if [ $1 -eq 1 ] ; then
    # Initial installation
    # Enabled by default per "runs once then goes away" exception
    for svc in init-local init config final; do
        chkconfig --add cloud-$svc
        chkconfig cloud-$svc on
    done
fi

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    for svc in init-local init config final; do
        chkconfig cloud-$svc off
        chkconfig --del cloud-$svc
    done
    # One-shot services -> no need to stop
fi

%postun
# One-shot services -> no need to restart


%files
%doc ChangeLog LICENSE TODO README.fedora
%config(noreplace) %{_sysconfdir}/cloud/cloud.cfg
%dir               %{_sysconfdir}/cloud/cloud.cfg.d
%config(noreplace) %{_sysconfdir}/cloud/cloud.cfg.d/*.cfg
%doc               %{_sysconfdir}/cloud/cloud.cfg.d/README
%dir               %{_sysconfdir}/cloud/templates
%config(noreplace) %{_sysconfdir}/cloud/templates/*
%{_initrddir}/cloud-*
%{python_sitelib}/*
%{_libexecdir}/%{name}
%{_bindir}/cloud-init*
%doc %{_datadir}/doc/%{name}
%dir %{_sharedstatedir}/cloud

%config(noreplace) %{_sysconfdir}/rsyslog.d/21-cloudinit.conf


%changelog
* Mon Jan 27 2014 Sam Kottler <shk@redhat.com> - 0.7.4-2
- Add runtime requirement on python-jsonpatch

* Wed Jan 22 2014 Sam Kottler <shk@redhat.com> - 0.7.4-1
- update to 0.7.4 [BZ:907547]

* Wed Jun 26 2013 Steven Hardy <shardy@redhat.com> 0.7.2-2
- support optical drives with dev node /dev/sr1 (backport of LP rev 821))

* Tue May 28 2013 Steven Hardy <shardy@redhat.com> 0.7.2-1
- Update to 0.7.2
- Added dependency on python-requests
- Removed write-ssh-key-fingerprints patch (in upstream release)
- Added boto >= 2.6.0 requirement

* Fri Nov 16 2012 Alan Pevec <apevec@redhat.com> 0.7.1-2
- define default user (Joe VLcek)
- set distro to rhel in default config
- adjust logger call for older util-linux

* Wed Nov 14 2012 Alan Pevec <apevec@redhat.com> 0.7.1-1
- Update to 0.7.1

* Tue Oct  9 2012 Garrett Holmstrom <gholms@fedoraproject.org> - 0.7.0-1
- Rebased against version 0.7.0

* Thu Sep 13 2012 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.3-0.11.bzr532
- Use a FQDN (instance-data.) for instance data URL fallback [RH:850916 LP:1040200]

* Tue Sep 11 2012 Pádraig Brady <P@draigBrady.com> - 0.6.3-0.10.bzr532
- Add support for ext4 on EPEL5

* Thu Jul 19 2012 Jan van Eldik <Jan.van.Eldik@cern.ch> - 0.6.3-0.9.bzr532
- Support EPEL5 using python 2.6 and adjustment of chkconfig order

* Wed Jun 27 2012 Pádraig Brady <P@draigBrady.com> - 0.6.3-0.7.bzr532
- Add support for installing yum packages

* Mon Jun 18 2012 Pádraig Brady <P@draigBrady.com> - 0.6.3-0.6.bzr532
- Further adjustments to support EPEL 6

* Fri Jun 15 2012 Tomas Karasek <tomas.karasek@cern.ch> - 0.6.3-0.5.bzr532
- Fix cloud-init-cfg invocation in init script

* Tue May 22 2012 Pádraig Brady <P@draigBrady.com> - 0.6.3-0.4.bzr532
- Support EPEL 6

* Sat Mar 31 2012 Andy Grimm <agrimm@gmail.com> - 0.6.3-0.2.bzr532
- Fixed incorrect interpretation of relative path for
  AuthorizedKeysFile (BZ #735521)

* Mon Mar  5 2012 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.3-0.1.bzr532
- Rebased against upstream rev 532
- Fixed runparts() incompatibility with Fedora

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.2-0.8.bzr457
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Oct  5 2011 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.2-0.7.bzr457
- Disabled SSH key-deleting on startup

* Wed Sep 28 2011 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.2-0.6.bzr457
- Consolidated selinux file context patches
- Fixed cloud-init.service dependencies
- Updated sshkeytypes patch
- Dealt with differences from Ubuntu's sshd

* Sat Sep 24 2011 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.2-0.5.bzr457
- Rebased against upstream rev 457
- Added missing dependencies

* Fri Sep 23 2011 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.2-0.4.bzr450
- Added more macros to the spec file

* Fri Sep 23 2011 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.2-0.3.bzr450
- Fixed logfile permission checking
- Fixed SSH key generation
- Fixed a bad method call in FQDN-guessing [LP:857891]
- Updated localefile patch
- Disabled the grub_dpkg module
- Fixed failures due to empty script dirs [LP:857926]

* Fri Sep 23 2011 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.2-0.2.bzr450
- Updated tzsysconfig patch

* Wed Sep 21 2011 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.2-0.1.bzr450
- Initial packaging

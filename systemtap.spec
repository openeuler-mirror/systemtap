%ifarch x86_64
%{!?with_crash: %global with_crash 1}
%{!?with_dyninst: %global with_dyninst 1}
%{!?with_mokutil: %global with_mokutil 1}
%{!?with_openssl: %global with_openssl 1}
%global crash_config --enable-crash
%global dyninst_config --with-dyninst
%else
%{!?with_crash: %global with_crash 0}
%{!?with_dyninst: %global with_dyninst 0}
%{!?with_mokutil: %global with_mokutil 0}
%{!?with_openssl: %global with_openssl 0}
%global crash_config --disable-crash
%global dyninst_config --without-dyninst
%endif

%define udevrulesdir /usr/lib/udev/rules.d
%define dracutstap %{_prefix}/lib/dracut/modules.d/99stap
%define dracutbindir /sbin
%{!?_rpmmacrodir: %define _rpmmacrodir %{_rpmconfigdir}/macros.d}
%undefine __brp_mangle_shebangs

Name: systemtap
Version: 4.5
Release: 3
Summary: Linux trace and probe tool
License: GPLv2+ and Public Domain
URL: http://sourceware.org/systemtap
Source: https://sourceware.org/systemtap/ftp/releases/%{name}-%{version}.tar.gz

Patch1: 0001-Add-init-type-cast-to-resolve-gcc-issue.patch

BuildRequires: gcc-c++ emacs systemd python3-setuptools
BuildRequires: gettext-devel rpm-devel readline-devel
BuildRequires: pkgconfig(nss) pkgconfig(avahi-client)
BuildRequires: pkgconfig(ncurses) pkgconfig(json-c)
BuildRequires: jpackage-utils python3-devel
BuildRequires: elfutils-devel >= 0.142
BuildRequires: sqlite-devel > 3.7
%if %{with_dyninst}
BuildRequires: dyninst-devel >= 8.0
BuildRequires: pkgconfig(libselinux)
%endif
%if %{with_crash}
BuildRequires: crash-devel zlib-devel
%endif

Requires: systemtap-client = %{version}-%{release}

%description
SystemTap is an instrumentation system for systems running Linux.
Developers can write instrumentation scripts to collect data on
the operation of the system.  The base systemtap package contains/requires
the components needed to locally develop and execute systemtap scripts.

%package devel
Summary: Programmable system-wide instrumentation system - development headers, tools
License: GPLv2+
Requires: make kernel-devel systemd

%description devel
This package contains the components needed to compile a systemtap
script from source form into executable (.ko) forms.  It may be
installed on a self-contained developer workstation (along with the
systemtap-client and systemtap-runtime packages), or on a dedicated
remote server (alongside the systemtap-server package).  It includes
a copy of the standard tapset library and the runtime library C files.

%package server
Summary: Instrumentation System Server
License: GPLv2+
Requires: systemtap-devel = %{version}-%{release}
Requires: coreutils nss zip unzip
Requires(pre): shadow-utils
BuildRequires: nss-devel avahi-devel
%if %{with_openssl}
Requires: openssl
%endif

%description server
This is the remote script compilation server component of systemtap.
It announces itself to nearby clients with avahi (if available), and
compiles systemtap scripts to kernel objects on their demand.

%package runtime
Summary: Programmable system-wide instrumentation system - runtime
License: GPLv2+
Requires(pre): shadow-utils

%description runtime
SystemTap runtime contains the components needed to execute
a systemtap script that was already compiled into a module
using a local or remote systemtap-devel installation.

%package client
Summary: Programmable system-wide instrumentation system - client
License: GPLv2+
Requires: zip unzip
Requires: systemtap-runtime = %{version}-%{release}
Requires: coreutils grep sed unzip zip
Requires: openssh-clients
%if %{with_mokutil}
Requires: mokutil
%endif

%description client
This package contains/requires the components needed to develop
systemtap scripts, and compile them using a local systemtap-devel
or a remote systemtap-server installation, then run them using a
local or remote systemtap-runtime.  It includes script samples and
documentation, and a copy of the tapset library for reference.

%package sdt-devel
Summary: Static probe support tools
License: GPLv2+ and Public Domain
Requires: python3-pyparsing

%description sdt-devel
This package includes the <sys/sdt.h> header file used for static
instrumentation compiled into userspace programs and libraries, along
with the optional dtrace-compatibility preprocessor to process related
.d files into tracing-macro-laden .h headers.

%package testsuite
Summary: Instrumentation System Testsuite
License: GPLv2+
Requires: systemtap = %{version}-%{release}
Requires: systemtap-sdt-devel = %{version}-%{release}
Requires: systemtap-server = %{version}-%{release}
Requires: dejagnu which elfutils grep nc
Requires: gcc gcc-c++ make glibc-devel
Requires: strace nc avahi perf
Requires: systemtap-runtime-python3 = %{version}-%{release}
%if %{with_crash}
Requires: crash
%endif

%description testsuite
This package includes the dejagnu-based systemtap stress self-testing
suite.  This may be used by system administrators to thoroughly check
systemtap on the current system.

%package runtime-python3
Summary: Systemtap Python 3 Runtime Support
License: GPLv2+
URL: http://sourceware.org/systemtap
Requires: systemtap-runtime = %{version}-%{release}

%description runtime-python3
This package includes support files needed to run systemtap scripts
that probe python3 processes.

%package stap-exporter
Summary: Systemtap-prometheus interoperation mechanism
License: GPLv2+
URL: http://sourceware.org/systemtap
Requires: systemtap-runtime = %{version}-%{release}

%description stap-exporter
This package includes files for a systemd service that manages
systemtap sessions and relays prometheus metrics from the sessions
to remote requesters on demand.

%package help
Summary: systemtap manual
License: GPLv2+
URL: http://sourceware.org/systemtap

%description help
This package include systemtap manual

%prep
%autosetup -p1

%build
%configure \
		%{dyninst_config} \
		%{crash_config} \
		--with-bpf \
		--disable-httpd \
		--with-dracutstap=%{dracutstap} \
		--with-dracutbindir=%{dracutbindir} \
		--with-python3 \
		--with-python3-probes \
		--enable-pie \
		--with-rpm \
		--enable-sqlite \
		--disable-silent-rules \
		--with-extra-version="rpm %{version}-%{release}"

%make_build
%{_emacs_bytecompile} emacs/systemtap-mode.el

%install
rm -rf ${RPM_BUILD_ROOT}
make DESTDIR=$RPM_BUILD_ROOT install
%find_lang %{name}
for dir in $(ls -1d $RPM_BUILD_ROOT%{_mandir}/{??,??_??}) ; do
    dir=$(echo $dir | sed -e "s|^$RPM_BUILD_ROOT||")
    lang=$(basename $dir)
    echo "%%lang($lang) $dir/man*/*" >> %{name}.lang
done

ln -s %{_datadir}/systemtap/examples
find $RPM_BUILD_ROOT%{_datadir}/systemtap/examples -type f -name '*.stp' -print0 | xargs -0 sed -i -r -e '1s@^#!.+stap@#!%{_bindir}/stap@'
chmod 755 $RPM_BUILD_ROOT%{_bindir}/staprun
install -c -m 755 stap-prep $RPM_BUILD_ROOT%{_bindir}/stap-prep
cp -rp testsuite $RPM_BUILD_ROOT%{_datadir}/systemtap
mkdir docs.installed
mv $RPM_BUILD_ROOT%{_datadir}/doc/systemtap/*.pdf docs.installed/
install -D -m 644 macros.systemtap $RPM_BUILD_ROOT%{_rpmmacrodir}/macros.systemtap
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/stap-server
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/stap-server
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/stap-server/.systemtap
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/stap-server
touch $RPM_BUILD_ROOT%{_localstatedir}/log/stap-server/log
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/cache/systemtap
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/run/systemtap
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
install -m 644 initscript/logrotate.stap-server $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/stap-server

mkdir -p $RPM_BUILD_ROOT%{_unitdir}
touch $RPM_BUILD_ROOT%{_unitdir}/systemtap.service
install -m 644 initscript/systemtap.service $RPM_BUILD_ROOT%{_unitdir}/systemtap.service
mkdir -p $RPM_BUILD_ROOT%{_sbindir}
install -m 755 initscript/systemtap $RPM_BUILD_ROOT%{_sbindir}/systemtap-service

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/systemtap
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/systemtap/conf.d
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/systemtap/script.d
install -m 644 initscript/config.systemtap $RPM_BUILD_ROOT%{_sysconfdir}/systemtap/config

mkdir -p $RPM_BUILD_ROOT%{_unitdir}
touch $RPM_BUILD_ROOT%{_unitdir}/stap-server.service
install -m 644 stap-server.service $RPM_BUILD_ROOT%{_unitdir}/stap-server.service
mkdir -p $RPM_BUILD_ROOT%{_tmpfilesdir}
install -m 644 stap-server.conf $RPM_BUILD_ROOT%{_tmpfilesdir}/stap-server.conf

mkdir -p $RPM_BUILD_ROOT%{_emacs_sitelispdir}
install -p -m 644 emacs/systemtap-mode.el* $RPM_BUILD_ROOT%{_emacs_sitelispdir}
mkdir -p $RPM_BUILD_ROOT%{_emacs_sitestartdir}
install -p -m 644 emacs/systemtap-init.el $RPM_BUILD_ROOT%{_emacs_sitestartdir}/systemtap-init.el
for subdir in ftdetect ftplugin indent syntax
do
    mkdir -p $RPM_BUILD_ROOT%{_datadir}/vim/vimfiles/$subdir
    install -p -m 644 vim/$subdir/*.vim $RPM_BUILD_ROOT%{_datadir}/vim/vimfiles/$subdir
done

mkdir -p $RPM_BUILD_ROOT%{dracutstap}
install -p -m 755 initscript/99stap/module-setup.sh $RPM_BUILD_ROOT%{dracutstap}
install -p -m 755 initscript/99stap/install $RPM_BUILD_ROOT%{dracutstap}
install -p -m 755 initscript/99stap/check $RPM_BUILD_ROOT%{dracutstap}
install -p -m 755 initscript/99stap/start-staprun.sh $RPM_BUILD_ROOT%{dracutstap}
touch $RPM_BUILD_ROOT%{dracutstap}/params.conf

mkdir -p $RPM_BUILD_ROOT/stap-exporter
install -p -m 755 stap-exporter/stap-exporter $RPM_BUILD_ROOT%{_bindir}
install -m 644 stap-exporter/stap-exporter.service $RPM_BUILD_ROOT%{_unitdir}
install -m 644 stap-exporter/stap-exporter.8* $RPM_BUILD_ROOT%{_mandir}/man8

%pre runtime
getent group stapusr >/dev/null || groupadd -g 156 -r stapusr 2>/dev/null || groupadd -r stapusr
getent group stapsys >/dev/null || groupadd -g 157 -r stapsys 2>/dev/null || groupadd -r stapsys
getent group stapdev >/dev/null || groupadd -g 158 -r stapdev 2>/dev/null || groupadd -r stapdev
exit 0

%pre server
getent group stap-server >/dev/null || groupadd -g 155 -r stap-server 2>/dev/null || groupadd -r stap-server
getent passwd stap-server >/dev/null || \
  useradd -c "Systemtap Compile Server" -u 155 -g stap-server -d %{_localstatedir}/lib/stap-server -r -s /sbin/nologin stap-server 2>/dev/null || \
  useradd -c "Systemtap Compile Server" -g stap-server -d %{_localstatedir}/lib/stap-server -r -s /sbin/nologin stap-server

%pre testsuite
getent passwd stapusr >/dev/null || \
    useradd -c "Systemtap 'stapusr' User" -g stapusr -r -s /sbin/nologin stapusr
getent passwd stapsys >/dev/null || \
    useradd -c "Systemtap 'stapsys' User" -g stapsys -G stapusr -r -s /sbin/nologin stapsys
getent passwd stapdev >/dev/null || \
    useradd -c "Systemtap 'stapdev' User" -g stapdev -G stapusr -r -s /sbin/nologin stapdev
exit 0

%post server
test -e ~stap-server && chmod 750 ~stap-server
if [ ! -f ~stap-server/.systemtap/rc ]; then
  mkdir -p ~stap-server/.systemtap
  chown stap-server:stap-server ~stap-server/.systemtap
  numcpu=`/usr/bin/getconf _NPROCESSORS_ONLN`
  if [ -z "$numcpu" -o "$numcpu" -lt 1 ]; then numcpu=1; fi
  nproc=`expr $numcpu \* 30`
  echo "--rlimit-as=614400000 --rlimit-cpu=60 --rlimit-nproc=$nproc --rlimit-stack=1024000 --rlimit-fsize=51200000" > ~stap-server/.systemtap/rc
  chown stap-server:stap-server ~stap-server/.systemtap/rc
fi

test -e %{_localstatedir}/log/stap-server/log || {
     touch %{_localstatedir}/log/stap-server/log
     chmod 644 %{_localstatedir}/log/stap-server/log
     chown stap-server:stap-server %{_localstatedir}/log/stap-server/log
}
/bin/systemd-tmpfiles --create %{_tmpfilesdir}/stap-server.conf >/dev/null 2>&1 || :
exit 0

%triggerin client -- systemtap-server
if test -e ~stap-server/.systemtap/ssl/server/stap.cert; then
   %{_libexecdir}/systemtap/stap-authorize-cert ~stap-server/.systemtap/ssl/server/stap.cert %{_sysconfdir}/systemtap/ssl/client >/dev/null
   %{_libexecdir}/systemtap/stap-authorize-cert ~stap-server/.systemtap/ssl/server/stap.cert %{_sysconfdir}/systemtap/staprun >/dev/null
fi
exit 0

%preun server
if [ $1 = 0 ] ; then
    /bin/systemctl --no-reload disable stap-server.service >/dev/null 2>&1 || :
    /bin/systemctl stop stap-server.service >/dev/null 2>&1 || :
fi
exit 0

%postun server
if [ "$1" -ge "1" ] ; then
    /bin/systemctl condrestart stap-server.service >/dev/null 2>&1 || :
fi
exit 0

%postun
if [ "$1" -ge "1" ] ; then
    /bin/systemctl condrestart systemtap.service >/dev/null 2>&1 || :
fi
exit 0

%preun stap-exporter
/bin/systemctl stop stap-exporter.service >/dev/null 2>&1 || :
/bin/systemctl disable stap-exporter.service >/dev/null 2>&1 || :

%post
/bin/systemctl enable systemtap.service >/dev/null 2>&1 || :
(make -C %{_datadir}/systemtap/runtime/uprobes clean) >/dev/null 2>&1 || true
(/sbin/rmmod uprobes) >/dev/null 2>&1 || true

%preun
if [ $1 = 0 ] ; then
    /bin/systemctl --no-reload disable systemtap.service >/dev/null 2>&1 || :
    /bin/systemctl stop systemtap.service >/dev/null 2>&1 || :
fi
exit 0
(make -C %{_datadir}/systemtap/runtime/uprobes clean) >/dev/null 2>&1 || true
(/sbin/rmmod uprobes) >/dev/null 2>&1 || true

%files
%license COPYING
%doc README README.unprivileged AUTHORS NEWS 
%defattr(-,root,root)
%{_unitdir}/systemtap.service
%{_sbindir}/systemtap-service
%dir %{_sysconfdir}/systemtap
%dir %{_sysconfdir}/systemtap/conf.d
%dir %{_sysconfdir}/systemtap/script.d
%config(noreplace) %{_sysconfdir}/systemtap/config
%dir %{_localstatedir}/cache/systemtap
%ghost %{_localstatedir}/run/systemtap
%dir %{dracutstap}
%{dracutstap}/*

%files server -f systemtap.lang
%defattr(-,root,root)
%{_bindir}/stap-server
%dir %{_libexecdir}/systemtap
%{_libexecdir}/systemtap/stap-serverd
%{_libexecdir}/systemtap/stap-start-server
%{_libexecdir}/systemtap/stap-stop-server
%{_libexecdir}/systemtap/stap-gen-cert
%{_libexecdir}/systemtap/stap-sign-module
%{_libexecdir}/systemtap/stap-authorize-cert
%{_libexecdir}/systemtap/stap-env
%{_unitdir}/stap-server.service
%{_tmpfilesdir}/stap-server.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/stap-server
%dir %{_sysconfdir}/stap-server
%dir %attr(0750,stap-server,stap-server) %{_localstatedir}/lib/stap-server
%dir %attr(0700,stap-server,stap-server) %{_localstatedir}/lib/stap-server/.systemtap
%dir %attr(0755,stap-server,stap-server) %{_localstatedir}/log/stap-server
%ghost %config(noreplace) %attr(0644,stap-server,stap-server) %{_localstatedir}/log/stap-server/log
%ghost %attr(0755,stap-server,stap-server) %{_localstatedir}/run/stap-server
%{!?_licensedir:%global license %%doc}

%files devel -f systemtap.lang
%{_bindir}/stap
%{_bindir}/stap-prep
%{_bindir}/stap-report
%dir %{_datadir}/systemtap
%{_datadir}/systemtap/runtime
%{_datadir}/systemtap/tapset
%{!?_licensedir:%global license %%doc}
%dir %{_libexecdir}/systemtap
%{_emacs_sitelispdir}/*.el*
%{_emacs_sitestartdir}/systemtap-init.el
%{_datadir}/vim/vimfiles/*/*.vim
%{_libexecdir}/systemtap/python/stap-resolve-module-function.py

%files runtime -f systemtap.lang
%defattr(-,root,root)
%attr(4110,root,stapusr) %{_bindir}/staprun
%{_bindir}/stapsh
%{_bindir}/stap-merge
%{_bindir}/stap-report
%{_bindir}/stapbpf
%dir %{_libexecdir}/systemtap
%{_libexecdir}/systemtap/stapio
%{_libexecdir}/systemtap/stap-authorize-cert
%{!?_licensedir:%global license %%doc}
%if %{with_dyninst}
    %{_bindir}/stapdyn
%endif
%if %{with_crash}
    %dir %{_libdir}/systemtap
    %{_libdir}/systemtap/staplog.so*
%endif

%files client -f systemtap.lang
%defattr(-,root,root)
%{_datadir}/systemtap/examples
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc docs.installed/*.pdf
%{_bindir}/stap
%{_bindir}/stap-prep
%{_bindir}/stap-report
%dir %{_datadir}/systemtap
%{_datadir}/systemtap/tapset

%files sdt-devel
%defattr(-,root,root)
%{_bindir}/dtrace
%{_includedir}/sys/sdt.h
%{_includedir}/sys/sdt-config.h
%{_rpmmacrodir}/macros.systemtap
%{!?_licensedir:%global license %%doc}

%files testsuite
%defattr(-,root,root)
%dir %{_datadir}/systemtap
%{_datadir}/systemtap/testsuite

%files runtime-python3
%{python3_sitearch}/HelperSDT
%{python3_sitearch}/HelperSDT-*.egg-info

%files stap-exporter
%{_unitdir}/stap-exporter.service
%{_bindir}/stap-exporter
/etc/stap-exporter/*
/usr/sbin/stap-exporter
/etc/sysconfig/stap-exporter

%files help
%{_mandir}/man[1378]/*

%changelog
* Fri Apr 8 2022 zhouwenpei <zhouwenpei1@h-partners.com> - 4.5-3
- Add int type cast to resolve gcc issue for option Wformat=2

* Tue Feb 15 2022 zhouwenpei <zhouwenpei1@h-partners.com> - 4.5-2
- Remove requires on gcc and systemtap-devel

* Thu Dec 2 2021 zhouwenpei <zhouwenpei1@huawei.com> - 4.5-1
- upgrade to 4.5

* Mon Feb 1 2021 xinghe <xinghe1@huawei.com> - 4.4-1
- upgrade to 4.4

* Tue Jul 21 2020 jinzhimin <jinzhimin2@huawei.com> - 4.3-1
- upgrade to 4.3

* Fri Mar 13 2020 yuxiangyang <yuxiangyang4@huawei.com> - 4.1.3
- remove java-runtime

* Fri Feb 21 2020 yuxiangyang <yuxiangyang4@huawei.com> - 4.1.2
- Delete the requirement of python2-pyparsing

* Mon Aug 12 2019 openEuler Buildteam <buildteam@openeuler.org> - 4.1.1
- Package init

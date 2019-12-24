%ifarch x86_64
%{!?with_crash: %global with_crash 1}
%{!?with_dyninst: %global with_dyninst 1}
%{!?with_mokutil: %global with_mokutil 1}
%{!?with_openssl: %global with_openssl 1}
%{!?with_virthost: %global with_virthost 1}
%global virt_config --enable-virt
%global crash_config --enable-crash
%global dyninst_config --with-dyninst
%else
%{!?with_crash: %global with_crash 0}
%{!?with_dyninst: %global with_dyninst 0}
%{!?with_mokutil: %global with_mokutil 0}
%{!?with_openssl: %global with_openssl 0}
%{!?with_virthost: %global with_virthost 0}
%global virt_config --disable-virt
%global crash_config --disable-crash
%global dyninst_config --without-dyninst
%endif

%define initdir %{_initddir}
%define udevrulesdir /usr/lib/udev/rules.d
%define dracutstap %{_prefix}/lib/dracut/modules.d/99stap
%define dracutbindir /sbin
%{!?_rpmmacrodir: %define _rpmmacrodir %{_rpmconfigdir}/macros.d}
%undefine __brp_mangle_shebangs

Name: systemtap
Version: 4.1
Release: 2
Summary: Linux trace and probe tool
License: GPLv2+ and Public Domain
URL: http://sourceware.org/systemtap/
Source: https://sourceware.org/systemtap/ftp/releases/%{name}-%{version}.tar.gz

Patch9000:	fix-py3example-script-run-fail.patch
Patch9001:	fix-py3example-script-run-fail-2.patch
Patch9002:	fix-network-tcp-test.patch

BuildRequires: emacs gcc-c++ gettext-devel jpackage-utils java-devel
BuildRequires: readline-devel rpm-devel systemd pkgconfig(nss)
BuildRequires: pkgconfig(avahi-client) pkgconfig(json-c) pkgconfig(ncurses)
BuildRequires: python3-devel python3-setuptools nss-devel avahi-devel
BuildRequires: sqlite-devel > 3.7
BuildRequires: elfutils-devel >= 0.142
%if %{with_dyninst}
BuildRequires: dyninst-devel >= 8.0
BuildRequires: pkgconfig(libselinux)
%endif
%if %{with_crash}
BuildRequires: crash-devel zlib-devel
%endif
%if %{with_virthost}
BuildRequires: pkgconfig(libvirt) pkgconfig(libxml-2.0)
Requires: libvirt > 2.0
%endif

Requires: nss coreutils zip unzip shadow-utils chkconfig systemd
Requires: shadow-utils openssh-clients python3-pyparsing pyparsing
Requires: which elfutils grep nc gcc gcc-c++ make glibc-devel
Requires: strace nmap-ncat avahi perl iproute libxml2 findutils
Requires: kernel-devel
%if %{with_openssl}
Requires: openssl
%endif
%if %{with_mokutil}
Requires: mokutil
%endif
%if %{with_crash}
Requires: crash
%endif
Requires(pre): shadow-utils
Requires(post): chkconfig findutils coreutils
Requires(preun): chkconfig grep coreutils
Requires(postun): grep coreutils

Provides: systemtap-devel = %{version}-%{release}
Provides: systemtap-runtime = %{version}-%{release}
Provides: systemtap-server = %{version}-%{release}
Provides: systemtap-client = %{version}-%{release}
Provides: systemtap-initscript = %{version}-%{release}
Provides: systemtap-runtime_java = %{version}-%{release}
Provides: systemtap-runtime-python3 = %{version}-%{release}
Provides: systemtap-stap-exporter = %{version}-%{release}
%if %{with_virthost}
Provides: systemtap-runtime-virthost = %{version}-%{release}
%endif
Provides: systemtap-runtime-virtguest = %{version}-%{release}
Obsoletes: systemtap-devel
Obsoletes: systemtap-runtime
Obsoletes: systemtap-server
Obsoletes: systemtap-client
Obsoletes: systemtap-initscript
Obsoletes: systemtap-runtime_java
Obsoletes: systemtap-runtime-python3
Obsoletes: systemtap-stap-exporter
%if %{with_virthost}
Obsoletes: systemtap-runtime-virthost
%endif
Obsoletes: systemtap-runtime-virtguest

%description
SystemTap is an instrumentation system for systems running Linux.
Developers can write instrumentation scripts to collect data on
the operation of the system.  The base systemtap package contains/requires
the components needed to locally develop and execute systemtap scripts.

%package runtime-java
Summary: Systemtap java runtime
License: GPLv2+
Requires: %{name} = %{version}-%{release}
Requires: byteman > 2.0
Requires: iproute

%description runtime-java
Systemtap for java runtime support

%package runtime-python3
Summary: Systemtap python 3 runtime
License: GPLv2+
Requires: %{name} = %{version}-%{release}

%description runtime-python3
Systemtap for python3 runtime support


%package sdt-devel
Summary: Development package for systemtap
License: GPLv2+ and Public Domain
Requires: python3-pyparsing

%description sdt-devel
The sdt-development package for systemtap.

%package help
Summary: Help documents for systemtap
Requires: %{name} = %{version}-%{release}
%description help
The help documents for systemtap.

%package lang
Summary: Language package for systemtap
Requires: %{name} = %{version}-%{release}
%description lang
The language package for systemtap.

%package testsuite
Summary: Instrumentation System Testsuite
License: GPLv2+
URL: http://sourceware.org/systemtap/
Requires: systemtap = %{version}-%{release}
Requires: systemtap-devel = %{version}-%{release}
Requires: dejagnu which elfutils grep nc
Requires: gcc gcc-c++ make glibc-devel
Requires: strace
Requires: nmap-ncat
Requires: avahi
%if %{with_crash}
Requires: crash
%endif
Requires: systemtap-runtime-java = %{version}-%{release}
Requires: systemtap-runtime-python3 = %{version}-%{release}
Requires: perf

%description testsuite
Testsuite for systemtap.

%prep
%autosetup  %{?setup_elfutils} -p1

%build
%configure \
			%{dyninst_config} \
			%{crash_config} \
			%{virt_config} \
			--enable-sqlite \
			--enable-pie \
			--with-rpm \
			--with-java=%{_jvmdir}/java \
			--with-dracutstap=%{dracutstap} \
			--with-dracutbindir=%{dracutbindir} \
			--with-python3 \
			--without-python2-probes \
			--with-python3-probes \
			--disable-httpd \
			--with-bpf \
			--disable-silent-rules \
			--with-extra-version="rpm %{version}-%{release}"
%make_build
%{_emacs_bytecompile} emacs/systemtap-mode.el

%install
rm -rf ${RPM_BUILD_ROOT}
%make_install
%find_lang %{name}
for dir in $(ls -1d $RPM_BUILD_ROOT%{_mandir}/{??,??_??}) ; do
    dir=$(echo $dir | sed -e "s|^$RPM_BUILD_ROOT||")
    lang=$(basename $dir)
    echo "%%lang($lang) $dir/man*/*" >> %{name}.lang
done
cp testsuite $RPM_BUILD_ROOT%{_datadir}/systemtap -r
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/stap-server
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/stap-server
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/stap-server/.systemtap
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/stap-server
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/cache/systemtap
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/run/systemtap
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/systemtap/conf.d
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/systemtap/script.d
mkdir -p $RPM_BUILD_ROOT%{dracutstap}
mkdir -p $RPM_BUILD_ROOT%{udevrulesdir}
install -D -m 755 stap-prep $RPM_BUILD_ROOT%{_bindir}/stap-prep
install -D -m 644 macros.systemtap $RPM_BUILD_ROOT%{_rpmmacrodir}/macros.systemtap
install -D -m 644 initscript/logrotate.stap-server $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/stap-server
install -D -m 644 initscript/systemtap.service $RPM_BUILD_ROOT%{_unitdir}/systemtap.service
install -D -m 755 initscript/systemtap $RPM_BUILD_ROOT%{_sbindir}/systemtap-service
install -D -m 644 initscript/config.systemtap $RPM_BUILD_ROOT%{_sysconfdir}/systemtap/config
install -D -m 644 stap-server.service $RPM_BUILD_ROOT%{_unitdir}/stap-server.service
install -D -m 644 stap-server.conf $RPM_BUILD_ROOT%{_tmpfilesdir}/stap-server.conf
install -D -m 644 emacs/systemtap-init.el $RPM_BUILD_ROOT%{_emacs_sitestartdir}/systemtap-init.el
install -D -m 644 emacs/systemtap-mode.el* $RPM_BUILD_ROOT%{_emacs_sitelispdir}/
install -D -m 644 vim/ftdetect/*.vim $RPM_BUILD_ROOT%{_datadir}/vim/vimfiles/ftdetect/*.vim
install -D -m 644 vim/ftplugin/*.vim $RPM_BUILD_ROOT%{_datadir}/vim/vimfiles/ftplugin/*.vim
install -D -m 644 vim/indent/*.vim $RPM_BUILD_ROOT%{_datadir}/vim/vimfiles/indent/*.vim
install -D -m 644 vim/syntax/*.vim $RPM_BUILD_ROOT%{_datadir}/vim/vimfiles/syntax/*.vim
install -D -m 644 staprun/guest/99-stapsh.rules $RPM_BUILD_ROOT%{udevrulesdir}/
install -D -m 644 staprun/guest/stapsh@.service $RPM_BUILD_ROOT%{_unitdir}/
install -D -m 755 initscript/99stap/module-setup.sh $RPM_BUILD_ROOT%{dracutstap}/
install -D -m 755 initscript/99stap/install $RPM_BUILD_ROOT%{dracutstap}/
install -D -m 755 initscript/99stap/check $RPM_BUILD_ROOT%{dracutstap}/
install -D -m 755 initscript/99stap/start-staprun.sh $RPM_BUILD_ROOT%{dracutstap}/
install -D -m 755 stap-exporter/stap-exporter $RPM_BUILD_ROOT%{_bindir}/
install -D -m 644 stap-exporter/stap-exporter.service $RPM_BUILD_ROOT%{_unitdir}/
install -D -m 644 stap-exporter/stap-exporter.8* $RPM_BUILD_ROOT%{_mandir}/man8/
touch $RPM_BUILD_ROOT%{_localstatedir}/log/stap-server/log
touch $RPM_BUILD_ROOT%{dracutstap}/params.conf
touch $RPM_BUILD_ROOT%{_unitdir}/systemtap.service

%pre
getent group stapusr >/dev/null || groupadd -r stapusr
getent group stapsys >/dev/null || groupadd -r stapsys
getent group stapdev >/dev/null || groupadd -r stapde
getent group stap-server >/dev/null || groupadd -r stap-server
getent passwd stap-server >/dev/null || useradd -c "Systemtap Compile Server" -g stap-server -d /var/lib/stap-server -r -s /sbin/nologin stap-server

%post
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
test -e /var/log/stap-server/log || {
     touch /var/log/stap-server/log
     chmod 644 /var/log/stap-server/log
     chown stap-server:stap-server /var/log/stap-server/log
}
/bin/systemd-tmpfiles --create /usr/lib/tmpfiles.d/stap-server.conf >/dev/null 2>&1 || :
/bin/systemctl enable systemtap.service >/dev/null 2>&1 || :
if [ -d /dev/virtio-ports ]; then
   (find /dev/virtio-ports -iname 'org.systemtap.stapsh.[0-9]*' -type l \
      | xargs -n 1 basename \
      | xargs -n 1 -I {} /bin/systemctl start stapsh@{}.service) >/dev/null 2>&1 || :
fi
exit 0
make -C %{_datadir}/systemtap/runtime/uprobes clean || true
/sbin/rmmod uprobes || true

%preun
if [ $1 = 0 ]; then
   for service in `/bin/systemctl --full | grep stapsh@ | cut -d ' ' -f 1`; do
      /bin/systemctl stop $service >/dev/null 2>&1 || :
   done
fi
/bin/systemctl --no-reload disable stap-server.service >/dev/null 2>&1 || :
/bin/systemctl stop stap-server.service >/dev/null 2>&1 || :
make -C %{_datadir}/systemtap/runtime/uprobes clean || true
/sbin/rmmod uprobes || true
exit 0

%postun
if [ "$1" -ge "1" ] ; then
    /bin/systemctl condrestart stap-server.service >/dev/null 2>&1 || :
fi
if [ "$1" -ge "1" ]; then
   for service in `/bin/systemctl --full | grep stapsh@ | cut -d ' ' -f 1`; do
      /bin/systemctl condrestart $service >/dev/null 2>&1 || :
   done
fi

%triggerin -- systemtap-server
if test -e ~stap-server/.systemtap/ssl/server/stap.cert; then
   /usr/libexec/systemtap/stap-authorize-cert ~stap-server/.systemtap/ssl/server/stap.cert /etc/systemtap/ssl/client >/dev/null
   /usr/libexec/systemtap/stap-authorize-cert ~stap-server/.systemtap/ssl/server/stap.cert /etc/systemtap/staprun >/dev/null
fi
exit 0

%pre testsuite
getent passwd stapusr >/dev/null || \
    useradd -c "Systemtap 'stapusr' User" -g stapusr -r -s /sbin/nologin stapusr
getent passwd stapsys >/dev/null || \
    useradd -c "Systemtap 'stapsys' User" -g stapsys -G stapusr -r -s /sbin/nologin stapsys
getent passwd stapdev >/dev/null || \
    useradd -c "Systemtap 'stapdev' User" -g stapdev -G stapusr -r -s /sbin/nologin stapdev
exit 0


%triggerin -- java-1.8.0-openjdk, java-1.7.0-openjdk, java-1.6.0-openjdk
for f in %{_libexecdir}/systemtap/libHelperSDT_*.so; do
    arch=`basename $f | cut -f2 -d_ | cut -f1 -d.`
    for archdir in %{_jvmdir}/*openjdk*/jre/lib/${arch}; do
     if [ -d ${archdir} ]; then
            ln -sf %{_libexecdir}/systemtap/libHelperSDT_${arch}.so ${archdir}/libHelperSDT_${arch}.so
            ln -sf %{_libexecdir}/systemtap/HelperSDT.jar ${archdir}/../ext/HelperSDT.jar
     fi
    done
done

%triggerun -- java-1.8.0-openjdk, java-1.7.0-openjdk, java-1.6.0-openjdk
for f in %{_libexecdir}/systemtap/libHelperSDT_*.so; do
    arch=`basename $f | cut -f2 -d_ | cut -f1 -d.`
    for archdir in %{_jvmdir}/*openjdk*/jre/lib/${arch}; do
        rm -f ${archdir}/libHelperSDT_${arch}.so
        rm -f ${archdir}/../ext/HelperSDT.jar
    done
done

%triggerpostun -- java-1.8.0-openjdk, java-1.7.0-openjdk, java-1.6.0-openjdk
for f in %{_libexecdir}/systemtap/libHelperSDT_*.so; do
    arch=`basename $f | cut -f2 -d_ | cut -f1 -d.`
    for archdir in %{_jvmdir}/*openjdk*/jre/lib/${arch}; do
     if [ -d ${archdir} ]; then
            ln -sf %{_libexecdir}/systemtap/libHelperSDT_${arch}.so ${archdir}/libHelperSDT_${arch}.so
            ln -sf %{_libexecdir}/systemtap/HelperSDT.jar ${archdir}/../ext/HelperSDT.jar
     fi
    done
done

%files
%{_bindir}/*
%{_sbindir}/*
%{_libdir}/python3.7/site-packages/*
%{_datadir}/systemtap/examples/*
%{_datadir}/systemtap/tapset
%{_datadir}/systemtap/runtime/*
%{_datadir}/vim/vimfiles/*/*
%{dracutstap}
%{udevrulesdir}/*
%dir %{_libexecdir}/systemtap
%{_libexecdir}/systemtap/*
%{_unitdir}/stap-exporter.service
%{_unitdir}/stap-server.service
%{_unitdir}/stapsh@.service
%{_unitdir}/systemtap.service
%{_tmpfilesdir}/stap-server.conf
%{_emacs_sitelispdir}/*.el*
%{_emacs_sitestartdir}/systemtap-init.el
%config(noreplace) %{_sysconfdir}/logrotate.d/stap-server
%config(noreplace) %{_sysconfdir}/systemtap/config
%ghost %config(noreplace) %attr(0644,stap-server,stap-server) %{_localstatedir}/log/stap-server/log
/etc/sysconfig/stap-exporter
/etc/stap-exporter
%doc README README.unprivileged AUTHORS NEWS
%license COPYING
%if %{with_crash}
%dir %{_libdir}/systemtap
%{_libdir}/%{name}/staplog.so*
%{_exec_prefix}/lib/debug/usr/lib64/%{name}/staplog.so-%{version}-%{release}.x86_64.debug
%endif
%exclude %{_bindir}/dtrace
%exclude %{python3_sitearch}/HelperSDT
%exclude %{python3_sitearch}/HelperSDT-*.egg-info
%exclude %{_libexecdir}/systemtap/libHelperSDT_*.so
%exclude %{_libexecdir}/systemtap/HelperSDT.jar
%exclude %{_libexecdir}/systemtap/stapbm

%files runtime-java
%dir %{_libexecdir}/systemtap
%{_libexecdir}/systemtap/libHelperSDT_*.so
%{_libexecdir}/systemtap/HelperSDT.jar
%{_libexecdir}/systemtap/stapbm

%files runtime-python3
%{python3_sitearch}/HelperSDT
%{python3_sitearch}/HelperSDT-*.egg-info

%files sdt-devel
%defattr(-,root,root)
%{_bindir}/dtrace
%{_includedir}/sys/sdt.h
%{_includedir}/sys/sdt-config.h
%{_mandir}/man1/dtrace.1*
%{_rpmmacrodir}/macros.systemtap
%doc README AUTHORS NEWS
%license COPYING


%files testsuite
%defattr(-,root,root)
%dir %{_datadir}/systemtap
%{_datadir}/systemtap/testsuite


%files help
%{_mandir}/man1/*
%{_mandir}/man3/*
%{_mandir}/man7/*
%{_mandir}/man8/*
%{_datadir}/doc/*
%exclude %{_mandir}/man1/dtrace.1*

%files lang -f systemtap.lang

%changelog
* Tue Dec 24 2019 caomeng <caomeng5@huawei.com>
- fix build requirement about libvirt

* Mon Aug 12 2019 openEuler Buildteam <buildteam@openeuler.org> - 4.1.1
- Package init

%bcond_with dane
%bcond_without guile

Summary: A TLS protocol implementation
Name: compat-gnutls34
Version: 3.4.17
Release: 3%{?dist}
# The libraries are LGPLv2.1+, utilities are GPLv3+
License: GPLv3+ and LGPLv2+
Group: System Environment/Libraries
BuildRequires: p11-kit-devel >= 0.21.3, gettext-devel
BuildRequires: zlib-devel, readline-devel, libtasn1-devel >= 4.3
BuildRequires: libtool, automake, autoconf, texinfo
BuildRequires: autogen-libopts-devel >= 5.18 autogen
BuildRequires: compat-nettle32-devel >= 3.1.1
BuildRequires: trousers-devel >= 0.3.11.2
BuildRequires: libidn-devel
BuildRequires: gperf, net-tools, softhsm, datefudge
#Requires: crypto-policies
Requires: p11-kit-trust
Requires: libtasn1 >= 4.3
Requires: trousers >= 0.3.11.2

%if %{with dane}
BuildRequires: unbound-devel unbound-libs
%endif
%if %{with guile}
BuildRequires: guile-devel
%endif
URL: http://www.gnutls.org/
#Source0: ftp://ftp.gnutls.org/gcrypt/gnutls/%{name}-%{version}.tar.xz
#Source1: ftp://ftp.gnutls.org/gcrypt/gnutls/%{name}-%{version}.tar.xz.sig
# XXX patent tainted code removed.
Source0: gnutls-%{version}-hobbled.tar.xz
Source1: libgnutls-config
Source2: hobble-gnutls
Source3: compat-gnutls34.conf
Patch1: gnutls-3.2.7-rpath.patch
Patch3: gnutls-3.1.11-nosrp.patch
Patch4: gnutls-3.4.1-default-policy.patch
Patch5: gnutls-3.4.2-no-now-guile.patch
Patch6: gnutls-3.4.17-various-flaws1.patch

# Wildcard bundling exception https://fedorahosted.org/fpc/ticket/174
Provides: bundled(gnulib) = 20130424

%package c++
Summary: The C++ interface to GnuTLS
Requires: %{name}%{?_isa} = %{version}-%{release}

%package devel
Summary: Development files for the %{name} package
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: %{name}-c++%{?_isa} = %{version}-%{release}
%if %{with dane}
Requires: %{name}-dane%{?_isa} = %{version}-%{release}
%endif
Requires: pkgconfig
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info

%package utils
License: GPLv3+
Summary: Command line tools for TLS protocol
Group: Applications/System
Requires: %{name}%{?_isa} = %{version}-%{release}
%if %{with dane}
Requires: %{name}-dane%{?_isa} = %{version}-%{release}
%endif

%if %{with dane}
%package dane
Summary: A DANE protocol implementation for GnuTLS
Requires: %{name}%{?_isa} = %{version}-%{release}
%endif

%if %{with guile}
%package guile
Summary: Guile bindings for the GNUTLS library
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: guile
%endif

%description
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS 
protocols and technologies around them. It provides a simple C language 
application programming interface (API) to access the secure communications 
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and 
other required structures. 

%description c++
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS 
protocols and technologies around them. It provides a simple C language 
application programming interface (API) to access the secure communications 
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and 
other required structures. 

%description devel
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS 
protocols and technologies around them. It provides a simple C language 
application programming interface (API) to access the secure communications 
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and 
other required structures. 
This package contains files needed for developing applications with
the GnuTLS library.

%description utils
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS 
protocols and technologies around them. It provides a simple C language 
application programming interface (API) to access the secure communications 
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and 
other required structures. 
This package contains command line TLS client and server and certificate
manipulation tools.

%if %{with dane}
%description dane
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS 
protocols and technologies around them. It provides a simple C language 
application programming interface (API) to access the secure communications 
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and 
other required structures. 
This package contains library that implements the DANE protocol for verifying
TLS certificates through DNSSEC.
%endif

%if %{with guile}
%description guile
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS 
protocols and technologies around them. It provides a simple C language 
application programming interface (API) to access the secure communications 
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and 
other required structures. 
This package contains Guile bindings for the library.
%endif

%prep
%setup -q -n gnutls-%{version}

%patch1 -p1 -b .rpath
%patch3 -p1 -b .nosrp
%patch4 -p1 -b .default-policy
%patch5 -p1 -b .guile
%patch6 -p1 -b .various-flaws

sed 's/gnutls_srp.c//g' -i lib/Makefile.in
sed 's/gnutls_srp.lo//g' -i lib/Makefile.in
sed -i -e 's|sys_lib_dlsearch_path_spec="/lib /usr/lib|sys_lib_dlsearch_path_spec="/lib /usr/lib %{_libdir}|g' configure
rm -f lib/minitasn1/*.c lib/minitasn1/*.h
rm -f src/libopts/*.c src/libopts/*.h src/libopts/compat/*.c src/libopts/compat/*.h

%{SOURCE2} -e


%build
export PKG_CONFIG_PATH=/usr/lib64/compat-nettle32/pkgconfig/

CFLAGS="${CFLAGS:-%optflags}" ; export CFLAGS ;
CXXFLAGS="${CXXFLAGS:-%optflags}" ; export CXXFLAGS ;
FFLAGS="${FFLAGS:-%optflags}" ; export FFLAGS ;

./configure --build=x86_64-redhat-linux-gnu --host=x86_64-redhat-linux-gnu \
        --disable-dependency-tracking \
        --prefix=/usr/gnutls34 \
        --disable-static \
        --disable-openssl-compatibility \
        --disable-srp-authentication \
        --disable-non-suiteb-curves \
        --with-system-priority-file=%{_sysconfdir}/crypto-policies/back-ends/gnutls.config \
        --with-default-trust-store-pkcs11="pkcs11:model=p11-kit-trust;manufacturer=PKCS%2311%20Kit" \
        --with-trousers-lib=%{_libdir}/libtspi.so.1 \
%if %{with guile}
           --enable-guile \
%else
           --disable-guile \
%endif
%if %{with dane}
	   --with-unbound-root-key-file=/var/lib/unbound/root.key \
           --enable-dane \
%else
           --disable-dane \
%endif
           --disable-rpath

%make_build V=1

%install
%make_install
rm -f $RPM_BUILD_ROOT/usr/gnutls34/bin/srptool
rm -f $RPM_BUILD_ROOT/usr/gnutls34/bin/gnutls-srpcrypt
cp -f %{SOURCE1} $RPM_BUILD_ROOT/usr/gnutls34/bin/libgnutls-config
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/srptool.1
rm -f $RPM_BUILD_ROOT%{_mandir}/man3/*srp*
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
rm -f $RPM_BUILD_ROOT/usr/gnutls34/lib/*.la
rm -f $RPM_BUILD_ROOT/usr/gnutls34/lib/guile/2.0/guile-gnutls*.a
rm -f $RPM_BUILD_ROOT/usr/gnutls34/lib/guile/2.0/guile-gnutls*.la
rm -f $RPM_BUILD_ROOT/usr/gnutls34/lib/gnutls/libpkcs11mock1.*
%if %{without dane}
rm -f $RPM_BUILD_ROOT/usr/gnutls34/lib/pkgconfig/gnutls-dane.pc
%endif

mkdir -p $RPM_BUILD_ROOT/etc/ld.so.conf.d/
install %{SOURCE3} $RPM_BUILD_ROOT/etc/ld.so.conf.d/compat-gnutls34.conf

%find_lang gnutls

#%check
#make check %{?_smp_mflags}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%post guile -p /sbin/ldconfig

%postun guile -p /sbin/ldconfig

%files -f gnutls.lang
%defattr(-,root,root,-)
/etc/ld.so.conf.d/compat-gnutls34.conf
/usr/gnutls34/lib/libgnutls.so.30*
#%doc COPYING COPYING.LIB README AUTHORS

%files c++
/usr/gnutls34/lib/libgnutlsxx.so.*

%files devel
%defattr(-,root,root,-)
#/usr/gnutls/bin/libgnutls*-config
/usr/gnutls34/include/gnutls/*.h
/usr/gnutls34/lib/libgnutls*.so
/usr/gnutls34/lib/pkgconfig/*.pc
/usr/gnutls34/share/*
#%{_mandir}/man3/*
#%{_infodir}/gnutls*

%files utils
%defattr(-,root,root,-)
/usr/gnutls34/bin/*
%doc doc/certtool.cfg

%if %{with dane}
%files dane
%defattr(-,root,root,-)
/usr/gnutls34/lib/libgnutls-dane.so.*
%endif

%if %{with guile}
%files guile
%defattr(-,root,root,-)
/usr/gnutls34/lib/guile/2.0/guile-gnutls*.so*
/usr/gnutls34/share/guile/site/gnutls
/usr/gnutls34/share/guile/site/gnutls.scm
/usr/gnutls34/lib/guile/2.0/site-ccache/gnutls.go
/usr/gnutls34/lib/guile/2.0/site-ccache/gnutls/extra.go
%endif

%changelog
* Thu Nov 15 2018 2 - 3.4.17-3.1
-

* Mon Feb 1 2010 Support <support@atomicorp.com> 2.8.5-1
- Backport GNUtls to Centos/rhel 4 and 5

* Thu Jan 28 2010 Tomas Mraz <tmraz@redhat.com> 2.8.5-3
- drop superfluous rpath from binaries
- do not call autoreconf during build
- specify the license on utils subpackage

* Mon Jan 18 2010 Tomas Mraz <tmraz@redhat.com> 2.8.5-2
- do not create static libraries (#556052)

* Mon Nov  2 2009 Tomas Mraz <tmraz@redhat.com> 2.8.5-1
- upgrade to a new upstream version

* Wed Sep 23 2009 Tomas Mraz <tmraz@redhat.com> 2.8.4-1
- upgrade to a new upstream version

* Fri Aug 14 2009 Tomas Mraz <tmraz@redhat.com> 2.8.3-1
- upgrade to a new upstream version

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.8.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jun 10 2009 Tomas Mraz <tmraz@redhat.com> 2.8.1-1
- upgrade to a new upstream version

* Wed Jun  3 2009 Tomas Mraz <tmraz@redhat.com> 2.8.0-1
- upgrade to a new upstream version

* Mon May  4 2009 Tomas Mraz <tmraz@redhat.com> 2.6.6-1
- upgrade to a new upstream version - security fixes

* Tue Apr 14 2009 Tomas Mraz <tmraz@redhat.com> 2.6.5-1
- upgrade to a new upstream version, minor bugfixes only

* Fri Mar  6 2009 Tomas Mraz <tmraz@redhat.com> 2.6.4-1
- upgrade to a new upstream version

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Dec 15 2008 Tomas Mraz <tmraz@redhat.com> 2.6.3-1
- upgrade to a new upstream version

* Thu Dec  4 2008 Tomas Mraz <tmraz@redhat.com> 2.6.2-1
- upgrade to a new upstream version

* Tue Nov 11 2008 Tomas Mraz <tmraz@redhat.com> 2.4.2-3
- fix chain verification issue CVE-2008-4989 (#470079)

* Thu Sep 25 2008 Tomas Mraz <tmraz@redhat.com> 2.4.2-2
- add guile subpackage (#463735)
- force new libtool through autoreconf to drop unnecessary rpaths

* Tue Sep 23 2008 Tomas Mraz <tmraz@redhat.com> 2.4.2-1
- new upstream version

* Tue Jul  1 2008 Tomas Mraz <tmraz@redhat.com> 2.4.1-1
- new upstream version
- correct the license tag
- explicit --with-included-opencdk not needed
- use external lzo library, internal not included anymore

* Tue Jun 24 2008 Tomas Mraz <tmraz@redhat.com> 2.4.0-1
- upgrade to latest upstream

* Tue May 20 2008 Tomas Mraz <tmraz@redhat.com> 2.0.4-3
- fix three security issues in gnutls handshake - GNUTLS-SA-2008-1
  (#447461, #447462, #447463)

* Mon Feb  4 2008 Joe Orton <jorton@redhat.com> 2.0.4-2
- use system libtasn1

* Tue Dec  4 2007 Tomas Mraz <tmraz@redhat.com> 2.0.4-1
- upgrade to latest upstream

* Tue Aug 21 2007 Tomas Mraz <tmraz@redhat.com> 1.6.3-2
- license tag fix

* Wed Jun  6 2007 Tomas Mraz <tmraz@redhat.com> 1.6.3-1
- upgrade to latest upstream (#232445)

* Tue Apr 10 2007 Tomas Mraz <tmraz@redhat.com> 1.4.5-2
- properly require install-info (patch by Ville Skyttä)
- standard buildroot and use dist tag
- add COPYING and README to doc

* Wed Feb  7 2007 Tomas Mraz <tmraz@redhat.com> 1.4.5-1
- new upstream version
- drop libtermcap-devel from buildrequires

* Thu Sep 14 2006 Tomas Mraz <tmraz@redhat.com> 1.4.1-2
- detect forged signatures - CVE-2006-4790 (#206411), patch
  from upstream

* Tue Jul 18 2006 Tomas Mraz <tmraz@redhat.com> - 1.4.1-1
- upgrade to new upstream version, only minor changes

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.4.0-1.1
- rebuild

* Wed Jun 14 2006 Tomas Mraz <tmraz@redhat.com> - 1.4.0-1
- upgrade to new upstream version (#192070), rebuild
  of dependent packages required

* Tue May 16 2006 Tomas Mraz <tmraz@redhat.com> - 1.2.10-2
- added missing buildrequires

* Mon Feb 13 2006 Tomas Mraz <tmraz@redhat.com> - 1.2.10-1
- updated to new version (fixes CVE-2006-0645)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.2.9-3.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.2.9-3.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Tue Jan  3 2006 Jesse Keating <jkeating@redhat.com> 1.2.9-3
- rebuilt

* Fri Dec  9 2005 Tomas Mraz <tmraz@redhat.com> 1.2.9-2
- replaced *-config scripts with calls to pkg-config to
  solve multilib conflicts

* Wed Nov 23 2005 Tomas Mraz <tmraz@redhat.com> 1.2.9-1
- upgrade to newest upstream
- removed .la files (#172635)

* Sun Aug  7 2005 Tomas Mraz <tmraz@redhat.com> 1.2.6-1
- upgrade to newest upstream (rebuild of dependencies necessary)

* Mon Jul  4 2005 Tomas Mraz <tmraz@redhat.com> 1.0.25-2
- split the command line tools to utils subpackage

* Sat Apr 30 2005 Tomas Mraz <tmraz@redhat.com> 1.0.25-1
- new upstream version fixes potential DOS attack

* Sat Apr 23 2005 Tomas Mraz <tmraz@redhat.com> 1.0.24-2
- readd the version script dropped by upstream

* Fri Apr 22 2005 Tomas Mraz <tmraz@redhat.com> 1.0.24-1
- update to the latest upstream version on the 1.0 branch

* Wed Mar  2 2005 Warren Togami <wtogami@redhat.com> 1.0.20-6
- gcc4 rebuild

* Tue Jan  4 2005 Ivana Varekova <varekova@redhat.com> 1.0.20-5
- add gnutls Requires zlib-devel (#144069)

* Mon Nov 08 2004 Colin Walters <walters@redhat.com> 1.0.20-4
- Make gnutls-devel Require libgcrypt-devel

* Tue Sep 21 2004 Jeff Johnson <jbj@redhat.com> 1.0.20-3
- rebuild with release++, otherwise unchanged.

* Tue Sep  7 2004 Jeff Johnson <jbj@redhat.com> 1.0.20-2
- patent tainted SRP code removed.

* Sun Sep  5 2004 Jeff Johnson <jbj@redhat.com> 1.0.20-1
- update to 1.0.20.
- add --with-included-opencdk --with-included-libtasn1
- add --with-included-libcfg --with-included-lzo
- add --disable-srp-authentication.
- do "make check" after build.

* Fri Mar 21 2003 Jeff Johnson <jbj@redhat.com> 0.9.2-1
- upgrade to 0.9.2

* Tue Jun 25 2002 Jeff Johnson <jbj@redhat.com> 0.4.4-1
- update to 0.4.4.

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sat May 25 2002 Jeff Johnson <jbj@redhat.com> 0.4.3-1
- update to 0.4.3.

* Tue May 21 2002 Jeff Johnson <jbj@redhat.com> 0.4.2-1
- update to 0.4.2.
- change license to LGPL.
- include splint annotations patch.

* Tue Apr  2 2002 Nalin Dahyabhai <nalin@redhat.com> 0.4.0-1
- update to 0.4.0

* Thu Jan 17 2002 Nalin Dahyabhai <nalin@redhat.com> 0.3.2-1
- update to 0.3.2

* Wed Jan 10 2002 Nalin Dahyabhai <nalin@redhat.com> 0.3.0-1
- add a URL

* Wed Dec 20 2001 Nalin Dahyabhai <nalin@redhat.com>
- initial package

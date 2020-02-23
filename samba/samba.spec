# rpmbuild --rebuild --with testsuite --without clustering samba.src.rpm
#
# The testsuite is disabled by default. Set --with testsuite or bcond_without
# to run the Samba torture testsuite.
%bcond_with testsuite
# ctdb is enabled by default, you can disable it with: --without clustering
%bcond_without clustering

%define talloc_version 2.1.16
%define tdb_version 1.3.18
%define tevent_version 0.9.39
%define ldb_version 1.5.6

# This should be rc1 or nil
%define pre_release %nil

# This is a network daemon, do a hardened build
# Enables PIE and full RELRO protection
%global _hardened_build 1

%global with_libsmbclient 1
%global with_libwbclient 1

%global with_internal_talloc 1
%global with_internal_tevent 1
%global with_internal_tdb 1
%global with_internal_ldb 1

%global with_profiling 1

%global with_vfs_cephfs 0
%if 0%{?fedora}
%ifarch aarch64 ppc64le s390x x86_64
%global with_vfs_cephfs 1
%endif
%endif

# Disabled errors in all rawhide and f31, in all i386 and in some ppc64le (F30+)
%global with_vfs_glusterfs 0
# GlusterFS is a distributed file-system capable of scaling to several
# petabytes

%global with_intel_aes_accel 0
%ifarch x86_64
%global with_intel_aes_accel 1
%endif

%global libwbc_alternatives_version 0.15
%global libwbc_alternatives_suffix %nil
%if 0%{?__isa_bits} == 64
%global libwbc_alternatives_suffix -64
%endif

%global with_mitkrb5 0
%global with_dc 1

%if %{with testsuite}
%global with_dc 1
%endif

%global required_mit_krb5 1.15.1

%global _systemd_extra "Environment=KRB5CCNAME=FILE:/run/samba/krb5cc_samba"

# filter out perl requirements pulled in from examples in the docdir.
%global __requires_exclude_from ^%{_docdir}/.*$
%global __provides_exclude_from ^%{_docdir}/.*$


Name:           samba
Version:        4.10.13
Release:        1%{?dist}
Epoch:          3

%if 0%{?epoch} > 0
%define samba_depver %{epoch}:%{version}-%{release}
%else
%define samba_depver %{version}-%{release}
%endif

Summary:        Server and Client software to interoperate with Windows machines
License:        GPLv3+ and LGPLv3+
URL:            http://www.samba.org/

Source0:        https://ftp.samba.org/pub/samba/samba-%{version}%{pre_release}.tar.gz
Source1:        https://ftp.samba.org/pub/samba/samba-%{version}%{pre_release}.tar.asc
Source2:        gpgkey-52FBC0B86D954B0843324CDC6F33915B6568B7EA.gpg

# Red Hat specific replacement-files
Source10:       samba.log
Source11:       smb.conf.vendor
Source12:       smb.conf.example
Source13:       pam_winbind.conf
Source14:       samba.pamd

Source200:      README.dc
Source201:      README.downgrade

BuildRequires: gcc
BuildRequires: avahi-devel
BuildRequires: cups-devel
BuildRequires: dbus-devel
BuildRequires: docbook-style-xsl
BuildRequires: e2fsprogs-devel
BuildRequires: gawk
BuildRequires: gnupg2
BuildRequires: gpgme-devel
BuildRequires: jansson-devel
%if %{with_mitkrb5}
BuildRequires: krb5-devel >= %{required_mit_krb5}
%endif
BuildRequires: libacl-devel
BuildRequires: libaio-devel
BuildRequires: libarchive-devel
BuildRequires: libattr-devel
BuildRequires: libcap-devel
BuildRequires: libcmocka-devel
BuildRequires: libtirpc-devel
BuildRequires: libuuid-devel
BuildRequires: libxslt
BuildRequires: lmdb
BuildRequires: ncurses-devel
BuildRequires: openldap-devel
BuildRequires: pam-devel
BuildRequires: perl-generators
BuildRequires: perl(Archive::Tar)
BuildRequires: perl(ExtUtils::MakeMaker)
BuildRequires: perl(Parse::Yapp)
BuildRequires: perl(Test::More)
BuildRequires: popt-devel
BuildRequires: python2-devel
BuildRequires: python-dns
# This is required to avoid packaging the in tree
# copy of Samba
BuildRequires: python-iso8601
# For test in Fedora >= 28
BuildRequires: /usr/bin/rpcgen
BuildRequires: quota-devel
BuildRequires: readline-devel
BuildRequires: sed
BuildRequires: xfsprogs-devel
BuildRequires: xz
BuildRequires: zlib-devel >= 1.2.3

BuildRequires: pkgconfig(libsystemd)

%if %{with_vfs_glusterfs}
BuildRequires: glusterfs-api-devel >= 3.4.0.16
BuildRequires: glusterfs-devel >= 3.4.0.16
%endif

%if %{with_vfs_cephfs}
BuildRequires: libcephfs-devel
%endif

# pidl requirements
BuildRequires: perl(Parse::Yapp)

%if !%{with_internal_talloc}
BuildRequires: libtalloc-devel >= %{talloc_version}
BuildRequires: pytalloc-devel >= %{talloc_version}
%else
Provides:  libtalloc = %{talloc_version}
Obsoletes:  libtalloc <= %{talloc_version}
Provides:  pytalloc = %{talloc_version}
Obsoletes:  pytalloc <= %{talloc_version}
%endif

%if !%{with_internal_tevent}
BuildRequires: libtevent-devel >= %{tevent_version}
BuildRequires: python-tevent >= %{tevent_version}
%else
Provides: libtevent = %{tevent_version}
Obsoletes: libtevent <= %{tevent_version}
Provides: python-tevent = %{tevent_version}
Obsoletes: python-tevent <= %{tevent_version}
%endif

%if !%{with_internal_ldb}
# samba 4.8.12 pyldb-util (>=1.3.8 <=1.3.999): not found, Centos 7 verison is 1.4.2
BuildRequires: libldb-devel >= %{ldb_version}
BuildRequires: pyldb-devel >= %{ldb_version}
BuildRequires: pyldb >= %{ldb_version}
%else
Provides: libldb = %{ldb_version}
Obsoletes: libldb <= %{ldb_version}
Provides: pyldb = %{ldb_version}
Obsoletes: pyldb <= %{ldb_version}
%endif

%if !%{with_internal_tdb}
BuildRequires: libtdb-devel >= %{tdb_version}
BuildRequires: python-tdb >= %{tdb_version}
%else
Provides: libtdb = %{tdb_version}
Provides: python-tdb = %{tdb_version}
Obsoletes: libtdb <= %{tdb_version}
Obsoletes: python-tdb <= %{tdb_version}
%endif

%if %{with testsuite}
BuildRequires: ldb-tools
BuildRequires: tdb-tools
BuildRequires: python2-markdown
BuildRequires: python2-subunit
BuildRequires: lmdb-devel
%endif

%if %{with_dc}
%if %{with_mitkrb5}
BuildRequires: krb5-server >= %{required_mit_krb5}
%endif
BuildRequires: bind
# Required by samba-tool to run tests
BuildRequires: python2-crypto
BuildRequires: lmdb-devel
%endif
%if 0%{?rhel}
BuildRequires: compat-gnutls34-devel >= 3.4.7
BuildRequires: compat-nettle32-devel >= 3.1.1
%else
BuildRequires: gnutls-devel >= 3.4.7
BuildRequires: nettle-devel >= 3.1.1
%endif

Requires(pre): /usr/sbin/groupadd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

Requires(pre): %{name}-common = %{samba_depver}
Requires: %{name}-common = %{samba_depver}
Requires: %{name}-common-libs = %{samba_depver}
Requires: %{name}-common-tools = %{samba_depver}
Requires: %{name}-client-libs = %{samba_depver}
Requires: %{name}-libs = %{samba_depver}
%if %with_libwbclient
Requires: libwbclient = %{samba_depver}
%endif
Requires: pam

Provides: samba4 = %{samba_depver}
Obsoletes: samba4 < %{samba_depver}

# We don't build it outdated docs anymore
Provides: samba-doc = %{samba_depver}
Obsoletes: samba-doc < %{samba_depver}

# Is not supported yet
Provides: samba-domainjoin-gui = %{samba_depver}
Obsoletes: samba-domainjoin-gui < %{samba_depver}

# SWAT been deprecated and removed from samba
Provides: samba-swat = %{samba_depver}
Obsoletes: samba-swat < %{samba_depver}

Provides: samba4-swat = %{samba_depver}
Obsoletes: samba4-swat < %{samba_depver}

### SAMBA
%description
Samba is the standard Windows interoperability suite of programs for Linux and
Unix.

### CLIENT
%package client
Summary: Samba client programs
Requires(pre): %{name}-common = %{samba_depver}
Requires: %{name}-common = %{samba_depver}
Requires: %{name}-common-libs = %{samba_depver}
Requires: %{name}-client-libs = %{samba_depver}
%if %with_libsmbclient
Requires: libsmbclient = %{samba_depver}
%endif
%if %{with_internal_tdb}
Provides: tdb-tools = %{tdb_version}
Obsoletes: tdb-tools <= %{tdb_version}
%endif
%if %{with_internal_ldb}
Provides: ldb-tools = %{ldb_version}
Obsoletes: ldb-tools <= %{ldb_version}
%endif

Provides: samba4-client = %{samba_depver}
Obsoletes: samba4-client < %{samba_depver}

Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives

%description client
The %{name}-client package provides some SMB/CIFS clients to complement
the built-in SMB/CIFS filesystem in Linux. These clients allow access
of SMB/CIFS shares and printing to SMB/CIFS printers.

### CLIENT-LIBS
%package client-libs
Summary: Samba client libraries
Requires(pre): %{name}-common = %{samba_depver}
Requires: %{name}-common = %{samba_depver}
Requires: %{name}-common-libs = %{samba_depver}
%if %with_libwbclient
Requires: libwbclient = %{samba_depver}
%endif
%if %{with_mitkrb5}
Requires: krb5-libs >= %{required_mit_krb5}
%endif

%description client-libs
The samba-client-libs package contains internal libraries needed by the
SMB/CIFS clients.

### COMMON
%package common
Summary: Files used by both Samba servers and clients
BuildArch: noarch

Requires(post): systemd

Provides: samba4-common = %{samba_depver}
Obsoletes: samba4-common < %{samba_depver}

%description common
samba-common provides files necessary for both the server and client
packages of Samba.

### COMMON-LIBS
%package common-libs
Summary: Libraries used by both Samba servers and clients
Requires(pre): samba-common = %{samba_depver}
Requires: samba-common = %{samba_depver}
Requires: %{name}-client-libs = %{samba_depver}
%if %with_libwbclient
Requires: libwbclient = %{samba_depver}
%endif

%description common-libs
The samba-common-libs package contains internal libraries needed by the
SMB/CIFS clients.

### COMMON-TOOLS
%package common-tools
Summary: Tools for Samba servers and clients
Requires: samba-common-libs = %{samba_depver}
Requires: samba-client-libs = %{samba_depver}
Requires: samba-libs = %{samba_depver}
%if %with_libwbclient
Requires: libwbclient = %{samba_depver}
%endif

%description common-tools
The samba-common-tools package contains tools for Samba servers and
SMB/CIFS clients.

### DC
%package dc
Summary: Samba AD Domain Controller
Requires: %{name} = %{samba_depver}
Requires: %{name}-libs = %{samba_depver}
Requires: %{name}-dc-libs = %{samba_depver}
Requires: %{name}-winbind = %{samba_depver}
# samb-tool needs tdbbackup
Requires: tdb-tools
%if %{with_dc}
# samba-tool requirements, explicitly require python2 right now
Requires: python2
Requires: python2-%{name} = %{samba_depver}
Requires: %{name}-python-dc = %{samba_depver}
Requires: python2-crypto
# Force using libldb version to be the same as build version
# Otherwise LDB modules will not be loaded and samba-tool will fail
# See bug 1507420
%requires_eq libldb

### Note that samba-dc right now cannot be used with Python 3
### so we should make sure it does use python2 explicitly
%if 0
Requires: python3-crypto
Requires: python3-%{name} = %{samba_depver}
%endif
%if %{with_mitkrb5}
Requires: krb5-server >= %{required_mit_krb5}
%endif
%endif

Provides: samba4-dc = %{samba_depver}
Obsoletes: samba4-dc < %{samba_depver}

%description dc
The samba-dc package provides AD Domain Controller functionality

### DC-LIBS
%package dc-libs
Summary: Samba AD Domain Controller Libraries
Requires: %{name}-common-libs = %{samba_depver}
Requires: %{name}-libs = %{samba_depver}

Provides: samba4-dc-libs = %{samba_depver}
Obsoletes: samba4-dc-libs < %{samba_depver}

%description dc-libs
The %{name}-dc-libs package contains the libraries needed by the DC to
link against the SMB, RPC and other protocols.

### DC-BIND
%if %{with_dc}
%package dc-bind-dlz
Summary: Bind DLZ module for Samba AD
Requires: %{name}-common = %{samba_depver}
Requires: %{name}-dc-libs = %{samba_depver}
Requires: %{name}-dc = %{samba_depver}
Requires: bind

%description dc-bind-dlz
The %{name}-dc-bind-dlz package contains the libraries for bind to manage all
name server related details of Samba AD.
%endif # with_dc

### DEVEL
%package devel
Summary: Developer tools for Samba libraries
Requires: %{name}-libs = %{samba_depver}
Requires: %{name}-client-libs = %{samba_depver}

Provides: samba4-devel = %{samba_depver}
Obsoletes: samba4-devel < %{samba_depver}

%description devel
The %{name}-devel package contains the header files for the libraries
needed to develop programs that link against the SMB, RPC and other
libraries in the Samba suite.

### CEPH
%if %{with_vfs_cephfs}
%package vfs-cephfs
Summary: Samba VFS module for Ceph distributed storage system
Requires: %{name} = %{samba_depver}
Requires: %{name}-libs = %{samba_depver}

%description vfs-cephfs
Samba VFS module for Ceph distributed storage system integration.
%endif

### GLUSTER
%if %{with_vfs_glusterfs}
%package vfs-glusterfs
Summary: Samba VFS module for GlusterFS
Requires: glusterfs-api >= 3.4.0.16
Requires: glusterfs >= 3.4.0.16
Requires: %{name} = %{samba_depver}
Requires: %{name}-client-libs = %{samba_depver}
Requires: %{name}-libs = %{samba_depver}

Obsoletes: samba-glusterfs < %{samba_depver}
Provides: samba-glusterfs = %{samba_depver}

%description vfs-glusterfs
Samba VFS module for GlusterFS integration.
%endif

### KRB5-PRINTING
%package krb5-printing
Summary: Samba CUPS backend for printing with Kerberos
Requires(pre): %{name}-client
Requires: %{name}-client

Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives

%description krb5-printing
If you need Kerberos for print jobs to a printer connection to cups via the SMB
backend, then you need to install that package. It will allow cups to access
the Kerberos credentials cache of the user issuing the print job.

### LIBS
%package libs
Summary: Samba libraries
Requires: %{name}-client-libs = %{samba_depver}
%if %with_libwbclient
Requires: libwbclient = %{samba_depver}
%endif

Provides: samba4-libs = %{samba_depver}
Obsoletes: samba4-libs < %{samba_depver}

%description libs
The %{name}-libs package contains the libraries needed by programs that link
against the SMB, RPC and other protocols provided by the Samba suite.

### LIBSMBCLIENT
%if %with_libsmbclient
%package -n libsmbclient
Summary: The SMB client library
Requires(pre): %{name}-common = %{samba_depver}
Requires: %{name}-common = %{samba_depver}
Requires: %{name}-client-libs = %{samba_depver}

%description -n libsmbclient
The libsmbclient contains the SMB client library from the Samba suite.

%package -n libsmbclient-devel
Summary: Developer tools for the SMB client library
Requires: libsmbclient = %{samba_depver}

%description -n libsmbclient-devel
The libsmbclient-devel package contains the header files and libraries needed
to develop programs that link against the SMB client library in the Samba
suite.
%endif # with_libsmbclient

### LIBWBCLIENT
%if %with_libwbclient
%package -n libwbclient
Summary: The winbind client library
Requires: %{name}-client-libs = %{samba_depver}

%description -n libwbclient
The libwbclient package contains the winbind client library from the Samba
suite.

%package -n libwbclient-devel
Summary: Developer tools for the winbind library
Requires: libwbclient = %{samba_depver}

Provides: samba-winbind-devel = %{samba_depver}
Obsoletes: samba-winbind-devel < %{samba_depver}

%description -n libwbclient-devel
The libwbclient-devel package provides developer tools for the wbclient
library.
%endif # with_libwbclient

### PYTHON
%package python
Summary: Samba Python libraries
Requires: %{name} = %{samba_depver}
Requires: %{name}-client-libs = %{samba_depver}
Requires: %{name}-libs = %{samba_depver}
Requires: python-tevent
Requires: python-tdb
Requires: pyldb
Requires: pytalloc
Requires: python-dns

Provides: python2-%{name} = %{samba_depver}
Obsoletes: samba4-python < %{samba_depver}


%description python
The %{name}-python package contains the Python libraries needed by programs
that use SMB, RPC and other Samba provided protocols in Python programs.

%package python-test
Summary: Samba Python libraries
Requires: samba-python = %{samba_depver}

%description python-test
The %{name}-python-test package contains the Python libraries used by the test suite of Samba.
If you want to run full set of Samba tests, you need to install this package.

%if %{with_dc}
%package python-dc
Summary: Samba Python libraries for Samba AD
Requires: samba-python = %{samba_depver}

%description python-dc
The %{name}-python-dc package contains the Python libraries needed by programs
managing Samba AD.
%endif

### PIDL
%package pidl
Summary: Perl IDL compiler
Requires: perl(Parse::Yapp)
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
BuildArch: noarch

Provides: samba4-pidl = %{samba_depver}
Obsoletes: samba4-pidl < %{samba_depver}

%description pidl
The %{name}-pidl package contains the Perl IDL compiler used by Samba
and Wireshark to parse IDL and similar protocols

### TEST
%package test
Summary: Testing tools for Samba servers and clients
Requires: %{name} = %{samba_depver}
Requires: %{name}-common = %{samba_depver}
Requires: %{name}-winbind = %{samba_depver}

Requires: %{name}-client-libs = %{samba_depver}
Requires: %{name}-libs = %{samba_depver}
Requires: %{name}-test-libs = %{samba_depver}
%if %{with_dc}
Requires: %{name}-dc-libs = %{samba_depver}
%endif
Requires: %{name}-libs = %{samba_depver}
%if %with_libsmbclient
Requires: libsmbclient = %{samba_depver}
%endif
%if %with_libwbclient
Requires: libwbclient = %{samba_depver}
%endif

Provides: samba4-test = %{samba_depver}
Obsoletes: samba4-test < %{samba_depver}

%description test
%{name}-test provides testing tools for both the server and client
packages of Samba.

### TEST-LIBS
%package test-libs
Summary: Libraries need by the testing tools for Samba servers and clients
Requires: %{name}-client-libs = %{samba_depver}
Requires: %{name}-libs = %{samba_depver}

Provides: %{name}-test-devel = %{samba_depver}
Obsoletes: %{name}-test-devel < %{samba_depver}

%description test-libs
%{name}-test-libs provides libraries required by the testing tools.

### WINBIND
%package winbind
Summary: Samba winbind
Requires(pre): %{name}-common = %{samba_depver}
Requires: %{name}-common = %{samba_depver}
Requires: %{name}-common-libs = %{samba_depver}
Requires: %{name}-common-tools = %{samba_depver}
Requires: %{name}-client-libs = %{samba_depver}
Requires: %{name}-libs = %{samba_depver}
Requires: %{name}-winbind-modules = %{samba_depver}

Provides: samba4-winbind = %{samba_depver}
Obsoletes: samba4-winbind < %{samba_depver}

%description winbind
The samba-winbind package provides the winbind NSS library, and some client
tools.  Winbind enables Linux to be a full member in Windows domains and to use
Windows user and group accounts on Linux.

### WINBIND-CLIENTS
%package winbind-clients
Summary: Samba winbind clients
Requires: %{name}-common = %{samba_depver}
Requires: %{name}-common-libs = %{samba_depver}
Requires: %{name}-client-libs = %{samba_depver}
Requires: %{name}-libs = %{samba_depver}
Requires: %{name}-winbind = %{samba_depver}
%if %with_libwbclient
Requires: libwbclient = %{samba_depver}
%endif

Provides: samba4-winbind-clients = %{samba_depver}
Obsoletes: samba4-winbind-clients < %{samba_depver}

%description winbind-clients
The samba-winbind-clients package provides the wbinfo and ntlm_auth
tool.

### WINBIND-KRB5-LOCATOR
%package winbind-krb5-locator
Summary: Samba winbind krb5 locator
%if %with_libwbclient
Requires: libwbclient = %{samba_depver}
Requires: %{name}-winbind = %{samba_depver}
%else
Requires: %{name}-libs = %{samba_depver}
%endif

Provides: samba4-winbind-krb5-locator = %{samba_depver}
Obsoletes: samba4-winbind-krb5-locator < %{samba_depver}

# Handle winbind_krb5_locator.so as alternatives to allow
# IPA AD trusts case where it should not be used by libkrb5
# The plugin will be diverted to /dev/null by the FreeIPA
# freeipa-server-trust-ad subpackage due to higher priority
# and restored to the proper one on uninstall
Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives
Requires(preun): %{_sbindir}/update-alternatives

%description winbind-krb5-locator
The winbind krb5 locator is a plugin for the system kerberos library to allow
the local kerberos library to use the same KDC as samba and winbind use

### WINBIND-MODULES
%package winbind-modules
Summary: Samba winbind modules
Requires: %{name}-client-libs = %{samba_depver}
Requires: %{name}-libs = %{samba_depver}
%if %with_libwbclient
Requires: libwbclient = %{samba_depver}
%endif
Requires: pam

%description winbind-modules
The samba-winbind-modules package provides the NSS library and a PAM module
necessary to communicate to the Winbind Daemon

### CTDB
%if %{with clustering}
%package -n ctdb
Summary: A Clustered Database based on Samba's Trivial Database (TDB)

Requires: %{name}-client-libs = %{samba_depver}

Requires: coreutils
Requires: fileutils
# for ps and killall
Requires: psmisc
Requires: sed
Requires: tdb-tools
Requires: gawk
# for pkill and pidof:
Requires: procps-ng
# for netstat:
Requires: net-tools
Requires: ethtool
# for ip:
Requires: iproute
Requires: iptables
# for flock, getopt, kill:
Requires: util-linux

Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description -n ctdb
CTDB is a cluster implementation of the TDB database used by Samba and other
projects to store temporary data. If an application is already using TDB for
temporary data it is very easy to convert that application to be cluster aware
and use CTDB instead.

### CTDB-TEST
%package -n ctdb-tests
Summary: CTDB clustered database test suite

Requires: samba-client-libs = %{samba_depver}

Requires: ctdb = %{samba_depver}
%if 0%{?rhel}
Requires: nc
%else
Recommends: nc
%endif

Provides: ctdb-devel = %{samba_depver}
Obsoletes: ctdb-devel < %{samba_depver}

%description -n ctdb-tests
Test suite for CTDB.
CTDB is a cluster implementation of the TDB database used by Samba and other
projects to store temporary data. If an application is already using TDB for
temporary data it is very easy to convert that application to be cluster aware
and use CTDB instead.
%endif

%prep
zcat %{SOURCE0} | gpgv2 --quiet --keyring %{SOURCE2} %{SOURCE1} -
%autosetup -n samba-%{version}%{pre_release} -p1

%build
%global _talloc_lib ,talloc,pytalloc,pytalloc-util
%global _tevent_lib ,tevent,pytevent
%global _tdb_lib ,tdb,pytdb
%global _ldb_lib ,ldb,pyldb,pyldb-util

%if ! %{with_internal_talloc}
%global _talloc_lib ,!talloc,!pytalloc,!pytalloc-util
%endif

%if ! %{with_internal_tevent}
%global _tevent_lib ,!tevent,!pytevent
%endif

%if ! %{with_internal_tdb}
%global _tdb_lib ,!tdb,!pytdb
%endif

%if ! %{with_internal_ldb}
%global _ldb_lib ,!ldb,!pyldb,!pyldb-util
%endif

%global _samba_libraries !zlib,!popt%{_talloc_lib}%{_tevent_lib}%{_tdb_lib}%{_ldb_lib}

%global _samba_idmap_modules idmap_ad,idmap_rid,idmap_ldap,idmap_hash,idmap_tdb2
%global _samba_pdb_modules pdb_tdbsam,pdb_ldap,pdb_smbpasswd,pdb_wbc_sam,pdb_samba4
%global _samba_auth_modules auth_wbc,auth_unix,auth_server,auth_script,auth_samba4
%global _samba_vfs_modules vfs_dfs_samba4

%global _samba_modules %{_samba_idmap_modules},%{_samba_pdb_modules},%{_samba_auth_modules},%{_samba_vfs_modules}

%global _libsmbclient %nil
%global _libwbclient %nil

%if ! %with_libsmbclient
%global _libsmbclient smbclient,
%endif

%if ! %with_libwbclient
%global _libwbclient wbclient,
%endif

%global _samba_private_libraries %{_libsmbclient}%{_libwbclient}

%if 0%{?rhel}
export PKG_CONFIG_PATH=%{_libdir}/compat-gnutls34/pkgconfig:%{_libdir}/compat-nettle32/pkgconfig
%endif

/usr/bin/pkg-config "gnutls >= 3.4.7" --cflags --libs gnutls

# Avoid ./configure: line 16: python: command not found
export PYTHON=%{__python2}

%configure \
        --enable-fhs \
        --with-piddir=/run \
        --with-sockets-dir=/run/samba \
        --with-modulesdir=%{_libdir}/samba \
        --with-pammodulesdir=%{_libdir}/security \
        --with-lockdir=/var/lib/samba/lock \
        --with-statedir=/var/lib/samba \
        --with-cachedir=/var/lib/samba \
        --disable-rpath-install \
        --with-shared-modules=%{_samba_modules} \
        --bundled-libraries=%{_samba_libraries} \
        --with-pam \
        --with-pie \
        --with-relro \
        --without-fam \
%if (! %with_libsmbclient) || (! %with_libwbclient)
        --private-libraries=%{_samba_private_libraries} \
%endif
%if %with_mitkrb5
        --with-system-mitkrb5 \
        --with-experimental-mit-ad-dc \
%endif
%if ! %{with_dc}
        --without-ad-dc \
%endif
%if ! %with_vfs_glusterfs
        --disable-glusterfs \
%endif
%if %{with clustering}
        --with-cluster-support \
%endif
%if %with_profiling
        --with-profiling-data \
%endif
%if %{with testsuite}
        --enable-selftest \
%endif
%if %with_intel_aes_accel
        --accel-aes=intelaesni \
%endif
        --with-systemd \
        --systemd-install-services \
        --with-systemddir=/usr/lib/systemd/system \
        --systemd-smb-extra=%{_systemd_extra} \
        --systemd-nmb-extra=%{_systemd_extra} \
        --systemd-winbind-extra=%{_systemd_extra} \
        --systemd-samba-extra=%{_systemd_extra}

make %{?_smp_mflags}

%install
export PYTHON=%{__python2}
%make_install

# Workaround: make sure all general Python shebangs are pointing to Python 2
# otherwise it will not work when default python is different from Python 2.
# Samba tools aren't ready for Python 3 yet.
for i in %{buildroot}%{_bindir} %{buildroot}%{_sbindir} ; do
    find $i \
        ! -name '*.pyc' -a \
        ! -name '*.pyo' -a \
        -type f -exec grep -qsm1 '^#!.*\bpython' {} \; \
        -exec sed -i -e '1 s|^#!.*\bpython[^ ]*|#!%{__python2}|' {} \;
done

install -d -m 0755 %{buildroot}/usr/{sbin,bin}
install -d -m 0755 %{buildroot}%{_libdir}/security
install -d -m 0755 %{buildroot}/var/lib/samba
install -d -m 0755 %{buildroot}/var/lib/samba/drivers
install -d -m 0755 %{buildroot}/var/lib/samba/lock
install -d -m 0755 %{buildroot}/var/lib/samba/private
install -d -m 0755 %{buildroot}/var/lib/samba/scripts
install -d -m 0755 %{buildroot}/var/lib/samba/sysvol
install -d -m 0755 %{buildroot}/var/lib/samba/winbindd_privileged
install -d -m 0755 %{buildroot}/var/log/samba/old
install -d -m 0755 %{buildroot}/var/spool/samba
install -d -m 0755 %{buildroot}/var/run/samba
install -d -m 0755 %{buildroot}/var/run/winbindd
install -d -m 0755 %{buildroot}/%{_libdir}/samba
install -d -m 0755 %{buildroot}/%{_libdir}/samba/ldb
install -d -m 0755 %{buildroot}/%{_libdir}/pkgconfig

# Move libwbclient.so* into private directory, it cannot be just libdir/samba
# because samba uses rpath with this directory.
install -d -m 0755 %{buildroot}/%{_libdir}/samba/wbclient
mv %{buildroot}/%{_libdir}/libwbclient.so* %{buildroot}/%{_libdir}/samba/wbclient
if [ ! -f %{buildroot}/%{_libdir}/samba/wbclient/libwbclient.so.%{libwbc_alternatives_version} ]
then
    echo "Expected libwbclient version not found, please check if version has changed."
    exit -1
fi


touch %{buildroot}%{_libexecdir}/samba/cups_backend_smb

# Install other stuff
install -d -m 0755 %{buildroot}%{_sysconfdir}/logrotate.d
install -m 0644 %{SOURCE10} %{buildroot}%{_sysconfdir}/logrotate.d/samba

install -m 0644 %{SOURCE11} %{buildroot}%{_sysconfdir}/samba/smb.conf
install -m 0644 %{SOURCE12} %{buildroot}%{_sysconfdir}/samba/smb.conf.example

install -d -m 0755 %{buildroot}%{_sysconfdir}/security
install -m 0644 %{SOURCE13} %{buildroot}%{_sysconfdir}/security/pam_winbind.conf

install -d -m 0755 %{buildroot}%{_sysconfdir}/pam.d
install -m 0644 %{SOURCE14} %{buildroot}%{_sysconfdir}/pam.d/samba

echo 127.0.0.1 localhost > %{buildroot}%{_sysconfdir}/samba/lmhosts

# openLDAP database schema
install -d -m 0755 %{buildroot}%{_sysconfdir}/openldap/schema
install -m644 examples/LDAP/samba.schema %{buildroot}%{_sysconfdir}/openldap/schema/samba.schema

install -m 0744 packaging/printing/smbprint %{buildroot}%{_bindir}/smbprint

install -d -m 0755 %{buildroot}%{_tmpfilesdir}
install -m644 packaging/systemd/samba.conf.tmp %{buildroot}%{_tmpfilesdir}/samba.conf
# create /run/samba too.
echo "d /run/samba  755 root root" >> %{buildroot}%{_tmpfilesdir}/samba.conf
%if %{with clustering}
echo "d /run/ctdb 755 root root" >> %{buildroot}%{_tmpfilesdir}/ctdb.conf
%endif

install -d -m 0755 %{buildroot}%{_sysconfdir}/sysconfig
install -m 0644 packaging/systemd/samba.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/samba
%if %{with clustering}
cat > %{buildroot}%{_sysconfdir}/sysconfig/ctdb <<EOF
# CTDB configuration is now in %{_sysconfdir}/ctdb/ctdbd.conf
EOF

install -d -m 0755 %{buildroot}%{_sysconfdir}/ctdb
install -m 0644 ctdb/config/ctdb.conf %{buildroot}%{_sysconfdir}/ctdb/ctdb.conf
%endif

install -m 0644 %{SOURCE201} packaging/README.downgrade

%if ! %{with_dc}
install -m 0644 %{SOURCE200} packaging/README.dc
install -m 0644 %{SOURCE200} packaging/README.dc-libs
%endif

%if %{with clustering}
install -m 0644 ctdb/config/ctdb.service %{buildroot}%{_unitdir}
%endif

# NetworkManager online/offline script
install -d -m 0755 %{buildroot}%{_sysconfdir}/NetworkManager/dispatcher.d/
install -m 0755 packaging/NetworkManager/30-winbind-systemd \
            %{buildroot}%{_sysconfdir}/NetworkManager/dispatcher.d/30-winbind

# winbind krb5 plugins
install -d -m 0755 %{buildroot}%{_libdir}/krb5/plugins/libkrb5
touch %{buildroot}%{_libdir}/krb5/plugins/libkrb5/winbind_krb5_locator.so

%if !%{with_dc}
for i in \
    %{_libdir}/samba/libdfs-server-ad-samba4.so \
    %{_libdir}/samba/libdnsserver-common-samba4.so \
    %{_libdir}/samba/libdsdb-garbage-collect-tombstones-samba4.so \
    %{_mandir}/man8/samba.8 \
    %{_mandir}/man8/samba-tool.8 \
    %{_mandir}/man8/samba_gpupdate.8 \
    %{_libdir}/samba/ldb/ildap.so \
    %{_libdir}/samba/ldb/ldbsamba_extensions.so \
    %{_unitdir}/samba.service \
    %{python2_sitearch}/samba/dcerpc/dnsserver.so \
    %{python2_sitearch}/samba/dnsserver.py* \
    %{python2_sitearch}/samba/domain_update.py* \
    %{python2_sitearch}/samba/dsdb_dns.so \
    %{python2_sitearch}/samba/dsdb.so \
    %{python2_sitearch}/samba/forest_update.py* \
    %{python2_sitearch}/samba/gpclass.py* \
    %{python2_sitearch}/samba/gpo.so \
    %{python2_sitearch}/samba/kcc/debug.py* \
    %{python2_sitearch}/samba/kcc/graph.py* \
    %{python2_sitearch}/samba/kcc/graph_utils.py* \
    %{python2_sitearch}/samba/kcc/__init__.py* \
    %{python2_sitearch}/samba/kcc/kcc_utils.py* \
    %{python2_sitearch}/samba/kcc/ldif_import_export.py* \
    %{python2_sitearch}/samba/ms_forest_updates_markdown.py* \
    %{python2_sitearch}/samba/ms_schema_markdown.py* \
    %{python2_sitearch}/samba/provision/backend.py* \
    %{python2_sitearch}/samba/provision/common.py* \
    %{python2_sitearch}/samba/provision/__init__.py* \
    %{python2_sitearch}/samba/provision/kerberos_implementation.py* \
    %{python2_sitearch}/samba/provision/kerberos.py* \
    %{python2_sitearch}/samba/provision/sambadns.py* \
    %{python2_sitearch}/samba/samdb.py* \
    %{python2_sitearch}/samba/schema.py* \
    %{python2_sitearch}/samba/web_server/__init__.py* \
    %{_sbindir}/samba_gpupdate \
    ; do
    rm -f %{buildroot}$i
done
%endif

# This makes the right links, as rpmlint requires that
# the ldconfig-created links be recorded in the RPM.
/sbin/ldconfig -N -n %{buildroot}%{_libdir}


%check
%if %{with testsuite}
TDB_NO_FSYNC=1 make %{?_smp_mflags} test
%endif

%post
%systemd_post smb.service
%systemd_post nmb.service

%preun
%systemd_preun smb.service
%systemd_preun nmb.service

%postun
%systemd_postun_with_restart smb.service
%systemd_postun_with_restart nmb.service

%pre common
getent group printadmin >/dev/null || groupadd -r printadmin || :

%post common
/sbin/ldconfig
/usr/bin/systemd-tmpfiles --create %{_tmpfilesdir}/samba.conf
if [ -d /var/cache/samba ]; then
    mv /var/cache/samba/netsamlogon_cache.tdb /var/lib/samba/ 2>/dev/null
    mv /var/cache/samba/winbindd_cache.tdb /var/lib/samba/ 2>/dev/null
    rm -rf /var/cache/samba/
    ln -sf /var/cache/samba /var/lib/samba/
fi

%post client
%{_sbindir}/update-alternatives --install %{_libexecdir}/samba/cups_backend_smb \
    cups_backend_smb \
    %{_bindir}/smbspool 10

%postun client
if [ $1 -eq 0 ] ; then
    %{_sbindir}/update-alternatives --remove cups_backend_smb %{_bindir}/smbspool
fi

%post client-libs -p /sbin/ldconfig

%postun client-libs -p /sbin/ldconfig

%post common-libs -p /sbin/ldconfig

%postun common-libs -p /sbin/ldconfig

%if %{with_dc}
%post dc-libs -p /sbin/ldconfig

%postun dc-libs -p /sbin/ldconfig

%post dc
%systemd_post samba.service

%preun dc
%systemd_preun samba.service

%postun dc
%systemd_postun_with_restart samba.service
%endif

%post krb5-printing
%{_sbindir}/update-alternatives --install %{_libexecdir}/samba/cups_backend_smb \
    cups_backend_smb \
    %{_libexecdir}/samba/smbspool_krb5_wrapper 50

%postun krb5-printing
if [ $1 -eq 0 ] ; then
    %{_sbindir}/update-alternatives --remove cups_backend_smb %{_libexecdir}/samba/smbspool_krb5_wrapper
fi

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%if %with_libsmbclient
%post -n libsmbclient -p /sbin/ldconfig

%postun -n libsmbclient -p /sbin/ldconfig
%endif

%if %with_libwbclient
%posttrans -n libwbclient
# It has to be posttrans here to make sure all files of a previous version
# without alternatives support are removed
%{_sbindir}/update-alternatives \
        --install \
        %{_libdir}/libwbclient.so.%{libwbc_alternatives_version} \
        libwbclient.so.%{libwbc_alternatives_version}%{libwbc_alternatives_suffix} \
        %{_libdir}/samba/wbclient/libwbclient.so.%{libwbc_alternatives_version} \
        10
/sbin/ldconfig

%preun -n libwbclient
%{_sbindir}/update-alternatives \
        --remove \
        libwbclient.so.%{libwbc_alternatives_version}%{libwbc_alternatives_suffix} \
        %{_libdir}/samba/wbclient/libwbclient.so.%{libwbc_alternatives_version}
/sbin/ldconfig

%posttrans -n libwbclient-devel
%{_sbindir}/update-alternatives \
        --install %{_libdir}/libwbclient.so \
        libwbclient.so%{libwbc_alternatives_suffix} \
        %{_libdir}/samba/wbclient/libwbclient.so \
        10

%preun -n libwbclient-devel
# alternatives checks if the file which should be removed is a link or not, but
# not if it points to the /etc/alternatives directory or to some other place.
# When downgrading to a version where alternatives is not used and
# libwbclient.so is a link and not a file it will be removed. The following
# check removes the alternatives files manually if that is the case.
if [ "`readlink %{_libdir}/libwbclient.so`" == "libwbclient.so.%{libwbc_alternatives_version}" ]; then
    /bin/rm -f /etc/alternatives/libwbclient.so%{libwbc_alternatives_suffix} /var/lib/alternatives/libwbclient.so%{libwbc_alternatives_suffix} 2> /dev/null
else
    %{_sbindir}/update-alternatives --remove libwbclient.so%{libwbc_alternatives_suffix} %{_libdir}/samba/wbclient/libwbclient.so
fi

%endif # with_libwbclient

%post test -p /sbin/ldconfig

%postun test -p /sbin/ldconfig

%pre winbind
/usr/sbin/groupadd -g 88 wbpriv >/dev/null 2>&1 || :

%post winbind
%systemd_post winbind.service

%preun winbind
%systemd_preun winbind.service

%postun winbind
%systemd_postun_with_restart smb.service
%systemd_postun_with_restart nmb.service

%postun winbind-krb5-locator
if [ "$1" -ge "1" ]; then
        if [ "`readlink %{_sysconfdir}/alternatives/winbind_krb5_locator.so`" == "%{_libdir}/samba/krb5/winbind_krb5_locator.so" ]; then
                %{_sbindir}/update-alternatives --set winbind_krb5_locator.so %{_libdir}/samba/krb5/winbind_krb5_locator.so
        fi
fi

%post winbind-krb5-locator
%{_sbindir}/update-alternatives --install %{_libdir}/krb5/plugins/libkrb5/winbind_krb5_locator.so \
                                winbind_krb5_locator.so %{_libdir}/samba/krb5/winbind_krb5_locator.so 10

%preun winbind-krb5-locator
if [ $1 -eq 0 ]; then
        %{_sbindir}/update-alternatives --remove winbind_krb5_locator.so %{_libdir}/samba/krb5/winbind_krb5_locator.so
fi

%post winbind-modules -p /sbin/ldconfig

%postun winbind-modules -p /sbin/ldconfig

%if %{with clustering}
%post -n ctdb
/usr/bin/systemd-tmpfiles --create %{_tmpfilesdir}/ctdb.conf
%systemd_post ctdb.service

%preun -n ctdb
%systemd_preun ctdb.service

%postun -n ctdb
%systemd_postun_with_restart ctdb.service
%endif


### SAMBA
%files
%defattr(-,root,root,-)
%license COPYING
%doc README.md WHATSNEW.txt
%doc examples/autofs examples/LDAP examples/misc
%doc examples/printer-accounting examples/printing
%doc packaging/README.downgrade
%{_bindir}/smbstatus
%{_sbindir}/eventlogadm
%{_sbindir}/nmbd
%{_sbindir}/smbd
%if %{with_dc}
# This is only used by vfs_dfs_samba4
%{_libdir}/samba/libdfs-server-ad-samba4.so
%endif
%dir %{_libdir}/samba/auth
%{_libdir}/samba/auth/script.so
%{_libdir}/samba/auth/unix.so
%dir %{_libdir}/samba/vfs
%{_libdir}/samba/vfs/acl_tdb.so
%{_libdir}/samba/vfs/acl_xattr.so
%{_libdir}/samba/vfs/aio_fork.so
%{_libdir}/samba/vfs/aio_pthread.so
%{_libdir}/samba/vfs/audit.so
%{_libdir}/samba/vfs/btrfs.so
%{_libdir}/samba/vfs/cap.so
%{_libdir}/samba/vfs/catia.so
%{_libdir}/samba/vfs/commit.so
%{_libdir}/samba/vfs/crossrename.so
%{_libdir}/samba/vfs/default_quota.so
%if %{with_dc}
%{_libdir}/samba/vfs/dfs_samba4.so
%endif
%{_libdir}/samba/vfs/dirsort.so
%{_libdir}/samba/vfs/expand_msdfs.so
%{_libdir}/samba/vfs/extd_audit.so
%{_libdir}/samba/vfs/fake_perms.so
%{_libdir}/samba/vfs/fileid.so
%{_libdir}/samba/vfs/fruit.so
%{_libdir}/samba/vfs/full_audit.so
%{_libdir}/samba/vfs/linux_xfs_sgid.so
%{_libdir}/samba/vfs/media_harmony.so
%{_libdir}/samba/vfs/netatalk.so
%{_libdir}/samba/vfs/offline.so
%{_libdir}/samba/vfs/preopen.so
%{_libdir}/samba/vfs/readahead.so
%{_libdir}/samba/vfs/readonly.so
%{_libdir}/samba/vfs/recycle.so
%{_libdir}/samba/vfs/shadow_copy.so
%{_libdir}/samba/vfs/shadow_copy2.so
%{_libdir}/samba/vfs/shell_snap.so
%{_libdir}/samba/vfs/snapper.so
%{_libdir}/samba/vfs/streams_depot.so
%{_libdir}/samba/vfs/streams_xattr.so
%{_libdir}/samba/vfs/syncops.so
%{_libdir}/samba/vfs/time_audit.so
%{_libdir}/samba/vfs/unityed_media.so
%{_libdir}/samba/vfs/virusfilter.so
%{_libdir}/samba/vfs/worm.so
%{_libdir}/samba/vfs/xattr_tdb.so
%{_libdir}/samba/vfs/glusterfs_fuse.so

%{_unitdir}/nmb.service
%{_unitdir}/smb.service
%attr(1777,root,root) %dir /var/spool/samba
%dir %{_sysconfdir}/openldap/schema
%config %{_sysconfdir}/openldap/schema/samba.schema
%config(noreplace) %{_sysconfdir}/pam.d/samba
%{_mandir}/man1/smbstatus.1*
%{_mandir}/man8/eventlogadm.8*
%{_mandir}/man8/smbd.8*
%{_mandir}/man8/nmbd.8*
%{_mandir}/man8/vfs_acl_tdb.8*
%{_mandir}/man8/vfs_acl_xattr.8*
%{_mandir}/man8/vfs_aio_fork.8*
%{_mandir}/man8/vfs_aio_pthread.8*
%{_mandir}/man8/vfs_audit.8*
%{_mandir}/man8/vfs_btrfs.8*
%{_mandir}/man8/vfs_cap.8*
%{_mandir}/man8/vfs_catia.8*
%{_mandir}/man8/vfs_commit.8*
%{_mandir}/man8/vfs_crossrename.8*
%{_mandir}/man8/vfs_default_quota.8*
%{_mandir}/man8/vfs_dirsort.8*
%{_mandir}/man8/vfs_extd_audit.8*
%{_mandir}/man8/vfs_fake_perms.8*
%{_mandir}/man8/vfs_fileid.8*
%{_mandir}/man8/vfs_fruit.8*
%{_mandir}/man8/vfs_full_audit.8*
%{_mandir}/man8/vfs_linux_xfs_sgid.8*
%{_mandir}/man8/vfs_media_harmony.8*
%{_mandir}/man8/vfs_netatalk.8*
%{_mandir}/man8/vfs_offline.8*
%{_mandir}/man8/vfs_preopen.8*
%{_mandir}/man8/vfs_readahead.8*
%{_mandir}/man8/vfs_readonly.8*
%{_mandir}/man8/vfs_recycle.8*
%{_mandir}/man8/vfs_shadow_copy.8*
%{_mandir}/man8/vfs_shadow_copy2.8*
%{_mandir}/man8/vfs_shell_snap.8*
%{_mandir}/man8/vfs_snapper.8*
%{_mandir}/man8/vfs_streams_depot.8*
%{_mandir}/man8/vfs_streams_xattr.8*
%{_mandir}/man8/vfs_syncops.8*
%{_mandir}/man8/vfs_time_audit.8*
%{_mandir}/man8/vfs_unityed_media.8*
%{_mandir}/man8/vfs_virusfilter.8*
%{_mandir}/man8/vfs_worm.8*
%{_mandir}/man8/vfs_xattr_tdb.8*
%{_mandir}/man8/vfs_glusterfs_fuse.8*
%attr(775,root,printadmin) %dir /var/lib/samba/drivers

### CLIENT
%files client
%defattr(-,root,root)
%{_bindir}/cifsdd
%{_bindir}/dbwrap_tool
# Find why this is not in RHEL
%if 0%{?fedora} > 0
%{_bindir}/dumpmscat
%endif
%{_bindir}/findsmb
%{_bindir}/mvxattr
%{_bindir}/nmblookup
%{_bindir}/oLschema2ldif
%{_bindir}/regdiff
%{_bindir}/regpatch
%{_bindir}/regshell
%{_bindir}/regtree
%{_bindir}/rpcclient
%{_bindir}/samba-regedit
%{_bindir}/sharesec
%{_bindir}/smbcacls
%{_bindir}/smbclient
%{_bindir}/smbcquotas
%{_bindir}/smbget
%{_bindir}/smbprint
%{_bindir}/smbspool
%{_bindir}/smbtar
%{_bindir}/smbtree
%dir %{_libexecdir}/samba
%ghost %{_libexecdir}/samba/cups_backend_smb
%{_mandir}/man1/dbwrap_tool.1*
%{_mandir}/man1/nmblookup.1*
%{_mandir}/man1/oLschema2ldif.1*
%{_mandir}/man1/regdiff.1*
%{_mandir}/man1/regpatch.1*
%{_mandir}/man1/regshell.1*
%{_mandir}/man1/regtree.1*
%{_mandir}/man1/findsmb.1*
%{_mandir}/man1/log2pcap.1*
%{_mandir}/man1/mvxattr.1*
%{_mandir}/man1/rpcclient.1*
%{_mandir}/man1/sharesec.1*
%{_mandir}/man1/smbcacls.1*
%{_mandir}/man1/smbclient.1*
%{_mandir}/man1/smbcquotas.1*
%{_mandir}/man1/smbget.1*
%{_mandir}/man5/smbgetrc.5*
%{_mandir}/man1/smbtar.1*
%{_mandir}/man1/smbtree.1*
%{_mandir}/man7/traffic_learner.7.*
%{_mandir}/man7/traffic_replay.7.*
%{_mandir}/man8/cifsdd.8.*
%{_mandir}/man8/samba-regedit.8*
%{_mandir}/man8/smbspool.8*

%if %{with_internal_tdb}
%{_bindir}/tdbbackup
%{_bindir}/tdbdump
%{_bindir}/tdbrestore
%{_bindir}/tdbtool
%{_mandir}/man8/tdbbackup.8*
%{_mandir}/man8/tdbdump.8*
%{_mandir}/man8/tdbrestore.8*
%{_mandir}/man8/tdbtool.8*
%endif

%if %with_internal_ldb
%{_bindir}/ldbadd
%{_bindir}/ldbdel
%{_bindir}/ldbedit
%{_bindir}/ldbmodify
%{_bindir}/ldbrename
%{_bindir}/ldbsearch
%{_libdir}/samba/libldb-cmdline-samba4.so
%{_libdir}/samba/libldb-key-value-samba4.so
%ifnarch i686
# Unclear why this is not on i686,
%{_libdir}/samba/libldb-mdb-int-samba4.so
%endif
%{_libdir}/samba/libldb-tdb-err-map-samba4.so
%{_libdir}/samba/libldb-tdb-int-samba4.so
%{_libdir}/samba/ldb/asq.so
%{_libdir}/samba/ldb/paged_results.so
%{_libdir}/samba/ldb/paged_searches.so
%{_libdir}/samba/ldb/rdn_name.so
%{_libdir}/samba/ldb/sample.so
%{_libdir}/samba/ldb/server_sort.so
%{_libdir}/samba/ldb/skel.so
%{_libdir}/samba/ldb/tdb.so
%{_mandir}/man1/ldbadd.1.gz
%{_mandir}/man1/ldbdel.1.gz
%{_mandir}/man1/ldbedit.1.gz
%{_mandir}/man1/ldbmodify.1.gz
%{_mandir}/man1/ldbrename.1.gz
%{_mandir}/man1/ldbsearch.1.gz
%endif

### CLIENT-LIBS
%files client-libs
%defattr(-,root,root)
%{_libdir}/libdcerpc-binding.so.*
%{_libdir}/libndr.so.*
%{_libdir}/libndr-krb5pac.so.*
%{_libdir}/libndr-nbt.so.*
%{_libdir}/libndr-standard.so.*
%{_libdir}/libnetapi.so.*
%{_libdir}/libsamba-credentials.so.*
%{_libdir}/libsamba-errors.so.*
%{_libdir}/libsamba-passdb.so.*
%{_libdir}/libsamba-util.so.*
%{_libdir}/libsamba-hostconfig.so.*
%{_libdir}/libsamdb.so.*
%{_libdir}/libsmbconf.so.*
%{_libdir}/libsmbldap.so.*
%{_libdir}/libtevent-util.so.*
%{_libdir}/libdcerpc.so.*

%dir %{_libdir}/samba
%{_libdir}/samba/libCHARSET3-samba4.so
%{_libdir}/samba/libaddns-samba4.so
%{_libdir}/samba/libads-samba4.so
%{_libdir}/samba/libasn1util-samba4.so
%{_libdir}/samba/libauth-samba4.so
%{_libdir}/samba/libauthkrb5-samba4.so
%{_libdir}/samba/libcli-cldap-samba4.so
%{_libdir}/samba/libcli-ldap-common-samba4.so
%{_libdir}/samba/libcli-ldap-samba4.so
%{_libdir}/samba/libcli-nbt-samba4.so
%{_libdir}/samba/libcli-smb-common-samba4.so
%{_libdir}/samba/libcli-spoolss-samba4.so
%{_libdir}/samba/libcliauth-samba4.so
%{_libdir}/samba/libclidns-samba4.so
%{_libdir}/samba/libcmdline-contexts-samba4.so
%{_libdir}/samba/libcmdline-credentials-samba4.so
%{_libdir}/samba/libcommon-auth-samba4.so
%{_libdir}/samba/libctdb-event-client-samba4.so
%{_libdir}/samba/libdbwrap-samba4.so
%{_libdir}/samba/libdcerpc-samba-samba4.so
%{_libdir}/samba/libevents-samba4.so
%{_libdir}/samba/libflag-mapping-samba4.so
%{_libdir}/samba/libgenrand-samba4.so
%{_libdir}/samba/libgensec-samba4.so
%{_libdir}/samba/libgpext-samba4.so
%{_libdir}/samba/libgse-samba4.so
%{_libdir}/samba/libhttp-samba4.so
%{_libdir}/samba/libinterfaces-samba4.so
%{_libdir}/samba/libiov-buf-samba4.so
%{_libdir}/samba/libkrb5samba-samba4.so
%{_libdir}/samba/libldbsamba-samba4.so
%{_libdir}/samba/liblibcli-lsa3-samba4.so
%{_libdir}/samba/liblibcli-netlogon3-samba4.so
%{_libdir}/samba/liblibsmb-samba4.so
%{_libdir}/samba/libmessages-dgm-samba4.so
%{_libdir}/samba/libmessages-util-samba4.so
%if 0%{?fedora} > 0
# Unclear why this is not on RHEL,
%{_libdir}/samba/libmscat-samba4.so
%endif
%{_libdir}/samba/libmsghdr-samba4.so
%{_libdir}/samba/libmsrpc3-samba4.so
%{_libdir}/samba/libndr-samba-samba4.so
%{_libdir}/samba/libndr-samba4.so
%{_libdir}/samba/libnet-keytab-samba4.so
%{_libdir}/samba/libnetif-samba4.so
%{_libdir}/samba/libnpa-tstream-samba4.so
%{_libdir}/samba/libposix-eadb-samba4.so
%{_libdir}/samba/libprinting-migrate-samba4.so
%{_libdir}/samba/libreplace-samba4.so
%{_libdir}/samba/libregistry-samba4.so
%{_libdir}/samba/libsamba-cluster-support-samba4.so
%{_libdir}/samba/libsamba-debug-samba4.so
%{_libdir}/samba/libsamba-modules-samba4.so
%{_libdir}/samba/libsamba-security-samba4.so
%{_libdir}/samba/libsamba-sockets-samba4.so
%{_libdir}/samba/libsamba3-util-samba4.so
%{_libdir}/samba/libsamdb-common-samba4.so
%{_libdir}/samba/libsecrets3-samba4.so
%{_libdir}/samba/libserver-id-db-samba4.so
%{_libdir}/samba/libserver-role-samba4.so
%{_libdir}/samba/libsmb-transport-samba4.so
%{_libdir}/samba/libsmbclient-raw-samba4.so
%{_libdir}/samba/libsmbd-base-samba4.so
%{_libdir}/samba/libsmbd-conn-samba4.so
%{_libdir}/samba/libsmbd-shim-samba4.so
%{_libdir}/samba/libsmbldaphelper-samba4.so
%{_libdir}/samba/libsys-rw-samba4.so
%{_libdir}/samba/libsocket-blocking-samba4.so
%{_libdir}/samba/libtalloc-report-samba4.so
%{_libdir}/samba/libtdb-wrap-samba4.so
%{_libdir}/samba/libtime-basic-samba4.so
%{_libdir}/samba/libtorture-samba4.so
%{_libdir}/samba/libtrusts-util-samba4.so
%{_libdir}/samba/libutil-cmdline-samba4.so
%{_libdir}/samba/libutil-reg-samba4.so
%{_libdir}/samba/libutil-setid-samba4.so
%{_libdir}/samba/libutil-tdb-samba4.so

%if ! %with_libwbclient
%{_libdir}/samba/libwbclient.so.*
%{_libdir}/samba/libwinbind-client-samba4.so
%endif # ! with_libwbclient

%if ! %with_libsmbclient
%{_libdir}/samba/libsmbclient.so.*
%{_mandir}/man7/libsmbclient.7*
%endif # ! with_libsmbclient

%if %{with_internal_talloc}
%{_libdir}/samba/libtalloc.so.2
%{_libdir}/samba/libtalloc.so.%{talloc_version}
%{_libdir}/samba/libpytalloc-util.so.2
%{_libdir}/samba/libpytalloc-util.so.%{talloc_version}
%{_mandir}/man3/talloc.3.gz
%endif

%if %{with_internal_tevent}
%{_libdir}/samba/libtevent.so.0
%{_libdir}/samba/libtevent.so.%{tevent_version}
%endif

%if %{with_internal_tdb}
%{_libdir}/samba/libtdb.so.1
%{_libdir}/samba/libtdb.so.%{tdb_version}
%endif

%if %{with_internal_ldb}
%{_libdir}/samba/libldb.so.1
%{_libdir}/samba/libldb.so.%{ldb_version}
%{_libdir}/samba/libpyldb-util.so.1
%{_libdir}/samba/libpyldb-util.so.%{ldb_version}
%{_mandir}/man3/ldb.3.gz
%endif

### COMMON
%files common
%defattr(-,root,root)
%{_tmpfilesdir}/samba.conf
%dir %{_sysconfdir}/logrotate.d/
%config(noreplace) %{_sysconfdir}/logrotate.d/samba
%attr(0700,root,root) %dir /var/log/samba
%attr(0700,root,root) %dir /var/log/samba/old
%ghost %dir /var/run/samba
%ghost %dir /var/run/winbindd
%dir /var/lib/samba
%if %{with_dc}
%attr(770,root,named) %dir /var/lib/samba/private
%else
%attr(700,root,root) %dir /var/lib/samba/private
%endif
%dir /var/lib/samba/lock
%attr(755,root,root) %dir %{_sysconfdir}/samba
%config(noreplace) %{_sysconfdir}/samba/smb.conf
%{_sysconfdir}/samba/smb.conf.example
%config(noreplace) %{_sysconfdir}/samba/lmhosts
%config(noreplace) %{_sysconfdir}/sysconfig/samba
%{_mandir}/man5/lmhosts.5*
%{_mandir}/man5/smb.conf.5*
%{_mandir}/man5/smbpasswd.5*
%{_mandir}/man7/samba.7*

### COMMON-libs
%files common-libs
%defattr(-,root,root)
# common libraries
%{_libdir}/samba/libpopt-samba3-cmdline-samba4.so
%{_libdir}/samba/libpopt-samba3-samba4.so
%if %{with_intel_aes_accel}
%{_libdir}/samba/libaesni-intel-samba4.so
%endif
%{_libdir}/samba/pdb/

%files common-tools
%defattr(-,root,root)
%{_bindir}/net
%{_bindir}/pdbedit
%{_bindir}/profiles
%{_bindir}/smbcontrol
%{_bindir}/smbpasswd
%{_bindir}/testparm
%{_mandir}/man1/profiles.1*
%{_mandir}/man1/smbcontrol.1*
%{_mandir}/man1/testparm.1*
%{_mandir}/man8/net.8*
%{_mandir}/man8/pdbedit.8*
%{_mandir}/man8/smbpasswd.8*

### DC
%files dc
%defattr(-,root,root)

%if %{with_dc}
%{_unitdir}/samba.service
%{_bindir}/samba-tool
%{_sbindir}/samba
%{_sbindir}/samba_kcc
%{_sbindir}/samba_dnsupdate
%{_sbindir}/samba-gpupdate
%{_sbindir}/samba_spnupdate
%{_sbindir}/samba_upgradedns
%if %with_mitkrb5
%{_libdir}/krb5/plugins/kdb/samba.so
%endif
%{_libdir}/samba/auth/samba4.so
%{_libdir}/samba/libpac-samba4.so
%dir %{_libdir}/samba/gensec
%{_libdir}/samba/gensec/krb5.so
%{_libdir}/samba/ldb/
%{_libdir}/samba/vfs/posix_eadb.so
%dir /var/lib/samba/sysvol
%{_datadir}/samba/setup
%{_mandir}/man8/samba.8*
%{_mandir}/man8/samba-gpupdate.8*
%{_mandir}/man8/samba-tool.8*
%else # with_dc
%doc packaging/README.dc
%endif # with_dc

### DC-LIBS
%files dc-libs
%defattr(-,root,root)
%if %{with_dc}
%{_libdir}/samba/libdb-glue-samba4.so
%{_libdir}/samba/libprocess-model-samba4.so
%{_libdir}/samba/libservice-samba4.so
%dir %{_libdir}/samba/process_model
%{_libdir}/samba/process_model/prefork.so
%{_libdir}/samba/process_model/standard.so
%dir %{_libdir}/samba/service
%{_libdir}/samba/service/cldap.so
%{_libdir}/samba/service/dcerpc.so
%{_libdir}/samba/service/dns.so
%{_libdir}/samba/service/dns_update.so
%{_libdir}/samba/service/drepl.so
%{_libdir}/samba/service/kcc.so
%{_libdir}/samba/service/kdc.so
%{_libdir}/samba/service/ldap.so
%{_libdir}/samba/service/nbtd.so
%{_libdir}/samba/service/ntp_signd.so
%{_libdir}/samba/service/s3fs.so
%{_libdir}/samba/service/web.so
%{_libdir}/samba/service/winbindd.so
%{_libdir}/samba/service/wrepl.so
%{_libdir}/libdcerpc-server.so.*
%{_libdir}/samba/libdnsserver-common-samba4.so
%{_libdir}/samba/libdsdb-module-samba4.so
%{_libdir}/samba/libdsdb-garbage-collect-tombstones-samba4.so
%{_libdir}/samba/libscavenge-dns-records-samba4.so
%else
%doc packaging/README.dc-libs
%endif # with_dc

### DC-BIND
%if %{with_dc}
%files dc-bind-dlz
%dir %{_libdir}/samba/bind9
%{_libdir}/samba/bind9/dlz_bind9.so
%{_libdir}/samba/bind9/dlz_bind9_9.so
%{_libdir}/samba/bind9/dlz_bind9_10.so
%{_libdir}/samba/bind9/dlz_bind9_11.so
%{_libdir}/samba/bind9/dlz_bind9_12.so
%endif # with_dc

### DEVEL
%files devel
%defattr(-,root,root)
%{_includedir}/samba-4.0/charset.h
%{_includedir}/samba-4.0/core/doserr.h
%{_includedir}/samba-4.0/core/error.h
%{_includedir}/samba-4.0/core/hresult.h
%{_includedir}/samba-4.0/core/ntstatus.h
%{_includedir}/samba-4.0/core/ntstatus_gen.h
%{_includedir}/samba-4.0/core/werror.h
%{_includedir}/samba-4.0/core/werror_gen.h
%{_includedir}/samba-4.0/credentials.h
%{_includedir}/samba-4.0/dcerpc.h
%{_includedir}/samba-4.0/domain_credentials.h
%{_includedir}/samba-4.0/gen_ndr/atsvc.h
%{_includedir}/samba-4.0/gen_ndr/auth.h
%{_includedir}/samba-4.0/gen_ndr/dcerpc.h
%{_includedir}/samba-4.0/gen_ndr/krb5pac.h
%{_includedir}/samba-4.0/gen_ndr/lsa.h
%{_includedir}/samba-4.0/gen_ndr/misc.h
%{_includedir}/samba-4.0/gen_ndr/nbt.h
%{_includedir}/samba-4.0/gen_ndr/drsblobs.h
%{_includedir}/samba-4.0/gen_ndr/drsuapi.h
%{_includedir}/samba-4.0/gen_ndr/ndr_drsblobs.h
%{_includedir}/samba-4.0/gen_ndr/ndr_drsuapi.h
%{_includedir}/samba-4.0/gen_ndr/ndr_atsvc.h
%{_includedir}/samba-4.0/gen_ndr/ndr_dcerpc.h
%{_includedir}/samba-4.0/gen_ndr/ndr_krb5pac.h
%{_includedir}/samba-4.0/gen_ndr/ndr_misc.h
%{_includedir}/samba-4.0/gen_ndr/ndr_nbt.h
%{_includedir}/samba-4.0/gen_ndr/ndr_samr.h
%{_includedir}/samba-4.0/gen_ndr/ndr_samr_c.h
%{_includedir}/samba-4.0/gen_ndr/ndr_svcctl.h
%{_includedir}/samba-4.0/gen_ndr/ndr_svcctl_c.h
%{_includedir}/samba-4.0/gen_ndr/netlogon.h
%{_includedir}/samba-4.0/gen_ndr/samr.h
%{_includedir}/samba-4.0/gen_ndr/security.h
%{_includedir}/samba-4.0/gen_ndr/server_id.h
%{_includedir}/samba-4.0/gen_ndr/svcctl.h
%{_includedir}/samba-4.0/ldb_wrap.h
%{_includedir}/samba-4.0/lookup_sid.h
%{_includedir}/samba-4.0/machine_sid.h
%{_includedir}/samba-4.0/ndr.h
%dir %{_includedir}/samba-4.0/ndr
%{_includedir}/samba-4.0/ndr/ndr_dcerpc.h
%{_includedir}/samba-4.0/ndr/ndr_drsblobs.h
%{_includedir}/samba-4.0/ndr/ndr_drsuapi.h
%{_includedir}/samba-4.0/ndr/ndr_krb5pac.h
%{_includedir}/samba-4.0/ndr/ndr_svcctl.h
%{_includedir}/samba-4.0/ndr/ndr_nbt.h
%{_includedir}/samba-4.0/netapi.h
%{_includedir}/samba-4.0/param.h
%{_includedir}/samba-4.0/passdb.h
%{_includedir}/samba-4.0/policy.h
%{_includedir}/samba-4.0/rpc_common.h
%{_includedir}/samba-4.0/samba/session.h
%{_includedir}/samba-4.0/samba/version.h
%{_includedir}/samba-4.0/share.h
%{_includedir}/samba-4.0/smb2_lease_struct.h
%{_includedir}/samba-4.0/smbconf.h
%{_includedir}/samba-4.0/smb_ldap.h
%{_includedir}/samba-4.0/smbldap.h
%{_includedir}/samba-4.0/tdr.h
%{_includedir}/samba-4.0/tsocket.h
%{_includedir}/samba-4.0/tsocket_internal.h
%{_includedir}/samba-4.0/util_ldb.h
%{_includedir}/samba-4.0/util/
%{_libdir}/libdcerpc-binding.so
%{_libdir}/libdcerpc-samr.so
%{_libdir}/libdcerpc.so
%{_libdir}/libndr-krb5pac.so
%{_libdir}/libndr-nbt.so
%{_libdir}/libndr-standard.so
%{_libdir}/libndr.so
%{_libdir}/libnetapi.so
%{_libdir}/libsamba-credentials.so
%{_libdir}/libsamba-errors.so
%{_libdir}/libsamba-hostconfig.so
%{_libdir}/libsamba-policy.so
%{_libdir}/libsamba-util.so
%{_libdir}/libsamdb.so
%{_libdir}/libsmbconf.so
%{_libdir}/libtevent-util.so
%{_libdir}/pkgconfig/dcerpc.pc
%{_libdir}/pkgconfig/dcerpc_samr.pc
%{_libdir}/pkgconfig/ndr.pc
%{_libdir}/pkgconfig/ndr_krb5pac.pc
%{_libdir}/pkgconfig/ndr_nbt.pc
%{_libdir}/pkgconfig/ndr_standard.pc
%{_libdir}/pkgconfig/netapi.pc
%{_libdir}/pkgconfig/samba-credentials.pc
%{_libdir}/pkgconfig/samba-hostconfig.pc
%{_libdir}/pkgconfig/samba-policy.pc
%{_libdir}/pkgconfig/samba-util.pc
%{_libdir}/pkgconfig/samdb.pc
%{_libdir}/libsamba-passdb.so
%{_libdir}/libsmbldap.so

%if %with_dc
%{_includedir}/samba-4.0/dcerpc_server.h
%{_libdir}/libdcerpc-server.so
%{_libdir}/pkgconfig/dcerpc_server.pc
%endif

%if ! %with_libsmbclient
%{_includedir}/samba-4.0/libsmbclient.h
%endif # ! with_libsmbclient

%if ! %with_libwbclient
%{_includedir}/samba-4.0/wbclient.h
%endif # ! with_libwbclient

### VFS-CEPHFS
%if %{with_vfs_cephfs}
%files vfs-cephfs
%{_libdir}/samba/vfs/ceph.so
%{_mandir}/man8/vfs_ceph.8*
%endif

### VFS-GLUSTERFS
%if %{with_vfs_glusterfs}
%files vfs-glusterfs
%{_libdir}/samba/vfs/glusterfs.so
%{_mandir}/man8/vfs_glusterfs.8*
%endif

### KRB5-PRINTING
%files krb5-printing
%defattr(-,root,root)
%attr(0700,root,root) %{_libexecdir}/samba/smbspool_krb5_wrapper
%{_mandir}/man8/smbspool_krb5_wrapper.8*

### LIBS
%files libs
%defattr(-,root,root)
%{_libdir}/libdcerpc-samr.so.*
%{_libdir}/libsamba-policy.so.*

# libraries needed by the public libraries
%{_libdir}/samba/libMESSAGING-samba4.so
%{_libdir}/samba/libMESSAGING-SEND-samba4.so
%{_libdir}/samba/libLIBWBCLIENT-OLD-samba4.so
%{_libdir}/samba/libauth4-samba4.so
%{_libdir}/samba/libauth-unix-token-samba4.so
%{_libdir}/samba/libcluster-samba4.so
%{_libdir}/samba/libdcerpc-samba4.so
%{_libdir}/samba/libnon-posix-acls-samba4.so
%{_libdir}/samba/libsamba-net-samba4.so
%{_libdir}/samba/libsamba-python-samba4.so
%{_libdir}/samba/libshares-samba4.so
%{_libdir}/samba/libsmbpasswdparser-samba4.so
%{_libdir}/samba/libxattr-tdb-samba4.so
%if ! %with_mitkrb5
%{_libdir}/samba/libHDB-SAMBA4-samba4.so
%{_libdir}/samba/libasn1-samba4.so.8
%{_libdir}/samba/libasn1-samba4.so.8.0.0
%{_libdir}/samba/libcom_err-samba4.so.0
%{_libdir}/samba/libcom_err-samba4.so.0.25
%{_libdir}/samba/libgssapi-samba4.so.2
%{_libdir}/samba/libgssapi-samba4.so.2.0.0
%{_libdir}/samba/libhcrypto-samba4.so.5
%{_libdir}/samba/libhcrypto-samba4.so.5.0.1
%{_libdir}/samba/libhdb-samba4.so.11
%{_libdir}/samba/libhdb-samba4.so.11.0.2
%{_libdir}/samba/libheimbase-samba4.so.1
%{_libdir}/samba/libheimbase-samba4.so.1.0.0
%{_libdir}/samba/libheimntlm-samba4.so.1
%{_libdir}/samba/libheimntlm-samba4.so.1.0.1
%{_libdir}/samba/libhx509-samba4.so.5
%{_libdir}/samba/libhx509-samba4.so.5.0.0
%{_libdir}/samba/libkdc-samba4.so.2
%{_libdir}/samba/libkdc-samba4.so.2.0.0
%{_libdir}/samba/libkrb5-samba4.so.26
%{_libdir}/samba/libkrb5-samba4.so.26.0.0
%{_libdir}/samba/libroken-samba4.so.19
%{_libdir}/samba/libroken-samba4.so.19.0.1
%{_libdir}/samba/libwind-samba4.so.0
%{_libdir}/samba/libwind-samba4.so.0.0.0
%endif


### LIBSMBCLIENT
%if %with_libsmbclient
%files -n libsmbclient
%defattr(-,root,root)
%{_libdir}/libsmbclient.so.*

### LIBSMBCLIENT-DEVEL
%files -n libsmbclient-devel
%defattr(-,root,root)
%{_includedir}/samba-4.0/libsmbclient.h
%{_libdir}/libsmbclient.so
%{_libdir}/pkgconfig/smbclient.pc
%{_mandir}/man7/libsmbclient.7*
%endif # with_libsmbclient

### LIBWBCLIENT
%if %with_libwbclient
%files -n libwbclient
%defattr(-,root,root)
%{_libdir}/samba/wbclient/libwbclient.so.*
%{_libdir}/samba/libwinbind-client-samba4.so

### LIBWBCLIENT-DEVEL
%files -n libwbclient-devel
%defattr(-,root,root)
%{_includedir}/samba-4.0/wbclient.h
%{_libdir}/samba/wbclient/libwbclient.so
%{_libdir}/pkgconfig/wbclient.pc
%endif # with_libwbclient

### PIDL
%files pidl
%defattr(-,root,root,-)
%attr(755,root,root) %{_bindir}/pidl
%dir %{perl_vendorlib}/Parse
%{perl_vendorlib}/Parse/Pidl.pm
%dir %{perl_vendorlib}/Parse/Pidl
%{perl_vendorlib}/Parse/Pidl/CUtil.pm
%{perl_vendorlib}/Parse/Pidl/Samba4.pm
%{perl_vendorlib}/Parse/Pidl/Expr.pm
%{perl_vendorlib}/Parse/Pidl/ODL.pm
%{perl_vendorlib}/Parse/Pidl/Typelist.pm
%{perl_vendorlib}/Parse/Pidl/IDL.pm
%{perl_vendorlib}/Parse/Pidl/Compat.pm
%dir %{perl_vendorlib}/Parse/Pidl/Wireshark
%{perl_vendorlib}/Parse/Pidl/Wireshark/Conformance.pm
%{perl_vendorlib}/Parse/Pidl/Wireshark/NDR.pm
%{perl_vendorlib}/Parse/Pidl/Dump.pm
%dir %{perl_vendorlib}/Parse/Pidl/Samba3
%{perl_vendorlib}/Parse/Pidl/Samba3/ServerNDR.pm
%{perl_vendorlib}/Parse/Pidl/Samba3/ClientNDR.pm
%dir %{perl_vendorlib}/Parse/Pidl/Samba4
%{perl_vendorlib}/Parse/Pidl/Samba4/Header.pm
%dir %{perl_vendorlib}/Parse/Pidl/Samba4/COM
%{perl_vendorlib}/Parse/Pidl/Samba4/COM/Header.pm
%{perl_vendorlib}/Parse/Pidl/Samba4/COM/Proxy.pm
%{perl_vendorlib}/Parse/Pidl/Samba4/COM/Stub.pm
%{perl_vendorlib}/Parse/Pidl/Samba4/Python.pm
%{perl_vendorlib}/Parse/Pidl/Samba4/Template.pm
%dir %{perl_vendorlib}/Parse/Pidl/Samba4/NDR
%{perl_vendorlib}/Parse/Pidl/Samba4/NDR/Server.pm
%{perl_vendorlib}/Parse/Pidl/Samba4/NDR/Client.pm
%{perl_vendorlib}/Parse/Pidl/Samba4/NDR/Parser.pm
%{perl_vendorlib}/Parse/Pidl/Samba4/TDR.pm
%{perl_vendorlib}/Parse/Pidl/NDR.pm
%{perl_vendorlib}/Parse/Pidl/Util.pm
%{_mandir}/man1/pidl*
%{_mandir}/man3/Parse::Pidl*

### PYTHON
%files python
%defattr(-,root,root,-)
%dir %{python2_sitearch}/samba
%{python2_sitearch}/samba/__init__.py*
%{python2_sitearch}/samba/_glue.so
%{python2_sitearch}/samba/_ldb.so
%{python2_sitearch}/samba/auth.so
%{python2_sitearch}/samba/colour.py*
%{python2_sitearch}/samba/common.py*
%{python2_sitearch}/samba/compat.py*
%{python2_sitearch}/samba/credentials.so
%{python2_sitearch}/samba/crypto.so
%{python2_sitearch}/samba/dbchecker.py*
%{python2_sitearch}/samba/descriptor.py*
%{python2_sitearch}/samba/drs_utils.py*
%{python2_sitearch}/samba/gensec.so
%{python2_sitearch}/samba/getopt.py*
%{python2_sitearch}/samba/graph.py*
%{python2_sitearch}/samba/hostconfig.py*
%{python2_sitearch}/samba/idmap.py*
%{python2_sitearch}/samba/join.py*
%{python2_sitearch}/samba/logger.py*
%{python2_sitearch}/samba/messaging.so
%{python2_sitearch}/samba/mdb_util.py*
%{python2_sitearch}/samba/ms_display_specifiers.py*
%{python2_sitearch}/samba/ms_schema.py*
%{python2_sitearch}/samba/ndr.py*
%{python2_sitearch}/samba/net.so
%{python2_sitearch}/samba/netbios.so
%{python2_sitearch}/samba/ntacls.py*
%{python2_sitearch}/samba/ntstatus.so
%{python2_sitearch}/samba/param.so
%{python2_sitearch}/samba/policy.so
%{python2_sitearch}/samba/posix_eadb.so
%{python2_sitearch}/samba/registry.so
%{python2_sitearch}/samba/remove_dc.py*
%{python2_sitearch}/samba/sd_utils.py*
%{python2_sitearch}/samba/security.so
%{python2_sitearch}/samba/sites.py*
%{python2_sitearch}/samba/smb.so
%{python2_sitearch}/samba/subnets.py*
%{python2_sitearch}/samba/upgrade.py*
%{python2_sitearch}/samba/upgradehelpers.py*
%{python2_sitearch}/samba/werror.so
%{python2_sitearch}/samba/xattr.py*
%{python2_sitearch}/samba/xattr_native.so
%{python2_sitearch}/samba/xattr_tdb.so

%{python2_sitearch}/samba/dcerpc/
%{python2_sitearch}/samba/emulate/
%{python2_sitearch}/samba/netcmd/
%{python2_sitearch}/samba/samba3/
%{python2_sitearch}/samba/subunit/
%{python2_sitearch}/samba/tdb_util.py*
%{python2_sitearch}/samba/third_party/

%if %{with_internal_tevent}
%{python2_sitearch}/tevent.*
%{python2_sitearch}/_tevent.so
%endif
%if %{with_internal_ldb}
%{python2_sitearch}/_ldb_text.*
%{python2_sitearch}/ldb.so
%endif
%if %{with_internal_tdb}
%{python2_sitearch}/_tdb_text.*
%{python2_sitearch}/tdb.so
%endif
%if %{with_internal_talloc}
%{python2_sitearch}/talloc.so
%endif


%if %{with_dc}
%files python-dc
%defattr(-,root,root,-)
%{python2_sitearch}/samba/domain_update.py*
%{python2_sitearch}/samba/dckeytab.so
%{python2_sitearch}/samba/dsdb.so
%{python2_sitearch}/samba/dsdb_dns.so
%{python2_sitearch}/samba/dnsserver.py*
%{python2_sitearch}/samba/forest_update.py*
%{python2_sitearch}/samba/gpclass.py*
%{python2_sitearch}/samba/gpo.so
%{python2_sitearch}/samba/ms_forest_updates_markdown.py*
%{python2_sitearch}/samba/ms_schema_markdown.py*
%{python2_sitearch}/samba/samdb.py*
%{python2_sitearch}/samba/schema.py*
%{python2_sitearch}/samba/uptodateness.py*

%{python2_sitearch}/samba/gp_ext_loader.py*
%{python2_sitearch}/samba/gp_parse/
%{python2_sitearch}/samba/gp_sec_ext.py*
%{python2_sitearch}/samba/kcc/
%{python2_sitearch}/samba/provision/
%{python2_sitearch}/samba/web_server/
%endif

%files python-test
%defattr(-,root,root,-)
%{python2_sitearch}/samba/tests/

### TEST
%files test
%defattr(-,root,root)
%{_bindir}/gentest
%{_bindir}/locktest
%{_bindir}/masktest
%{_bindir}/ndrdump
%{_bindir}/smbtorture
%{_mandir}/man1/gentest.1*
%{_mandir}/man1/locktest.1*
%{_mandir}/man1/masktest.1*
%{_mandir}/man1/ndrdump.1*
%{_mandir}/man1/smbtorture.1*
%{_mandir}/man1/vfstest.1*

%if %{with testsuite}
# files to ignore in testsuite mode
%{_libdir}/samba/libnss-wrapper.so
%{_libdir}/samba/libsocket-wrapper.so
%{_libdir}/samba/libuid-wrapper.so
%endif

### TEST-LIBS
%files test-libs
%defattr(-,root,root)
%if %with_dc
%{_libdir}/samba/libdlz-bind9-for-torture-samba4.so
%else
%{_libdir}/samba/libdsdb-module-samba4.so
%endif

### WINBIND
%files winbind
%defattr(-,root,root)
%{_libdir}/samba/idmap
%{_libdir}/samba/nss_info
%{_libdir}/samba/libnss-info-samba4.so
%{_libdir}/samba/libidmap-samba4.so
%{_sbindir}/winbindd
%attr(750,root,wbpriv) %dir /var/lib/samba/winbindd_privileged
%{_unitdir}/winbind.service
%{_sysconfdir}/NetworkManager/dispatcher.d/30-winbind
%{_mandir}/man8/winbindd.8*
%{_mandir}/man8/idmap_*.8*

### WINBIND-CLIENTS
%files winbind-clients
%defattr(-,root,root)
%{_bindir}/ntlm_auth
%{_bindir}/wbinfo
%if %with_mitkrb5
%{_libdir}/samba/krb5/winbind_krb5_localauth.so
%{_mandir}/man8/winbind_krb5_localauth.8*
%endif
%{_mandir}/man1/ntlm_auth.1.gz
%{_mandir}/man1/wbinfo.1*

### WINBIND-KRB5-LOCATOR
%files winbind-krb5-locator
%defattr(-,root,root)
%ghost %{_libdir}/krb5/plugins/libkrb5/winbind_krb5_locator.so
%{_libdir}/samba/krb5/winbind_krb5_locator.so
%{_mandir}/man8/winbind_krb5_locator.8*

### WINBIND-MODULES
%files winbind-modules
%defattr(-,root,root)
%{_libdir}/libnss_winbind.so*
%{_libdir}/libnss_wins.so*
%{_libdir}/security/pam_winbind.so
%config(noreplace) %{_sysconfdir}/security/pam_winbind.conf
%{_mandir}/man5/pam_winbind.conf.5*
%{_mandir}/man8/pam_winbind.8*

%if %{with clustering}
%files -n ctdb
%defattr(-,root,root)
%doc ctdb/README
# Obsolete
%config(noreplace, missingok) %{_sysconfdir}/sysconfig/ctdb

%dir %{_sysconfdir}/ctdb
%config(noreplace) %{_sysconfdir}/ctdb/ctdb.conf
%config(noreplace) %{_sysconfdir}/ctdb/notify.sh
%config(noreplace) %{_sysconfdir}/ctdb/debug-hung-script.sh
%config(noreplace) %{_sysconfdir}/ctdb/ctdb-crash-cleanup.sh
%config(noreplace) %{_sysconfdir}/ctdb/debug_locks.sh

%{_sysconfdir}/ctdb/functions
%{_sysconfdir}/ctdb/nfs-linux-kernel-callout
%{_sysconfdir}/ctdb/statd-callout
%config %{_sysconfdir}/sudoers.d/ctdb

# CTDB scripts, no config files
# script with executable bit means activated
%{_sysconfdir}/ctdb/events/

# CTDB scripts, no config files
# script with executable bit means activated
%dir %{_sysconfdir}/ctdb/nfs-checks.d
%{_sysconfdir}/ctdb/nfs-checks.d/README
%config(noreplace) %{_sysconfdir}/ctdb/nfs-checks.d/00.portmapper.check
%config(noreplace) %{_sysconfdir}/ctdb/nfs-checks.d/10.status.check
%config(noreplace) %{_sysconfdir}/ctdb/nfs-checks.d/20.nfs.check
%config(noreplace) %{_sysconfdir}/ctdb/nfs-checks.d/30.nlockmgr.check
%config(noreplace) %{_sysconfdir}/ctdb/nfs-checks.d/40.mountd.check
%config(noreplace) %{_sysconfdir}/ctdb/nfs-checks.d/50.rquotad.check

%{_sbindir}/ctdbd
%{_sbindir}/ctdbd_wrapper
%{_bindir}/ctdb
%{_bindir}/ctdb_local_daemons
%{_bindir}/ping_pong
%{_bindir}/ltdbtool
%{_bindir}/ctdb_diagnostics
%{_bindir}/onnode
%{_libexecdir}/ctdb/

%dir %{_localstatedir}/lib/ctdb/

%{_mandir}/man1/ctdb.1.gz
%{_mandir}/man1/ctdb_diagnostics.1.gz
%{_mandir}/man1/ctdbd.1.gz
%{_mandir}/man1/onnode.1.gz
%{_mandir}/man1/ltdbtool.1.gz
%{_mandir}/man1/ping_pong.1.gz
%{_mandir}/man1/ctdbd_wrapper.1.gz
%{_mandir}/man5/ctdb.conf.5.gz
%{_mandir}/man5/ctdb-script.options.5.gz
%{_mandir}/man5/ctdb.sysconfig.5.gz
%{_mandir}/man7/ctdb.7.gz
%{_mandir}/man7/ctdb-tunables.7.gz
%{_mandir}/man7/ctdb-statistics.7.gz

%{_tmpfilesdir}/ctdb.conf

%{_unitdir}/ctdb.service

%{_datadir}/ctdb/events

%files -n ctdb-tests
%defattr(-,root,root)
%doc ctdb/tests/README
%{_bindir}/ctdb_run_tests
%{_bindir}/ctdb_run_cluster_tests
%{_libexecdir}/ctdb/tests/
%{_datadir}/ctdb/tests/

%endif # with_clustering_support

%changelog
* Fri Jan 24 2020 Sérgio Basto <sergio@serjux.com> - 3:4.10.13-1
- Samba-4.10.13

* Thu Jan 23 2020 Sérgio Basto <sergio@serjux.com> - 3:4.10.12-1
- Samba-4.10.12

* Wed Dec 04 2019 Sérgio Basto <sergio@serjux.com> - 3:4.10.10-3
- Disable deps with krb5-server

* Thu Nov 28 2019 Sérgio Basto <sergio@serjux.com> - 3:4.10.10-2
- Provides/Obsoletes ldb-tools

* Wed Nov 27 2019 Sérgio Basto <sergio@serjux.com> - 3:4.10.10-1
- Samba-4.10.10

* Thu Oct 17 2019 Sérgio Basto <sergio@serjux.com> - 3:4.10.9-1
- New upstream version
- More simplifications in spec file

* Mon Oct 14 2019 Sérgio Basto <sergio@serjux.com> - 3:4.10.8-1
- Update to 4.10.8

* Sat Oct 12 2019 sergio@serjux.com - 1:4.8.12-1
- Update to 4.8.12
- use python2 instead python

* Fri Apr 12 2019 Sérgio Basto <sergio@serjux.com> - 1:4.8.11-2
- Enable HAVE_JSON_OBJECT

* Thu Apr 11 2019 Sérgio Basto <sergio@serjux.com> - 1:4.8.11-1
- Update to 4.8.11

* Thu Feb 21 2019 Sérgio Basto <sergio@serjux.com> - 1:4.8.8-3
- Review ldb modules rhbz #1497018, the quick fix is:
  ln -s /usr/lib64/ldb/modules/ldb/memberof.so /usr/lib64/samba/ldb/

* Fri Dec 21 2018 Sérgio Basto <sergio@serjux.com> - 1:4.8.8-2
- Disable MIT Kerberos still expermental, still have limitations and issues

* Thu Dec 20 2018 Sérgio Basto <sergio@serjux.com> - 1:4.8.8-1
- Update to 4.8.8

* Thu Dec 20 2018 Sérgio Basto <sergio@serjux.com> - 1:4.8.6-2
- With new compat-gnutls34

* Thu Nov 15 2018 Sérgio Basto <sergio@serjux.com> - 1:4.8.6-1
- Sync with F28 and Samba 4.8.6

* Fri Jun 22 2018 Sérgio Basto <sergio@serjux.com> - 1:4.7.7-1
- With samba-dc, requires gnutls-3.4.17 which may break a lot rpm deps.

* Wed Dec 20 2017 Andreas Schneider <asn@redhat.com> - 4.7.1-6
- resolves: #1476153 - Handle SMB echo responses more gracefully
- resolves: #1523212 - Fix SMB2 client read-after-free issue

* Mon Dec 04 2017 Andreas Schneider <asn@redhat.com> - 4.7.1-5
- resolves: #1505940 - Fix 'net ads keytab list'
- resolves: #1518732 - Enable AES-NI to make SMB3 encryption and signing
                       faster

* Tue Nov 28 2017 Andreas Schneider <asn@redhat.com> - 4.7.1-4
- resolves: #1510872 - Fix systemd startup of samba daemons

* Thu Nov 23 2017 Andreas Schneider <asn@redhat.com> - 4.7.1-3
- resolves: #1498353 - Fix broken MacOSX client which can't handle file_ids
                       correctly
- resolves: #1495490 - Fix client rename over SMB2
- resolves: #1510598 - Fix client volume cmd over SMB2

* Fri Nov 17 2017 Andreas Schneider <asn@redhat.com> - 4.7.1-2
- resolves: #1514316 - CVE-2017-14746 CVE-2017-15275

* Thu Nov 02 2017 Andreas Schneider <asn@redhat.com> - 4.7.1-1
- related: #1470048 - Update to version 4.7.1

* Thu Oct 26 2017 Andreas Schneider <asn@redhat.com> - 4.7.0-4
- resolves: #1506489 - Fix python dependency issues

* Wed Oct 25 2017 Andreas Schneider <asn@redhat.com> - 4.7.0-3
- related: #1470048 - Fix dependency issues
- resolves: #1486318 - Move /var/lib/samba/lock to common package
- resolves: #1497162 - Fix smbcacls command line password handling

* Tue Oct 24 2017 Andreas Schneider <asn@redhat.com> - 4.7.0-2
- related: #1470048 - Fix package names

* Mon Oct 23 2017 Andreas Schneider <asn@redhat.com> - 4.7.0-1
- resolves: #1470048 - Rebase Samba to version 4.7.0
- resolves: #1335710 - Improve performance of smbd for a lot
                       of new client connections

* Thu Sep 14 2017 Andreas Schneider <asn@redhat.com> - 4.6.2-11
- resolves: #1491214 - CVE-2017-12150 CVE-2017-12151 CVE-2017-12163

* Wed Aug 23 2017 Andreas Schneider <asn@redhat.com> - 4.6.2-10
- resolves: #1480310 - Require at least krb5 version 1.15.1
- resolves: #1482133 - Fix password changes for users via smbpasswd
- resolves: #1452003 - Be more graceful on FSCTL_VALIDATE_NEGOTIATE_INFO
                       returned errors
- resolves: #1485390 - Do not print kerberos warning when not enforced

* Mon Aug 14 2017 Andreas Schneider <asn@redhat.com> - 4.6.2-9
- resolves: #1479897 - Fix 'net ads changetrustpw'

* Thu Jun 22 2017 Andreas Schneider <asn@redhat.com> - 4.6.2-8
- resolves: #1459936 - Fix regression with "follow symlinks = no"

* Tue Jun 20 2017 Andreas Schneider <asn@redhat.com> - 4.6.2-7
- resolves: #1461336 - Fix smbclient username parsing
- resolves: #1460937 - Fix username normalization with winbind

* Tue Jun 13 2017 Andreas Schneider <asn@redhat.com> - 4.6.2-6
- resolves: #1459179 - Fix smbclient session setup printing

* Wed Jun 07 2017 Andreas Schneider <asn@redhat.com> - 4.6.2-5
- related: #1277999 - Add missing patchset

* Wed May 31 2017 Andreas Schneider <asn@redhat.com> - 4.6.2-4
- resolves: #1431986 - Fix expand_msdfs VFS module

* Thu May 18 2017 Guenther Deschner <gdeschner@redhat.com> - 4.6.2-3
- resolves: #1450785 - Security fix for CVE-2017-7494

* Tue May 09 2017 Andreas Schneider <asn@redhat.com> - 4.6.2-2
- resolves: #1448544 - Fix spoolss 32bit driver upload

* Mon Apr 03 2017 Andreas Schneider <asn@redhat.com> - 4.6.2-1
- resolves: #1435734 - Fix refreshing winbind tickets

* Fri Mar 31 2017 Guenther Deschner <gdeschner@redhat.com> - 4.6.2-0
- Update to Samba 4.6.2
- related: #1430260 - Security fix for CVE-2017-2619

* Thu Mar 23 2017 Guenther Deschner <gdeschner@redhat.com> - 4.6.1-0
- Update to Samba 4.6.1
- resolves: #1430260 - Security fix for CVE-2017-2619

* Tue Mar 21 2017 Andreas Schneider <asn@redhat.com> - 4.6.0-5
- related: #1391954 - Fix kerberos cross-realm referrals
- resolves: #1430755 - Fix 'net ads' keytab handling

* Wed Mar 15 2017 Alexander Bokovoy <abokovoy@redhat.com> - 4.6.0-4
- Export internal arcfour_crypt_blob in Python as samba.arcfour_encrypt
- related: #1391954 - Update to Samba 4.6.0

* Fri Mar 10 2017 Alexander Bokovoy <abokovoy@redhat.com> - 4.6.0-3
- Ensure we set realm when updating ccache in auth/credentials
- resolves: #1430759 - use GSSAPI gss_acquire_cred_from call for gssproxy support

* Fri Mar 10 2017 Alexander Bokovoy <abokovoy@redhat.com> - 4.6.0-2
- resolves: #1430759 - use GSSAPI gss_acquire_cred_from call for gssproxy support

* Tue Mar 07 2017 Andreas Schneider <asn@redhat.com> - 4.6.0-1
- related: #1391954 - Update to Samba 4.6.0
- resolves: #1401505 - Improved idmap_hash documentation
- resolves: #1218926 - Samba ignores default_keytab_name in krb5.conf
- resolves: #1389786 - Add 'net ads dns unregister'

* Thu Mar 02 2017 Andreas Schneider <asn@redhat.com> - 4.6.0-0.1.rc4
- related: #1391954 - Update to Samba 4.6.0rc4
- resolves: #1420130 - samba_krb5_wrapper does not list devices when called with
                       no arguments
- resolves: #1277999 - Change RPC port range to Windows defaults

* Wed Feb 15 2017 Andreas Schneider <asn@redhat.com> - 4.6.0-0.1.rc3
- resolves: #1391954 - Update to Samba 4.6.0rc3
- resolves: #1271082 - Wrong groups listed when id command is called before login
- resolves: #1327810 - Use 'printcap cache time' for the house keeping interval
- resolves: #1356932 - Improve documentation for 'ldap ssl' in smb.conf manpage
- resolves: #1365111 - Fix printer removal if "List in Directory" checkbox is
                       unticked and printer is not listed in AD
- resolves: #1368439 - Fix ntlm_auth wrong password issues
- resolves: #1397871 - Include the system krb5.conf in winbinds generated conf
- resolves: #1397891 - Fix marsalling of spoolss SetPrinter info level 2
- resolves: #1397895 - Add missing support APD_COPY_FROM_DIRECTORY in
                       AddPrinterDriver
- resolves: #1403242 - Samba can not access trusted domains through transitive
                       trusts
- resolves: #1403975 - Fix trusted domain logins
- resolves: #1411978 - Include the system krb5.conf in winbinds generated conf
- resolves: #1416746 - Fix division by zero error in ctdb 05.system event script

* Tue Nov 15 2016 Andreas Schneider <asn@redhat.com> - 4.4.4-11
- related: #1377729 - Fix return code if ip not defined in gethostbyname

* Wed Nov 09 2016 Andreas Schneider <asn@redhat.com> - 4.4.4-11
- related: #1377307 - Add missing patch to patchset

* Tue Nov 08 2016 Andreas Schneider <asn@redhat.com> - 4.4.4-10
- resolves: #1377690 - Fix linking nss_wins with libreplace
- resolves: #1377729 - Fix nss_wins function definitions for gethostbyname*
- resolves: #1377307 - Fix %G substitution in AD case
- resolves: #1377751 - Fix regression of smbclient unable to connect to
                       Apple and Azure

* Wed Aug 31 2016 Andreas Schneider <asn@redhat.com> - 4.4.4-9
- related: #1365479 - Fix idmap range check

* Fri Aug 26 2016 Andreas Schneider <asn@redhat.com> - 4.4.4-8
- related: #1193493 - Fix smbget url credentials parsing

* Tue Aug 23 2016 Andreas Schneider <asn@redhat.com> - 4.4.4-7
- resolves: #1365479 - Fix idmap range checks for ad and hash backend

* Tue Aug 16 2016 Andreas Schneider <asn@redhat.com> - 4.4.4-6
- resolves: #1367316 - Increase required Kerbersion version number
- resolves: #1366477 - Fix using the right krb5 ccache in libads
- resolves: #1356501 - Fix high CPU usage with smbclient connection to
                       non-reachable IP

* Wed Aug 03 2016 Andreas Schneider <asn@redhat.com> - 4.4.4-5
- resolves: #1359091 - Package /usr/lib/samba/ldb in the common-libs package
- resolves: #1360788 - Fix multilib issue with ctdb-tests package
- resolves: #1362385 - Fix Samba ignoring supplementary groups
- resolves: #1364051 - Fix smbd panic with stale ctdb entries

* Mon Jul 04 2016 Andreas Schneider <asn@redhat.com> - 4.4.4-4
- resolves: #1351655 - Fix winbind meomory leak with each cached credentials
                       login
- resolves: #1351961 - Fix CVE-2016-2119

* Thu Jun 23 2016 Andreas Schneider <asn@redhat.com> - 4.4.4-3
- related: #1260214 - Correctly warn about missing realm for ad domains
                      with 'security=domain'

* Tue Jun 21 2016 Andreas Schneider <asn@redhat.com> - 4.4.4-2
- resolves: #1348223 - Fix sasl wrapped ldap connections

* Wed Jun 08 2016 Andreas Schneider <asn@redhat.com> - 4.4.4-1
- resolves: #1303076 - Rebase Samba to version 4.4.4
- resolves: #1314673 - Fix CVE-2015-7560
- resolves: #1263322 - Add '--no-dns-updates' option to 'net ads join'
- resolves: #1264433 - Fix segfault in pam_winbind.so with invalid config
                       options
- resolves: #1193504 - Fix smbget to retrieve files recursively
- resolves: #1193502 - Fix smbget to use command line credentials
- resolves: #1193493 - Fix smbget url credentials parsing
- resolves: #1273999 - Support printing with Kerberos credentials on newer
                       CUPS versions
- resolves: #1296821 - Define /etc/pam.d/samba as a non replaceable config
- resolves: #1261107 - Fix memory leak because of missing talloc stackframe
- resolves: #1333562 - Fix memory leak after smbc_free_context()
- resolves: #1315422 - Fix regression from CVE-2015-5252
- resolves: #1316899 - Fixed idmap_hash module issues when used with others
- resolves: #1322691 - Fix badlock related bugs
- Fix CVE-2015-5370
- Fix CVE-2016-2110
- Fix CVE-2016-2111
- Fix CVE-2016-2112
- Fix CVE-2016-2113
- Fix CVE-2016-2114
- Fix CVE-2016-2115
- Fix CVE-2016-2118
- resolves: #1327951 - Fix regression with anonymous connections from OS X
- resolves: #1327845 - Fix pcap_cache_reload() with spoolssd
- resolves: #1289640 - Fix ctdb selinux issue with read only tracking dbs
- resolves: #1341208 - Fix enumerating groups over NSS with idmap_ad
- resolves: #1345827 - Fix resolving trusted domain users on domain member
- resolves: #1346334 - Fix typo in smb.conf.example
- resolves: #1335292 - Fix site-aware 'net ads join -k'
- resolves: #1260214 - Accept empty realm for ad domains with 'security=domain'

* Tue May 24 2016 Guenther Deschner <gdeschner@redhat.com> - 4.2.10-8
- Fix krb5 encryption type setup during join (as admin and non-admin user)
- resolves: #1312109

* Mon May 02 2016 Alexander Bokovoy <abokovoy@redhat.com> - 4.2.10-7
- Fix regressions introduced with security tightening as part of Badlock release
- resolves: #1330199

* Tue Apr 12 2016 Alexander Bokovoy <abokovoy@redhat.com> - 4.2.10-6
- Fix domain member winbind not being able to talk to trusted domains' DCs
- relates: #1322691

* Mon Apr 11 2016 Alexander Bokovoy <abokovoy@redhat.com> - 4.2.10-5
- Fix crash in smb.conf processing
- relates: #1322691

* Fri Apr 08 2016 Alexander Bokovoy <abokovoy@redhat.com> - 4.2.10-4
- Fix LDAP SASL bind with arcfour-hmac-md5
- resolves: #1322691

* Thu Apr 07 2016 Alexander Bokovoy <abokovoy@redhat.com> - 4.2.10-3
- Make sure the package owns /var/lib/samba and uses it for cache purposes
- resolves: #1322691

* Wed Apr 06 2016 Alexander Bokovoy <abokovoy@redhat.com> - 4.2.10-2
- Remove ldb modules and internal libraries for DC when not packaging DC build
- resolves: #1322691

* Mon Apr 04 2016 Alexander Bokovoy <abokovoy@redhat.com> - 4.2.10-1
- resolves: #1322691

* Fri Mar 04 2016 Andreas Schneider <asn@redhat.com> - 4.2.3-12
- resolves: #1314673 - Fix CVE-2015-7560

* Fri Dec 11 2015 Guenther Deschner <gdeschner@redhat.com> - 4.2.3-11
- resolves: #1290711
- CVE-2015-3223 Remote DoS in Samba (AD) LDAP server
- CVE-2015-5299 Missing access control check in shadow copy code
- CVE-2015-5252 Insufficient symlink verification in smbd
- CVE-2015-5296 Samba client requesting encryption vulnerable to
                downgrade attack

* Tue Oct 27 2015 Andreas Schneider <asn@redhat.com> - 4.2.3-10
- related: #1273393 - Fix use after free with nss_wins module loaded

* Thu Oct 22 2015 Andreas Schneider <asn@redhat.com> - 4.2.3-9
- resolves: #1273912 - Fix dependencies to samba-common
- resolves: #1273393 - Fix user after free in smb name resolution

* Wed Oct 21 2015 Andreas Schneider <asn@redhat.com> - 4.2.3-8
- resolves: #1271608 - Fix upgrade path from previous rhel version

* Tue Sep 01 2015 Andreas Schneider <asn@redhat.com> - 4.2.3-7
- resolves: #1258293 - Fix quota on XFS filesystems

* Mon Aug 24 2015 Andreas Schneider <asn@redhat.com> - 4.2.3-6
- resolves: #1255322 - Fix 'map to guest = Bad uid' option
- resolves: #1255326 - Fix segfault with 'mangling method = hash'

* Wed Aug 19 2015 Andreas Schneider <asn@redhat.com> - 4.2.3-5
- resolves: #1253193 - Fix 'force group'

* Wed Jul 29 2015 Andreas Schneider <asn@redhat.com> - 4.2.3-4
- resolves: #1246166 - Fix a 'net ads keytab' segfault

* Tue Jul 21 2015 Andreas Schneider <asn@redhat.com> - 4.2.3-3
- resolves: #1225719 - Fix possible segfault if we can't connect to the DC

* Mon Jul 20 2015 Andreas Schneider <asn@redhat.com> - 4.2.3-2
- resolves: #1238194 - Fix the 'dfree command'
- resolves: #1216062 - Document netbios name length limitation

* Tue Jul 14 2015 Andreas Schneider <asn@redhat.com> - 4.2.3-1
- related: #1196140 - Rebase to version 4.2.3
- resolves: #1237036 - Fix DCERPC PDU calculation
- resolves: #1237039 - Fix winbind request cancellation
- resolves: #1223981 - Fix possible segfault with smbX protocol setting

* Mon Jun 22 2015 Andreas Schneider <asn@redhat.com> - 4.2.2-3
- resolves: #1228809 - Allow reauthentication without signing

* Thu Jun 18 2015 Andreas Schneider <asn@redhat.com> - 4.2.2-2
- related: #1196140 - Add missing build dependency for libarchive
- related: #1196140 - Make sure we do a hardened build

* Wed Jun 17 2015 Andreas Schneider <asn@redhat.com> - 4.2.2-1
- resolves: #1196140 - Rebase Samba to version 4.2.2
- resolves: #1186403 - Split patches to fix multiarch conflicts
- resolves: #1167325 - Retrieve printer GUID from AD if it is not in the
                       registry
- resolves: #1220174 - Fix issues with winbind library dependencies
- resolves: #1211658 - Fix stale cache entries on printer rename
- resolves: #1228809 - Fix reconnect on session exparation

* Tue May 12 2015 - Guenther Deschner <gdeschner@redhat.com> - 4.1.12-22
- resolves: #1202347 - Fix NETLOGON authentication without winbindd.

* Thu Apr 09 2015 Andreas Schneider <asn@redhat.com> - 4.1.12-21
- related: #1205703 - Rebuild Samba with new binutils package.

* Thu Apr 02 2015 Andreas Schneider <asn@redhat.com> - 4.1.12-20
- resolves: #1205703 - Fix build with RELRO support.

* Mon Feb 16 2015 - Guenther Deschner <gdeschner@redhat.com> - 4.1.12-19
- related: #1191341 - Update patchset for CVE-2015-0240.

* Thu Feb 12 2015 - Guenther Deschner <gdeschner@redhat.com> - 4.1.12-18
- resolves: #1191341 - CVE-2015-0240: RCE in netlogon server.

* Fri Jan 09 2015 - Andreas Schneider <asn@redhat.com> - 4.1.12-17
- related: #1177768 - Add missing requires to libwbclient.

* Thu Jan 08 2015 Andreas Schneider <asn@redhat.com> - 4.1.12-16
- related: #1177768 - Add missing requires to libwbclient.

* Thu Jan 08 2015 Andreas Schneider <asn@redhat.com> - 4.1.12-15
- resolves: #1177768 - Fix possible segfault with 'net ads kerberos pac dump'.

* Tue Dec 16 2014 - Andreas Schneider <asn@redhat.com> - 4.1.12-14
- resolves: #1171689 - Fix smbstatus if executed as user to print error message.

* Fri Dec 12 2014 - Andreas Schneider <asn@redhat.com> - 4.1.12-13
- resolves: #1172089 - Fix 'net rpc join' with schannel changes.
- resolves: #1170883 - Fix 'net time system' segfault.

* Tue Nov 25 2014 - Andreas Schneider <asn@redhat.com> - 4.1.12-12
- related: #1162526 - Fix multilib with using alternatives for libwbclient.

* Tue Nov 25 2014 - Andreas Schneider <asn@redhat.com> - 4.1.12-11
- resolves: #1163748 - Fix smbclient -L fails against new Windows versions
                       over TCP.
- resolves: #1167849 - Fix smbstatus --profile always returning EXIT_FAILURE.

* Thu Nov 20 2014 - Andreas Schneider <asn@redhat.com> - 4.1.12-10
- related: #1162526 - Fix multilib with using alternatives for libwbclient.

* Thu Nov 20 2014 - Andreas Schneider <asn@redhat.com> - 4.1.12-9
- resolves: #1162552 - Fix net ads join segfault on big endian systems.
- resolves: #1164203 - Fix net ads join segfault with existing keytab.

* Thu Nov 13 2014 - Guenther Deschner <gdeschner@redhat.com> - 4.1.12-8
- related: #1162526 - Fix multilib issues when using alternatives for libwbclient.

* Wed Nov 12 2014 - Andreas Schneider <asn@redhat.com> - 4.1.12-7
- resolves: #1162526 - Use alternatives for libwbclient.

* Mon Nov 03 2014 - Andreas Schneider <asn@redhat.com> - 4.1.12-6
- related: #1156391 - Fix netbios name truncation during registration.

* Wed Oct 29 2014 - Andreas Schneider <asn@redhat.com> - 4.1.12-5
- resolves: #1156391 - Fix netbios name truncation during registration.

* Thu Oct 09 2014 - Guenther Deschner <gdeschner@redhat.com> - 4.1.12-4
- related: #1117770 - Fix empty full_name field with samlogon.

* Fri Sep 26 2014 - Guenther Deschner <gdeschner@redhat.com> - 4.1.12-3
- resolves: #878351 - Fix usage of AES keys by default.
- resolves: #861366 - Fix KRB5 locator to use same KDC for joining and DNS update.

* Tue Sep 16 2014 - Andreas Schneider <asn@redhat.com> - 4.1.12-2
- resolves: #1138554 - Fix consuming a lot of CPU when re-reading printcap info.
- resolves: #1134323 - Fix running Samba on little endian Power8 (ppc64le).
- resolves: #1113064 - Fix case sensitivity options with SMB2 protocols.
- resolves: #1088924 - Fix applying ACL masks when setting ACLs.
- resolves: #1135723 - Fix 'force user' regression.
- resolves: #1117770 - Fix empty full_name field with samlogon.
- resolves: #1101210 - Fix telling systemd that nmbd is waiting for interfaces.
- resolves: #1127931 - Fix getgroups() with idmap_ad returning non-mapped groups.
- resolves: #1144963 - Fix idmap_ad with SFU against trusted domains.
- resolves: #1140568 - Fix a segfault in the smbclient echo command.
- resolves: #1089940 - Improve service principal guessing in 'net ads'.
- resolves: #955561 - Fix overwriting of SPNs in AD during 'net ads join'.
- resolves: #955562 - Add precreated SPNS from AD during keytab initialization.

* Mon Sep 08 2014 - Andreas Schneider <asn@redhat.com> - 4.1.12-1
- related: #1110820 - Rebase Samba to latest release.

* Tue Aug 26 2014 - Andreas Schneider <asn@redhat.com> - 4.1.11-1
- resolves: #1110820 - Rebase Samba to latest release.

* Mon Aug 25 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-37
- resolves: #1072352 - Make pidl a noarch subpackage.
- resolves: #1133516 - Create a samba-test-libs package.
- resolves: #1132873 - Add support to rebuild without clustering.

* Fri Aug 01 2014 - Guenther Deschner <gdeschner@redhat.com> - 4.1.1-36
- resolves: #1126014 - CVE-2014-3560: remote code execution in nmbd.

* Wed Jul 02 2014 - Guenther Deschner <gdeschner@redhat.com> - 4.1.1-35
- resolves: #1115060 - Fix potential Samba file corruption.

* Wed Jun 11 2014 - Guenther Deschner <gdeschner@redhat.com> - 4.1.1-34
- resolves: #1105505 - CVE-2014-0244: DoS in nmbd.
- resolves: #1108845 - CVE-2014-3493: DoS in smbd with unicode path names.
- resolves: #1105574 - CVE-2014-0178: Uninitialized memory exposure.

* Mon May 05 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-33
- related: #717484 - Add missing configure line to enable profiling data support.

* Tue Apr 22 2014 - Guenther Deschner <gdeschner@redhat.com> - 4.1.1-32
- related: #1082653 - Reuse IPv6 address during the AD domain join.

* Thu Apr 03 2014 - Guenther Deschner <gdeschner@redhat.com> - 4.1.1-31
- resolves: #1082653 - Add IPv6 workaround for MIT kerberos.

* Thu Apr 03 2014 - Alexander Bokovoy <abokovoy@redhat.com> - 4.1.1-30
- resolves: #1083859  - Force KRB5CCNAME in Samba systemd units.
- related: #1082598 - Fully enables systemd integration.

* Tue Apr 01 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-29
- resolves: #1082598 - Add missing BuildRequires for systemd-devel.

* Wed Mar 26 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-28
- resolves: #1077918 - Make daemons systemd aware.

* Mon Mar 24 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-27
- resolves: #1077857 - Fix internal error received while adding trust.

* Fri Mar 21 2014 - Guenther Deschner <gdeschner@redhat.com> - 4.1.1-26
- resolves: #1079008 - Fix fragmented rpc handling.

* Tue Mar 18 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-25
- resolves: #1077651 - Fix 'force user' option for shares.

* Wed Mar 12 2014 - Guenther Deschner <gdeschner@redhat.com> - 4.1.1-24
- resolves: #1053748 - Enhance "net ads kerberos pac" tool.

* Mon Mar 10 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-23
- resolves: #1072804 - Fix CVE-2013-4496.
- resolves: #1072804 - Fix CVE-2013-6442.

* Fri Mar 07 2014 - Guenther Deschner <gdeschner@redhat.com> - 4.1.1-22
- resolves: #1024788 - Fix joining over IPv6.

* Tue Mar 04 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-21
- resolves: #1066536 - Fix NBT queries with more than 9 or more components.

* Thu Feb 27 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-20
- resolves: #1070692 - Don't package perl(Parse::Yapp::Driver)

* Tue Feb 25 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-19
- related: #1067606 - Add missing directories.

* Tue Feb 25 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-18
- related: #1067606 - Fix installation of pidl files.

* Tue Feb 25 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-17
- resolves: #1067606 - Fix wbinfo with one-way trust.
- resolves: #1069569 - Fix memory leak reading the printer list.

* Thu Feb 20 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-16
- resolves: #1063186 - Fix force_user with security=ads.

* Wed Feb 05 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-15
- resolves: #1029001 - Fix force_user with security=ads.

* Tue Jan 28 2014 Daniel Mach <dmach@redhat.com> - 4.1.1-14
- Mass rebuild 2014-01-24

* Mon Jan 13 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-13
- resolves: #1051582 - Fix warnings an resource leaks reported by rpmdiff.

* Fri Jan 10 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-12
- resolves: #1050886 - Fix full CPU utilization in winbindd.
- resolves: #1051400 - Fix segfault in smbd.
- resolves: #1051402 - Fix SMB2 server panic when a smb2 brlock times out.

* Thu Jan 09 2014 - Andreas Schneider <asn@redhat.com> - 4.1.1-11
- resolves: #1042845 - Do not build with libbsd.

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 4.1.1-10
- Mass rebuild 2013-12-27

* Wed Dec 11 2013 - Andreas Schneider <asn@redhat.com> - 4.1.1-9
- resolves: #1033122 - Fix dropbox regression.
- resolves: #1040464 - Fix %G substituion for config parameters.

* Wed Dec 11 2013 - Guenther Deschner <gdeschner@redhat.com> - 4.1.1-8
- resolves: #1040052 - Fix winbind debug message NULL pointer derreference.

* Mon Dec 09 2013 - Andreas Schneider <asn@redhat.com> - 4.1.1-7
- resolves: #1039499 - Fix CVE-2012-6150.

* Fri Nov 29 2013 - Guenther Deschner <gdeschner@redhat.com> - 4.1.1-6
- resolves: #1033109 - Fix winbind cache keysize limitations.

* Wed Nov 27 2013 - Andreas Schneider <asn@redhat.com> - 4.1.1-5
- resolves: #1034160 - Make sure we don't build the fam notify module.

* Mon Nov 25 2013 - Andreas Schneider <asn@redhat.com> - 4.1.1-4
- resolves: #1034048 - Fix group name substitution in template homedir.
- resolves: #1018041 - Fix CVE-2013-4408.
- related: #884169 - Fix several covscan warnings.

* Mon Nov 18 2013 - Guenther Deschner <gdeschner@redhat.com> - 4.1.1-3
- resolves: #948509 - Fix manpage correctness.

* Fri Nov 15 2013 - Andreas Schneider <asn@redhat.com> - 4.1.1-2
- related: #884169 - Fix strict aliasing warnings.

* Mon Nov 11 2013 - Andreas Schneider <asn@redhat.com> - 4.1.1-1
- resolves: #1024543 - Fix CVE-2013-4475.
- Update to Samba 4.1.1.

* Mon Nov 11 2013 - Andreas Schneider <asn@redhat.com> - 4.1.0-5
- related: #884169 - Fix the upgrade path.

* Wed Oct 30 2013 - Andreas Schneider <asn@redhat.com> - 4.1.0-4
- related: #884169 - Add direct dependency to samba-libs in the
                     glusterfs package.
- resolves: #996567 - Fix userPrincipalName composition.
- related: #884169 - Fix memset call with zero length in in ntdb.

* Fri Oct 18 2013 - Andreas Schneider <asn@redhat.com> - 4.1.0-3
- resolves: #1019384 - Build glusterfs VFS plguin.

* Tue Oct 15 2013 - Andreas Schneider <asn@redhat.com> - 4.1.0-2
- related: #1014656 - Fix dependency of samba-winbind-modules package.

* Fri Oct 11 2013 - Andreas Schneider <asn@redhat.com> - 4.1.0-1
- related: #985609 - Update to Samba 4.1.0.

* Tue Oct 01 2013 - Andreas Schneider <asn@redhat.com> - 2:4.1.0-0.8
- related: #985609 - Update to Samba 4.1.0rc4.
- resolves: #1014656 - Split out a samba-winbind-modules package.

* Wed Sep 11 2013 - Andreas Schneider <asn@redhat.com> - 2:4.1.0-0.7
- related: #985609 - Update to Samba 4.1.0rc3.
- resolves: #1005422 - Add support for KEYRING ccache type in pam_winbindd.

* Wed Sep 04 2013 - Andreas Schneider <asn@redhat.com> - 2:4.1.0-0.6
- resolves: #717484 - Enable profiling data support.

* Thu Aug 22 2013 - Guenther Deschner <gdeschner@redhat.com> - 2:4.1.0-0.5
- resolves: #996160 - Fix winbind with trusted domains.

* Wed Aug 14 2013 - Andreas Schneider <asn@redhat.com> 2:4.1.0-0.4
- resolves: #996160 - Fix winbind nbt name lookup segfault.

* Mon Aug 12 2013 - Andreas Schneider <asn@redhat.com> - 2:4.1.0-0.3
- related: #985609 - Update to Samba 4.1.0rc2.

* Wed Jul 24 2013 - Andreas Schneider <asn@redhat.com> - 2:4.1.0-0.2
- resolves: #985985 - Fix file conflict between samba and wine.
- resolves: #985107 - Add support for new default location for Kerberos
                      credential caches.

* Sat Jul 20 2013 Petr Pisar <ppisar@redhat.com> - 2:4.1.0-0.1.rc1.1
- Perl 5.18 rebuild

* Wed Jul 17 2013 - Andreas Schneider <asn@redhat.com> - 2:4.1.0-0.1
- Update to Samba 4.1.0rc1.
- resolves: #985609

* Mon Jul 15 2013 - Andreas Schneider <asn@redhat.com> - 2:4.0.7-2
- resolves: #972692 - Build with PIE and full RELRO.
- resolves: #884169 - Add explicit dependencies suggested by rpmdiff.
- resolves: #981033 - Local user's krb5cc deleted by winbind.
- resolves: #984331 - Fix samba-common tmpfiles configuration file in wrong
                      directory.

* Wed Jul 03 2013 - Andreas Schneider <asn@redhat.com> - 2:4.0.7-1
- Update to Samba 4.0.7.

* Fri Jun 07 2013 - Andreas Schneider <asn@redhat.com> - 2:4.0.6-3
- Add UPN enumeration to passdb internal API (bso #9779).

* Wed May 22 2013 - Andreas Schneider <asn@redhat.com> - 2:4.0.6-2
- resolves: #966130 - Fix build with MIT Kerberos.
- List vfs modules in spec file.

* Tue May 21 2013 - Andreas Schneider <asn@redhat.com> - 2:4.0.6-1
- Update to Samba 4.0.6.
- Remove SWAT.

* Wed Apr 10 2013 - Andreas Schneider <asn@redhat.com> - 2:4.0.5-1
- Update to Samba 4.0.5.
- Add UPN enumeration to passdb internal API (bso #9779).
- resolves: #928947 - samba-doc is obsolete now.
- resolves: #948606 - LogRotate should be optional, and not a hard "Requires".

* Fri Mar 22 2013 - Andreas Schneider <asn@redhat.com> - 2:4.0.4-3
- resolves: #919405 - Fix and improve large_readx handling for broken clients.
- resolves: #924525 - Don't use waf caching.

* Wed Mar 20 2013 - Andreas Schneider <asn@redhat.com> - 2:4.0.4-2
- resolves: #923765 - Improve packaging of README files.

* Wed Mar 20 2013 - Andreas Schneider <asn@redhat.com> - 2:4.0.4-1
- Update to Samba 4.0.4.

* Mon Mar 11 2013 - Andreas Schneider <asn@redhat.com> - 2:4.0.3-4
- resolves: #919333 - Create /run/samba too.

* Mon Mar 04 2013 - Andreas Schneider <asn@redhat.com> - 2:4.0.3-3
- Fix the cache dir to be /var/lib/samba to support upgrades.

* Thu Feb 14 2013 - Andreas Schneider <asn@redhat.com> - 2:4.0.3-2
- resolves: #907915 - libreplace.so => not found

* Thu Feb 07 2013 - Andreas Schneider <asn@redhat.com> - 2:4.0.3-1
- Update to Samba 4.0.3.
- resolves: #907544 - Add unowned directory /usr/lib64/samba.
- resolves: #906517 - Fix pidl code generation with gcc 4.8.
- resolves: #908353 - Fix passdb backend ldapsam as module.

* Wed Jan 30 2013 - Andreas Schneider <asn@redhat.com> - 2:4.0.2-1
- Update to Samba 4.0.2.
- Fixes CVE-2013-0213.
- Fixes CVE-2013-0214.
- resolves: #906002
- resolves: #905700
- resolves: #905704
- Fix conn->share_access which is reset between user switches.
- resolves: #903806
- Add missing example and make sure we don't introduce perl dependencies.
- resolves: #639470

* Wed Jan 16 2013 - Andreas Schneider <asn@redhat.com> - 2:4.0.1-1
- Update to Samba 4.0.1.
- Fixes CVE-2013-0172.

* Mon Dec 17 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-174
- Fix typo in winbind-krb-locator post uninstall script.

* Tue Dec 11 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-173
- Update to Samba 4.0.0.

* Thu Dec 06 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-171.rc6
- Fix typo in winbind-krb-locator post uninstall script.

* Tue Dec 04 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-170.rc6
- Update to Samba 4.0.0rc6.
- Add /etc/pam.d/samba for swat to work correctly.
- resolves #882700

* Fri Nov 23 2012 Guenther Deschner <gdeschner@redhat.com> - 2:4.0.0-169.rc5
- Make sure ncacn_ip_tcp client code looks for NBT_NAME_SERVER name types.

* Thu Nov 15 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-168.rc5
- Reduce dependencies of samba-devel and create samba-test-devel package.

* Tue Nov 13 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-167.rc5
- Use workaround for winbind default domain only when set.
- Build with old ctdb support.

* Tue Nov 13 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-166.rc5
- Update to Samba 4.0.0rc5.

* Mon Nov 05 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-165.rc4
- Fix library dependencies of libnetapi.

* Mon Nov 05 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-164.rc4
- resolves: #872818 - Fix perl dependencies.

* Tue Oct 30 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-163.rc4
- Update to Samba 4.0.0rc4.

* Mon Oct 29 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-162.rc3
- resolves: #870630 - Fix scriptlets interpeting a comment as argument.

* Fri Oct 26 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-161.rc3
- Add missing Requries for python modules.
- Add NetworkManager dispatcher script for winbind.

* Fri Oct 19 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-160.rc3
- resolves: #867893 - Move /var/log/samba to samba-common package for
                      winbind which requires it.

* Thu Oct 18 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-159.rc3
- Compile default auth methods into smbd.

* Tue Oct 16 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-158.rc3
- Move pam_winbind.conf and the manpages to the right package.

* Tue Oct 16 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-157.rc3
* resolves: #866959 - Build auth_builtin as static module.

* Tue Oct 16 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-156.rc3
- Update systemd Requires to reflect latest packaging guidelines.

* Tue Oct 16 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-155.rc3
- Add back the AES patches which didn't make it in rc3.

* Tue Oct 16 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-154.rc3
- Update to 4.0.0rc3.
- resolves: #805562 - Unable to share print queues.
- resolves: #863388 - Unable to reload smbd configuration with systemctl.

* Wed Oct 10 2012 - Alexander Bokovoy <abokovoy@redhat.com> - 2:4.0.0-153.rc2
- Use alternatives to configure winbind_krb5_locator.so
- Fix Requires for winbind.

* Thu Oct 04 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-152.rc2
- Add kerberos AES support.
- Fix printing initialization.

* Tue Oct 02 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-151.rc2
- Update to 4.0.0rc2.

* Wed Sep 26 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-150.rc1
- Fix Obsoletes/Provides for update from samba4.
- Bump release number to be bigger than samba4.

* Wed Sep 26 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-96.rc1
- Package smbprint again.

* Wed Sep 26 2012 - Andreas Schneider <asn@redhat.com> - 2:4.0.0-95.rc1
- Update to 4.0.0rc1.

* Mon Aug 20 2012 Guenther Deschner <gdeschner@redhat.com> - 2:3.6.7-94.2
- Update to 3.6.7

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2:3.6.6-93.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jul 19 2012 Guenther Deschner <gdeschner@redhat.com> - 2:3.6.6-93
- Fix printing tdb upgrade for 3.6.6
- resolves: #841609

* Sun Jul 15 2012 Ville Skyttä <ville.skytta@iki.fi> - 2:3.6.6-92
- Call ldconfig at libwbclient and -winbind-clients post(un)install time.
- Fix empty localization files, use %%find_lang to find and %%lang-mark them.
- Escape macros in %%changelog.
- Fix source tarball URL.

* Tue Jun 26 2012 Guenther Deschner <gdeschner@redhat.com> - 2:3.6.6-91
- Update to 3.6.6

* Thu Jun 21 2012 Andreas Schneider <asn@redhat.com> - 2:3.6.5-90
- Fix ldonfig.
- Require systemd for samba-common package.
- resolves: #829197

* Mon Jun 18 2012 Andreas Schneider <asn@redhat.com> - 2:3.6.5-89
- Fix usrmove paths.
- resolves: #829197

* Tue May 15 2012 Andreas Schneider <asn@redhat.com> - 2:3.6.5-88
- Move tmpfiles.d config to common package as it is needed for smbd and
  winbind.
- Make sure tmpfiles get created after installation.

* Wed May 09 2012 Guenther Deschner <gdeschner@redhat.com> - 2:3.6.5-87
- Correctly use system iniparser library

* Fri May 04 2012 Andreas Schneider <asn@redhat.com> - 2:3.6.5-86
- Bump Epoch to fix a problem with a Samba4 update in testing.

* Mon Apr 30 2012 Guenther Deschner <gdeschner@redhat.com> - 1:3.6.5-85
- Security Release, fixes CVE-2012-2111
- resolves: #817551

* Mon Apr 23 2012 Andreas Schneider <asn@redhat.com> - 1:3.6.4-84
- Fix creation of /var/run/samba.
- resolves: #751625

* Fri Apr 20 2012 Guenther Deschner <gdeschner@redhat.com> - 1:3.6.4-83
- Avoid private krb5_locate_kdc usage
- resolves: #754783

* Thu Apr 12 2012 Jon Ciesla <limburgher@gmail.com> - 1:3.6.4-82
- Update to 3.6.4
- Fixes CVE-2012-1182

* Mon Mar 19 2012 Andreas Schneider <asn@redhat.com> - 1:3.6.3-81
- Fix provides for of libwclient-devel for samba-winbind-devel.

* Thu Feb 23 2012 Andreas Schneider <asn@redhat.com> - 1:3.6.3-80
- Add commented out 'max protocol' to the default config.

* Mon Feb 13 2012 Andreas Schneider <asn@redhat.com> - 1:3.6.3-79
- Create a libwbclient package.
- Replace winbind-devel with libwbclient-devel package.

* Mon Jan 30 2012 Andreas Schneider <asn@redhat.com> - 1:3.6.3-78
- Update to 3.6.3
- Fixes CVE-2012-0817

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.6.1-77.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Dec 05 2011 Andreas Schneider <asn@redhat.com> - 1:3.6.1-77
- Fix winbind cache upgrade.
- resolves: #760137

* Fri Nov 18 2011 Andreas Schneider <asn@redhat.com> - 1:3.6.1-76
- Fix piddir to match with systemd files.
- Fix crash bug in the debug system.
- resolves: #754525

* Fri Nov 04 2011 Andreas Schneider <asn@redhat.com> - 1:3.6.1-75
- Fix systemd dependencies
- resolves: #751397

* Wed Oct 26 2011 Andreas Schneider <asn@redhat.com> - 1:3.6.1-74
- Update to 3.6.1

* Tue Oct 04 2011 Guenther Deschner <gdeschner@redhat.com> - 1:3.6.0-73
- Fix nmbd startup
- resolves: #741630

* Tue Sep 20 2011 Tom Callaway <spot@fedoraproject.org> - 1:3.6.0-72
- convert to systemd
- restore epoch from f15

* Sat Aug 13 2011 Guenther Deschner <gdeschner@redhat.com> - 3.6.0-71
- Update to 3.6.0 final

* Sun Jul 31 2011 Guenther Deschner <gdeschner@redhat.com> - 3.6.0rc3-70
- Update to 3.6.0rc3

* Tue Jun 07 2011 Guenther Deschner <gdeschner@redhat.com> - 3.6.0rc2-69
- Update to 3.6.0rc2

* Tue May 17 2011 Guenther Deschner <gdeschner@redhat.com> - 3.6.0rc1-68
- Update to 3.6.0rc1

* Wed Apr 27 2011 Guenther Deschner <gdeschner@redhat.com> - 3.6.0pre3-67
- Update to 3.6.0pre3

* Wed Apr 13 2011 Guenther Deschner <gdeschner@redhat.com> - 3.6.0pre2-66
- Update to 3.6.0pre2

* Fri Mar 11 2011 Guenther Deschner <gdeschner@redhat.com> - 3.6.0pre1-65
- Enable quota support

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:3.6.0-64pre1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Nov 24 2010 Guenther Deschner <gdeschner@redhat.com> - 3.6.0pre1-64
- Add %%ghost entry for /var/run using tmpfs
- resolves: #656685

* Thu Aug 26 2010 Guenther Deschner <gdeschner@redhat.com> - 3.6.0pre1-63
- Put winbind krb5 locator plugin into a separate rpm
- resolves: #627181

* Tue Aug 03 2010 Guenther Deschner <gdeschner@redhat.com> - 3.6.0pre1-62
- Update to 3.6.0pre1

* Wed Jun 23 2010 Guenther Deschner <gdeschner@redhat.com> - 3.5.4-61
- Update to 3.5.4

* Wed May 19 2010 Guenther Deschner <gdeschner@redhat.com> - 3.5.3-60
- Update to 3.5.3
- Make sure nmb and smb initscripts return LSB compliant return codes
- Fix winbind over ipv6

* Wed Apr 07 2010 Guenther Deschner <gdeschner@redhat.com> - 3.5.2-59
- Update to 3.5.2

* Mon Mar 08 2010 Simo Sorce <ssorce@redhat.com> - 3.5.1-58
- Security update to 3.5.1
- Fixes CVE-2010-0728

* Mon Mar 08 2010 Guenther Deschner <gdeschner@redhat.com> - 3.5.0-57
- Remove cifs.upcall and mount.cifs entirely

* Mon Mar 01 2010 Guenther Deschner <gdeschner@redhat.com> - 3.5.0-56
- Update to 3.5.0

* Fri Feb 19 2010 Guenther Deschner <gdeschner@redhat.com> - 3.5.0rc3-55
- Update to 3.5.0rc3

* Tue Jan 26 2010 Guenther Deschner <gdeschner@redhat.com> - 3.5.0rc2-54
- Update to 3.5.0rc2

* Fri Jan 15 2010 Jeff Layton <jlayton@redhat.com> - 3.5.0rc1-53
- separate out CIFS tools into cifs-utils package

* Fri Jan 08 2010 Guenther Deschner <gdeschner@redhat.com> - 3.5.0rc1-52
- Update to 3.5.0rc1

* Tue Dec 15 2009 Guenther Deschner <gdeschner@redhat.com> - 3.5.0pre2-51
- Update to 3.5.0pre2
- Remove umount.cifs

* Wed Nov 25 2009 Guenther Deschner <gdeschner@redhat.com> - 3.4.3-49
- Various updates to inline documentation in default smb.conf file
- resolves: #483703

* Thu Oct 29 2009 Guenther Deschner <gdeschner@redhat.com> - 3.4.3-48
- Update to 3.4.3

* Fri Oct 09 2009 Simo Sorce <ssorce@redhat.com> - 3.4.2-47
- Spec file cleanup
- Fix sources upstream location
- Remove conditionals to build talloc and tdb, now they are completely indepent
  packages in Fedora
- Add defattr() where missing
- Turn all tabs into 4 spaces
- Remove unused migration script
- Split winbind-clients out of main winbind package to avoid multilib to include
  huge packages for no good reason

* Thu Oct 01 2009 Guenther Deschner <gdeschner@redhat.com> - 3.4.2-0.46
- Update to 3.4.2
- Security Release, fixes CVE-2009-2813, CVE-2009-2948 and CVE-2009-2906

* Wed Sep 16 2009 Tomas Mraz <tmraz@redhat.com> - 3.4.1-0.45
- Use password-auth common PAM configuration instead of system-auth

* Wed Sep 09 2009 Guenther Deschner <gdeschner@redhat.com> - 3.4.1-0.44
- Update to 3.4.1

* Thu Aug 20 2009 Guenther Deschner <gdeschner@redhat.com> - 3.4.0-0.43
- Fix cli_read()
- resolves: #516165

* Thu Aug 06 2009 Guenther Deschner <gdeschner@redhat.com> - 3.4.0-0.42
- Fix required talloc version number
- resolves: #516086

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:3.4.0-0.41.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jul 17 2009 Guenther Deschner <gdeschner@redhat.com> - 3.4.0-0.41
- Fix Bug #6551 (vuid and tid not set in sessionsetupX and tconX)
- Specify required talloc and tdb version for BuildRequires

* Fri Jul 03 2009 Guenther Deschner <gdeschner@redhat.com> - 3.4.0-0.40
- Update to 3.4.0

* Fri Jun 19 2009 Guenther Deschner <gdeschner@redhat.com> - 3.4.0rc1-0.39
- Update to 3.4.0rc1

* Mon Jun 08 2009 Guenther Deschner <gdeschner@redhat.com> - 3.4.0pre2-0.38
- Update to 3.4.0pre2

* Thu Apr 30 2009 Guenther Deschner <gdeschner@redhat.com> - 3.4.0pre1-0.37
- Update to 3.4.0pre1

* Wed Apr 29 2009 Guenther Deschner <gdeschner@redhat.com> - 3.3.4-0.36
- Update to 3.3.4

* Mon Apr 20 2009 Guenther Deschner <gdeschner@redhat.com> - 3.3.3-0.35
- Enable build of idmap_tdb2 for clustered setups

* Wed Apr  1 2009 Guenther Deschner <gdeschner@redhat.com> - 3.3.3-0.34
- Update to 3.3.3

* Thu Mar 26 2009 Simo Sorce <ssorce@redhat.com> - 3.3.2-0.33
- Fix nmbd init script nmbd reload was causing smbd not nmbd to reload the
  configuration
- Fix upstream bug 6224, nmbd was waiting 5+ minutes before running elections on
  startup, causing your own machine not to show up in the network for 5 minutes
  if it was the only client in that workgroup (fix committed upstream)

* Thu Mar 12 2009 Guenther Deschner <gdeschner@redhat.com> - 3.3.2-0.31
- Update to 3.3.2
- resolves: #489547

* Thu Mar  5 2009 Guenther Deschner <gdeschner@redhat.com> - 3.3.1-0.30
- Add libcap-devel to requires list (resolves: #488559)

* Tue Mar  3 2009 Simo Sorce <ssorce@redhat.com> - 3.3.1-0.29
- Make the talloc and ldb packages optionsl and disable their build within
  the samba3 package, they are now built as part of the samba4 package
  until they will both be released as independent packages.

* Wed Feb 25 2009 Guenther Deschner <gdeschner@redhat.com> - 3.3.1-0.28
- Enable cluster support

* Tue Feb 24 2009 Guenther Deschner <gdeschner@redhat.com> - 3.3.1-0.27
- Update to 3.3.1

* Sat Feb 21 2009 Simo Sorce <ssorce@redhat.com> - 3.3.0-0.26
- Rename ldb* tools to ldb3* to avoid conflicts with newer ldb releases

* Tue Feb  3 2009 Guenther Deschner <gdeschner@redhat.com> - 3.3.0-0.25
- Update to 3.3.0 final
- Add upstream fix for ldap connections to AD (Bug #6073)
- Remove bogus perl dependencies (resolves: #473051)

* Fri Nov 28 2008 Guenther Deschner <gdeschner@redhat.com> - 3.3.0-0rc1.24
- Update to 3.3.0rc1

* Thu Nov 27 2008 Simo Sorce <ssorce@redhat.com> - 3.2.5-0.23
- Security Release, fixes CVE-2008-4314

* Thu Sep 18 2008 Guenther Deschner <gdeschner@redhat.com> - 3.2.4-0.22
- Update to 3.2.4
- resolves: #456889
- move cifs.upcall to /usr/sbin

* Wed Aug 27 2008 Guenther Deschner <gdeschner@redhat.com> - 3.2.3-0.21
- Security fix for CVE-2008-3789

* Mon Aug 25 2008 Guenther Deschner <gdeschner@redhat.com> - 3.2.2-0.20
- Update to 3.2.2

* Mon Aug 11 2008 Simo Sorce <ssorce@redhat.com> - 3.2.1-0.19
- Add fix for CUPS problem, fixes bug #453951

* Wed Aug  6 2008 Simo Sorce <ssorce@redhat.com> - 3.2.1-0.18
- Update to 3.2.1

* Tue Jul  1 2008 Guenther Deschner <gdeschner@redhat.com> - 3.2.0-2.17
- Update to 3.2.0 final
- resolves: #452622

* Tue Jun 10 2008 Guenther Deschner <gdeschner@redhat.com> - 3.2.0-1.rc2.16
- Update to 3.2.0rc2
- resolves: #449522
- resolves: #448107

* Fri May 30 2008 Guenther Deschner <gdeschner@redhat.com> - 3.2.0-1.rc1.15
- Fix security=server
- resolves: #449038, #449039

* Wed May 28 2008 Guenther Deschner <gdeschner@redhat.com> - 3.2.0-1.rc1.14
- Add fix for CVE-2008-1105
- resolves: #446724

* Fri May 23 2008 Guenther Deschner <gdeschner@redhat.com> - 3.2.0-1.rc1.13
- Update to 3.2.0rc1

* Wed May 21 2008 Simo Sorce <ssorce@redhat.com> - 3.2.0-1.pre3.12
- make it possible to print against Vista and XP SP3 as servers
- resolves: #439154

* Thu May 15 2008 Guenther Deschner <gdeschner@redhat.com> - 3.2.0-1.pre3.11
- Add "net ads join createcomputer=ou1/ou2/ou3" fix (BZO #5465)

* Fri May 09 2008 Guenther Deschner <gdeschner@redhat.com> - 3.2.0-1.pre3.10
- Add smbclient fix (BZO #5452)

* Fri Apr 25 2008 Guenther Deschner <gdeschner@redhat.com> - 3.2.0-1.pre3.9
- Update to 3.2.0pre3

* Tue Mar 18 2008 Guenther Deschner <gdeschner@redhat.com> - 3.2.0-1.pre2.8
- Add fixes for libsmbclient and support for r/o relocations

* Mon Mar 10 2008 Guenther Deschner <gdeschner@redhat.com> - 3.2.0-1.pre2.7
- Fix libnetconf, libnetapi and msrpc DSSETUP call

* Thu Mar 06 2008 Guenther Deschner <gdeschner@redhat.com> - 3.2.0-1.pre2.6
- Create separate packages for samba-winbind and samba-winbind-devel
- Add cifs.spnego helper

* Wed Mar 05 2008 Guenther Deschner <gdeschner@redhat.com> - 3.2.0-1.pre2.3
- Update to 3.2.0pre2
- Add talloc and tdb lib and devel packages
- Add domainjoin-gui package

* Fri Feb 22 2008 Simo Sorce <ssorce@redhat.com> - 3.2.0-0.pre1.3
- Try to fix GCC 4.3 build
- Add --with-dnsupdate flag and also make sure other flags are required just to
  be sure the features are included without relying on autodetection to be
  successful

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:3.2.0-1.pre1.2
- Autorebuild for GCC 4.3

* Tue Dec 04 2007 Release Engineering <rel-eng at fedoraproject dot org> - 3.2.0-0.pre1.2
- Rebuild for openldap bump

* Thu Oct 18 2007 Guenther Deschner <gdeschner@redhat.com> 3.2.0-0.pre1.1.fc9
- 32/64bit padding fix (affects multilib installations)

* Mon Oct 8 2007 Simo Sorce <ssorce@redhat.com> 3.2.0-0.pre1.fc9
- New major relase, minor switched from 0 to 2
- License change, the code is now GPLv3+
- Numerous improvements and bugfixes included
- package libsmbsharemodes too
- remove smbldap-tools as they are already packaged separately in Fedora
- Fix bug 245506 

* Tue Oct 2 2007 Simo Sorce <ssorce@redhat.com> 3.0.26a-1.fc8
- rebuild with AD DNS Update support

* Tue Sep 11 2007 Simo Sorce <ssorce@redhat.com> 3.0.26a-0.fc8
- upgrade to the latest upstream realease
- includes security fixes released today in 3.0.26

* Fri Aug 24 2007 Simo Sorce <ssorce@redhat.com> 3.0.25c-4.fc8
- add fix reported upstream for heavy idmap_ldap memleak

* Tue Aug 21 2007 Simo Sorce <ssorce@redhat.com> 3.0.25c-3.fc8
- fix a few places were "open" is used an interfere with the new glibc

* Tue Aug 21 2007 Simo Sorce <ssorce@redhat.com> 3.0.25c-2.fc8
- remove old source
- add patch to fix samba bugzilla 4772

* Tue Aug 21 2007 Guenther Deschner <gdeschner@redhat.com> 3.0.25c-0.fc8
- update to 3.0.25c

* Fri Jun 29 2007 Simo Sorce <ssorce@redhat.com> 3.0.25b-3.fc8
- handle cases defined in #243766

* Tue Jun 26 2007 Simo Sorce <ssorce@redhat.com> 3.0.25b-2.fc8
- update to 3.0.25b
- better error codes for init scripts: #244823

* Tue May 29 2007 Günther Deschner <gdeschner@redhat.com>
- fix pam_smbpass patch.

* Fri May 25 2007 Simo Sorce <ssorce@redhat.com>
- update to 3.0.25a as it contains many fixes
- add a fix for pam_smbpass made by Günther but committed upstream after 3.0.25a was cut.

* Mon May 14 2007 Simo Sorce <ssorce@redhat.com>
- final 3.0.25
- includes security fixes for CVE-2007-2444,CVE-2007-2446,CVE-2007-2447

* Mon Apr 30 2007 Günther Deschner <gdeschner@redhat.com>
- move to 3.0.25rc3

* Thu Apr 19 2007 Simo Sorce <ssorce@redhat.com>
- fixes in the spec file
- moved to 3.0.25rc1
- addedd patches (merged upstream so they will be removed in 3.0.25rc2)

* Wed Apr 4 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-12.fc7
- fixes in smb.conf
- advice in smb.conf to put scripts in /var/lib/samba/scripts
- create /var/lib/samba/scripts so that selinux can be happy
- fix Vista problems with msdfs errors

* Tue Apr 03 2007 Guenther Deschner <gdeschner@redhat.com> 3.0.24-11.fc7
- enable PAM and NSS dlopen checks during build
- fix unresolved symbols in libnss_wins.so (bug #198230)

* Fri Mar 30 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-10.fc7
- set passdb backend = tdbsam as default in smb.conf
- remove samba-docs dependency from swat, that was a mistake
- put back COPYING and other files in samba-common
- put examples in samba not in samba-docs
- leave only stuff under docs/ in samba-doc

* Thu Mar 29 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-9.fc7
- integrate most of merge review proposed changes (bug #226387)
- remove libsmbclient-devel-static and simply stop shipping the
  static version of smbclient as it seem this is deprecated and
  actively discouraged

* Wed Mar 28 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-8.fc7
- fix for bug #176649

* Mon Mar 26 2007 Simo Sorce <ssorce@redhat.com>
- remove patch for bug 106483 as it introduces a new bug that prevents
  the use of a credentials file with the smbclient tar command
- move the samba private dir from being the same as the config dir
  (/etc/samba) to /var/lib/samba/private

* Mon Mar 26 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-7.fc7
- make winbindd start earlier in the init process, at the same time
  ypbind is usually started as well
- add a sepoarate init script for nmbd called nmb, we need to be able
  to restart nmbd without dropping al smbd connections unnecessarily

* Fri Mar 23 2007 Simo Sorce <ssorce@redhat.com>
- add samba.schema to /etc/openldap/schema

* Thu Mar 22 2007 Florian La Roche <laroche@redhat.com>
- adjust the Requires: for the scripts, add "chkconfig --add smb"

* Tue Mar 20 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-6.fc7
- do not put comments inline on smb.conf options, they may be read
  as part of the value (for example log files names)

* Mon Mar 19 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-5.fc7
- actually use the correct samba.pamd file not the old samba.pamd.stack file
- fix logifles and use upstream convention of log.* instead of our old *.log
  Winbindd creates its own log.* files anyway so we will be more consistent
- install our own (enhanced) default smb.conf file
- Fix pam_winbind acct_mgmt PAM result code (prevented local users from
  logging in). Fixed by Guenther.
- move some files from samba to samba-common as they are used with winbindd
  as well

* Fri Mar 16 2007 Guenther Deschner <gdeschner@redhat.com> 3.0.24-4.fc7
- fix arch macro which reported Vista to Samba clients.

* Thu Mar 15 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-3.fc7
- Directories reorg, tdb files must go to /var/lib, not
  to /var/cache, add migration script in %%post common
- Split out libsmbclient, devel and doc packages
- Remove libmsrpc.[h|so] for now as they are not really usable
- Remove kill -HUP from rotate, samba use -HUP for other things
  noit to reopen logs

* Tue Feb 20 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-2.fc7
- New upstream release
- Fix packaging issue wrt idmap modules used only by smbd
- Addedd Vista Patchset for compatibility with Windows Vista
- Change default of "msdfs root", it seem to cause problems with
  some applications and it has been proposed to change it for
  3.0.25 upstream

* Fri Sep 1 2006 Jay Fenlason <fenlason@redhat.com> 3.0.23c-2
- New upstream release.

* Tue Aug 8 2006 Jay Fenlason <fenlason@redhat.com> 3.0.23b-2
- New upstream release.

* Mon Jul 24 2006 Jay Fenlason <fenlason@redhat.com> 3.0.23a-3
- Fix the -logfiles patch to close
  bz#199607 Samba compiled with wrong log path.
  bz#199206 smb.conf has incorrect log file path

* Mon Jul 24 2006 Jay Fenlason <fenlason@redhat.com> 3.0.23a-2
- Upgrade to new upstream 3.0.23a
- include upstream samr_alias patch

* Tue Jul 11 2006 Jay Fenlason <fenlason@redhat.com> 3.0.23-2
- New upstream release.
- Use modified filter-requires-samba.sh from packaging/RHEL/setup/
  to get rid of bogus dependency on perl(Unicode::MapUTF8)
- Update the -logfiles and -smb.conf patches to work with 3.0.23

* Thu Jul 6 2006 Jay Fenlason <fenlason@redhat.com> 3.0.23-0.RC3
- New upstream RC release.
- Update the -logfiles, and -passwd patches for
  3.0.23rc3
- Include the change to smb.init from Bastien Nocera <bnocera@redhat.com>)
  to close
  bz#182560 Wrong retval for initscript when smbd is dead
- Update this spec file to build with 3.0.23rc3
- Remove the -install.mount.smbfs patch, since we don't install
  mount.smbfs any more.

* Wed Jun 14 2006 Tomas Mraz <tmraz@redhat.com> - 2.0.21c-3
- rebuilt with new gnutls

* Fri Mar 17 2006 Jay Fenlason <fenlason@redhat.com> 2.0.21c-2
- New upstream version.

* Mon Feb 13 2006 Jay Fenlason <fenlason@redhat.com> 3.0.21b-2
- New upstream version.
- Since the rawhide kernel has dropped support for smbfs, remove smbmount
  and smbumount.  Users should use mount.cifs instead.
- Upgrade to 3.0.21b

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0:3.0.20b-2.1.1
- bump again for double-long bug on ppc(64)

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Sun Nov 13 2005 Jay Fenlason <fenlason@redhat.com> 3.0.20b-2
- turn on -DLDAP_DEPRECATED to allow access to ldap functions that have
  been depricated in 2.3.11, but which don't have well-documented
  replacements (ldap_simple_bind_s(), for example).
- Upgrade to 3.0.20b, which includes all the previous upstream patches.
- Updated the -warnings patch for 3.0.20a.
- Include  --with-shared-modules=idmap_ad,idmap_rid to close
  bz#156810 --with-shared-modules=idmap_ad,idmap_rid
- Include the new samba.pamd from Tomas Mraz (tmraz@redhat.com) to close
  bz#170259 pam_stack is deprecated

* Sun Nov 13 2005 Warren Togami <wtogami@redhat.com> 3.0.20-3
- epochs from deps, req exact release
- rebuild against new openssl

* Mon Aug 22 2005 Jay Fenlason <fenlason@redhat.com> 3.0.20-2
- New upstream release
  Includes five upstream patches -bug3010_v1, -groupname_enumeration_v3,
    -regcreatekey_winxp_v1, -usrmgr_groups_v1, and -winbindd_v1
  This obsoletes the -pie and -delim patches
  the -warning and -gcc4 patches are obsolete too
  The -man, -passwd, and -smbspool patches were updated to match 3.0.20pre1
  Also, the -quoting patch was implemented differently upstream
  There is now a umount.cifs executable and manpage
  We run autogen.sh as part of the build phase
  The testprns command is now gone
  libsmbclient now has a man page
- Include -bug106483 patch to close
  bz#106483 smbclient: -N negates the provided password, despite documentation
- Added the -warnings patch to quiet some compiler warnings.
- Removed many obsolete patches from CVS.

* Mon May 2 2005 Jay Fenlason <fenlason@redhat.com> 3.0.14a-2
- New upstream release.
- the -64bit-timestamps, -clitar, -establish_trust, user_rights_v1,
  winbind_find_dc_v2 patches are now obsolete.

* Thu Apr 7 2005 Jay Fenlason <fenlason@redhat.com> 3.0.13-2
- New upstream release
- add my -quoting patch, to fix swat with strings that contain
  html meta-characters, and to use correct quote characters in
  lists, closing bz#134310
- include the upstream winbindd_2k3sp1 patch
- include the -smbclient patch.
- include the -hang patch from upstream.

* Thu Mar 24 2005 Florian La Roche <laroche@redhat.com>
- add a "exit 0" to the postun of the main samba package

* Wed Mar  2 2005 Tomas Mraz <tmraz@redhat.com> 3.0.11-5
- rebuild with openssl-0.9.7e

* Thu Feb 24 2005 Jay Fenlason <fenlason@redhat.com> 3.0.11-4
- Use the updated filter-requires-samba.sh file, so we don't accidentally
  pick up a dependency on perl(Crypt::SmbHash)

* Fri Feb 18 2005 Jay Fenlason <fenlason@redhat.com> 3.0.11-3
- add -gcc4 patch to compile with gcc 4.
- remove the now obsolete -smbclient-kerberos.patch
- Include four upstream patches from
  http://samba.org/~jerry/patches/post-3.0.11/
  (Slightly modified the winbind_find_dc_v2 patch to apply easily with
  rpmbuild).

* Fri Feb 4 2005 Jay Fenlason <fenlason@redhat.com> 3.0.11-2
- include -smbspool patch to close bz#104136

* Wed Jan 12 2005 Jay Fenlason <fenlason@redhat.com> 3.0.10-4
- Update the -man patch to fix ntlm_auth.1 too.
- Move pam_smbpass.so to the -common package, so both the 32
  and 64-bit versions will be installed on multiarch platforms.
  This closes bz#143617
- Added new -delim patch to fix mount.cifs so it can accept
  passwords with commas in them (via environment or credentials
  file) to close bz#144198

* Wed Jan 12 2005 Tim Waugh <twaugh@redhat.com> 3.0.10-3
- Rebuilt for new readline.

* Fri Dec 17 2004 Jay Fenlason <fenlason@redhat.com> 3.0.10-2
- New upstream release that closes CAN-2004-1154  bz#142544
- Include the -64bit patch from Nalin.  This closes bz#142873
- Update the -logfiles patch to work with 3.0.10
- Create /var/run/winbindd and make it part of the -common rpm to close
  bz#142242

* Mon Nov 22 2004 Jay Fenlason <fenlason@redhat.com> 3.0.9-2
- New upstream release.  This obsoletes the -secret patch.
  Include my changetrustpw patch to make "net ads changetrustpw" stop
  aborting.  This closes #134694
- Remove obsolete triggers for ancient samba versions.
- Move /var/log/samba to the -common rpm.  This closes #76628
- Remove the hack needed to get around the bad docs files in the
  3.0.8 tarball.
- Change the comment in winbind.init to point at the correct pidfile.
  This closes #76641

* Mon Nov 22 2004 Than Ngo <than@redhat.com> 3.0.8-4
- fix unresolved symbols in libsmbclient which caused applications
  such as KDE's konqueror to fail when accessing smb:// URLs. #139894

* Thu Nov 11 2004 Jay Fenlason <fenlason@redhat.com> 3.0.8-3.1
- Rescue the install.mount.smbfs patch from Juanjo Villaplana
  (villapla@si.uji.es) to prevent building the srpm from trashing your
  installed /usr/bin/smbmount

* Tue Nov 9 2004 Jay Fenlason <fenlason@redhat.com> 3.0.8-3
- Include the corrected docs tarball, and use it instead of the
  obsolete docs from the upstream 3.0.8 tarball.
- Update the logfiles patch to work with the updated docs.

* Mon Nov 8 2004 Jay Fenlason <fenlason@redhat.com> 3.0.8-2
- New upstream version fixes CAN-2004-0930.  This obsoletes the
  disable-sendfile, salt, signing-shortkey and fqdn patches.
- Add my <fenlason@redhat.com> ugly non-ascii-domain patch.
- Updated the pie patch for 3.0.8.
- Updated the logfiles patch for 3.0.8.

* Tue Oct 26 2004 Jay Fenlason <fenlason@redhat.com> 3.0.8-0.pre2
- New upstream version
- Add Nalin's signing-shortkey patch.

* Tue Oct 19 2004 Jay Fenlason <fenlason@redhat.com> 3.0.8-0.pre1.3
- disable the -salt patch, because it causes undefined references in
  libsmbclient that prevent gnome-vfs from building.

* Fri Oct 15 2004 Jay Fenlason <fenlason@redhat.com> 3.0.8-0.pre1.2
- Re-enable the x_fclose patch that was accidentally disabled
  in 3.0.8-0.pre1.1.  This closes #135832
- include Nalin's -fqdn and -salt patches.

* Wed Oct 13 2004 Jay Fenlason <fenlason@redhat.com> 3.0.8-0.pre1.1
- Include disable-sendfile patch to default "use sendfile" to "no".
  This closes #132779

* Wed Oct 6 2004 Jay Fenlason <fenlason@redhat.com>
- Include patch from Steven Lawrance (slawrance@yahoo.com) that modifies
  smbmnt to work with 32-bit uids.

* Mon Sep 27 2004 Jay Fenlason <fenlason@redhat.com> 3.0.8-0.pre1
- new upstream release.  This obsoletes the ldapsam_compat patches.

* Wed Sep 15 2004 Jay Fenlason <fenlason@redhat.com> 3.0.7-4
- Update docs section to not carryover the docs/manpages directory
  This moved many files from /usr/share/doc/samba-3.0.7/docs/* to
  /usr/share/doc/samba-3.0.7/*
- Modify spec file as suggested by Rex Dieter (rdieter@math.unl.edu)
  to correctly create libsmbclient.so.0 and to use %%_initrddir instead
  of rolling our own.  This closes #132642
- Add patch to default "use sendfile" to no, since sendfile appears to
  be broken
- Add patch from Volker Lendecke <vl@samba.org> to help make
  ldapsam_compat work again.
- Add patch from "Vince Brimhall" <vbrimhall@novell.com> for ldapsam_compat
  These two patches close bugzilla #132169

* Mon Sep 13 2004 Jay Fenlason <fenlason@redhat.com> 3.0.7-3
- Upgrade to 3.0.7, which fixes CAN-2004-0807 CAN-2004-0808
  This obsoletes the 3.0.6-schema patch.
- Update BuildRequires line to include openldap-devel openssl-devel
  and cups-devel

* Mon Aug 16 2004 Jay Fenlason <fenlason@redhat.com> 3.0.6-3
- New upstream version.
- Include post 3.0.6 patch from "Gerald (Jerry) Carter" <jerry@samba.org>
  to fix a duplicate in the LDAP schema.
- Include 64-bit timestamp patch from Ravikumar (rkumar@hp.com)
  to allow correct timestamp handling on 64-bit platforms and fix #126109.
- reenable the -pie patch.  Samba is too widely used, and too vulnerable
  to potential security holes to disable an important security feature
  like -pie.  The correct fix is to have the toolchain not create broken
  executables when programs compiled -pie are stripped.
- Remove obsolete patches.
- Modify this spec file to put libsmbclient.{a,so} in the right place on
  x86_64 machines.

* Thu Aug  5 2004 Jason Vas Dias <jvdias@redhat.com> 3.0.5-3
- Removed '-pie' patch - 3.0.5 uses -fPIC/-PIC, and the combination
- resulted in executables getting corrupt stacks, causing smbmnt to
- get a SIGBUS in the mount() call (bug 127420).

* Fri Jul 30 2004 Jay Fenlason <fenlason@redhat.com> 3.0.5-2
- Upgrade to 3.0.5, which is a regression from 3.0.5pre1 for a
  security fix.
- Include the 3.0.4-backport patch from the 3E branch.  This restores
  some of the 3.0.5pre1 and 3.0.5rc1 functionality.

* Tue Jul 20 2004 Jay Fenlason <fenlason@redhat.com> 3.0.5-0.pre1.1
- Backport base64_decode patche to close CAN-2004-0500
- Backport hash patch to close CAN-2004-0686
- use_authtok patch from Nalin Dahyabhai <nalin@redhat.com>
- smbclient-kerberos patch from Alexander Larsson <alexl@redhat.com>
- passwd patch uses "*" instead of "x" for "hashed" passwords for
  accounts created by winbind.  "x" means "password is in /etc/shadow" to
  brain-damaged pam_unix module.

* Fri Jul 2 2004 Jay Fenlason <fenlason@redhat.com> 3.0.5.0pre1.0
- New upstream version
- use %% { SOURCE1 } instead of a hardcoded path
- include -winbind patch from Gerald (Jerry) Carter (jerry@samba.org)
  https://bugzilla.samba.org/show_bug.cgi?id=1315
  to make winbindd work against Windows versions that do not have
  128 bit encryption enabled.
- Moved %%{_bindir}/net to the -common package, so that folks who just
  want to use winbind, etc don't have to install -client in order to
  "net join" their domain.
- New upstream version obsoletes the patches added in 3.0.3-5
- Remove smbgetrc.5 man page, since we don't ship smbget.

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue May 4 2004 Jay Fenlason <fenlason@redhat.com> 3.0.3-5
- Patch to allow password changes from machines patched with
  Microsoft hotfix MS04-011.
- Include patches for https://bugzilla.samba.org/show_bug.cgi?id=1302
  and https://bugzilla.samba.org/show_bug.cgi?id=1309

* Thu Apr 29 2004 Jay Fenlason <fenlason@redhat.com> 3.0.3-4
- Samba 3.0.3 released.

* Wed Apr 21 2004 jay Fenlason <fenlason@redhat.com> 3.0.3-3.rc1
- New upstream version
- updated spec file to make libsmbclient.so executable.  This closes
  bugzilla #121356

* Mon Apr 5 2004 Jay Fenlason <fenlason@redhat.com> 3.0.3-2.pre2
- New upstream version  
- Updated configure line to remove --with-fhs and to explicitly set all
  the directories that --with-fhs was setting.  We were overriding most of
  them anyway.  This closes #118598

* Mon Mar 15 2004 Jay Fenlason <fenlason@redhat.com> 3.0.3-1.pre1
- New upstream version.
- Updated -pie and -logfiles patches for 3.0.3pre1
- add krb5-devel to buildrequires, fixes #116560
- Add patch from Miloslav Trmac (mitr@volny.cz) to allow non-root to run
  "service smb status".  This fixes #116559

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Feb 16 2004 Jay Fenlason <fenlason@redhat.com> 3.0.2a-1
- Upgrade to 3.0.2a

* Mon Feb 16 2004 Karsten Hopp <karsten@redhat.de> 3.0.2-7 
- fix ownership in -common package

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Jay Fenlason <fenlason@redhat.com>
- Change all requires lines to list an explicit epoch.  Closes #102715
- Add an explicit Epoch so that %%{epoch} is defined.

* Mon Feb 9 2004 Jay Fenlason <fenlason@redhat.com> 3.0.2-5
- New upstream version: 3.0.2 final includes security fix for #114995
  (CAN-2004-0082)
- Edit postun script for the -common package to restart winbind when
  appropriate.  Fixes bugzilla #114051.

* Mon Feb 2 2004 Jay Fenlason <fenlason@redhat.com> 3.0.2-3rc2
- add %%dir entries for %%{_libdir}/samba and %%{_libdir}/samba/charset
- Upgrade to new upstream version
- build mount.cifs for the new cifs filesystem in the 2.6 kernel.

* Mon Jan 19 2004 Jay Fenlason <fenlason@redhat.com> 3.0.2-1rc1
- Upgrade to new upstream version

* Wed Dec 17 2003 Felipe Alfaro Solana <felipe_alfaro@linuxmail.org> 3.0.1-1
- Update to 3.0.1
- Removed testparm patch as it's already merged
- Removed Samba.7* man pages
- Fixed .buildroot patch
- Fixed .pie patch
- Added new /usr/bin/tdbdump file

* Thu Sep 25 2003 Jay Fenlason <fenlason@redhat.com> 3.0.0-15
- New 3.0.0 final release
- merge nmbd-netbiosname and testparm patches from 3E branch
- updated the -logfiles patch to work against 3.0.0
- updated the pie patch
- update the VERSION file during build
- use make -j if avaliable
- merge the winbindd_privileged change from 3E
- merge the "rm /usr/lib" patch that allows Samba to build on 64-bit
  platforms despite the broken Makefile

* Mon Aug 18 2003 Jay Fenlason <fenlason@redhat.com>
- Merge from samba-3E-branch after samba-3.0.0rc1 was released

* Wed Jul 23 2003 Jay Fenlason <fenlason@redhat.com> 3.0.0-3beta3
- Merge from 3.0.0-2beta3.3E
- (Correct log file names (#100981).)
- (Fix pidfile directory in samab.log)
- (Remove obsolete samba-3.0.0beta2.tar.bz2.md5 file)
- (Move libsmbclient to the -common package (#99449))

* Sun Jun 22 2003 Nalin Dahyabhai <nalin@redhat.com> 2.2.8a-4
- rebuild

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed May 28 2003 Jay Fenlason <fenlason@redhat.com> 2.2.8a-2
- add libsmbclient.so for gnome-vfs-extras
- Edit specfile to specify /var/run for pid files
- Move /tmp/.winbindd/socket to /var/run/winbindd/socket

* Wed May 14 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- add proper ldconfig calls

* Thu Apr 24 2003 Jay Fenlason <fenlason@redhat.com> 2.2.8a-1
- upgrade to 2.2.8a
- remove old .md5 files
- add "pid directory = /var/run" to the smb.conf file.  Fixes #88495
- Patch from jra@dp.samba.org to fix a delete-on-close regression

* Mon Mar 24 2003 Jay Fenlason <fenlason@redhat.com> 2.2.8-0
- Upgrade to 2.2.8
- removed commented out patches.
- removed old patches and .md5 files from the repository.
- remove duplicate /sbin/chkconfig --del winbind which causes
  warnings when removing samba.
- Fixed minor bug in smbprint that causes it to fail when called with
  more than 10 parameters: the accounting file (and spool directory
  derived from it) were being set wrong due to missing {}.  This closes
  bug #86473.
- updated smb.conf patch, includes new defaults to close bug #84822.

* Mon Feb 24 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Feb 20 2003 Jonathan Blandford <jrb@redhat.com> 2.2.7a-5
- remove swat.desktop file

* Thu Feb 20 2003 Nalin Dahyabhai <nalin@redhat.com> 2.2.7a-4
- relink libnss_wins.so with SHLD="%%{__cc} -lnsl" to force libnss_wins.so to
  link with libnsl, avoiding unresolved symbol errors on functions in libnsl

* Mon Feb 10 2003 Jay Fenlason <fenlason@redhat.com> 2.2.7a-3
- edited spec file to put .so files in the correct directories
  on 64-bit platforms that have 32-bit compatability issues
  (sparc64, x86_64, etc).  This fixes bugzilla #83782.
- Added samba-2.2.7a-error.patch from twaugh.  This fixes
  bugzilla #82454.

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Thu Jan  9 2003 Jay Fenlason <fenlason@redhat.com> 2.2.7a-1
- Update to 2.2.7a
- Change default printing system to CUPS
- Turn on pam_smbpass
- Turn on msdfs

* Sat Jan  4 2003 Jeff Johnson <jbj@redhat.com> 2.2.7-5
- use internal dep generator.

* Sat Dec 14 2002 Tim Powers <timp@redhat.com> 2.2.7-4
- don't use rpms internal dep generator

* Mon Dec 02 2002 Elliot Lee <sopwith@redhat.com> 2.2.7-3
- Fix missing doc files.
- Fix multilib issues

* Wed Nov 20 2002 Bill Nottingham <notting@redhat.com> 2.2.7-2
- update to 2.2.7
- add patch for LFS in smbclient (<tcallawa@redhat.com>)

* Wed Aug 28 2002 Trond Eivind Glomsød <teg@redhat.com> 2.2.5-10
- logrotate fixes (#65007)

* Mon Aug 26 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.5-9
- /usr/lib was used in place of %%{_libdir} in three locations (#72554)

* Mon Aug  5 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.5-8
- Initscript fix (#70720)

* Fri Jul 26 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.5-7
- Enable VFS support and compile the "recycling" module (#69796)
- more selective includes of the examples dir 

* Tue Jul 23 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.5-6
- Fix the lpq parser for better handling of LPRng systems (#69352)

* Tue Jul 23 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.5-5
- desktop file fixes (#69505)

* Wed Jun 26 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.5-4
- Enable ACLs

* Tue Jun 25 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.5-3
- Make it not depend on Net::LDAP - those are doc files and examples

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu Jun 20 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.5-1
- 2.2.5

* Fri Jun 14 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.4-5
- Move the post/preun of winbind into the -common subpackage, 
  where the script is (#66128)

* Tue Jun  4 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.4-4
- Fix pidfile locations so it runs properly again (2.2.4 
  added a new directtive - #65007)

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue May 14 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.4-2
- Fix #64804

* Thu May  9 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.4-1
- 2.2.4
- Removed some zero-length and CVS internal files
- Make it build

* Wed Apr 10 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.3a-6
- Don't use /etc/samba.d in smbadduser, it should be /etc/samba

* Thu Apr  4 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.3a-5
- Add libsmbclient.a w/headerfile for KDE (#62202)

* Tue Mar 26 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.3a-4
- Make the logrotate script look the correct place for the pid files 

* Thu Mar 14 2002 Nalin Dahyabhai <nalin@redhat.com> 2.2.3a-3
- include interfaces.o in pam_smbpass.so, which needs symbols from interfaces.o
  (patch posted to samba-list by Ilia Chipitsine)

* Thu Feb 21 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.3a-2
- Rebuild

* Thu Feb  7 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.3a-1
- 2.2.3a

* Mon Feb  4 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.3-1
- 2.2.3

* Thu Nov 29 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2.2-8
- New pam configuration file for samba

* Tue Nov 27 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2.2-7
- Enable PAM session controll and password sync

* Tue Nov 13 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2.2-6
- Move winbind files to samba-common. Add separate initscript for
  winbind 
- Fixes for winbind - protect global variables with mutex, use
  more secure getenv

* Thu Nov  8 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2.2-5
- Teach smbadduser about "getent passwd" 
- Fix more pid-file references
- Add (conditional) winbindd startup to the initscript, configured in
  /etc/sysconfig/samba

* Wed Nov  7 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2.2-4
- Fix pid-file reference in logrotate script
- include pam and nss modules for winbind

* Mon Nov  5 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2.2-3
- Add "--with-utmp" to configure options (#55372)
- Include winbind, pam_smbpass.so, rpcclient and smbcacls
- start using /var/cache/samba, we need to keep state and there is
  more than just locks involved

* Sat Nov 03 2001 Florian La Roche <Florian.LaRoche@redhat.de> 2.2.2-2
- add "reload" to the usage string in the startup script

* Mon Oct 15 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2.2-1
- 2.2.2

* Tue Sep 18 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2.1a-5
- Add patch from Jeremy Allison to fix IA64 alignment problems (#51497)

* Mon Aug 13 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Don't include smbpasswd in samba, it's in samba-common (#51598)
- Add a disabled "obey pam restrictions" statement - it's not
  active, as we use encrypted passwords, but if the admin turns
  encrypted passwords off the choice is available. (#31351)

* Wed Aug  8 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Use /var/cache/samba instead of /var/lock/samba 
- Remove "domain controller" keyword from smb.conf, it's 
  deprecated (from #13704)
- Sync some examples with smb.conf.default
- Fix password synchronization (#16987)

* Fri Jul 20 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Tweaks of BuildRequires (#49581)

* Wed Jul 11 2001 Trond Eivind Glomsrød <teg@redhat.com>
- 2.2.1a bugfix release

* Tue Jul 10 2001 Trond Eivind Glomsrød <teg@redhat.com>
- 2.2.1, which should work better for XP

* Sat Jun 23 2001 Trond Eivind Glomsrød <teg@redhat.com>
- 2.2.0a security fix
- Mark lograte and pam configuration files as noreplace

* Fri Jun 22 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Add the /etc/samba directory to samba-common

* Thu Jun 21 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Add improvements to the smb.conf as suggested in #16931

* Tue Jun 19 2001 Trond Eivind Glomsrød <teg@redhat.com>
- (these changes are from the non-head version)
- Don't include /usr/sbin/samba, it's the same as the initscript
- unset TMPDIR, as samba can't write into a TMPDIR owned
  by root (#41193)
- Add pidfile: lines for smbd and nmbd and a config: line
  in the initscript  (#15343)
- don't use make -j
- explicitly include /usr/share/samba, not just the files in it

* Tue Jun 19 2001 Bill Nottingham <notting@redhat.com>
- mount.smb/mount.smbfs go in /sbin, *not* %%{_sbindir}

* Fri Jun  8 2001 Preston Brown <pbrown@redhat.com>
- enable encypted passwords by default

* Thu Jun  7 2001 Helge Deller <hdeller@redhat.de> 
- build as 2.2.0-1 release
- skip the documentation-directories docbook, manpages and yodldocs
- don't include *.sgml documentation in package
- moved codepage-directory to /usr/share/samba/codepages
- make it compile with glibc-2.2.3-10 and kernel-headers-2.4.2-2   

* Mon May 21 2001 Helge Deller <hdeller@redhat.de> 
- updated to samba 2.2.0
- moved codepages to %%{_datadir}/samba/codepages
- use all available CPUs for building rpm packages
- use %%{_xxx} defines at most places in spec-file
- "License:" replaces "Copyright:"
- dropped excludearch sparc
- de-activated japanese patches 100 and 200 for now 
  (they need to be fixed and tested wth 2.2.0)
- separated swat.desktop file from spec-file and added
  german translations
- moved /etc/sysconfig/samba to a separate source-file
- use htmlview instead of direct call to netscape in 
  swat.desktop-file

* Mon May  7 2001 Bill Nottingham <notting@redhat.com>
- device-remove security fix again (<tridge@samba.org>)

* Fri Apr 20 2001 Bill Nottingham <notting@redhat.com>
- fix tempfile security problems, officially (<tridge@samba.org>)
- update to 2.0.8

* Sun Apr  8 2001 Bill Nottingham <notting@redhat.com>
- turn of SSL, kerberos

* Thu Apr  5 2001 Bill Nottingham <notting@redhat.com>
- fix tempfile security problems (patch from <Marcus.Meissner@caldera.de>)

* Thu Mar 29 2001 Bill Nottingham <notting@redhat.com>
- fix quota support, and quotas with the 2.4 kernel (#31362, #33915)

* Mon Mar 26 2001 Nalin Dahyabhai <nalin@redhat.com>
- tweak the PAM code some more to try to do a setcred() after initgroups()
- pull in all of the optflags on i386 and sparc
- don't explicitly enable Kerberos support -- it's only used for password
  checking, and if PAM is enabled it's a no-op anyway

* Mon Mar  5 2001 Tim Waugh <twaugh@redhat.com>
- exit successfully from preun script (bug #30644).

* Fri Mar  2 2001 Nalin Dahyabhai <nalin@redhat.com>
- rebuild in new environment

* Wed Feb 14 2001 Bill Nottingham <notting@redhat.com>
- updated japanese stuff (#27683)

* Fri Feb  9 2001 Bill Nottingham <notting@redhat.com>
- fix trigger (#26859)

* Wed Feb  7 2001 Bill Nottingham <notting@redhat.com>
- add i18n support, japanese patch (#26253)

* Wed Feb  7 2001 Trond Eivind Glomsrød <teg@redhat.com>
- i18n improvements in initscript (#26537)

* Wed Jan 31 2001 Bill Nottingham <notting@redhat.com>
- put smbpasswd in samba-common (#25429)

* Wed Jan 24 2001 Bill Nottingham <notting@redhat.com>
- new i18n stuff

* Sun Jan 21 2001 Bill Nottingham <notting@redhat.com>
- rebuild

* Thu Jan 18 2001 Bill Nottingham <notting@redhat.com>
- i18n-ize initscript
- add a sysconfig file for daemon options (#23550)
- clarify smbpasswd man page (#23370)
- build with LFS support (#22388)
- avoid extraneous pam error messages (#10666)
- add Urban Widmark's bug fixes for smbmount (#19623)
- fix setgid directory modes (#11911)
- split swat into subpackage (#19706)

* Wed Oct 25 2000 Nalin Dahyabhai <nalin@redhat.com>
- set a default CA certificate path in smb.conf (#19010)
- require openssl >= 0.9.5a-20 to make sure we have a ca-bundle.crt file

* Mon Oct 16 2000 Bill Nottingham <notting@redhat.com>
- fix swat only_from line (#18726, others)
- fix attempt to write outside buildroot on install (#17943)

* Mon Aug 14 2000 Bill Nottingham <notting@redhat.com>
- add smbspool back in (#15827)
- fix absolute symlinks (#16125)

* Sun Aug 6 2000 Philipp Knirsch <pknirsch@redhat.com>
- bugfix for smbadduser script (#15148)

* Mon Jul 31 2000 Matt Wilson <msw@redhat.com>
- patch configure.ing (patch11) to disable cups test
- turn off swat by default

* Fri Jul 28 2000 Bill Nottingham <notting@redhat.com>
- fix condrestart stuff

* Fri Jul 21 2000 Bill Nottingham <notting@redhat.com>
- add copytruncate to logrotate file (#14360)
- fix init script (#13708)

* Sat Jul 15 2000 Bill Nottingham <notting@redhat.com>
- move initscript back
- remove 'Using Samba' book from %%doc 
- move stuff to /etc/samba (#13708)
- default configuration tweaks (#13704)
- some logrotate tweaks

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Tue Jul 11 2000 Bill Nottingham <notting@redhat.com>
- fix logrotate script (#13698)

* Thu Jul  6 2000 Bill Nottingham <notting@redhat.com>
- fix initscripts req (prereq /etc/init.d)

* Wed Jul 5 2000 Than Ngo <than@redhat.de>
- add initdir macro to handle the initscript directory
- add a new macro to handle /etc/pam.d/system-auth

* Thu Jun 29 2000 Nalin Dahyabhai <nalin@redhat.com>
- enable Kerberos 5 and SSL support
- patch for duplicate profile.h headers

* Thu Jun 29 2000 Bill Nottingham <notting@redhat.com>
- fix init script

* Tue Jun 27 2000 Bill Nottingham <notting@redhat.com>
- rename samba logs (#11606)

* Mon Jun 26 2000 Bill Nottingham <notting@redhat.com>
- initscript munging

* Fri Jun 16 2000 Bill Nottingham <notting@redhat.com>
- configure the swat stuff usefully
- re-integrate some specfile tweaks that got lost somewhere

* Thu Jun 15 2000 Bill Nottingham <notting@redhat.com>
- rebuild to get rid of cups dependency

* Wed Jun 14 2000 Nalin Dahyabhai <nalin@redhat.com>
- tweak logrotate configurations to use the PID file in /var/lock/samba

* Sun Jun 11 2000 Bill Nottingham <notting@redhat.com>
- rebuild in new environment

* Thu Jun  1 2000 Nalin Dahyabhai <nalin@redhat.com>
- change PAM setup to use system-auth

* Mon May  8 2000 Bill Nottingham <notting@redhat.com>
- fixes for ia64

* Sat May  6 2000 Bill Nottingham <notting@redhat.com>
- switch to %%configure

* Wed Apr 26 2000 Nils Philippsen <nils@redhat.de>
- version 2.0.7

* Sun Mar 26 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- simplify preun

* Thu Mar 16 2000 Bill Nottingham <notting@redhat.com>
- fix yp_get_default_domain in autoconf
- only link against readline for smbclient
- fix log rotation (#9909)

* Fri Feb 25 2000 Bill Nottingham <notting@redhat.com>
- fix trigger, again.

* Mon Feb  7 2000 Bill Nottingham <notting@redhat.com>
- fix trigger.

* Fri Feb  4 2000 Bill Nottingham <notting@redhat.com>
- turn on quota support

* Mon Jan 31 2000 Cristian Gafton <gafton@redhat.com>
- rebuild to fox dependencies
- man pages are compressed

* Fri Jan 21 2000 Bill Nottingham <notting@redhat.com>
- munge post scripts slightly

* Wed Jan 19 2000 Bill Nottingham <notting@redhat.com>
- turn on mmap again. Wheee.
- ship smbmount on alpha

* Mon Dec  6 1999 Bill Nottingham <notting@redhat.com>
- turn off mmap. ;)

* Wed Dec  1 1999 Bill Nottingham <notting@redhat.com>
- change /var/log/samba to 0700
- turn on mmap support

* Thu Nov 11 1999 Bill Nottingham <notting@redhat.com>
- update to 2.0.6

* Fri Oct 29 1999 Bill Nottingham <notting@redhat.com>
- add a %%defattr for -common

* Tue Oct  5 1999 Bill Nottingham <notting@redhat.com>
- shift some files into -client
- remove /home/samba from package.

* Tue Sep 28 1999 Bill Nottingham <notting@redhat.com>
- initscript oopsie. killproc <name> -HUP, not other way around.

* Sun Sep 26 1999 Bill Nottingham <notting@redhat.com>
- script cleanups. Again.

* Wed Sep 22 1999 Bill Nottingham <notting@redhat.com>
- add a patch to fix dropped reconnection attempts

* Mon Sep  6 1999 Jeff Johnson <jbj@redhat.com>
- use cp rather than mv to preserve /etc/services perms (#4938 et al).
- use mktemp to generate /etc/tmp.XXXXXX file name.
- add prereqs on sed/mktemp/killall (need to move killall to /bin).
- fix trigger syntax (i.e. "samba < 1.9.18p7" not "samba < samba-1.9.18p7")

* Mon Aug 30 1999 Bill Nottingham <notting@redhat.com>
- sed "s|nawk|gawk|" /usr/bin/convert_smbpasswd

* Sat Aug 21 1999 Bill Nottingham <notting@redhat.com>
- fix typo in mount.smb

* Fri Aug 20 1999 Bill Nottingham <notting@redhat.com>
- add a %%trigger to work around (sort of) broken scripts in
  previous releases

* Mon Aug 16 1999 Bill Nottingham <notting@redhat.com>
- initscript munging

* Mon Aug  9 1999 Bill Nottingham <notting@redhat.com>
- add domain parsing to mount.smb

* Fri Aug  6 1999 Bill Nottingham <notting@redhat.com>
- add a -common package, shuffle files around.

* Fri Jul 23 1999 Bill Nottingham <notting@redhat.com>
- add a chmod in %%postun so /etc/services & inetd.conf don't become unreadable

* Wed Jul 21 1999 Bill Nottingham <notting@redhat.com>
- update to 2.0.5
- fix mount.smb - smbmount options changed again.........
- fix postun. oops.
- update some stuff from the samba team's spec file.

* Fri Jun 18 1999 Bill Nottingham <notting@redhat.com>
- split off clients into separate package
- don't run samba by default

* Mon Jun 14 1999 Bill Nottingham <notting@redhat.com>
- fix one problem with mount.smb script
- fix smbpasswd on sparc with a really ugly kludge

* Thu Jun 10 1999 Dale Lovelace <dale@redhat.com>
- fixed logrotate script

* Tue May 25 1999 Bill Nottingham <notting@redhat.com>
- turn of 64-bit locking on 32-bit platforms

* Thu May 20 1999 Bill Nottingham <notting@redhat.com>
- so many releases, so little time
- explicitly uncomment 'printing = bsd' in sample config

* Tue May 18 1999 Bill Nottingham <notting@redhat.com>
- update to 2.0.4a
- fix mount.smb arg ordering

* Fri Apr 16 1999 Bill Nottingham <notting@redhat.com>
- go back to stop/start for restart (-HUP didn't work in testing)

* Fri Mar 26 1999 Bill Nottingham <notting@redhat.com>
- add a mount.smb to make smb mounting a little easier.
- smb filesystems apparently don't work on alpha. Oops.

* Thu Mar 25 1999 Bill Nottingham <notting@redhat.com>
- always create codepages

* Tue Mar 23 1999 Bill Nottingham <notting@redhat.com>
- logrotate changes

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 3)

* Fri Mar 19 1999 Preston Brown <pbrown@redhat.com>
- updated init script to use graceful restart (not stop/start)

* Tue Mar  9 1999 Bill Nottingham <notting@redhat.com>
- update to 2.0.3

* Thu Feb 18 1999 Bill Nottingham <notting@redhat.com>
- update to 2.0.2

* Mon Feb 15 1999 Bill Nottingham <notting@redhat.com>
- swat swat

* Tue Feb  9 1999 Bill Nottingham <notting@redhat.com>
- fix bash2 breakage in post script

* Fri Feb  5 1999 Bill Nottingham <notting@redhat.com>
- update to 2.0.0

* Mon Oct 12 1998 Cristian Gafton <gafton@redhat.com>
- make sure all binaries are stripped

* Thu Sep 17 1998 Jeff Johnson <jbj@redhat.com>
- update to 1.9.18p10.
- fix %%triggerpostun.

* Tue Jul 07 1998 Erik Troan <ewt@redhat.com>
- updated postun triggerscript to check $0
- clear /etc/codepages from %%preun instead of %%postun

* Mon Jun 08 1998 Erik Troan <ewt@redhat.com>
- made the %%postun script a tad less agressive; no reason to remove
  the logs or lock file (after all, if the lock file is still there,
  samba is still running)
- the %%postun and %%preun should only exectute if this is the final
  removal
- migrated %%triggerpostun from Red Hat's samba package to work around
  packaging problems in some Red Hat samba releases

* Sun Apr 26 1998 John H Terpstra <jht@samba.anu.edu.au>
- minor tidy up in preparation for release of 1.9.18p5
- added findsmb utility from SGI package

* Wed Mar 18 1998 John H Terpstra <jht@samba.anu.edu.au>
- Updated version and codepage info.
- Release to test name resolve order

* Sat Jan 24 1998 John H Terpstra <jht@samba.anu.edu.au>
- Many optimisations (some suggested by Manoj Kasichainula <manojk@io.com>
- Use of chkconfig in place of individual symlinks to /etc/rc.d/init/smb
- Compounded make line
- Updated smb.init restart mechanism
- Use compound mkdir -p line instead of individual calls to mkdir
- Fixed smb.conf file path for log files
- Fixed smb.conf file path for incoming smb print spool directory
- Added a number of options to smb.conf file
- Added smbadduser command (missed from all previous RPMs) - Doooh!
- Added smbuser file and smb.conf file updates for username map


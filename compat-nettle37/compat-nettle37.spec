# Recent so-version, so we do not bump accidentally.
%global nettle_so_ver 8
%global hogweed_so_ver 6

%global suffix_ver 3.7
%global nettle_checksum c4de959abe62f96e5a02b43886e32315fe7b986fa78e81d0f6ce61e728d5e4e85fad237058b248943817e2d2f13c071989503ad78493ba26720a403675404338/

Name:           compat-nettle37
Version:        3.7.3
Release:        1%{?dist}
Summary:        A low-level cryptographic library

Group:          Development/Libraries
License:        LGPLv3+ or GPLv2+
URL:            http://www.lysator.liu.se/~nisse/nettle/
#Source0:        http://www.lysator.liu.se/~nisse/archive/%%{name}-%%{version}.tar.gz
Source0:        https://src.fedoraproject.org/lookaside/pkgs/nettle/nettle-%{version}-hobbled.tar.xz/sha512/%{nettle_checksum}/nettle-%{version}-hobbled.tar.xz

Patch0: 		https://git.centos.org/rpms/nettle/raw/c9-beta/f/SOURCES/nettle-3.7.2-suppress-maybe-uninit.patch

BuildRequires:  gmp-devel
BuildRequires:  m4
BuildRequires:  texinfo-tex
BuildRequires:  libtool
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  gettext-devel
Provides:       compat-nettle32 = %{version}-%{release}
Obsoletes:      compat-nettle32 < %{version}-%{release}
Provides:       compat-nettle34 = %{version}-%{release}
Obsoletes:      compat-nettle34 < %{version}-%{release}
Provides:       nettle = %{version}-%{release}

Requires(post): info
Requires(preun): info


%package devel
Summary:        Development headers for a low-level cryptographic library
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       gmp-devel%{?_isa}
Provides:       compat-nettle32-devel = %{version}-%{release}
Obsoletes:      compat-nettle32-devel < %{version}-%{release}
Provides:       compat-nettle34-devel = %{version}-%{release}
Obsoletes:      compat-nettle34-devel < %{version}-%{release}
Provides:       nettle-devel = %{version}-%{release}

%description
Nettle is a cryptographic library that is designed to fit easily in more
or less any context: In crypto toolkits for object-oriented languages
(C++, Python, Pike, ...), in applications like LSH or GNUPG, or even in
kernel space.

%description devel
Nettle is a cryptographic library that is designed to fit easily in more
or less any context: In crypto toolkits for object-oriented languages
(C++, Python, Pike, ...), in applications like LSH or GNUPG, or even in
kernel space.  This package contains the files needed for developing 
applications with nettle.


%prep
%setup -q -n nettle-%{version}
# Disable -ggdb3 which makes debugedit unhappy
sed s/ggdb3/g/ -i configure
sed 's/ecc-192.c//g' -i Makefile.in
sed 's/ecc-224.c//g' -i Makefile.in
sed 's/ecc-secp192r1.c//g' -i Makefile.in
sed 's/ecc-secp224r1.c//g' -i Makefile.in
%patch0 -p1

# https://stackoverflow.com/a/46769674/778517
sed -i 's/EVP_MD_CTX_new/EVP_MD_CTX_create/' examples/nettle-openssl.c
sed -i 's/EVP_MD_CTX_free/EVP_MD_CTX_destroy/' examples/nettle-openssl.c

%build
autoreconf -ifv
%configure --enable-shared --disable-arm-neon --enable-fat
%make_build


%install
%make_install
make install-shared DESTDIR=$RPM_BUILD_ROOT INSTALL="install -p"
#mkdir -p $RPM_BUILD_ROOT%{_infodir}
#install -p -m 644 nettle.info $RPM_BUILD_ROOT%{_infodir}/nettle-%{suffix_ver}.info
rm -f $RPM_BUILD_ROOT%{_libdir}/*.a
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
rm -f $RPM_BUILD_ROOT%{_infodir}/nettle.info
rm -f $RPM_BUILD_ROOT%{_bindir}/nettle-lfib-stream
rm -f $RPM_BUILD_ROOT%{_bindir}/pkcs1-conv
rm -f $RPM_BUILD_ROOT%{_bindir}/sexp-conv
rm -f $RPM_BUILD_ROOT%{_bindir}/nettle-hash
rm -f $RPM_BUILD_ROOT%{_bindir}/nettle-pbkdf2

chmod 0755 $RPM_BUILD_ROOT%{_libdir}/libnettle.so.%{nettle_so_ver}.*
chmod 0755 $RPM_BUILD_ROOT%{_libdir}/libhogweed.so.%{hogweed_so_ver}.*


%check
make check

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%doc AUTHORS NEWS README
%license COPYINGv2 COPYING.LESSERv3
%{_libdir}/libnettle.so.%{nettle_so_ver}
%{_libdir}/libnettle.so.%{nettle_so_ver}.*
%{_libdir}/libhogweed.so.%{hogweed_so_ver}
%{_libdir}/libhogweed.so.%{hogweed_so_ver}.*

%files devel
%doc descore.README nettle.html nettle.pdf
%{_includedir}/nettle
%{_libdir}/pkgconfig/*.pc
%{_libdir}/lib*.so


%changelog
* Sat Sep 19 2020 Sérgio Basto <sergio@serjux.com> - 3.4.1-4
- Devel package back to default location, as can't be installed along
  nettle-devel from system

* Sun Sep 13 2020 Sérgio Basto <sergio@serjux.com> - 3.4.1-3
- Improve packaging using pkgconfig and add export PKG_CONFIG_PATH
  (in /etc/profile.d/%{name}.sh)

* Wed Sep 02 2020 Sérgio Basto <sergio@serjux.com> - 3.4.1-2
- Fix suffix on binaries

* Sun Aug 30 2020 Sérgio Basto <sergio@serjux.com> - 3.4.1-1
- Update to 3.4.1

* Fri Jul 29 2016 Nikos Mavrogiannopoulos <nmav@redhat.com> - 3.2-2
- Imported nettle 3.2 from fedora 24.

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.15-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.15-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Apr 10 2008 Ian Weller <ianweller@gmail.com> 1.15-5
- Moved static lib to -static

* Mon Mar 24 2008 Ian Weller <ianweller@gmail.com> 1.15-4
- Added libraries and ldconfig

* Mon Feb 18 2008 Ian Weller <ianweller@gmail.com> 1.15-3
- Added provides -static to -devel

* Sun Feb 17 2008 Ian Weller <ianweller@gmail.com> 1.15-2
- Removed redundant requires
- Removed redundant documentation between packages
- Fixed license tag
- Fixed -devel description
- Added the static library back to -devel
- Added make clean

* Fri Feb 08 2008 Ian Weller <ianweller@gmail.com> 1.15-1
- First package build.

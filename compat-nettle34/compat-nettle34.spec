%global suffix_ver 3.4
%global nettle_checksum sha512/9a5b4c316222f22feb692106ceae299c2b59229ef96cac1739095c65c9ddee4b1d542579e5b49d4863bd6a8c093611f0fdd1c7cb3251844c85b7e089e406ffc5

Name:           compat-nettle34
Version:        3.4.1
Release:        4%{?dist}
Summary:        A low-level cryptographic library

Group:          Development/Libraries
License:        LGPLv3+ or GPLv2+
URL:            http://www.lysator.liu.se/~nisse/nettle/
#Source0:        http://www.lysator.liu.se/~nisse/archive/%%{name}-%%{version}.tar.gz
Source0:        https://src.fedoraproject.org/lookaside/pkgs/nettle/nettle-%{version}-hobbled.tar.xz/%{nettle_checksum}/nettle-%{version}-hobbled.tar.xz

Patch0:		https://git.centos.org/rpms/nettle/raw/c8s/f/SOURCES/nettle-3.3-remove-ecc-testsuite.patch
Patch1:		nettle-3.4.1-c99.patch

BuildRequires:  gmp-devel
BuildRequires:  m4
BuildRequires:  texinfo-tex
BuildRequires:  libtool
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  gettext-devel
Provides:       compat-nettle32 = %{version}-%{release}
Obsoletes:      compat-nettle32 < %{version}-%{release}
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
%patch0 -p1
%patch1 -p1


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
chmod 0755 $RPM_BUILD_ROOT%{_libdir}/libnettle.so.6.*
chmod 0755 $RPM_BUILD_ROOT%{_libdir}/libhogweed.so.4.*

# Rename some files to avoid conflicts with base packages
mv $RPM_BUILD_ROOT%{_infodir}/nettle.info $RPM_BUILD_ROOT%{_infodir}/nettle-%{suffix_ver}.info
mv $RPM_BUILD_ROOT%{_bindir}/nettle-lfib-stream $RPM_BUILD_ROOT%{_bindir}/nettle-lfib-stream-%{suffix_ver}
mv $RPM_BUILD_ROOT%{_bindir}/pkcs1-conv $RPM_BUILD_ROOT%{_bindir}/pkcs1-conv-%{suffix_ver}
mv $RPM_BUILD_ROOT%{_bindir}/sexp-conv $RPM_BUILD_ROOT%{_bindir}/sexp-conv-%{suffix_ver}
mv $RPM_BUILD_ROOT%{_bindir}/nettle-hash $RPM_BUILD_ROOT%{_bindir}/nettle-hash-%{suffix_ver}
mv $RPM_BUILD_ROOT%{_bindir}/nettle-pbkdf2 $RPM_BUILD_ROOT%{_bindir}/nettle-pbkdf2-%{suffix_ver}


%check
make check

%post
/sbin/install-info %{_infodir}/nettle-%{suffix_ver}.info %{_infodir}/dir || :
/sbin/ldconfig

%preun
if [ $1 = 0 ]; then
  /sbin/install-info --delete %{_infodir}/nettle-%{suffix_ver}.info %{_infodir}/dir || :
fi

%postun -p /sbin/ldconfig

%files
%doc AUTHORS NEWS README TODO
%license COPYINGv2 COPYING.LESSERv3
%{_infodir}/nettle-%{suffix_ver}.info.gz
%{_bindir}/nettle-lfib-stream-%{suffix_ver}
%{_bindir}/pkcs1-conv-%{suffix_ver}
%{_bindir}/sexp-conv-%{suffix_ver}
%{_bindir}/nettle-hash-%{suffix_ver}
%{_bindir}/nettle-pbkdf2-%{suffix_ver}
%{_libdir}/libnettle.so.6
%{_libdir}/libnettle.so.6.*
%{_libdir}/libhogweed.so.4
%{_libdir}/libhogweed.so.4.*

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

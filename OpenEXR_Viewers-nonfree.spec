%global _default_patch_fuzz 2

# nVidia Cg toolkit is not free
%define with_Cg         1
%if %with_Cg
%define real_name       OpenEXR_Viewers-nonfree
%define V_suffix        -nonfree
%define priority        10
%else
%define real_name       OpenEXR_Viewers
%define V_suffix        -fedora
%define priority        5
%endif

%if 0%{?fedora} < 21
# https://bugzilla.redhat.com/1017873
%define openexr_ctl 1
%endif

Name:           %{real_name}
Version:        2.2.0
Release:        3%{?dist}
Summary:        Viewers programs for OpenEXR

Group:          Applications/Multimedia
License:        AMPAS BSD
URL:            http://www.openexr.com
Source0:        http://download.savannah.nongnu.org/releases/openexr/openexr_viewers-%{version}.tar.gz
# missing header from ^^, should be fixed/included in subsequent releases
Source1:        namespaceAlias.h
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
ExclusiveArch:  i686 x86_64

Patch1: openexr_viewers-2.0.1-dso.patch
# fix ftbfs due to missing header
Patch2: openexr_viewers-2.1.0-headers.patch

BuildRequires:  libtool

BuildRequires:  fltk-devel >= 1.1
BuildRequires:  pkgconfig(OpenEXR) >= 2.1
%if %with_Cg
BuildRequires:  Cg
BuildRequires:  freeglut-devel
Provides: OpenEXR_Viewers = %{version}
%else
BuildConflicts:  Cg
%endif

%if 0%{?openexr_ctl}
BuildRequires:  OpenEXR_CTL-devel
BuildRequires:  OpenEXR_CTL
Requires:  OpenEXR_CTL
%endif
Requires(post): /usr/sbin/alternatives
Requires(preun): /usr/sbin/alternatives


%description
exrdisplay is a simple still image viewer that optionally applies color
transforms to OpenEXR images, using ctl as explained in this document:
doc/OpenEXRViewers.pdf

%if %with_Cg
playexr is a program that plays back OpenEXR image sequences, optionally
with CTL support, applying rendering and display transforms in line with
the current discussions at the AMPAS Image Interchange Framework committee
(September 2006).

This is the nonfree version compiled with nVidia Cg support
See: http://developer.nvidia.com/object/cg_toolkit.html
%else

%package docs
Summary:        Documentation for %{name}
Group:          Documentation

%description docs
This package contains documentation files for %{name}.
%endif

%prep
%setup -q -n openexr_viewers-%{version}

%patch1 -p1 -b .dso
cp -n %{SOURCE1} exrdisplay/namespaceAlias.h
#patch2 -p1 -b .header

%if %{_lib} == lib64
sed -i -e 's|ACTUAL_PREFIX/lib/CTL|ACTUAL_PREFIX/lib64/CTL|' configure.ac
%endif
#Needed for patch1 and to update CTL compiler test
#autoconf
./bootstrap
sed -i -e 's|#include <vector>\n    using namespace Ctl|#include <vector>\n    #include <cstdlib>\nusing namespace Ctl|' configure


%build
export CXXFLAGS="$RPM_OPT_FLAGS -L%{_libdir}"
%configure  --disable-static \
  --disable-openexrtest \
  --disable-openexrctltest \
%if %with_Cg
  --with-cg-prefix=%{_prefix}
%endif

# Missing libs for playexr
sed -i -e 's|LIBS =|LIBS = -lglut|' playexr/Makefile

make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

# Remove the config.h - uneeded afaik
rm -rf $RPM_BUILD_ROOT%{_includedir}

# move the binary
mv $RPM_BUILD_ROOT%{_bindir}/exrdisplay $RPM_BUILD_ROOT%{_bindir}/exrdisplay%{V_suffix}

# Removing installed docs
rm -rf $RPM_BUILD_ROOT%{_datadir}/doc

# Owernship of the alternative provides
touch $RPM_BUILD_ROOT%{_bindir}/exrdisplay

%clean
rm -rf $RPM_BUILD_ROOT

%post
alternatives --install %{_bindir}/exrdisplay exrdisplay %{_bindir}/exrdisplay%{V_suffix} %{priority} ||:


%preun
if [ $1 -eq 0 ]; then
  alternatives --remove exrdisplay %{_bindir}/exrdisplay%{V_suffix} || :
fi

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING NEWS README
%ghost %{_bindir}/exrdisplay
%{_bindir}/exrdisplay%{V_suffix}
%if %with_Cg
%{_bindir}/playexr
%else

%files docs
%defattr(-,root,root,-)
%doc doc/OpenEXRViewers.odt doc/OpenEXRViewers.pdf
%endif

%changelog
* Thu Aug 31 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 2.2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Mar 25 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 2.2.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Jul 20 2016 Leigh Scott <leigh123linux@googlemail.com> - 2.2.0-1
- 2.2.0

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Jun 06 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Nov 27 2013 Rex Dieter <rdieter@fedoraproject.org> 2.1.0-1
- 2.1.0

* Fri Oct 11 2013 Rex Dieter <rdieter@fedoraproject.org> 2.0.1-3
- OpenEXR_Viewers FTBFS: ImplicitDSO Linking issues (#1017880)

* Thu Oct 10 2013 Rex Dieter <rdieter@fedoraproject.org> 2.0.1-2
- make OpenEXR_CTL support optional (since it doesn't support openexr-2.x yet)

* Sat Oct 05 2013 Nicolas Chauvet <kwizart@gmail.com> - 2.0.1-1
- Update to 2.0.1

* Sat Sep 14 2013 Bruno Wolff III <bruno@wolff.to> - 1.0.2-13
- Rebuild for ilmbase related soname bumps

* Fri Aug 02 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.2-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Mar 11 2013 Rex Dieter <rdieter@fedoraproject.org> - 1.0.2-11
- rebuild (OpenEXR)

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.2-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.2-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.2-8
- Rebuilt for c++ ABI breakage

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Jun 24 2011 Rex Dieter <rdieter@fedoraproject.org> 1.0.2-6
- FTBFS OpenEXR_Viewers-1.0.2-3.fc15: ImplicitDSOLinking (#716011)

* Fri May 27 2011 Nicolas Chauvet <kwizart@gmail.com> - 1.0.2-5
- Update gcc44 patch
- Rebuild for new fltk
- Drop old Obsoletes OpenEXR-utils < 1.6.0

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Sep 05 2010 Nicolas Chauvet <kwizart@gmail.com> - 1.0.2-2
- Fix CTL Module search path on lib64
- Fix OpenEXR_CTL detection at build time.

* Mon Aug 23 2010 Nicolas Chauvet <kwizart@gmail.com> - 1.0.2-1
- Update to 1.0.2

* Tue Oct 20 2009 kwizart < kwizart at gmail.com > - 1.0.1-7
- Rebuild for F-12

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Feb 12 2009 kwizart < kwizart at gmail.com > - 1.0.1-4
- Rebuild for gcc44

* Fri Oct 17 2008 kwizart < kwizart at gmail.com > - 1.0.1-3
- Rebuild for F-10

* Sat May 10 2008 kwizart < kwizart at gmail.com > - 1.0.1-2
- Ghost the alternative provides
- Obsoletes OpenEXR-utils

* Wed Jan  9 2008 kwizart < kwizart at gmail.com > - 1.0.1-1
- Initial package for Fedora


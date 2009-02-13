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

Name:           %{real_name}
Version:        1.0.1
Release:        4%{?dist}.1
Summary:        Viewers programs for OpenEXR

Group:          Applications/Multimedia
License:        AMPAS BSD
URL:            http://www.openexr.com
Source0:        http://download.savannah.nongnu.org/releases/openexr/openexr_viewers-%{version}.tar.gz
Patch0:         openexr_viewers-1.0.1-gcc43.patch
Patch1:         openexr_viewers-1.0.1-gcc44.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  OpenEXR_CTL-devel
BuildRequires:  OpenEXR_CTL
BuildRequires:  fltk-devel
%if %with_Cg
ExclusiveArch:  i386 x86_64
BuildRequires:  Cg
BuildRequires:  freeglut-devel
Provides: OpenEXR_Viewers = %{version}
%else
BuildConflicts:  Cg
%endif
# Last version was in F-7 - Can be dropped in F-10
Obsoletes: OpenEXR-utils < 1.6.0

Requires:  OpenEXR_CTL
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
%patch0 -p1 -b .gcc43
%patch1 -p1 -b .gcc44


%build
export CXXFLAGS="$RPM_OPT_FLAGS -L%{_libdir}"
%configure  --disable-static \
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
* Thu Feb 12 2009 kwizart < kwizart at gmail.com > - 1.0.1-4.1
- Rebuild for gcc44
- Restore build for i386 and x86_64 for now.

* Wed Oct 15 2008 kwizart < kwizart at gmail.com > - 1.0.1-3
- Fix: we are -nonfree
- Cg only exist on i386 x86_64

* Sat May 10 2008 kwizart < kwizart at gmail.com > - 1.0.1-2
- Ghost the alternative provides
- Obsoletes OpenEXR-utils

* Wed Jan  9 2008 kwizart < kwizart at gmail.com > - 1.0.1-1
- Initial package for Fedora


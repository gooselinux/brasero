Name:      brasero
Version:   2.28.3
Release:   6%{?dist}
Summary:   Gnome CD/DVD burning application
Group:     Applications/Multimedia
License:   GPLv2+
URL:       http://www.gnome.org/projects/brasero/
Source0:   http://ftp.gnome.org/pub/GNOME/sources/brasero/2.28/%{name}-%{version}.tar.bz2
Source1:   nautilus-burn-icons.tar.bz2

# upstream translations
# https://bugzilla.redhat.com/show_bug.cgi?id=576069
Patch0: brasero-translations.patch

# Make docs show up in rarian/yelp
Patch1: brasero-doc-category.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  glib2-devel >= 2.15.6

BuildRequires:  gettext intltool gtk-doc
BuildRequires:  desktop-file-utils
BuildRequires:  GConf2-devel >= 2.0.0
BuildRequires:  libgnomeui-devel >= 2.10.0
BuildRequires:  gstreamer-devel >= 0.10.15
BuildRequires:  gstreamer-plugins-base-devel >= 0.10.0
BuildRequires:  totem-pl-parser-devel >= 2.22.0
BuildRequires:  libnotify-devel >= 0.3.0
BuildRequires:  libxml2-devel >= 2.6.0
BuildRequires:  dbus-glib-devel >= 0.7.2
BuildRequires:  gnome-doc-utils >= 0.3.2
BuildRequires:  scrollkeeper
BuildRequires:  libxslt
BuildRequires:  libburn-devel >= 0.4.0
BuildRequires:  libisofs-devel >= 0.6.4
BuildRequires:  nautilus-devel >= 2.22.2
BuildRequires:  libSM-devel
BuildRequires:  unique-devel

# needed explicit require, please see bug 596833
Requires:  brasero-libs = %{version}-%{release}

Requires:  dvd+rw-tools
Requires:  cdrecord
Requires:  mkisofs
Requires:  cdda2wav
%ifnarch s390 s390x
Requires:  cdrdao
%endif

Requires(post):    shared-mime-info
Requires(postun):  shared-mime-info
Requires(pre):     GConf2
Requires(post):    GConf2
Requires(preun):   GConf2

%description
Simple and easy to use CD/DVD burning application for the Gnome
desktop.


%package   libs
Summary:   Libraries for %{name}
Group:     System Environment/Libraries
Obsoletes: nautilus-cd-burner-libs < 2.25.4
Requires:  %{name} = %{version}-%{release}


%description libs
The %{name}-libs package contains the runtime shared libraries for
%{name}.


%package   nautilus
Summary:   Nautilus extension for %{name}
Group:     User Interface/Desktops

Provides:  nautilus-cd-burner = %{version}-%{release}
Obsoletes: nautilus-cd-burner < 2.25.4
Requires:  %{name} = %{version}-%{release}

%description nautilus
The %{name}-nautilus package contains the brasero nautilus extension.


%package        devel
Summary:        Headers for developing programs that will use %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       pkgconfig
Obsoletes:      nautilus-cd-burner-devel < 2.25.4


%description devel
This package contains the static libraries and header files needed for
developing brasero applications.


%prep
%setup -q
%patch0 -p1 -b .translations
%patch1 -p1 -b .doc-category

%build
%configure \
	--enable-nautilus \
	--enable-libburnia \
	--enable-search \
	--enable-playlist \
	--enable-preview \
	--enable-inotify \
	--disable-caches \
	--disable-static \
	--disable-schemas-install
sed -i -e 's! -shared ! -Wl,--as-needed\0!g' libtool
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install DESTDIR=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -type f -name "*.la" -exec rm -f {} ';'

%find_lang %{name}

sed -i 's/cd:x/cd;x/' $RPM_BUILD_ROOT%{_datadir}/applications/%{name}.desktop
sed -i -e 's/Icon=brasero/Icon=nautilus-burn/' \
    $RPM_BUILD_ROOT%{_datadir}/applications/%{name}-nautilus.desktop

desktop-file-install --vendor ""                   \
    --dir $RPM_BUILD_ROOT%{_datadir}/applications  \
    $RPM_BUILD_ROOT%{_datadir}/applications/%{name}.desktop

desktop-file-install --vendor ""                   \
    --dir $RPM_BUILD_ROOT%{_datadir}/applications  \
    $RPM_BUILD_ROOT%{_datadir}/applications/%{name}-nautilus.desktop

tar xf %{SOURCE1} -C $RPM_BUILD_ROOT%{_datadir}/icons

%clean
rm -rf $RPM_BUILD_ROOT


%post
umask 022
update-mime-database %{_datadir}/mime &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor || :
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
  %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi
update-desktop-database &> /dev/null ||:
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/%{name}.schemas > /dev/null  || :
killall -HUP gconfd-2 &>/dev/null || :


%post libs -p /sbin/ldconfig


%postun
umask 022
update-mime-database %{_datadir}/mime &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor || :
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
  %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi
update-desktop-database &> /dev/null ||:
if [ "$1" -gt 1 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/%{name}.schemas >/dev/null || :
  killall -HUP gconfd-2 &>/dev/null || :
fi


%postun libs -p /sbin/ldconfig


%preun
if [ "$1" -eq 0 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/%{name}.schemas > /dev/null || :
  killall -HUP gconfd-2 &>/dev/null || :
fi


%files -f %{name}.lang
%defattr(-,root,root,-)
%doc AUTHORS COPYING NEWS README
%{_mandir}/man1/%{name}.*
%{_bindir}/*
%{_libdir}/%{name}
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/applications/%{name}-copy-*.desktop
%{_datadir}/gnome/help/%{name}
%{_datadir}/omf/%{name}
%{_datadir}/icons/hicolor/*/apps/*
%{_datadir}/mime/packages/*
%{_sysconfdir}/gconf/schemas/%{name}.schemas


%files libs
%defattr(-,root,root,-)
%{_libdir}/*.so.*


%files nautilus
%defattr(-,root,root,-)
%{_libdir}/nautilus/extensions-2.0/*.so
%{_datadir}/applications/brasero-nautilus.desktop


%files devel
%defattr(-,root,root,-)
%doc %{_datadir}/gtk-doc/html/libbrasero-media
%doc %{_datadir}/gtk-doc/html/libbrasero-burn
%doc ChangeLog
%{_includedir}/brasero
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc


%changelog
* Fri May 28 2010 Tomas Bzatek <tbzatek@redhat.com> 2.28.3-6
- Fix requires in subpackages

* Mon May  3 2010 Matthias Clasen <mclasen@redhat.com> 2.28.3-5
- Use nicer icons for CD/DVD Burner
Resolves: #588542

* Mon May  3 2010 Matthias Clasen <mclasen@redhat.com> 2.28.3-4
- Make docs show up in yelp
Resolves: #588518

* Mon May  3 2010 Matthias Clasen <mclasen@redhat.com> 2.28.3-3
- Update translations
Resolves: #576069

* Fri Jan  8 2010 Tomas Bzatek <tbzatek@redhat.com> 2.28.3-2
- Spec file cleanup

* Tue Dec 15 2009 Tomas Bzatek <tbzatek@redhat.com> 2.28.3-1
- Update to 2.28.3

* Wed Dec  2 2009 Matthias Clasen <mclasen@redhat.com> 2.28.2-4
- Make the libbeagle dep more automatic

* Thu Nov 12 2009 Matthias Clasen <mclasen@redhat.com> 2.28.2-3
- Obsolete nautilus-cd-burner-devel and -libs as well

* Mon Oct 26 2009 Matthias Clasen <mclasen@redhat.com> 2.28.2-2
- Avoid a stray underline in a button label

* Tue Oct 20 2009 Matthias Clasen <mclasen@redhat.com> 2.28.2-1
- Update to 2.28.2

* Wed Oct 07 2009 Bastien Nocera <bnocera@redhat.com> 2.28.1-2
- Fix command-line parsing (#527484)

* Mon Oct  5 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.1-1
- Update to 2.28.1, fixes a number of crashes and other serious bugs:
 - Fix a crash when we try to download a missing gstreamer plugin through PK
 - Don't fail if a drive cannot be checksumed after a burn
 - Fix a data corruption when libisofs was used for a dummy session
 - Fix #596625: brasero crashed with SIGSEGV in brasero_track_data_cfg_add
 - Fix progress reporting
 ...

* Fri Oct  2 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-2
- Fix ejecting after burning

* Tue Sep 22 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-1
- Update to 2.28.0

* Fri Sep 11 2009 Karsten Hopp <karsten@redhat.com> 2.27.92-2
- fix requirements on s390, s390x where we don't have cdrdao

* Mon Sep  7 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.92-1
- Update to 2.27.92

* Tue Aug 25 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.91-1
- Update to 2.27.91

* Mon Aug 10 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.90-1
- Update to 2.27.90

* Mon Aug  3 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.5-2
- Fix a nautilus segfault when burning  

* Tue Jul 28 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.5-1
- Update to 2.27.5

* Sun Jul 26 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.4-3
- Move ChangeLog to -devel to save some space

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.27.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 14 2009 Matthias Clasen <mclasen@redhat.com> 2.27.4-1
- Update to 2.27.4

* Tue Jun 16 2009 Matthias Clasen <mclasen@redhat.com> 2.27.3-1
- Update to 2.27.3

* Wed May 27 2009 Bastien Nocera <bnocera@redhat.com> 2.27.2-1
- Update to 2.27.2

* Tue May 26 2009 Bastien Nocera <bnocera@redhat.com> 2.27.1-2
- Add missing unique-devel BR

* Mon May 18 2009 Bastien Nocera <bnocera@redhat.com> 2.27.1-1
- Update to 2.27.1

* Fri May  1 2009 Bill Nottingham <notting@redhat.com> - 2.26.1-3
- require main package in brasero-nautilus (#498632)

* Fri Apr 17 2009 Denis Leroy <denis@poolshark.org> - 2.26.1-2
- Obsoletes nautilus-cd-burner

* Tue Apr 14 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-1
- Update to 2.26.1
- See http://download.gnome.org/sources/brasero/2.26/brasero-2.26.1.news

* Mon Apr 13 2009 Denis Leroy <denis@poolshark.org> - 2.26.0-2
- Removed duplicate desktop source

* Sun Mar 29 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-1
- Update to 2.26.0

* Mon Mar 02 2009 - Bastien Nocera <bnocera@redhat.com> - 2.25.91.2-3
- Fix icon and Bugzilla component

* Mon Mar 02 2009 - Bastien Nocera <bnocera@redhat.com> - 2.25.91.2-2
- Fix regressions in burn:/// and blank media handling

* Tue Feb 24 2009 Denis Leroy <denis@poolshark.org> - 2.25.91.2-1
- Update to upstream 2.25.91.2
- Dvdcss patch upstreamed
- Split nautilus extension into subpackage (#485918)

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.90-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Feb  7 2009 Denis Leroy <denis@poolshark.org> - 2.25.90-2
- Added patch to fix dynamic load of libdvdcss (#484413)

* Tue Feb  3 2009 Denis Leroy <denis@poolshark.org> - 2.25.90-1
- Update to upstream 2.25.90
- Split media library into separate RPM (#483754)
- Added patch to validate desktop files

* Tue Jan 20 2009 Denis Leroy <denis@poolshark.org> - 0.9.1-1
- Update to upstream 0.9.1
- Added development package

* Tue Dec 16 2008 Denis Leroy <denis@poolshark.org> - 0.8.3-1
- Update to upstream 0.8.4
- Enabled nautilus extension

* Mon Sep 15 2008 Denis Leroy <denis@poolshark.org> - 0.8.2-1
- Update to upstream 0.8.2

* Wed Aug 27 2008 Denis Leroy <denis@poolshark.org> - 0.8.1-1
- Update to upstream 0.8.1
- Desktop patch upstreamed

* Sun Jul  6 2008 Denis Leroy <denis@poolshark.org> - 0.7.91-1
- Update to unstable 0.7.91
- open flags patch upstreamed

* Wed Jun 11 2008 Denis Leroy <denis@poolshark.org> - 0.7.90-1
- Update to unstable 0.7.90
- Added patch to validate desktop file
- BRs updated

* Fri May 16 2008 Denis Leroy <denis@poolshark.org> - 0.7.1-4
- Rebuild for new totem-pl-parser

* Sat Feb 23 2008 Denis Leroy <denis@poolshark.org> - 0.7.1-3
- Fixed desktop mime field

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.7.1-2
- Autorebuild for GCC 4.3

* Tue Jan 29 2008 Denis Leroy <denis@poolshark.org> - 0.7.1-1
- Update to 0.7.1 upstream, bugfix release

* Sun Dec 30 2007 Denis Leroy <denis@poolshark.org> - 0.7.0-1
- Update to upstream 0.7.0, updated BRs
- Forward-ported open() permission patch

* Mon Dec 10 2007 Denis Leroy <denis@poolshark.org> - 0.6.1-4
- Changed totem-devel req to totem-pl-parser-devel

* Sun Dec  9 2007 Denis Leroy <denis@poolshark.org> - 0.6.1-3
- Rebuild with new libbeagle

* Fri Nov  9 2007 Denis Leroy <denis@poolshark.org> - 0.6.1-2
- Rebuild to pick up new totem version (#361361)

* Sat Aug 25 2007 Denis Leroy <denis@poolshark.org> - 0.6.1-1
- Update to upstream version 0.6.1
- Filter UI patch is now upstream

* Fri Aug 17 2007 Denis Leroy <denis@poolshark.org> - 0.6.0-2
- Updated License tag
- Fixed open() O_CREAT problem

* Fri Aug 10 2007 Denis Leroy <denis@poolshark.org> - 0.6.0-1
- Update to 0.6.0
- Removed libburn support until it compiles against libisofs 0.2.8
- Fixed project URL
- Added patch to port to new Gtk+ tooltip interface
- Added patch to fix filter dialog crash

* Sun Jun  3 2007 Denis Leroy <denis@poolshark.org> - 0.5.2-4
- Removed beagle support for ppc64

* Tue May 22 2007 Denis Leroy <denis@poolshark.org> - 0.5.2-3
- Added umask 022 to scriptlets (#230781)

* Mon May 21 2007 Denis Leroy <denis@poolshark.org> - 0.5.2-2
- Rebuild to pick up new totem library

* Mon Feb 26 2007 Denis Leroy <denis@poolshark.org> - 0.5.2-1
- Update to 0.5.2
- Removed libisofs patch, now upstream

* Wed Jan 17 2007 Denis Leroy <denis@poolshark.org> - 0.5.1-2
- Added patch to support libisofs.so.4 and libburn.so.6

* Thu Nov 16 2006 Denis Leroy <denis@poolshark.org> - 0.5.1-1
- Update to 0.5.1

* Sun Oct 29 2006 Denis Leroy <denis@poolshark.org> - 0.5.0-1
- Update to 0.5.0
- Updated icon paths
- Added gconf schemas sections

* Tue Oct  3 2006 Denis Leroy <denis@poolshark.org> - 0.4.4-3
- fixed homepage URL

* Tue Sep 26 2006 Denis Leroy <denis@poolshark.org> - 0.4.4-2
- BRs cleanup

* Fri Sep 22 2006 Denis Leroy <denis@poolshark.org> - 0.4.4-1
- First version
foo

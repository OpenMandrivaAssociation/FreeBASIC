%bcond_without bootstrap

%global oname FreeBASIC
%global name %(echo %oname | tr [:upper:] [:lower:])

# set arch
%ifarch x86_64
%global fbarch x86_64
%else
%global fbarch x86
%endif

# compiler name
%global compiler fbc

Summary:	A FreeBASIC compiler
Name:		%{name}
Version:	1.10.1
Release:	1
License:	GPLv2+ and LGPLv2+
Group:		Development/Other
Url:		https://freebasic.net
%if ! %{with bootstrap}
Source0:	https://download.sourceforge.net/fbc/FreeBASIC-%{version}-source.tar.xz
%else
Source0:	https://download.sourceforge.net/fbc/FreeBASIC-%{version}-source-bootstrap.tar.xz
%endif
Patch0:		freebasic-1.10.1-makefile.patch
Patch1:		freebasic-1.10.1-fbdoc_makefile.patch
Patch2:		freebasic-1.10.1-fbhelp_path.patch

BuildRequires:	binutils
BuildRequires:	gpm-devel
%if ! %{with bootstrap}
BuildRequires:	freebasic
%endif
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xext)
BuildRequires:	pkgconfig(xpm)
BuildRequires:	pkgconfig(xrandr)
BuildRequires:	pkgconfig(xrender)
BuildRequires:	pkgconfig(libffi)
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(glu)
BuildRequires:	pkgconfig(libcurl)
BuildRequires:	pkgconfig(mariadb)
BuildRequires:	pkgconfig(libpcre)

Requires:	%{name}-rtlib = %{version}
Requires:	%{name}-gfxlib2 = %{version}
%rename		%{compiler}

%description
%{oname} is a free, easy-to-use tool to help you collect, organize, cite,
and share your research sources.

%files
%license doc/lgpl.txt
%doc changelog.txt readme.txt todo.txt
%{_bindir}/%{compiler}
%{_includedir}/freebasic/
%{_datadir}/freebasic/examples/
%{_datadir}/pixmaps/%{compiler}.xpm
%{_iconsdir}/hicolor/*/apps/%{compiler}*.png
%{_iconsdir}/hicolor/*/apps/%{compiler}*.svg
%{_mandir}/man1/%{compiler}.1.*

#--------------------------------------------------------------------

%package rtlib
Summary:	FreeBASIC run-time library
Group:		Development/Other

%description rtlib
This package contains the run-time library
for progams written in %{oname}.

%files rtlib
%license doc/lgpl.txt
%{_libdir}/freebasic/linux-%{fbarch}/fbextra.x
%{_libdir}/freebasic/linux-%{fbarch}/fbrt0.o
%{_libdir}/freebasic/linux-%{fbarch}/fbrt0pic.o
%{_libdir}/freebasic/linux-%{fbarch}/libfb.a
%{_libdir}/freebasic/linux-%{fbarch}/libfbmt.a
%{_libdir}/freebasic/linux-%{fbarch}/libfbpic.a
%{_libdir}/freebasic/linux-%{fbarch}/libfbmtpic.a

#--------------------------------------------------------------------

%package gfxlib2
Summary:	FreeBASIC run-time library
Group:		Development/Other
#Requires:	%{name}-rtlib = %{version}
%rename		%{compiler}-gfxlib2

%description gfxlib2
This package contains the graphics library
for progams written in %{oname}.

%files gfxlib2
%license doc/lgpl.txt
%{_libdir}/freebasic/linux-%{fbarch}/libfbgfx.a
%{_libdir}/freebasic/linux-%{fbarch}/libfbgfxmt.a
%{_libdir}/freebasic/linux-%{fbarch}/libfbgfxpic.a
%{_libdir}/freebasic/linux-%{fbarch}/libfbgfxmtpic.a

#---------------------------------------------------------------------

%package doc-html
Summary:	Free BASIC run-time library
Group:		Development/Other
Buildarch:	noarch
%rename		%{compiler}-doc-html

%description doc-html
This package contains the HTML manual for %{oanme} langauge.

%files doc-html
%docdir %{_docdir}/freebasic/html/
%{_docdir}/freebasic/html/*
%doc doc/lgpl.txt

#--------------------------------------------------------------------

%package -n fbhelp
Summary:	FreeBASIC fbhelp
Group:		Development/Other

%description -n fbhelp
Old-style utility for access to %{oname} documentation.

%files -n fbhelp
%license doc/lgpl.txt
%{_bindir}/fbhelp
%{_datadir}/fbhelp/fbhelp/

#---------------------------------------------------------------------

%prep
%autosetup -p1 -n %{oname}-%{version}-source%{?with_bootstrap:\-bootstrap}

# remove per-built binaries
find . \( -name \*.a -o -name \*.o -o -name \*.so -o -name fbc \) -type f -delete
find . -name deleteme.txt -type f -delete

# fix path for 64bit archs
%if %{with bootstrap}
%if "%{_lib}" == "lib64"
sed -i -e 's|"lib"|"lib64"|g' bootstrap/linux-x86_64/fbc.c
%endif
%endif

%build
%setup_compile_flags
export CFLAGS="${optflags} -std=gnu89"
export CXXFLAGS="${optflags} -std=gnu89"

export CC=gcc
export CXX=g++

# be verbose
#export V=1

%if "%{_lib}" == "lib64"
export ENABLE_LIB64=1
%endif

# compiler falgs
FBCFLAGS=" -maxerr 1 -w all -g -RR -R -asm att"
FBFLAGS=" -i inc -g"

# GFX flag for fbhelp
GFXFLAG="GFX=1"

# compiler target
TARGET="linux"

# enable suffix
# ENABLE_PREFIX=1
# ENABLE_SUFFIX=-%{version}

%if %{with bootstrap}
FBC="./bootstrap/%{compiler}"
%else
FBC="%{_bindir}/%{compiler}"
%endif

# run-time lib
%make_build rtlib CC="${CC}" CFLAGS="${CFLAGS}"

# graphic lib
%make_build gfxlib2 CC="${CC}" CFLAGS="${CFLAGS}"

# static compiler from C/ASM with related C libs
%if %with bootstrap
%make_build bootstrap FBFLAGS+=" -gen gas64" CC="${CC}" BOOTSTRAP_CFLAGS="${CFLAGS}"
#make_build clean-compiler
%endif

# complier
%make_build compiler FBC="${FBC}" FBFLAGS="${FBFLAGS}" FBCFLAGS="${FBCFLAGS}" CC="${CC}" CFLAGS="${CFLAGS}"

# clean bootstrap
%if %{with bootstrap}
%make_build clean-bootstrap
%endif

# from here use the just compiled compiler
FBC=./bin/fbc

# fbhelp
%make_build -C doc/fbhelp TARGET=${TARGET} FBC=../../"${FBC}" FBCFLAGS="${FBCFLAGS} -i ../../inc" "${GFXFLAG}"

# fbdoc
%make_build -C doc/fbdoc FBC="../../${FBC}" FBFLAGS="${FBCFLAGS} -i ../../inc -exx -g -i ../libfbdoc"

# mkfbhelp
%make_build -C doc/makefbhelp FBC="../../${FBC}" FBFLAGS="${FBCFLAGS} -i ../../inc"

# manual in various format
#	html
%make_build -C doc/manual FB-manual-%{version}-html.zip
#	fbhelp
#make -C doc/manual fbhelp.daz
%make_build -C doc/manual FB-manual-%{version}-fbhelp.zip
#	txt
#make -C doc/manual FB-manual-%{version}.txt
%make_build -C doc/manual FB-manual-%{version}-txt.zip
#	wakka
##make -C doc/manual FB-manual-%{version}-wakka.zip
#	chm format (FIXME: substitute hhc with ... )
#make -C doc/manual FB-manual-%{version}.chm
#make -C doc/manual FB-manual-%{version}-chm.zip

%install
%if "%{_lib}" == "lib64"
export ENABLE_LIB64=1
%endif

# compiler
%make_install install-compiler prefix="%{_prefix}"
%make_install install-includes prefix="%{_prefix}"

# run-time lib
%make_install install-rtlib prefix="%{_prefix}"

# graphic lib
%make_install install-gfxlib2 prefix="%{_prefix}"

# fbhelp
install -dm 0755 %{buildroot}/%{_bindir}/
install -pm 0755 doc/fbhelp/fbhelp %{buildroot}/%{_bindir}/

# manual
install -dm 0755 %{buildroot}/%{_mandir}/man1/
install -pm 0644 doc/fbc.1 %{buildroot}/%{_mandir}/man1/

# examples
install -dm 0755 %{buildroot}/%{_datadir}/%{name}/
#install -dm 644 examples/ %{buildroot}/%{_datadir}/%{name}/
cp -ar examples/ %{buildroot}/%{_datadir}/%{name}/

# remove empty files
find %{buildroot}/%{_datadir}/%{name}/examples/ -name deleteme.txt

# html docs
install -dm 0755 %{buildroot}/%{_datadir}/doc/%{name}/html/
unzip doc/manual/FB-manual-%{version}-html.zip -d %{buildroot}/%{_datadir}/doc/%{name}/html/
ln -sf 00index.html %{buildroot}/%{_datadir}/doc/%{name}/html/index.html

# fbhelp docs
install -dm 755 %{buildroot}/%{_datadir}/fbhelp/fbhelp/
install -pm 644 doc/manual/fbhelp.daz %{buildroot}/%{_datadir}/fbhelp/fbhelp/

# icons
#	hicolor
for s in 16x16 22x22 32x32 64x64 48x48 128x128 256x256 ; do
	install -pm 0755 -d %{buildroot}%{_datadir}/icons/hicolor/${s}/apps/
	convert -scale ${s} contrib/fblogo64.png %{buildroot}%{_iconsdir}/hicolor/${s}/apps/%{compiler}.png
	convert -scale ${s} contrib/fblogo64a.png %{buildroot}%{_iconsdir}/hicolor/${s}/apps/%{compiler}a.png
	convert -scale ${s} contrib/fbhorse64a.png %{buildroot}%{_iconsdir}/hicolor/${s}/apps/%{compiler}_horsea.png
done
#	scacable
install -pm 0755 -d %{buildroot}%{_iconsdir}/hicolor/scalable/apps/
install -pm 644 contrib/fblogo.svg %{buildroot}%{_iconsdir}/hicolor/scalable/apps/%{compiler}.svg
#	pixmap
install -pm 0755 -d %{buildroot}%{_datadir}/pixmaps/
install -pm 644 contrib/fblogo.xpm %{buildroot}%{_datadir}/pixmaps/%{compiler}.xpm

%check
# local compiler
%if "%{_lib}" == "lib64"
FBC="../bin/%{compiler} LD_PATH=lib/freebasic/linux-x86_64;lib64/freebasic/linux-x86_64;"
%else
FBC="../bin/%{compiler} LD_PATH=lib/freebasic/linux-i686;lib64/freebasic/linux-x86_64;"
%endif

# be verbose
export V=1

# some tests fail to compile
%make -k cunit-tests FCB="${FBC}" || true
%make -k log-tests FCB="${FBC}" || true
%make -k warning-tests FCB="${FBC}" || true


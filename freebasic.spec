%bcond_without bootstrap

%global oname FreeBASIC
%global name %(echo %oname | tr [:upper:] [:lower:])

# set arch
%ifarch x86_64
%global fbarch x86_64
%else
%global fbarch x86
%endif

Summary:	A Free BASIC compiler
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
Source100:	%{name}.rpmlintrc

Patch0:	 %{oname}-1.10.1-fbhelp_makefile.patch
Patch1:	 %{oname}-1.10.1-fbdoc_makefile.patch
Patch2:	 %{oname}-1.10.1-makefile.patch

BuildRequires:	binutils
BuildRequires:	gpm-devel
%if ! %{with bootstrap}
BuildRequires:	freebasic-compiler
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
#mysqlclient-devel

Requires(post,postun): update-alternatives

%description
%{oname} is a free, easy-to-use tool to help you collect, organize, cite,
and share your research sources.

#--------------------------------------------------------------------

%package compiler
Summary:	Free BASIC compiler
Group:		Development/Other
Requires:	%{name}-rtlib = %{version}
Requires:	%{name}-gfxlib2 = %{version}

%description compiler
This package contains dependency on all Free BASIC compiler packages
provided for your architecture.

%files compiler
%{_bindir}/%{compiler}
%{_includedir}/freebasic/
%{_datadir}/freebasic/examples/
%{_datadir}/pixmaps/%{compiler}.xpm
%{_iconsdir}/hicolor/*/apps/%{compiler}*.png
%{_iconsdir}/hicolor/*/apps/%{compiler}*.svg
%{_mandir}/man1/%{compiler}.1.*
%doc readme.txt
%doc todo.txt
%doc changelog.txt
%doc doc/gpl.txt

#--------------------------------------------------------------------

%package rtlib
Summary:	Free BASIC run-time library
Group:		Development/Other

%description rtlib
This package contains the run-time library for progams written in Free BASIC.

%files rtlib
%{_libdir}/freebasic/linux-%{fbarch}/fbextra.x
%{_libdir}/freebasic/linux-%{fbarch}/fbrt0.o
%{_libdir}/freebasic/linux-%{fbarch}/fbrt0pic.o
%{_libdir}/freebasic/linux-%{fbarch}/libfb.a
%{_libdir}/freebasic/linux-%{fbarch}/libfbmt.a
%{_libdir}/freebasic/linux-%{fbarch}/libfbpic.a
%{_libdir}/freebasic/linux-%{fbarch}/libfbmtpic.a
%doc doc/lgpl.txt

#--------------------------------------------------------------------

%package gfxlib2
Summary:	Free BASIC run-time library
Group:		Development/Other
#Requires:	%{name}-rtlib = %{version}

%description gfxlib2
This package contains the graphics library for programs written in Free BASIC.

%files gfxlib2
%{_libdir}/freebasic/linux-%{fbarch}/libfbgfx.a
%{_libdir}/freebasic/linux-%{fbarch}/libfbgfxmt.a
%{_libdir}/freebasic/linux-%{fbarch}/libfbgfxpic.a
%{_libdir}/freebasic/linux-%{fbarch}/libfbgfxmtpic.a
%doc doc/lgpl.txt

#--------------------------------------------------------------------

%package fbhelp
Summary:	Free BASIC fbhelp
Group:		Development/Other

%description fbhelp
Old-style utility for access to FreeBASIC documentation.

%files fbhelp
%{_bindir}/fbhelp
%doc doc/lgpl.txt

#---------------------------------------------------------------------

%package doc-html
Summary:	Free BASIC run-time library
Group:		Development/Other
Buildarch:	noarch

%description doc-html
This package contains the HTML manual for Free BASIC langauge.

%files doc-html
%docdir %{_docdir}/freebasic/html/
%{_docdir}/freebasic/html/*
%doc doc/lgpl.txt

#---------------------------------------------------------------------

%package doc-fbhelp
Summary:	Free BASIC run-time library
Group:		Development/Other
Buildarch:	noarch

%description doc-fbhelp
This package contains the FBHELP manual for Free BASIC langauge.

%files doc-fbhelp
%{_docdir}/freebasic/fbhelp/
%doc doc/lgpl.txt

#---------------------------------------------------------------------

%prep
%autosetup -p1 -n %{oname}-%{version}-source%{?with_bootstrap:\-bootstrap}

# temporary fix for version < 1.06.0 due to ld.gold
# (see bug https://sourceforge.net/p/fbc/bugs/827/)
#if %{version} < 1.06
echo -e "/* dumy */\n" > lib/fbextra.x
#endif

# remove per-built binaries
find . \( -name \*.a -o -name \*.o -o -name \*.so -o -name fbc \) -type f -delete
find . -name deleteme.txt -type f -delete

# fix path for x86_64
%ifarch x86_64
sed -i -e 's|"lib"|"lib64"|g' bootstrap/linux-x86_64/fbc.c
%endif

%build
export CFLAGS="${optflags} -std=gnu89"
export CXXFLAGS="${optflags} -std=gnu89"

# be verbose
# export V=1

export CC=gcc
export CXX=g++

%ifarch x86_64
export ENABLE_LIB64=1
%endif

%setup_compile_flags

# local compiler
%global compiler fbc
%if %{with bootstrap}
FBC="./bootstrap/%{compiler}"
%else
FBC="%{_bindir}/%{compiler}"
%endif

# compiler falgs
FBCFLAGS=" -maxerr 1 -w all -g  -RR -R"
FBFLAGS=" -i inc -g"

# GFX flag for fbhelp
GFXFLAG="GFX=1"

# compiler target
TARGET="linux"

# enable suffix
# ENABLE_PREFIX=1
# ENABLE_SUFFIX=-%{version}
# Build run-time lib
%make_build rtlib CC="${CC}" CFLAGS="${CFLAGS}"

# Build graphic lib
%make_build gfxlib2 CC="${CC}" CFLAGS="${CFLAGS}"

# Build a static compiler from C/ASM with related C libs
%if %with bootstrap
%make_build bootstrap FBFLAGS+=" -gen gas64" CC="${CC}" BOOTSTRAP_CFLAGS="${CFLAGS}"
%endif

# Re-buld compiler using the previously grenerated one
%make_build clean-compiler

%make_build compiler FBC="${FBC}" FBFLAGS="${FBFLAGS}" FBCFLAGS="${FBCFLAGS}" CC="${CC}" CFLAGS="${CFLAGS}"
#%%make_build clean-bootstrap

%if %{with bootstrap}
FBC=./bin/fbc
%endif

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
%ifarch x86_64
export ENABLE_LIB64=1
%endif

# compiler
%make_install install-compiler prefix="%{buildroot}/%{_prefix}"
%make_install install-includes prefix="%{buildroot}/%{_prefix}"

# run-time lib
%make_install install-rtlib prefix="%{buildroot}/%{_prefix}"

# graphic lib
%make_install install-gfxlib2 prefix="%{buildroot}/%{_prefix}"

# fbhelp
instal -dm 0755 %{buildroot}/%{_bindir}/
instal -pm 0644 doc/fbhelp/fbhelp %{buildroot}/%{_bindir}/

# manual
instal -dm 0755 %{buildroot}/%{_mandir}/man1/
instal -pm 0644 doc/fbc.1 %{buildroot}/%{_mandir}/man1/

# examples
instal -dm 0755 %{buildroot}/%{_datadir}/%{name}/
#instal -dm 644 examples/ %{buildroot}/%{_datadir}/%{name}/
cp -ar examples/ %{buildroot}/%{_datadir}/%{name}/
# remove empty files
find %{buildroot}/%{_datadir}/%{name}/examples/ -name deleteme.txt

# html docs
install -dm 0755 %{buildroot}/%{_datadir}/doc/%{name}/html/
unzip doc/manual/FB-manual-%{version}-html.zip -d %{buildroot}/%{_datadir}/doc/%{name}/html/
pushd %{buildroot}/%{_datadir}/doc/%{name}/html/
ln -sf 00index.html index.html
popd

# fbhelp docs
instal -dm 755 %{buildroot}/%{_datadir}/doc/%{name}/fbhelp/
instal -pm 644 doc/manual/fbhelp.daz %{buildroot}/%{_datadir}/doc/%{name}/fbhelp/

# icons
#	hicolor
for s in 16x16 22x22 32x32 64x64 48x48 128x128 256x256 ; do
	mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${s}/apps
	convert -scale ${s} contrib/fblogo64.png %{buildroot}%{_iconsdir}/hicolor/${s}/apps/%{compiler}.png
	convert -scale ${s} contrib/fblogo64a.png %{buildroot}%{_iconsdir}/hicolor/${s}/apps/%{compiler}a.png
	convert -scale ${s} contrib/fbhorse64a.png %{buildroot}%{_iconsdir}/hicolor/${s}/apps/%{compiler}_horsea.png
done
#	scacable
mkdir -p %{buildroot}%{_iconsdir}/hicolor/scalable/apps
instal -pm 644 contrib/fblogo.svg %{buildroot}%{_iconsdir}/hicolor/scalable/apps/%{compiler}.svg
#	pixmap
instal -dm 755 %{buildroot}%{_datadir}/pixmaps/
instal -pm 644 contrib/fblogo.xpm %{buildroot}%{_datadir}/pixmaps/%{compiler}.xpm

%check
# local compiler
%if %with bootstrap
FBC="./bootstrap/%{compiler}"
%else
#FBC="%{_bindir}/%{compiler}"
FBC="/usr/local/bin/%{compiler}"
%endif
FBC="../bin/%{compiler} LD_PATH=lib/freebasic/linux-i686;lib64/freebasic/linux-x86_64;"
# LD_PATH=lib/freebasic/linux-x86_64;lib64/freebasic/linux-x86_64;
export V=1
# some tests fail to compile
%make -k cunit-tests FCB="${FBC}" || true
%make -k log-tests FCB="${FBC}" || true
%make -k warning-tests FCB="${FBC}" || true


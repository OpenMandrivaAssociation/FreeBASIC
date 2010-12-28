Packager: Alexander Kazancev <kazancas@mail.ru>
Vendor: Mandriva Russia, http://www.mandriva.ru
License:	GPL
Group:		Education
Version:	0.21.1
Release:	%mkrel 1
Summary:	FreeBASIC language compiler
Summary:ru      Компилятор языка FreeBasic
Name:		FreeBASIC
Source:		http://downloads.sourceforge.net/fbc/%{name}-%{version}-source.tar.lzma
URL: http://freebasic.net
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root
Buildrequires: libgpm-devel, libtermcap-devel, libbinutils2-devel, binutils, FreeBASIC
Suggests:	geany

%description	
FreeBASIC - is a completely free, open-source, 32-bit BASIC compiler, with syntax similar to MS-QuickBASIC, that adds new features such as pointers, unsigned data types, inline assembly, object orientation, and many others.
%description -l ru
FreeBASIC это полностью свободный, открытый, 32 разрядный компилятор BASIC 

%prep
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT

%setup -q -n %{name}-%{version}-source

cd src/rtlib
./configure --prefix=/usr --with-x
make
cp -v libfb*.a ../../lib/linux/
cp -v fbrt*.o ../../lib/linux/

cd ..
cd gfxlib2
./configure --prefix=/usr --with-x
make
cp -v libfb*.a ../../lib/linux/

#little_hack
mkdir -p /usr/local/lib/freebasic/linux/
cp -v /usr/lib/freebasic/linux/* /usr/local/lib/freebasic/linux/

cd ..
cd compiler
./configure --prefix=/usr
make
cp -v fbc_new ../../fbc


%install

mkdir -p $RPM_BUILD_ROOT/usr

./install.sh -i $RPM_BUILD_ROOT/usr

mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
mv $RPM_BUILD_ROOT/usr/man/man1/* $RPM_BUILD_ROOT%{_mandir}/man1/
rm -rf $RPM_BUILD_ROOT/usr/man

%clean
rm -rf $RPM_BUILD_ROOT
rm -rf /usr/local/lib/freebasic/

%files
%defattr(-, root, root)
%{_datadir}/freebasic/
%{_libdir}/freebasic/
/usr/include/freebasic/
%{_mandir}/man1/fbc.1.lzma
%{_bindir}/fbc



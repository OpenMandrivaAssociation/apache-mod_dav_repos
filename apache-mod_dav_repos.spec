#Module-Specific definitions
%define mod_name mod_dav_repos
%define mod_conf 79_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	DSO module for the apache Web server
Name:		apache-%{mod_name}
Version:	0.9.6
Release:	%mkrel 7
Group:		System/Servers
License:	Apache License 
URL:		https://catacomb.tigris.org/
Source0:	http://catacomb.tigris.org/catacomb-%{version}.tar.gz
Source1:	%{mod_conf}
# wget -rm http://www.webdav.org/catacomb/catacomb_HOWTO.html
Source2:	catacomb_HOWTO.html
Patch1:		catacomb-0.9.2-version.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
Requires:	apache-mod_dav
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Catacomb is a WebDAV repository module for use with the Apache WebDAV module,
mod_dav. Apache mod_dav parses WebDAV and DeltaV protocol requests into
operations on a repository providing persistent storage of resources and their
properties. The default repository for mod_dav is provided by a separate
module, mod_dav_fs, which stores resource bodies as files in the filesystem,
and stores properties in a (G)DBM database. 

Catacomb provides a replacement for mod_dav_fs called mod_dav_repos that stores
resources and their properties in a relational database (MySQL). The primary
advantage of this approach is the searching capabilities of the database are
used to implement the DASL protocol. Additionally, the database allows
straightforward implementation of the versioning capabilities of the DeltaV
protocol.

By shifting to relational database technology, Catacomb is a platform that
contains important aspects of typical document management systems: the ability
to store large numbers of documents, and search over their metadata.
Furthermore, it is possible (via source code modification) to change the set of
predefined properties stored in the main schema of the relational database.
Properties in the main schema are faster to search. 

This project is the first open source implementation of the DASL and
DeltaV(linear versioning) protocols. We plan on tracking the evolution of this
protocol. 

%prep

%setup -q -n catacomb-%{version}
%patch1 -p1

cp %{SOURCE1} %{mod_conf}
cp %{SOURCE2} catacomb_HOWTO.html

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

# lib64 fixes
perl -pi -e "s|/lib\b|/%{_lib}|g" Makefile*

perl -pi -e "s|/bin/apxs|/sbin/apxs|g" configure*

%build
rm -f configure
autoconf

%configure \
    --with-apache=%{_prefix}

%{_sbindir}/apxs -c mod_dav_repos.c dbms.c lock.c props.c repos.c search.c util.c version.c

%install
rm -rf %{buildroot}

# fix strange permissions
chmod 644 README TODO catacomb_HOWTO.html data.sql table_pgsql.sql table_psql.sql table.sql

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README TODO catacomb_HOWTO.html data.sql table_pgsql.sql table_psql.sql table.sql
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}

Summary:        Netscape Portable Runtime
Name:           nspr
Version:        4.19.0
Release:        1%{?dist}
License:        MPLv2.0
URL:            http://www.mozilla.org/projects/nspr/
Group:          System Environment/Libraries
BuildRoot:      %{_tmppath}/%{name}-%{version}-root

# Sources available at https://ftp.mozilla.org/pub/mozilla.org/nspr/releases/
# When hg tag based snapshots are being used, refer to documentation at
# https://wiki.mozilla.org/NSS:UsingHG and check out https://hg.mozilla.org/projects/nspr
Source0:        %{name}-%{version}-beta.tar.gz

Patch1:         nspr-config-pc.patch
# Upstream: https://bugzilla.mozilla.org/show_bug.cgi?id=853902
Patch2:         nspr-561901.patch

%description
NSPR provides platform independence for non-GUI operating system 
facilities. These facilities include threads, thread synchronization, 
normal file and network I/O, interval timing and calendar time, basic 
memory management (malloc and free) and shared library linking.

%package devel
Summary:        Development libraries for the Netscape Portable Runtime
Group:          Development/Libraries
Requires:       nspr = %{version}-%{release}
Requires:       pkgconfig

%description devel
Header files for doing development with the Netscape Portable Runtime.

%prep

%setup -q

# Original nspr-config is not suitable for our distribution,
# because on different platforms it contains different dynamic content.
# Therefore we produce an adjusted copy of nspr-config that will be 
# identical on all platforms.
# However, we need to use original nspr-config to produce some variables
# that go into nspr.pc for pkg-config.

cp ./nspr/config/nspr-config.in ./nspr/config/nspr-config-pc.in
%patch1 -p0 -b .flags
%patch2 -p0

%build

# partial RELRO support as a security enhancement
LDFLAGS+=-Wl,-z,relro
export LDFLAGS

./nspr/configure \
                 --prefix=%{_prefix} \
                 --libdir=%{_libdir} \
                 --includedir=%{_includedir}/nspr4 \
%ifarch x86_64 ppc64 ia64 s390x sparc64
                 --enable-64bit \
%endif
                 --enable-optimize="$RPM_OPT_FLAGS" \
                 --disable-debug

make

%check

# Run test suite.
perl ./nspr/pr/tests/runtests.pl 2>&1 | tee output.log

TEST_FAILURES=`grep -c FAILED ./output.log` || :
if [ $TEST_FAILURES -ne 0 ]; then
  echo "error: test suite returned failure(s)"
  exit 1
fi
echo "test suite completed"

%install

%{__rm} -Rf $RPM_BUILD_ROOT

DESTDIR=$RPM_BUILD_ROOT \
  make install

NSPR_LIBS=`./config/nspr-config --libs`
NSPR_CFLAGS=`./config/nspr-config --cflags`
NSPR_VERSION=`./config/nspr-config --version`
%{__mkdir_p} $RPM_BUILD_ROOT/%{_libdir}/pkgconfig

%{__mkdir_p} $RPM_BUILD_ROOT/%{_lib}

# Get rid of the things we don't want installed (per upstream)
%{__rm} -rf \
   $RPM_BUILD_ROOT/%{_bindir}/compile-et.pl \
   $RPM_BUILD_ROOT/%{_bindir}/prerr.properties \
   $RPM_BUILD_ROOT/%{_libdir}/libnspr4.a \
   $RPM_BUILD_ROOT/%{_libdir}/libplc4.a \
   $RPM_BUILD_ROOT/%{_libdir}/libplds4.a \
   $RPM_BUILD_ROOT/%{_datadir}/aclocal/nspr.m4 \
   $RPM_BUILD_ROOT/%{_includedir}/nspr4/md

for file in libnspr4.so libplc4.so libplds4.so
do
  mv -f $RPM_BUILD_ROOT/%{_libdir}/$file $RPM_BUILD_ROOT/%{_lib}/$file
  ln -sf ../../%{_lib}/$file $RPM_BUILD_ROOT/%{_libdir}/$file
done


%clean
%{__rm} -Rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
/%{_lib}/libnspr4.so
/%{_lib}/libplc4.so
/%{_lib}/libplds4.so

%files devel
%defattr(-, root, root)
%{_libdir}/libnspr4.so
%{_libdir}/libplc4.so
%{_libdir}/libplds4.so
%{_includedir}/nspr4
%{_libdir}/pkgconfig/nspr.pc
%{_bindir}/nspr-config

%changelog
* Tue Mar  6 2018 Daiki Ueno <dueno@redhat.com> - 4.19.0-1
- Rebase to NSPR 4.19

* Wed Feb 28 2018 Daiki Ueno <dueno@redhat.com> - 4.19.0-0.1.beta
- Rebase to NSPR 4.19 BETA

* Wed Nov  8 2017 Daiki Ueno <dueno@redhat.com> - 4.17.0-1
- Rebase to NSPR 4.17

* Fri Oct 21 2016 Daiki Ueno <dueno@redhat.com> - 4.13.1-1
- Rebase to NSPR 4.13.1

* Mon Oct  3 2016 Daiki Ueno <dueno@redhat.com> - 4.13.0-1
- Rebase to NSPR 4.13

* Mon Jan 18 2016 Elio Maldonado <emaldona@redhat.com> - 4.11.0-1
- Rebase to NSPR 4.11
- Resolves: Bug 1297891 - Rebase RHEL 6.8 to NSPR 4.11 in preparation for Firefox 45

* Fri Oct 16 2015 Elio Maldonado <emaldona@redhat.com> - 4.10.8-2
- Resolves: Bug 1269361 - CVE-2015-7183
- nspr: heap-buffer overflow in PL_ARENA_ALLOCATE can lead to crash (under ASAN), potential memory corruption

* Sun Mar 22 2015 Elio Maldonado <emaldona@redhat.com> - 4.10.8-1
- Rebase to nspr-4.10.8
- Resolves: Bug 1200920 - Rebase nspr to 4.10.8 for Firefox 38 ESR [RHEL-6.6]

* Wed Jun 11 2014 Elio Maldonado <emaldona@redhat.com> - 4.10.6-1
- Rebase to nspr-4.10.6
- Resolves: rhbz#1099618 - Rebase nspr in RHEL 6.6 to NSPR 4.10.6

* Thu May 22 2014 Elio Maldonado <emaldona@redhat.com> - 4.10.5-1
- Rebase to nspr-4.10.5
- Resolves: rhbz#1099618 - Rebase nspr in RHEL 6.6 to NSPR 4.10.5

* Wed Nov 27 2013 Elio Maldonado <emaldona@redhat.com> - 4.10.0-2
- Rebase to nspr-4.10.2
- Resolves: rhbz#1032488 - CVE-2013-5607 (MFSA 2013-103) Avoid unsigned integer wrapping in PL_ArenaAllocate (MFSA 2013-103)

* Sat Sep 07 2013 Elio Maldonado <emaldona@redhat.com> - 4.10.0-1
- Update Version to 4.10.0 to prevent Mozilla apps update problems as
- reported and fixed on https://bugzilla.redhat.com/show_bug.cgi?id=981166
- Resolves: rhbz#1002643 - Rebase RHEL 6 to NSPR 4.10 (for FF 24.x)

* Thu Sep 05 2013 Elio Maldonado <emaldona@redhat.com> - 4.9.5-4
- Rebase to nspr-4.10
- Resolves: rhbz#1002643 - Rebase RHEL 6 to NSPR 4.10 (for FF 24.x)

* Fri Aug 23 2013 Elio Maldonado <emaldona@redhat.com> - 4.9.5-3
- Bump the release tag so it's higher than the one for rhel-6.4.z
- Resolves: rhbz#919180 - Rebase to nspr-4.9.5

* Fri Mar 22 2013 Elio Maldonado <emaldona@redhat.com> - 4.9.5-2
- Add upstream URL for an existing patch per packaging guidelines
- Sync up the release tags

* Fri Mar 22 2013 Elio Maldonado <emaldona@redhat.com> - 4.9.5-1
- Resolves: rhbz#919180 - Rebase to nspr-4.9.5

* Fri Oct 12 2012 Elio Maldonado <emaldona@redhat.com> - 4.9.2-1
- Update to nspr-4.9.2
- Related: rhbz#863286

* Wed Jul 11 2012 Elio Maldonado <emaldona@redhat.com> - 4.9.1-4
- Related: rhbz#833149 - Update License to MPLv2.0

* Fri Jun 22 2012 Elio Maldonado <emaldona@redhat.com> - 4.9.1-3
- Resolves: rhbz#833149 - Prevent multilib regressions

* Thu Jun 21 2012 Elio Maldonado <emaldona@redhat.com> - 4.9.1-2
- Resolves: rhbz#833149 - remove unwanted changes to nspr.pc

* Wed Jun 20 2012 Elio Maldonado <emaldona@redhat.com> - 4.9.1-1
- Resolves: rhbz#833149 - Update to NSPR_4_9_1_RTM

* Thu Mar 01 2012 Elio Maldonado <emaldona@redhat.com> - 4.9-1
- Resolves: rhbz#799193 - Update to 4.9

* Wed Jan 18 2012 Elio Maldonado <emaldona@redhat.com> - 4.8.9-2
- Related: Bug 744069 - Avoid %%post/un shell invocations and dependencies.

* Wed Jan 18 2012 elio maldonado <emaldona@redhat.com> - 4.8.9-1
- Resolves: Bug 744069 - Rebase nspr to 4.8.9 or higher

* Fri Jul 22 2011 Elio Maldonado <emaldona@redhat.com> - 4.8.8-3
- Add partial RELRO support as a security enhancement

* Mon Jul 18 2011 Elio Maldonado <emaldona@redhat.com> - 4.8.8-2
- Run the nspr test suite in the %%check section

* Mon Jul 11 2011 Elio Maldonado <emaldona@redhat.com> - 4.8.8-1
- Update to 4.8.8

* Mon Jan 17 2011 Elio Maldonado <emaldona@redhat.com> - 4.8.7-1
- Update to 4.8.7

* Tue Aug 24 2010 Kai Engert <kaie@redhat.com> - 4.8.6-1
- update to 4.8.6

* Wed May 12 2010 Elio Maldonado <emaldona@redhat.com> - 4.8.4-2
- Don't call free when unloading the library on s390x

* Tue Feb 23 2010 Elio Maldonado <emaldona@redhat.com> - 4.8.4-1
- Update to 4.8.4

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 4.8.2-1.1
- Rebuilt for RHEL 6

* Tue Oct 13 2009 Kai Engert <kaie@redhat.com> - 4.8.2-1
- update to 4.8.2

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jun 30 2009 Christopher Aillon <caillon@redhat.com> 4.8-1
- update to 4.8

* Fri Jun 05 2009 Kai Engert <kaie@redhat.com> - 4.7.4-2
- update to 4.7.4

* Wed Mar 04 2009 Kai Engert <kaie@redhat.com> - 4.7.3-5
- add a workaround for bug 487844

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.7.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Dec  3 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 4.7.3-3
- Rebuild for pkgconfig

* Wed Nov 19 2008 Kai Engert <kaie@redhat.com> - 4.7.3-2
- update to 4.7.3
* Thu Oct 23 2008 Kai Engert <kaie@redhat.com> - 4.7.2-2
- update to 4.7.2

* Thu Oct  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 4.7.1-5
- forgot to cvs add patch... whoops. :/

* Thu Oct  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 4.7.1-4
- properly handle sparc64 in nspr code

* Tue Sep 30 2008 Dennis Gilmore <dennis@ausil.us> - 4.7.1-3
- add sparc64 to the list of 64 bit arches

* Mon Jun 02 2008 Kai Engert <kengert@redhat.com> - 4.7.1-2
- Update to 4.7.1

* Thu Mar 20 2008 Jesse Keating <jkeating@redhat.com> - 4.7.0.99.2-2
- Drop the old obsoletes/provides that aren't needed anymore.

* Mon Mar 17 2008 Kai Engert <kengert@redhat.com> - 4.7.0.99.2-1
- Update to NSPR_4_7_1_BETA2
* Tue Feb 26 2008 Kai Engert <kengert@redhat.com> - 4.7.0.99.1-2
- Addressed cosmetic review comments from bug 226202
* Fri Feb 22 2008 Kai Engert <kengert@redhat.com> - 4.7.0.99.1-1
- Update to NSPR 4.7.1 Beta 1
- Use /usr/lib{64} as devel libdir, create symbolic links.
* Sat Feb 09 2008 Kai Engert <kengert@redhat.com> - 4.7-1
- Update to NSPR 4.7

* Thu Jan 24 2008 Kai Engert <kengert@redhat.com> - 4.6.99.3-1
* NSPR 4.7 beta snapshot 20080120

* Mon Jan 07 2008 Kai Engert <kengert@redhat.com> - 4.6.99-2
- move .so files to /lib

* Wed Nov 07 2007 Kai Engert <kengert@redhat.com> - 4.6.99-1
- NSPR 4.7 alpha

* Tue Aug 28 2007 Kai Engert <kengert@redhat.com> - 4.6.7-3
- Updated license tag

* Fri Jul 06 2007 Kai Engert <kengert@redhat.com> - 4.6.7-2
- Update to 4.6.7

* Fri Jul 06 2007 Kai Engert <kengert@redhat.com> - 4.6.6-2
- Update thread-cleanup patch to latest upstream version
- Add upstream patch to support PR_STATIC_ASSERT

* Wed Mar 07 2007 Kai Engert <kengert@redhat.com> - 4.6.6-1
- Update to 4.6.6
- Adjust IPv6 patch to latest upstream version

* Sat Feb 24 2007 Kai Engert <kengert@redhat.com> - 4.6.5-2
- Update to latest ipv6 upstream patch
- Add upstream patch to fix a thread cleanup issue
- Now requires pkgconfig

* Mon Jan 22 2007 Wan-Teh Chang <wtchang@redhat.com> - 4.6.5-1
- Update to 4.6.5

* Tue Jan 16 2007 Kai Engert <kengert@redhat.com> - 4.6.4-2
- Include upstream patch to fix ipv6 support (rhbz 222554)

* Tue Nov 21 2006 Kai Engert <kengert@redhat.com> - 4.6.4-1
- Update to 4.6.4

* Thu Sep 14 2006 Kai Engert <kengert@redhat.com> - 4.6.3-1
- Update to 4.6.3

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 4.6.2-1.1
- rebuild

* Fri May 26 2006 Kai Engert <kengert@redhat.com> - 4.6.2-1
- Update to 4.6.2
- Tweak nspr-config to be identical on all platforms.

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 4.6.1-2.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 4.6.1-2.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Thu Jan  5 2006 Kai Engert <kengert@redhat.com> 4.6.1-2
- Do not use -ansi when compiling, because of a compilation
  problem with latest glibc and anonymous unions.
  See also bugzilla.mozilla.org # 322427.

* Wed Jan  4 2006 Kai Engert <kengert@redhat.com>
- Add an upstream patch to fix gcc visibility issues.

* Tue Jan  3 2006 Christopher Aillon <caillon@redhat.com>
- Stop shipping static libraries; NSS and dependencies no longer
  require static libraries to build.

* Thu Dec 15 2005 Christopher Aillon <caillon@redhat.com> 4.6.1-1
- Update to 4.6.1

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Jul 15 2005 Christopher Aillon <caillon@redhat.com> 4.6-4
- Use the NSPR version numbering scheme reported by NSPR,
  which unfortunately is not exactly the same as the real
  version (4.6 != 4.6.0 according to RPM and pkgconfig).

* Fri Jul 15 2005 Christopher Aillon <caillon@redhat.com> 4.6-3
- Correct the CFLAGS reported by pkgconfig

* Tue Jul 12 2005 Christopher Aillon <caillon@redhat.com> 4.6-2
- Temporarily include the static libraries allowing nss and 
  its dependencies to build. 

* Tue Jul 12 2005 Christopher Aillon <caillon@redhat.com> 4.6-1
- Update to NSPR 4.6

* Wed Apr 20 2005 Christopher Aillon <caillon@redhat.com> 4.4.1-2
- NSPR doesn't have make install, but it has make real_install.  Use it.

* Thu Apr 14 2005 Christopher Aillon <caillon@redhat.com> 4.4.1-1
- Let's make an RPM.

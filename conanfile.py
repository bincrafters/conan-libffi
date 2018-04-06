from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os

class LibffiConan(ConanFile):
    name = 'libffi'

    source_version = '3.0.11'
    package_version = '3'
    version = '%s-%s' % (source_version, package_version)

    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/vuo/conan-libffi'
    license = 'https://github.com/libffi/libffi/blob/master/LICENSE'
    description = 'A portable, high level programming interface to various calling conventions'
    source_dir = 'libffi-%s' % source_version
    build_dir = '_build'

    def source(self):
        tools.get('https://sourceware.org/pub/libffi/libffi-%s.tar.gz' % self.source_version,
                  sha256='70bfb01356360089aa97d3e71e3edf05d195599fd822e922e50d46a0055a6283')
        tools.replace_in_file('%s/configure' % self.source_dir,
                              'multi_os_directory=`$CC -print-multi-os-directory`',
                              'multi_os_directory=')

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.flags.append('-Oz')
            autotools.flags.append('-mmacosx-version-min=10.10')
            autotools.link_flags.append('-Wl,-install_name,@rpath/libffi.dylib')
            autotools.configure(configure_dir='../%s' % self.source_dir,
                                args=['--quiet',
                                      '--disable-debug',
                                      '--disable-dependency-tracking',
                                      '--disable-static',
                                      '--enable-shared',
                                      '--prefix=%s' % os.getcwd()])
            autotools.make(args=['install'])
 
    def package(self):
        self.copy('*.h', src='%s/include' % self.build_dir, dst='include')
        self.copy('libffi.dylib', src='%s/lib' % self.build_dir, dst='lib')
        self.copy(pattern='*.pc', dst='', keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['ffi']

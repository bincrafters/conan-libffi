from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import platform
from contextlib import contextmanager


class LibffiConan(ConanFile):
    name = "libffi"
    version = "3.3-rc0"
    description = "A portable, high level programming interface to various calling conventions"
    topics = ("conan", "libffi")
    url = "https://github.com/bincrafters/conan-libffi"
    homepage = "https://sourceware.org/libffi/"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    exports = ["win64_intel.S"]
    _source_subfolder = "sources"

    def source(self):
        url = "https://github.com/libffi/libffi/releases/download/v{version}/{name}-{version}.tar.gz"
        sha256 = "403d67aabf1c05157855ea2b1d9950263fb6316536c8c333f5b9ab1eb2f20ecf"
        tools.get(url.format(name=self.name, version=self.version), sha256=sha256)
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

        os.rename(os.path.join(self.source_folder, "win64_intel.S"),
                  os.path.join(self.source_folder, self._source_subfolder, "src", "x86", "win64_intel.S"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            if self.options.shared:
                del self.options.fPIC

    def configure(self):
        if self.settings.compiler != "Visual Studio":
            del self.settings.compiler.libcxx

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("msys2_installer/latest@bincrafters/stable")

    def _get_auto_tools(self):
        return AutoToolsBuildEnvironment(self, win_bash=self.settings.os == "Windows")

    @contextmanager
    def _create_auto_tools_environment(self):
        extra_env_vars = {}
        if self.settings.compiler == "Visual Studio":
            self.package_folder = tools.unix_path(self.package_folder)
            msvcc = tools.unix_path(os.path.join(self.source_folder, self._source_subfolder, "msvcc.sh"))
            msvcc.replace("\\", "/")
            msvcc_args = ["-DFFI_BUILDING_DLL" if self.options.shared else "-DFFI_BUILDING"]
            if "MT" in self.settings.compiler.runtime:
                msvcc_args.append("-DUSE_STATIC_RTL")
            if "d" in self.settings.compiler.runtime:
                msvcc_args.append("-DUSE_DEBUG_RTL")
            if self.settings.arch == "x86_64":
                msvcc_args.append("-m64")
            elif self.settings.arch == "x86":
                msvcc_args.append("-m32")
            if msvcc_args:
                msvcc = "{} {}".format(msvcc, " ".join(msvcc_args))
            extra_env_vars.update(tools.vcvars_dict(self.settings))
            extra_env_vars.update({
                "INSTALL": tools.unix_path(os.path.join(self.source_folder, self._source_subfolder, "install-sh")),
                "LIBTOOL": tools.unix_path(os.path.join(self.source_folder, self._source_subfolder, "ltmain.sh")),
                "CC": msvcc,
                "CXX": msvcc,
                "LD": "link",
                "CPP": "cl -nologo -EP",
                "CXXCPP": "cl -nologo -EP",
            })
        with tools.environment_append(extra_env_vars):
            yield

    def build(self):
        config_args = [
            "--enable-debug" if self.settings.build_type == "Debug" else "--disable-debug",
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--disable-static" if self.options.shared else "--enable-static",
            "--with-gcc-arch={}".format("x86-64" if self.settings.arch == "x86_64" else "i686"),
        ]
        autotools = self._get_auto_tools()
        build = None
        host = None
        if self.settings.compiler == "Visual Studio":
            build = "{}-{}-{}".format(
                "x86_64" if "64" in platform.machine() else "i686",
                "pc" if self.settings.arch == "x86" else "w64",
                "cygwin")
            host = "{}-{}-{}".format(
                "x86_64" if self.settings.arch == "x86_64" else "i686",
                "pc" if self.settings.arch == "x86" else "w64",
                "cygwin")
        else:
            if autotools.host and "x86-" in autotools.host:
                autotools.host = autotools.host.replace("x86", "i686")
        with self._create_auto_tools_environment():
            autotools.configure(configure_dir=os.path.join(self.source_folder, self._source_subfolder),
                                build=build,
                                host=host,
                                args=config_args)
            autotools.make()
            if tools.get_env("CONAN_RUN_TESTS", False):
                autotools.make(target="check")
 
    def package(self):
        if self.settings.os == "Windows":
            self.copy("*.h", src="{}/include".format(self.build_folder), dst="include")
        if self.settings.compiler == "Visual Studio":
            self.copy("*.lib", src="{}/.libs".format(self.build_folder), dst="lib")
            self.copy("*.dll", src="{}/.libs".format(self.build_folder), dst="bin")
        else:
            autotools = self._get_auto_tools()
            with self._create_auto_tools_environment():
                with tools.chdir(self.build_folder):
                    autotools.install()
        self.copy("LICENSE", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        if not self.options.shared:
            self.cpp_info.defines.append("FFI_BUILDING")
        libdirs = ["lib"]
        if os.path.exists(os.path.join(self.package_folder, "lib64")):
            libdirs.append("lib64")
        if os.path.exists(os.path.join(self.package_folder, "lib32")):
            libdirs.append("lib32")
        self.cpp_info.libdirs = libdirs
        self.cpp_info.libs = tools.collect_libs(self)

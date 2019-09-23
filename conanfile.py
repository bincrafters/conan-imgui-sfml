from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os.path


class ImguiSfmlConan(ConanFile):
    name = "imgui-sfml"
    version = "2.1"
    description = 'ImGui binding for use with SFML'
    topics = ('conan', 'sfml', 'gui', 'imgui')
    url = "https://github.com/bincrafters/conan-imgui-sfml"
    homepage = 'https://github.com/eliasdaler/imgui-sfml'
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "MIT"
    exports = ["LICENSE"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {
        'shared': [True, False],
        'fPIC': [True, False],
        'imconfig': 'ANY',
        'imconfig_install_folder': 'ANY',
        'imgui_version': 'ANY'
    }
    default_options = {
        'shared': False,
        'fPIC': True,
        'imconfig': None,
        'imconfig_install_folder': None,
        'imgui_version': '1.72',
        'sfml:window': True,
        'sfml:graphics': True
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _imgui_subfolder = os.path.join(_source_subfolder, "imgui")

    requires = (
        'sfml/2.5.1@bincrafters/stable'
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        imconfig = self.options.imconfig
        if imconfig:
            if not os.path.isfile(str(imconfig)):
                raise ConanInvalidConfiguration("Provided user config is not a file or doesn't exist")
            else:
                self._imconfig_path = os.path.abspath(str(self.options.imconfig))
        if not self.options.imgui_version:
            raise ConanInvalidConfiguration("ImGui version is empty")

    def source(self):
        source_url = "https://github.com/eliasdaler/imgui-sfml"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version), sha256="16a589cb7219ebe3147b13cfe44e50de315deedf6ca8bd67d4ef91de3a09478e")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        source_url = "https://github.com/ocornut/imgui"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.options.imgui_version), sha256="d3fa6071b28b260b513e36aeb4d002b3ad3430f4bf511ded20d11c7b20d41e5b")
        extracted_dir = "imgui-{}".format(self.options.imgui_version)
        os.rename(extracted_dir, self._imgui_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['IMGUI_DIR'] = os.path.join(self.source_folder, self._imgui_subfolder)
        cmake.definitions['SFML_DIR'] = os.path.join(self.deps_cpp_info['sfml'].lib_paths[0], 'cmake', 'SFML')
        cmake.definitions['IMGUI_SFML_BUILD_EXAMPLES'] = 'OFF'
        cmake.definitions['IMGUI_SFML_FIND_SFML'] = 'ON'
        if self.options.imconfig_install_folder:
            cmake.definitions['IMGUI_SFML_CONFIG_INSTALL_DIR'] = self.options.imconfig_install_folder
        if self.options.imconfig:
            cmake.definitions['IMGUI_SFML_USE_DEFAULT_CONFIG'] = 'OFF'
            cmake.definitions['IMGUI_SFML_CONFIG_NAME'] = os.path.basename(self._imconfig_path)
            cmake.definitions['IMGUI_SFML_CONFIG_DIR'] = os.path.dirname(self._imconfig_path)
        else:
            cmake.definitions['IMGUI_SFML_USE_DEFAULT_CONFIG'] = 'ON'

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

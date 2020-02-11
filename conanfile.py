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
    generators = "cmake"
    exports_sources = ['CMakeLists.txt', '0001-conan-libs.patch']
    exports = ['LICENSE.md']

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
        'imgui_version': '1.75',
        'sfml:window': True,
        'sfml:graphics': True
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _imgui_subfolder = os.path.join(_source_subfolder, "imgui")
    _imconfig_path = ""

    requires = (
        'sfml/2.5.1@bincrafters/stable'
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        imconfig = self.options.imconfig
        if imconfig:
            if not os.path.isfile(str(imconfig)):
                raise ConanInvalidConfiguration("Provided user config is not a file or doesn't exist")
            else:
                self._imconfig_path = os.path.abspath(str(self.options.imconfig))
        if not self.options.imgui_version:
            raise ConanInvalidConfiguration("ImGui version is empty")

    def configure(self):
        self.options['sfml'].shared = self.options.shared

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        tools.get(**self.conan_data["sources"]["imgui-{}".format(self.options.imgui_version)])
        extracted_dir = "imgui-{}".format(self.options.imgui_version)
        os.rename(extracted_dir, self._imgui_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['IMGUI_DIR'] = os.path.join(self.source_folder, self._imgui_subfolder)
        cmake.definitions['SFML_DIR'] = os.path.join(self.deps_cpp_info['sfml'].lib_paths[0], 'cmake', 'SFML')
        cmake.definitions['IMGUI_SFML_BUILD_EXAMPLES'] = 'OFF'
        cmake.definitions['IMGUI_SFML_FIND_SFML'] = 'OFF'
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
        tools.patch(self._source_subfolder, patch_file="0001-conan-libs.patch")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os.path
import glob


class ImguiSfmlConan(ConanFile):
    name = "imgui-sfml"
    version = "2.1"
    description = "ImGui binding for use with SFML"
    topics = ("conan", "sfml", "gui", "imgui")
    url = "https://github.com/bincrafters/conan-imgui-sfml"
    homepage = "https://github.com/bincrafters/imgui-sfml"
    license = "MIT"
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/*"]

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "imconfig": "ANY",
        "imconfig_install_folder": "ANY",
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "imconfig": None,
        "imconfig_install_folder": None,
        "sfml:window": True,
        "sfml:graphics": True
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _imgui_subfolder = os.path.join(_source_subfolder, "imgui")
    _imconfig_path = ""

    requires = (
        "sfml/2.5.1@bincrafters/stable"
    )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        imconfig = self.options.imconfig
        if imconfig:
            if not os.path.isfile(str(imconfig)):
                raise ConanInvalidConfiguration("Provided user config is not a file or doesn't exist")
            else:
                self._imconfig_path = os.path.abspath(str(self.options.imconfig))

    def configure(self):
        self.options["sfml"].shared = self.options.shared

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][0])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        tools.get(**self.conan_data["sources"][self.version][1])
        extracted_dir = glob.glob("imgui-*")[0]
        os.rename(extracted_dir, self._imgui_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["IMGUI_DIR"] = os.path.join(self.source_folder, self._imgui_subfolder)

        # FIXME: Shipping the default config/find CMake files is against (newer) Conan conventions
        # Packages should be independent of specific build systems for customers
        # This SFML/cmake path is becoming eventually invalid
        # Try to migrate to one of the Conan CMake generators like cmake_find_package_multi
        cmake.definitions["SFML_DIR"] = os.path.join(self.deps_cpp_info["sfml"].lib_paths[0], "cmake", "SFML")

        cmake.definitions["IMGUI_SFML_BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["IMGUI_SFML_FIND_SFML"] = "OFF"
        if self.options.imconfig_install_folder:
            cmake.definitions["IMGUI_SFML_CONFIG_INSTALL_DIR"] = self.options.imconfig_install_folder
        if self.options.imconfig:
            cmake.definitions["IMGUI_SFML_USE_DEFAULT_CONFIG"] = "OFF"
            cmake.definitions["IMGUI_SFML_CONFIG_NAME"] = os.path.basename(self._imconfig_path)
            cmake.definitions["IMGUI_SFML_CONFIG_DIR"] = os.path.dirname(self._imconfig_path)
        else:
            cmake.definitions["IMGUI_SFML_USE_DEFAULT_CONFIG"] = "ON"

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        if "patches" in self.conan_data and self.version in self.conan_data["patches"]:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "ImGui-SFML"
        self.cpp_info.names["cmake_find_package_multi"] = "ImGui-SFML"

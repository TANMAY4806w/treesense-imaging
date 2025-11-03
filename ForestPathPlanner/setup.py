from setuptools import setup, Extension

# Define the extension module
pathfinder_module = Extension(
    "pathfinder",
    sources=["pathfinder.cpp"],  # C++ source file
    extra_compile_args=["/std:c++17"],  # Force C++17 (Windows MSVC)
)

# Setup script
setup(
    name="pathfinder",
    version="1.0",
    description="Forest Path Finder C++ Extension",
    ext_modules=[pathfinder_module],
)

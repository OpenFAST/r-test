#
# Copyright 2017 National Renewable Energy Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or impClied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

cmake_minimum_required(VERSION 2.8.12)
project(DISCON_ITIBarge Fortran)

if(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
  set(CMAKE_MACOSX_RPATH 1)
endif()

set(SOURCE_PATH "${CMAKE_CURRENT_LIST_DIR}/DISCON_ITIBarge.F90")
file(TO_CMAKE_PATH ${SOURCE_PATH} SOURCE_PATH)

set(CMAKE_Fortran_FLAGS "-m64 -fbacktrace -ffree-line-length-none -fdefault-real-8 -C -DDOUBLE_PRECISION -DIMPLICIT_DLLEXPORT")
set(CMAKE_SHARE_LINKER_FLAGS "-shared")

add_library(DISCON_ITIBarge SHARED ${SOURCE_PATH})
set_target_properties(DISCON_ITIBarge PROPERTIES PREFIX "" SUFFIX ".dll")

install(TARGETS DISCON_ITIBarge DESTINATION "${CMAKE_CURRENT_LIST_DIR}/..")

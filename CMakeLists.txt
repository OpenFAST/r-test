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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

cmake_minimum_required(VERSION 2.8.12)
project(OpenFAST_RegressionTest_Data Fortran)

set(SERVODATA_DIR "${CMAKE_CURRENT_LIST_DIR}/glue-codes/openfast/5MW_Baseline/ServoData")
add_subdirectory("${SERVODATA_DIR}/DISCON" "${SERVODATA_DIR}/DISCON/build")
add_subdirectory("${SERVODATA_DIR}/DISCON_ITI" "${SERVODATA_DIR}/DISCON_ITI/build")
add_subdirectory("${SERVODATA_DIR}/DISCON_OC3" "${SERVODATA_DIR}/DISCON_OC3/build")

add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/glue-codes/openfast-cpp/5MW_Baseline/ServoData/DISCON" "${CMAKE_CURRENT_LIST_DIR}/glue-codes/openfast-cpp/5MW_Baseline/ServoData/DISCON/build")

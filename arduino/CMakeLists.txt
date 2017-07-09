#=============================================================================#
# Author: MarkStevens
# Date:   2012/04/17
#                                                                             #
# Description: Arduino nano board for measuring weight.
#                                                                             #
#=============================================================================#

cmake_minimum_required(VERSION 2.8)
#====================================================================#
#  Settings                                                          #
#====================================================================#

set(CMAKE_TOOLCHAIN_FILE ${CMAKE_SOURCE_DIR}/arduino-cmake/cmake/ArduinoToolchain.cmake) # Arduino Toolchain
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -pedantic")

project(LoadCellNano C CXX)
set(FIRMWARE_NAME kamikaze)

set(${FIRMWARE_NAME}_BOARD uno)               # Arduino Target board
set(${FIRMWARE_NAME}_SRCS  kamikaze.cc)

set(${FIRMWARE_NAME}_PORT /dev/ttyACM1)            # Serial upload port
link_directories(${CMAKE_SOURCE_DIR}/../arduino)
set(${FIRMWARE_NAME}_NO_AUTOLIBS false)

#====================================================================#
#  Target generation                                                 #
#====================================================================#
generate_arduino_firmware(${FIRMWARE_NAME})

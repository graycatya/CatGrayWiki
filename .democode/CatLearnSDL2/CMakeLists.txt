cmake_minimum_required (VERSION 3.0)
cmake_policy(VERSION 3.0)

project(CatLearnSDL2)

set(CMAKE_CXX_STANDARD 17) # 这对 MSVC 没有任何作用，请使用下面的target_compile_options
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS ON)

IF(NOT CMAKE_BUILD_TYPE)
  SET(CMAKE_BUILD_TYPE Debug CACHE STRING "Choose the type of build (Debug or Release)" FORCE)
ENDIF(NOT CMAKE_BUILD_TYPE)

set(CHAPTERS
    1.sdl_basic
    2.sdl_window
    3.sdl_event
    4.sdl_thread
    5.sdl_yuv
    6.sdl_pcm
)

configure_file(configuration/root_directory.h.in configuration/root_directory.h)
include_directories(${CMAKE_BINARY_DIR}/configuration)

# 首先创建其他项目所需的相关静态库
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/SDL)
set(LIBS ${LIBS} SDL2-static)

function(create_project_from_sources demo)
	file(GLOB SOURCE
            "src/${demo}/*.h"
            "src/${demo}/*.cpp"
            "src/${demo}/*.vs"
            "src/${demo}/*.fs"
            "src/${demo}/*.tcs"
            "src/${demo}/*.tes"
            "src/${demo}/*.gs"
            "src/${demo}/*.cs"
    )
	if (demo STREQUAL "")
		SET(replaced "")
		string(REPLACE "/" "_" replaced ${demo})
		set(NAME ${replaced})
	else()
		set(NAME "${demo}")
	endif()
    add_executable(${NAME} ${SOURCE})
    target_link_libraries(${NAME} ${LIBS})
    if(MSVC)
		target_compile_options(${NAME} PRIVATE /std:c++17 /MP)
        target_link_options(${NAME} PUBLIC /ignore:4099)
    endif(MSVC)
    if(WIN32)
        set_target_properties(${NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin/${demo}")
        set_target_properties(${NAME} PROPERTIES VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}/bin/${demo}/Debug")
    elseif(UNIX AND NOT APPLE)
        set_target_properties(${NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin/${demo}")
    elseif(APPLE)
        set_target_properties(${NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin/${demo}")
        set_target_properties(${NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_SOURCE_DIR}/bin/${demo}")
        set_target_properties(${NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}/bin/${demo}")
    endif(WIN32)
    # copy shader files to build directory
    file(GLOB SHADERS
             "src/${demo}/*.vs"
             # "src/${demo}/*.frag"
             "src/${demo}/*.fs"
             "src/${demo}/*.tcs"
             "src/${demo}/*.tes"
             "src/${demo}/*.gs"
             "src/${demo}/*.cs"
    )
	# copy dlls
	file(GLOB DLLS "dlls/*.dll")
    foreach(SHADER ${SHADERS})
        if(WIN32)
            # configure_file(${SHADER} "test")
            add_custom_command(TARGET ${NAME} PRE_BUILD COMMAND ${CMAKE_COMMAND} -E copy ${SHADER} $<TARGET_FILE_DIR:${NAME}>)
			add_custom_command(TARGET ${NAME} PRE_BUILD COMMAND ${CMAKE_COMMAND} -E copy ${DLLS} $<TARGET_FILE_DIR:${NAME}>)
        elseif(UNIX AND NOT APPLE)
            file(COPY ${SHADER} DESTINATION ${CMAKE_SOURCE_DIR}/bin/${demo})
        elseif(APPLE)
            # 创建符号链接 *.vs *.fs *.gs
            get_filename_component(SHADERNAME ${SHADER} NAME)
            makeLink(${SHADER} ${CMAKE_SOURCE_DIR}/bin/${demo}/${SHADERNAME} ${NAME})
        endif(WIN32)
    endforeach(SHADER)
    # 如果为 Visual Studio 进行编译，还要为每个项目使用配置文件（特别是用于设置工作目录）
    # if(MSVC)
    #     configure_file(${CMAKE_SOURCE_DIR}/configuration/visualstudio.vcxproj.user.in ${CMAKE_CURRENT_BINARY_DIR}/${NAME}.vcxproj.user @ONLY)
    # endif(MSVC)
endfunction()


foreach(DEMO ${CHAPTERS})
    create_project_from_sources(${DEMO})
endforeach(DEMO)

include_directories(${CMAKE_SOURCE_DIR}/SDL/include)
include_directories(${CMAKE_SOURCE_DIR}/includes)
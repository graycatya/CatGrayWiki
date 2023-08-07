PARENT_DIR = $$replace(PWD, "/demo3", "")

QT += core

INCLUDEPATH += $$PARENT_DIR/glfw/include

INCLUDEPATH += $$PARENT_DIR/glad/include

SOURCES += $$PARENT_DIR/glad/src/glad.c \
    main.cpp

win32: {
    # 执行Windows平台相关操作

    # 判断是否使用的是MSVC编译器
    msvc: {
        LIBS += -lgdi32 -lopengl32 -lkernel32 -luser32 -lshell32 -lglu32
        message("QMAKE_MSC_VER : $$QMAKE_MSC_VER")
        CONFIG(debug, debug|release) {
            message("debug")
            contains(DEFINES, WIN64) {
                message("WIN64")
                LIBS += -L$$PARENT_DIR/glfw/lib-vc2019 -lglfw3
            } else {
                message("WIN32")
                LIBS += -L$$PARENT_DIR/glfw/lib-vc2019 -lglfw3
            }
        } else {
            message("release")
            contains(DEFINES, WIN64) {
                message("WIN64")
                LIBS += -L$$PARENT_DIR/glfw/lib-vc2019 -lglfw3
            } else {
                message("WIN32")
                LIBS += -L$$PARENT_DIR/glfw/lib-vc2019 -lglfw3
            }
        }
    }
    else: {
        # 执行其他编译器相关操作
    }
}
else: {
    # 执行其他平台相关操作
}

SOURCES += \
    main.cpp

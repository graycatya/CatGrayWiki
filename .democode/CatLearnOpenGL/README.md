# 声明

这是参考learnopengl代码仓库临摹学习使用

## learnopengl.com 代码存储库

包含代码示例和学习opengl的所有章节 [https://learnopengl.com](https://learnopengl.com).。

## windows构建

所有相关库都在libs中找到，所有dl都在为windows预编译的dll中找到cmake脚本知道在哪里可以找到库，所以只需运行c make脚本并生成选择的项目请记住，提供的库是使用特定编译器版本生成的，该版本可能会或可能不会在您的系统上运行，从而生成大量链接错误，在这种情况下，建议您从源代码中自己构建库。

## linux构建

首先确保你有cmake git和gcc，以root身份输入 `apt-get install g++ cmake git`，然后获取所需的包
使用root sudo并输入`apt-get install libsoil-dev libglm-dev libassimp-dev libglew-dev libglfw3-dev libxinerama-dev libxcursor-dev  libxi-dev libfreetype-dev libgl1-mesa-dev xorg-dev`。

**通过 cmake-gui 构建:** 源目录是 CatLearnOpenGL 并指定构建目录为 CatLearnOpenGL/build 在 learn open gl 中创建构建目录对于链接到资源文件很重要，它也会被 git 忽略，点击配置并指定您的编译器文件建议使用 unix makefile 解决所有丢失的目录或库，然后点击生成导航到构建目录(`cd CatLearnOpenGL/build`) 并在终端中键入 `make` 这应该在相应的章节文件夹中生成可执行文件。

** 通过cmake命令行构建 **

```shell
cd /path/to/CatLearnOpenGL
mkdir build && cd build
cmake ..
cmake --build .
```

请注意，由于查找着色器和资源文件的问题，代码块或其他 IDE 可能会在运行程序时出现问题，但是它仍然应该能够生成可执行文件来解决此问题，可以设置一个环境变量来告诉教程在其中可以找到资源文件的环境变量名为 LOGL_ROOT_PATH，并且可以设置为 CatLearnOpenGL 目录树的根路径，例如:

```shell
export LOGL_ROOT_PATH=/home/user/tutorials/CatLearnOpenGL
```

运行 `ls $LOGL_ROOT_PATH` 应列出此自述文件和资源目录等内容。


## Mac OS X 构建

在 Mac OS X 上构建相当简单：
```
brew install cmake assimp glm glfw freetype
cmake -S . -B build
cmake --build build -j$(sysctl -n hw.logicalcpu)
```

## mac平台创建xcode项目

谢谢 [@caochao](https://github.com/caochao)：
克隆repo后，转到repo的根路径，运行以下命令：

```
mkdir xcode
cd xcode
cmake -G Xcode ..
```

## Glitter

多通创建了一个名为[Glitter](https://github.com/Polytonic/Glitter)的项目，这是一个非常简单的opengl样板。运行一个CatLearnOpenGL项目所需的一切(包括所有库)，仅此而已。
完美，如果你想跟随章节，而不是必须手动编译和链接所有第三方库的麻烦！
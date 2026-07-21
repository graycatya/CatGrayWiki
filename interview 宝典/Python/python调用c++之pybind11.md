# Python 调用 C/C++ 之 pybind11 教程

## 目录

1. [pybind11 简介](#1-pybind11-简介)
2. [环境搭建](#2-环境搭建)
3. [第一个示例：导出函数](#3-第一个示例导出函数)
4. [数据类型映射](#4-数据类型映射)
5. [导出 C++ 类](#5-导出-c-类)
6. [函数重载与默认参数](#6-函数重载与默认参数)
7. [STL 容器支持](#7-stl-容器支持)
8. [NumPy 互操作](#8-numpy-互操作)
9. [继承与多态](#9-继承与多态)
10. [枚举与属性](#10-枚举与属性)
11. [异常处理](#11-异常处理)
12. [构建系统集成](#12-构建系统集成)
13. [实战案例](#13-实战案例)
14. [性能对比与最佳实践](#14-性能对比与最佳实践)
15. [常见问题 FAQ](#15-常见问题-faq)

---

## 1. pybind11 简介

### 1.1 什么是 pybind11？

**pybind11** 是一个轻量级的**仅头文件库**（header-only），用于在 Python 和 C++11 之间创建绑定。它能让你将 C++ 函数、类、数据结构等无缝暴露给 Python 调用。

### 1.2 与其他方案的对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| **ctypes** | Python 内置，无需编译 | 只能调用 C 接口，类型不安全 |
| **cffi** | 灵活，运行时绑定 | 需要写接口声明 |
| **SWIG** | 支持多种语言 | 生成的代码臃肿，难以调试 |
| **Boost.Python** | 功能强大 | 依赖 Boost，编译慢，体积大 |
| **Cython** | 性能接近 C | 学习成本高，语法特殊 |
| **pybind11** | 轻量、现代 C++、类型安全 | 仅支持 C++11+ |

> **选择 pybind11 的理由**：header-only、与 Python C API 深度整合、支持 C++14/17 特性、社区活跃（PyTorch、OpenCV 等项目在用）。

### 1.3 核心原理

pybind11 基于 Python C API，通过模板元编程自动生成类型转换代码：

```
Python 对象  ←→  pybind11::object  ←→  C++ 原生类型
```

- **调用方向**：Python → C/C++（性能关键路径）
- **数据转换**：自动处理 Python str ↔ std::string、Python list ↔ std::vector 等

---

## 2. 环境搭建

### 2.1 安装依赖

```bash
# pip 安装（推荐）
pip install pybind11

# 或从源码编译
git clone https://github.com/pybind/pybind11.git
cd pybind11
mkdir build && cd build
cmake ..
make install
```

### 2.2 项目结构建议

```
my_project/
├── src/                    # C++ 源码
│   ├── bindings.cpp        # pybind11 绑定代码
│   ├── math_utils.h
│   └── math_utils.cpp
├── setup.py                # setuptools 构建脚本
├── CMakeLists.txt          # CMake 构建脚本（二选一）
├── tests/
│   └── test_bindings.py
└── example.py              # 使用示例
```

---

## 3. 第一个示例：导出函数

### 3.1 最简单的绑定

**C++ 代码**（`bindings.cpp`）：

```cpp
#include <pybind11/pybind11.h>

// 要暴露给 Python 的 C++ 函数
int add(int a, int b) {
    return a + b;
}

double multiply(double a, double b) {
    return a * b;
}

std::string greet(const std::string &name) {
    return "Hello, " + name + "!";
}

// pybind11 绑定模块
PYBIND11_MODULE(my_module, m) {
    m.doc() = "pybind11 example module";  // 模块文档字符串

    m.def("add", &add, "A function that adds two numbers",
          pybind11::arg("a") = 0,  // 参数 a，默认值 0
          pybind11::arg("b") = 0); // 参数 b，默认值 0

    m.def("multiply", &multiply, "A function that multiplies two numbers");

    m.def("greet", &greet, "Greet someone by name");
}
```

**编译**（使用 cppimport，最简单方式）：

```python
# example.py
import cppimport

# 直接 import C++ 源文件，自动编译
# 需要 pip install cppimport
import my_module
# 注意：需要先将 bindings.cpp 命名为 my_module.cpp
```

### 3.2 使用 `c++` 代码块编译（命令行）

```bash
# macOS / Linux
c++ -O3 -Wall -shared -std=c++11 -fPIC \
    $(python3 -m pybind11 --includes) \
    bindings.cpp -o my_module$(python3-config --extension-suffix)

# Windows (MSVC)
cl /O2 /EHsc /std:c++11 /LD \
    /I"C:\Python3X\include" /I"path\to\pybind11\include" \
    bindings.cpp /link /OUT:my_module.pyd
```

### 3.3 Python 调用

```python
import my_module

print(my_module.add(3, 5))         # 输出: 8
print(my_module.add(10))           # 输出: 10 (b 使用默认值 0)
print(my_module.multiply(2.5, 4.0)) # 输出: 10.0
print(my_module.greet("World"))     # 输出: Hello, World!
```

---

## 4. 数据类型映射

### 4.1 基础类型自动转换表

| C++ 类型 | Python 类型 | 方向 | 说明 |
|-----------|-------------|------|------|
| `int` / `long` | `int` | 双向 | - |
| `float` / `double` | `float` | 双向 | - |
| `bool` | `bool` | 双向 | - |
| `std::string` | `str` | 双向 | UTF-8 编码 |
| `const char *` | `str` | 双向 | - |
| `std::wstring` | `str` | 双向 | 宽字符转换 |
| `pybind11::bytes` | `bytes` | 双向 | 二进制数据 |
| `nullptr_t` | `None` | 双向 | - |

### 4.2 参数传递方式

```cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

// 值传递：会发生拷贝
void process_by_value(std::vector<int> data) {
    for (auto &x : data) x *= 2;
}

// 引用传递：修改会反映回 Python（需要 stl.h）
void process_by_reference(std::vector<int> &data) {
    for (auto &x : data) x *= 2;
}

PYBIND11_MODULE(type_demo, m) {
    m.def("by_value", &process_by_value);
    m.def("by_reference", &process_by_reference);
}
```

```python
import type_demo

# 值传递：不会修改原列表
data = [1, 2, 3]
type_demo.by_value(data)
print(data)  # [1, 2, 3] — 未修改

# 引用传递：会修改原列表
type_demo.by_reference(data)
print(data)  # [2, 4, 6] — 已修改
```

### 4.3 返回 Python 原生类型

```cpp
// 返回元组
py::tuple get_info() {
    return py::make_tuple(42, "answer", true);
}

// 返回字典
py::dict get_config() {
    py::dict d;
    d["debug"] = true;
    d["version"] = "1.0.0";
    d["max_connections"] = 100;
    return d;
}

// 使用 py::object 返回任意对象
py::object get_anything() {
    auto list = py::list();
    list.append(py::int_(1));
    list.append(py::str("hello"));
    return list;
}
```

---

## 5. 导出 C++ 类

### 5.1 基本类绑定

```cpp
#include <pybind11/pybind11.h>
namespace py = pybind11;

class Calculator {
public:
    Calculator(double initial = 0.0) : value_(initial) {}

    double add(double x) {
        value_ += x;
        return value_;
    }

    double subtract(double x) {
        value_ -= x;
        return value_;
    }

    double multiply(double x) {
        value_ *= x;
        return value_;
    }

    double getValue() const { return value_; }
    void setValue(double v) { value_ = v; }

private:
    double value_;
};

PYBIND11_MODULE(calculator, m) {
    py::class_<Calculator>(m, "Calculator")
        .def(py::init<>())                           // 默认构造函数
        .def(py::init<double>(),                      // 带参构造函数
             py::arg("initial") = 0.0)
        .def("add", &Calculator::add)                 // 成员函数
        .def("subtract", &Calculator::subtract)
        .def("multiply", &Calculator::multiply)
        .def("get_value", &Calculator::getValue)      // Python 风格命名
        .def("set_value", &Calculator::setValue)
        // 属性方式访问
        .def_property("value",
                      &Calculator::getValue,
                      &Calculator::setValue)
        // 只读属性
        .def_property_readonly("result", &Calculator::getValue)
        .def("__repr__", [](const Calculator &c) {
            return "<Calculator value=" + std::to_string(c.getValue()) + ">";
        });
}
```

**Python 调用**：

```python
import calculator

# 创建对象
c = calculator.Calculator(10.0)
print(c)  # <Calculator value=10.000000>

# 方法调用
c.add(5.0)
print(c.get_value())  # 15.0

# 属性方式
c.value = 20.0
print(c.value)  # 20.0

# 链式调用（如果返回 self 需要特殊处理）
result = c.add(10).multiply(2)
```

### 5.2 支持链式调用

```cpp
// 修改 Calculator 类使其返回引用
class Calculator {
public:
    Calculator& add(double x) { value_ += x; return *this; }
    Calculator& subtract(double x) { value_ -= x; return *this; }
    Calculator& multiply(double x) { value_ *= x; return *this; }
};

// 绑定中添加
py::class_<Calculator>(m, "Calculator")
    // ... 其他绑定 ...
    .def("add", &Calculator::add,
         py::return_value_policy::reference);
```

### 5.3 静态成员与类方法

```cpp
class MathUtils {
public:
    static double pi() { return 3.14159265359; }
    static int factorial(int n) {
        return (n <= 1) ? 1 : n * factorial(n - 1);
    }
    static const char* version;
};

const char* MathUtils::version = "2.0.0";

PYBIND11_MODULE(math_utils, m) {
    py::class_<MathUtils>(m, "MathUtils")
        .def_static("pi", &MathUtils::pi)
        .def_static("factorial", &MathUtils::factorial)
        .def_property_readonly_static("version",
            [](py::object /* self */) { return MathUtils::version; });
}
```

---

## 6. 函数重载与默认参数

### 6.1 处理 C++ 函数重载

```cpp
#include <pybind11/pybind11.h>
namespace py = pybind11;

// 多个重载版本
double process(int x) {
    return x * 2.0;
}

double process(double x) {
    return x * 3.0;
}

double process(int x, double y) {
    return x + y;
}

PYBIND11_MODULE(overload_demo, m) {
    // 方式一：使用 py::overload_cast（推荐，C++14）
    m.def("process", py::overload_cast<int>(&process));
    m.def("process", py::overload_cast<double>(&process));
    m.def("process", py::overload_cast<int, double>(&process));

    // 方式二：手动转换（C++11 兼容）
    // m.def("process", static_cast<double(*)(int)>(&process));
    // m.def("process", static_cast<double(*)(double)>(&process));
}
```

```python
import overload_demo

print(overload_demo.process(10))       # 20.0 — 调用 int 版本
print(overload_demo.process(10.5))     # 31.5 — 调用 double 版本
print(overload_demo.process(10, 3.14)) # 13.14 — 调用 int, double 版本
```

### 6.2 关键字参数与默认值

```cpp
int compute(int a, int b = 10, int c = 100) {
    return a * b + c;
}

PYBIND11_MODULE(kwargs_demo, m) {
    using namespace pybind11::literals;  // 启用 _a 字面量

    m.def("compute", &compute,
          "a"_a, "b"_a = 10, "c"_a = 100,
          "A function with keyword arguments");

    // 或使用 py::arg
    // m.def("compute", &compute,
    //       py::arg("a"), py::arg("b") = 10, py::arg("c") = 100);
}
```

```python
import kwargs_demo

print(kwargs_demo.compute(1))           # 110
print(kwargs_demo.compute(1, b=5))      # 105
print(kwargs_demo.compute(a=1, c=200))  # 210
```

---

## 7. STL 容器支持

### 7.1 引入 STL 头文件

```cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>       // vector, map, set, list 等自动转换
#include <pybind11/stl_bind.h>  // 绑定 STL 容器为可修改类型
```

### 7.2 自动转换 vs 显式绑定

```cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include <vector>
#include <map>

namespace py = pybind11;

// 自动转换：每次调用都会在 Python/C++ 间拷贝数据
std::vector<int> double_elements(const std::vector<int> &input) {
    std::vector<int> result;
    for (int x : input) result.push_back(x * 2);
    return result;
}

std::map<std::string, int> get_scores() {
    return {{"Alice", 95}, {"Bob", 87}, {"Charlie", 92}};
}

PYBIND11_MODULE(stl_demo, m) {
    m.def("double_elements", &double_elements);
    m.def("get_scores", &get_scores);
}
```

```python
import stl_demo

# list 自动 ↔ std::vector
result = stl_demo.double_elements([1, 2, 3, 4])
print(result)  # [2, 4, 6, 8]

# dict 自动 ↔ std::map
scores = stl_demo.get_scores()
print(scores)  # {'Alice': 95, 'Bob': 87, 'Charlie': 92}
```

### 7.3 就地修改（避免拷贝）

```cpp
// 使用 stl_bind.h 绑定可修改容器
PYBIND11_MAKE_OPAQUE(std::vector<int>);
PYBIND11_MAKE_OPAQUE(std::vector<std::string>);

PYBIND11_MODULE(stl_bind_demo, m) {
    py::bind_vector<std::vector<int>>(m, "VectorInt");
    py::bind_vector<std::vector<std::string>>(m, "VectorString");

    m.def("modify_vector", [](std::vector<int> &v) {
        for (auto &x : v) x *= 10;
    });
}
```

---

## 8. NumPy 互操作

### 8.1 零拷贝访问 NumPy 数组

```cpp
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

// 对 NumPy 数组做逐元素操作
py::array_t<double> add_arrays(py::array_t<double> input1,
                                py::array_t<double> input2) {
    // 获取缓冲区信息（带类型检查和自动转换）
    auto buf1 = input1.request();
    auto buf2 = input2.request();

    if (buf1.size != buf2.size)
        throw std::runtime_error("Arrays must have the same size");

    // 分配输出数组
    auto result = py::array_t<double>(buf1.size);
    auto buf3 = result.request();

    // 直接操作底层指针（零拷贝）
    double *ptr1 = static_cast<double*>(buf1.ptr);
    double *ptr2 = static_cast<double*>(buf2.ptr);
    double *ptr3 = static_cast<double*>(buf3.ptr);

    for (size_t i = 0; i < buf1.size; i++) {
        ptr3[i] = ptr1[i] + ptr2[i];
    }

    return result;
}

// 多维数组操作示例
// 二维数组矩阵乘法（简化示意，实际应使用 BLAS）
py::array_t<double> matrix_multiply(py::array_t<double> a,
                                     py::array_t<double> b) {
    auto buf_a = a.request();
    auto buf_b = b.request();

    if (buf_a.ndim != 2 || buf_b.ndim != 2)
        throw std::runtime_error("Both inputs must be 2D arrays");

    int m = buf_a.shape[0];
    int k = buf_a.shape[1];
    int n = buf_b.shape[1];

    if (k != buf_b.shape[0])
        throw std::runtime_error("Inner dimensions must match");

    auto result = py::array_t<double>({m, n});
    auto buf_r = result.request();

    double *pa = static_cast<double*>(buf_a.ptr);
    double *pb = static_cast<double*>(buf_b.ptr);
    double *pr = static_cast<double*>(buf_r.ptr);

    // 简单三重循环
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int p = 0; p < k; p++) {
                sum += pa[i * k + p] * pb[p * n + j];
            }
            pr[i * n + j] = sum;
        }
    }

    return result;
}

PYBIND11_MODULE(numpy_demo, m) {
    m.doc() = "NumPy interop demo";
    m.def("add_arrays", &add_arrays, "Element-wise addition");
    m.def("matrix_multiply", &matrix_multiply, "Matrix multiplication");
}
```

```python
import numpy as np
import numpy_demo

a = np.array([1.0, 2.0, 3.0, 4.0])
b = np.array([5.0, 6.0, 7.0, 8.0])
print(numpy_demo.add_arrays(a, b))  # [6. 8. 10. 12.]

# 矩阵乘法示例
x = np.array([[1.0, 2.0], [3.0, 4.0]])
y = np.array([[5.0, 6.0], [7.0, 8.0]])
print(numpy_demo.matrix_multiply(x, y))
# [[19. 22.]
#  [43. 50.]]
```

### 8.2 Eigen 集成

```cpp
#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <Eigen/Dense>

namespace py = pybind11;

// 直接接受/返回 Eigen 矩阵
Eigen::MatrixXd add_matrices(const Eigen::MatrixXd &a,
                              const Eigen::MatrixXd &b) {
    return a + b;
}

Eigen::VectorXd solve_linear(const Eigen::MatrixXd &A,
                              const Eigen::VectorXd &b) {
    return A.colPivHouseholderQr().solve(b);
}

PYBIND11_MODULE(eigen_demo, m) {
    m.def("add_matrices", &add_matrices);
    m.def("solve_linear", &solve_linear);
}
```

> **注意**：Eigen 绑定会自动在 NumPy 数组和 Eigen 矩阵间转换，且**支持零拷贝**（当内存布局匹配时）。

---

## 9. 继承与多态

### 9.1 基类与派生类绑定

```cpp
#include <pybind11/pybind11.h>
namespace py = pybind11;

class Animal {
public:
    virtual ~Animal() = default;
    virtual std::string speak() const = 0;
    std::string type() const { return type_; }
protected:
    std::string type_ = "Animal";
};

class Dog : public Animal {
public:
    Dog() { type_ = "Dog"; }
    std::string speak() const override { return "Woof!"; }
    void wag_tail() const { /* ... */ }
};

class Cat : public Animal {
public:
    Cat() { type_ = "Cat"; }
    std::string speak() const override { return "Meow!"; }
    void purr() const { /* ... */ }
};

// 接受基类引用的函数
std::string make_sound(const Animal &animal) {
    return animal.speak();
}

PYBIND11_MODULE(inheritance_demo, m) {
    // 绑定基类
    py::class_<Animal>(m, "Animal")
        .def("speak", &Animal::speak)
        .def("type", &Animal::type);

    // 绑定派生类（指定基类）
    py::class_<Dog, Animal>(m, "Dog")
        .def(py::init<>())
        .def("speak", &Dog::speak)
        .def("wag_tail", &Dog::wag_tail);

    py::class_<Cat, Animal>(m, "Cat")
        .def(py::init<>())
        .def("speak", &Cat::speak)
        .def("purr", &Cat::purr);

    m.def("make_sound", &make_sound);
}
```

```python
import inheritance_demo

dog = inheritance_demo.Dog()
cat = inheritance_demo.Cat()

print(dog.speak())              # Woof!
print(cat.speak())              # Meow!
print(inheritance_demo.make_sound(dog))  # Woof!
print(inheritance_demo.make_sound(cat))  # Meow!

# Python 端也可以继承 C++ 类（跳床类）
```

### 9.2 跳床类（Trampoline）

支持 Python 端重写虚函数：

```cpp
// 跳床类：让 Python 能重写 C++ 虚函数
class PyAnimal : public Animal {
public:
    using Animal::Animal;  // 继承构造函数

    std::string speak() const override {
        PYBIND11_OVERRIDE_PURE(
            std::string,   // 返回类型
            Animal,        // 基类
            speak,         // 函数名
            /* 参数为空 */
        );
    }
};

// 绑定时的修改
py::class_<Animal, PyAnimal>(m, "Animal")
    .def(py::init<>())
    .def("speak", &Animal::speak);
```

```python
import inheritance_demo

# Python 端继承 C++ 类
class Duck(inheritance_demo.Animal):
    def speak(self):
        return "Quack!"

duck = Duck()
print(duck.speak())  # Quack!
print(inheritance_demo.make_sound(duck))  # Quack!
```

---

## 10. 枚举与属性

### 10.1 枚举绑定

```cpp
enum class Color { Red, Green, Blue };
enum class Status { Success = 0, Warning = 1, Error = 2 };

PYBIND11_MODULE(enum_demo, m) {
    py::enum_<Color>(m, "Color")
        .value("Red", Color::Red)
        .value("Green", Color::Green)
        .value("Blue", Color::Blue)
        .export_values();  // 导出为模块级别常量

    py::enum_<Status>(m, "Status")
        .value("Success", Status::Success)
        .value("Warning", Status::Warning)
        .value("Error", Status::Error)
        // 支持整数运算
        .def("__int__", [](Status s) { return static_cast<int>(s); });
}
```

```python
import enum_demo

print(enum_demo.Red)                # Color.Red
print(enum_demo.Color.Green)        # Color.Green
print(int(enum_demo.Status.Error))  # 2

# 枚举比较
assert enum_demo.Color.Red == enum_demo.Color.Red
```

### 10.2 只读属性与静态属性

```cpp
class Config {
public:
    static constexpr int MAX_CONNECTIONS = 1000;
    static constexpr const char* APP_NAME = "MyApp";
    static constexpr double PI = 3.14159265359;

    int timeout() const { return timeout_; }
    void set_timeout(int t) { timeout_ = t; }

private:
    int timeout_ = 30;
};

PYBIND11_MODULE(config_demo, m) {
    py::class_<Config>(m, "Config")
        .def(py::init<>())
        .def_property("timeout", &Config::timeout, &Config::set_timeout)
        // 类级别属性
        .def_property_readonly_static("MAX_CONNECTIONS",
            [](py::object) { return Config::MAX_CONNECTIONS; })
        .def_property_readonly_static("APP_NAME",
            [](py::object) { return Config::APP_NAME; })
        .def_property_readonly_static("PI",
            [](py::object) { return Config::PI; });
}
```

---

## 11. 异常处理

### 11.1 C++ 异常 → Python 异常

```cpp
#include <stdexcept>

double divide(double a, double b) {
    if (b == 0.0)
        throw std::invalid_argument("division by zero");
    return a / b;
}

class Database {
public:
    void connect(const std::string &host) {
        if (host.empty())
            throw std::runtime_error("Host cannot be empty");
        connected_ = true;
    }
private:
    bool connected_ = false;
};

PYBIND11_MODULE(exception_demo, m) {
    m.def("divide", &divide);

    // 注册自定义异常转换
    static py::exception<Database> db_exc(m, "DatabaseError");

    py::class_<Database>(m, "Database")
        .def(py::init<>())
        .def("connect", &Database::connect);
}
```

```python
import exception_demo

try:
    result = exception_demo.divide(10, 0)
except ZeroDivisionError:
    print("Caught division by zero!")

try:
    db = exception_demo.Database()
    db.connect("")
except RuntimeError as e:
    print(f"Database error: {e}")
```

### 11.2 自定义异常类型

```cpp
class MyException : public std::exception {
public:
    explicit MyException(const std::string &msg) : msg_(msg) {}
    const char* what() const noexcept override { return msg_.c_str(); }
private:
    std::string msg_;
};

void risky_function(int value) {
    if (value < 0)
        throw MyException("Value must be non-negative, got " + std::to_string(value));
}

PYBIND11_MODULE(custom_exc, m) {
    // 注册自定义 Python 异常
    py::register_exception<MyException>(m, "MyCustomError");

    m.def("risky_function", &risky_function);
}
```

```python
import custom_exc

try:
    custom_exc.risky_function(-5)
except custom_exc.MyCustomError as e:
    print(f"Caught custom error: {e}")
```

---

## 12. 构建系统集成

### 12.1 CMake 方式（推荐中型以上项目）

**项目结构**：

```
myproject/
├── CMakeLists.txt
├── src/
│   ├── CMakeLists.txt
│   ├── core.cpp
│   ├── core.h
│   └── bindings.cpp
└── tests/
    └── test_core.py
```

**根 `CMakeLists.txt`**：

```cmake
cmake_minimum_required(VERSION 3.14)
project(MyProject VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找 pybind11
find_package(pybind11 REQUIRED)

# 或使用 add_subdirectory
# add_subdirectory(extern/pybind11)

add_subdirectory(src)
```

**`src/CMakeLists.txt`**：

```cmake
# 核心 C++ 库
add_library(core STATIC
    core.cpp
)

target_include_directories(core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# Python 绑定模块
pybind11_add_module(my_module
    bindings.cpp
)

target_link_libraries(my_module PRIVATE core)
```

**编译命令**：

```bash
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
```

### 12.2 setuptools 方式（推荐 pip 包）

**`setup.py`**：

```python
from setuptools import setup, find_packages
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "my_module",
        [
            "src/bindings.cpp",
            "src/core.cpp",
        ],
        include_dirs=["src"],
        cxx_std=17,
        extra_compile_args=["-O3"],
        define_macros=[("VERSION_INFO", '"1.0.0"')],
    ),
]

setup(
    name="my_module",
    version="1.0.0",
    author="Your Name",
    description="A pybind11 example module",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    packages=find_packages(),
    python_requires=">=3.7",
)
```

**安装**：

```bash
pip install .              # 安装
pip install -e .           # 开发模式（修改 C++ 后需重新编译）
```

### 12.3 使用 scikit-build（现代方案）

**`pyproject.toml`**：

```toml
[build-system]
requires = ["scikit-build-core>=0.5", "pybind11"]
build-backend = "scikit_build_core.build"

[project]
name = "my_module"
version = "1.0.0"
```

**`CMakeLists.txt`**（同 CMake 方式，scikit-build 自动处理 pybind11 查找）。

```bash
pip install .  # scikit-build 会自动调用 CMake
```

---

## 13. 实战案例

### 13.1 案例一：图像处理滤镜

```cpp
// image_filter.cpp
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <algorithm>
#include <cmath>

namespace py = pybind11;

// 灰度化
py::array_t<uint8_t> grayscale(py::array_t<uint8_t> img) {
    auto buf = img.request();
    if (buf.ndim != 3 || buf.shape[2] != 3)
        throw std::runtime_error("Expected HxWx3 RGB image");

    int h = buf.shape[0], w = buf.shape[1];
    auto result = py::array_t<uint8_t>({h, w});
    auto buf_r = result.request();

    uint8_t *src = static_cast<uint8_t*>(buf.ptr);
    uint8_t *dst = static_cast<uint8_t*>(buf_r.ptr);

    for (int i = 0; i < h * w; i++) {
        int r = src[i * 3 + 0];
        int g = src[i * 3 + 1];
        int b = src[i * 3 + 2];
        dst[i] = static_cast<uint8_t>(0.299 * r + 0.587 * g + 0.114 * b);
    }

    return result;
}

// 高斯模糊（简化版 3x3 核）
py::array_t<uint8_t> gaussian_blur(py::array_t<uint8_t> img, int radius = 1) {
    auto buf = img.request();
    int h = buf.shape[0], w = buf.shape[1], c = buf.shape[2];

    auto result = py::array_t<uint8_t>({h, w, c});
    auto buf_r = result.request();

    uint8_t *src = static_cast<uint8_t*>(buf.ptr);
    uint8_t *dst = static_cast<uint8_t*>(buf_r.ptr);

    // 3x3 高斯核
    const float kernel[9] = {1, 2, 1, 2, 4, 2, 1, 2, 1};
    const float sum = 16.0f;

    for (int y = 1; y < h - 1; y++) {
        for (int x = 1; x < w - 1; x++) {
            for (int ch = 0; ch < c; ch++) {
                float val = 0;
                for (int dy = -1; dy <= 1; dy++) {
                    for (int dx = -1; dx <= 1; dx++) {
                        val += src[((y + dy) * w + (x + dx)) * c + ch]
                               * kernel[(dy + 1) * 3 + (dx + 1)];
                    }
                }
                dst[(y * w + x) * c + ch] = static_cast<uint8_t>(val / sum);
            }
        }
    }

    return result;
}

PYBIND11_MODULE(image_filter, m) {
    m.doc() = "Fast image processing filters";
    m.def("grayscale", &grayscale, "Convert RGB image to grayscale");
    m.def("gaussian_blur", &gaussian_blur,
          py::arg("img"), py::arg("radius") = 1,
          "Apply Gaussian blur to an image");
}
```

```python
import numpy as np
from PIL import Image
import image_filter

# 加载图片
img = np.array(Image.open("photo.jpg"))

# C++ 加速处理
gray = image_filter.grayscale(img)
blurred = image_filter.gaussian_blur(img, radius=1)

# 保存结果
Image.fromarray(gray).save("gray.jpg")
Image.fromarray(blurred).save("blurred.jpg")
```

### 13.2 案例二：数值计算库

```cpp
// numerical.cpp
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <vector>
#include <cmath>

namespace py = pybind11;

// 快速傅里叶变换辅助（简化版离散傅里叶变换）
// 实际项目中建议调用 FFTW 或 MKL
std::vector<std::complex<double>> dft(const std::vector<double> &signal) {
    size_t N = signal.size();
    std::vector<std::complex<double>> result(N);

    for (size_t k = 0; k < N; k++) {
        std::complex<double> sum(0, 0);
        for (size_t n = 0; n < N; n++) {
            double angle = -2.0 * M_PI * k * n / N;
            sum += signal[n] * std::complex<double>(cos(angle), sin(angle));
        }
        result[k] = sum;
    }

    return result;
}

// 数值积分：辛普森法则
double simpson_integrate(
    const std::function<double(double)> &f,
    double a, double b, int n = 1000
) {
    if (n % 2 != 0) n++;  // n 必须为偶数

    double h = (b - a) / n;
    double sum = f(a) + f(b);

    for (int i = 1; i < n; i++) {
        double x = a + i * h;
        sum += (i % 2 == 0) ? 2 * f(x) : 4 * f(x);
    }

    return sum * h / 3.0;
}

PYBIND11_MODULE(numerical, m) {
    m.doc() = "Numerical computing utilities";

    m.def("dft", &dft, py::arg("signal"),
          "Compute Discrete Fourier Transform");

    m.def("simpson_integrate", &simpson_integrate,
          py::arg("f"), py::arg("a"), py::arg("b"), py::arg("n") = 1000,
          "Numerical integration using Simpson's rule");
}
```

```python
import numpy as np
import numerical

# DFT
t = np.linspace(0, 1, 100, endpoint=False)
signal = np.sin(2 * np.pi * 5 * t) + 0.5 * np.sin(2 * np.pi * 20 * t)
spectrum = numerical.dft(signal.tolist())

# 数值积分
import math
result = numerical.simpson_integrate(lambda x: math.sin(x), 0, math.pi * 2, n=10000)
print(f"∫ sin(x) dx from 0 to 2π = {result}")  # ≈ 0
```

### 13.3 案例三：C 语言库的包装

```cpp
// wrap_clib.cpp
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <zlib.h>
#include <vector>
#include <stdexcept>

namespace py = pybind11;

// 包装 zlib 的 compress 函数
py::bytes zlib_compress(const py::bytes &data, int level = 6) {
    auto str = data.cast<std::string>();

    uLongf compressed_size = compressBound(str.size());
    std::vector<Bytef> buffer(compressed_size);

    int ret = compress2(
        buffer.data(), &compressed_size,
        reinterpret_cast<const Bytef*>(str.data()), str.size(),
        level
    );

    if (ret != Z_OK)
        throw std::runtime_error("Compression failed");

    return py::bytes(
        reinterpret_cast<char*>(buffer.data()), compressed_size
    );
}

py::bytes zlib_decompress(const py::bytes &data, size_t expected_size = 0) {
    auto str = data.cast<std::string>();

    uLongf decompressed_size = expected_size ? expected_size : str.size() * 4;
    std::vector<Bytef> buffer(decompressed_size);

    int ret;
    do {
        ret = uncompress(
            buffer.data(), &decompressed_size,
            reinterpret_cast<const Bytef*>(str.data()), str.size()
        );

        if (ret == Z_BUF_ERROR) {
            decompressed_size *= 2;
            buffer.resize(decompressed_size);
            ret = uncompress(
                buffer.data(), &decompressed_size,
                reinterpret_cast<const Bytef*>(str.data()), str.size()
            );
        }
    } while (ret == Z_BUF_ERROR);

    if (ret != Z_OK)
        throw std::runtime_error("Decompression failed");

    return py::bytes(
        reinterpret_cast<char*>(buffer.data()), decompressed_size
    );
}

PYBIND11_MODULE(zlib_wrapper, m) {
    m.doc() = "Python wrapper for zlib C library";
    m.def("compress", &zlib_compress,
          py::arg("data"), py::arg("level") = 6);
    m.def("decompress", &zlib_decompress,
          py::arg("data"), py::arg("expected_size") = 0);
}
```

---

## 14. 性能对比与最佳实践

### 14.1 性能测试

```python
import time
import numpy as np
import my_module

# 测试 C++ vs Python 纯循环
def python_sum_of_squares(n):
    total = 0.0
    for i in range(n):
        total += i * i
    return total

# C++ 版本
def bench():
    n = 10_000_000

    start = time.time()
    result_py = python_sum_of_squares(n)
    elapsed_py = time.time() - start

    start = time.time()
    result_cpp = my_module.sum_of_squares(n)
    elapsed_cpp = time.time() - start

    print(f"Python: {elapsed_py:.4f}s")
    print(f"C++ pybind11: {elapsed_cpp:.4f}s")
    print(f"Speedup: {elapsed_py / elapsed_cpp:.1f}x")
    # 典型结果: Speedup: 50-100x

bench()
```

### 14.2 最佳实践清单

| 实践 | 说明 |
|------|------|
| **减少 Python ↔ C++ 转换** | 批量处理数据，减少跨语言调用次数 |
| **使用引用传递大数据** | `const std::vector<T>&` 避免不必要拷贝 |
| **利用 NumPy 零拷贝** | `py::array` 直接访问内存，避免数据搬运 |
| **合理使用 `py::call_guard<py::gil_scoped_release>()`** | 长时间计算时释放 GIL，允许多线程并发 |
| **返回 py::object 而非 STL 容器** | 当不需要修改时，避免容器自动转换的开销 |
| **使用 Release 模式编译** | `-O3 -DNDEBUG` 可以带来 2-5 倍性能提升 |
| **避免在循环中调用绑定的 C++ 函数** | 函数调用本身有开销，尽量将循环移到 C++ 侧 |

### 14.3 释放 GIL 示例

```cpp
// 长时间计算时释放 GIL
m.def("heavy_computation", [](int n) {
    py::gil_scoped_release release;  // 释放 GIL
    double result = 0.0;
    for (int i = 0; i < n; i++) {
        result += std::sin(i) * std::cos(i);
    }
    // release 析构时自动重新获取 GIL
    return result;
});
```

---

## 15. 常见问题 FAQ

### Q1: 如何调试 pybind11 代码？

```bash
# 使用 gdb/lldb
gdb --args python3 your_script.py

# 打印 Python 异常
catch throw
run
# 崩溃时用 py-bt 查看 Python 调用栈
```

### Q2: 如何处理返回指针/引用时的所有权问题？

```cpp
// return_value_policy 选项：
// - reference        : 仅引用，Python 不管理生命周期
// - reference_internal : 引用内部对象，生命周期绑定到父对象
// - take_ownership   : Python 接管所有权（调用 delete）
// - copy             : 返回副本（默认）
// - move             : 移动语义

m.def("create_widget", &create_widget,
      py::return_value_policy::take_ownership);
```

### Q3: 如何在 C++ 侧调用 Python 函数？

```cpp
void for_each_element(py::list list, py::function callback) {
    for (auto item : list) {
        callback(item);  // 调用 Python 回调
    }
}
```

### Q4: 如何保护 C++ 类型不被隐式转换？

```cpp
// 使用 py::is_final 禁止 Python 端继承
py::class_<MyClass>(m, "MyClass", py::is_final());

// 使用 non-copyable
py::class_<Singleton, std::unique_ptr<Singleton, py::nodelete>>(m, "Singleton");
```

### Q5: 如何打包为 wheel 发布？

```bash
# 安装 build 工具
pip install build

# 构建 wheel
python -m build

# wheel 文件在 dist/ 目录
# 上传到 PyPI
pip install twine
twine upload dist/*
```

### Q6: macOS/Linux/Windows 跨平台编译注意事项？

- **Windows**：需要安装 Visual Studio Build Tools，使用 MSVC 编译器
- **macOS**：需安装 Xcode Command Line Tools，注意 `MACOSX_DEPLOYMENT_TARGET`
- **Linux**：使用 GCC ≥ 5.0 或 Clang ≥ 3.3，注意 `manylinux` 兼容性
- **通用方案**：使用 `cibuildwheel` 工具自动构建多平台 wheel

---

## 总结

pybind11 是现代 C++ 项目与 Python 互操作的**首选方案**，核心优势：

1. **Header-only**：零编译依赖，开箱即用
2. **类型安全**：自动类型推导 + 编译期检查
3. **高性能**：接近原生 C++ 速度，支持零拷贝
4. **生态丰富**：NumPy、Eigen、STL 深度整合
5. **双向调用**：既能 C++ → Python，也能 Python → C++

常用头文件速查：

```cpp
#include <pybind11/pybind11.h>       // 核心
#include <pybind11/stl.h>            // STL 容器自动转换
#include <pybind11/stl_bind.h>       // 绑定 STL 容器
#include <pybind11/numpy.h>          // NumPy 互操作
#include <pybind11/eigen.h>          // Eigen 矩阵支持
#include <pybind11/functional.h>     // std::function 支持
#include <pybind11/chrono.h>         // 时间类型支持
#include <pybind11/complex.h>        // 复数支持
#include <pybind11/embed.h>          // 嵌入式 Python 解释器
```

---

> **参考资源**：
> - [pybind11 官方文档](https://pybind11.readthedocs.io/)
> - [pybind11 GitHub](https://github.com/pybind/pybind11)
> - [Python C API 参考](https://docs.python.org/3/c-api/)

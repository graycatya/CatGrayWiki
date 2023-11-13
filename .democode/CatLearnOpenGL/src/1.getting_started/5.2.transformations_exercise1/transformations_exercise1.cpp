int main()
{
    [...]
    while(!glfwWindowShouldClose(window))
    {
        [...]        
        // create transformations
        glm::mat4 transform = glm::mat4(1.0f);
        transform = glm::rotate(transform, (float)glfwGetTime(), glm::vec3(0.0f, 0.0f, 1.0f)); // switched the order
        transform = glm::translate(transform, glm::vec3(0.5f, -0.5f, 0.0f)); // switched the order               
        [...]
    }
}

/*为什么我们的容器现在旋转我们的屏幕?：
== ===================================================
记住，矩阵乘法是反向应用的。这一次的翻译是这样的
首先应用于将其定位在屏幕右下角的容器。
在平移之后，旋转应用于平移后的容器。

旋转变换也被称为基的变换
当我们深入研究线性代数的时候。因为我们要改变
在容器的基础上，下一个翻译结果将翻译容器
基于新的基向量。一旦矢量稍微旋转，垂直
例如，翻译也会进行轻微的翻译。

如果我们首先应用旋转，那么它们会围绕旋转原点(0,0,0)解决，但是
因为容器是首先被平移的，所以它的旋转原点不再是(0,0,0)
看起来它好像在绕着原点旋转。

如果你在想象或计算上有困难，不要担心。如果你
尝试转换，你很快就会掌握它;所需要的一切
就是实践和经验。
* /
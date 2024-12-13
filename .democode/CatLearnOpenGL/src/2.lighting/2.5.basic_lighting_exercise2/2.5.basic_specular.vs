#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;

out vec3 FragPos;
out vec3 Normal;
// 尝试使用不同的环境光、漫反射和镜面强度，观察它们怎么是影响光照效果的。
// 同样，尝试实验一下镜面光照的反光度因子。
// 尝试理解为什么某一个值能够有着特定视觉输出。
out vec3 LightPos;

// 现在我们在顶点着色器中定义统一，并将“视图空间”光点传递给片段着色器。
// lightPos当前在世界空间中。
uniform vec3 lightPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    
    FragPos = vec3(view * model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(view * model))) * aNormal;

    // 将世界空间光位置转换为视图空间光位置
    LightPos = vec3(view * vec4(lightPos, 1.0));
    
}
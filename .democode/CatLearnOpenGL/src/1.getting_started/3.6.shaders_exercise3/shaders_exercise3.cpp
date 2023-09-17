// 顶点着色器:
// ==============
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;

// out vec3 ourColor;
out vec3 ourPosition;

void main()
{
    gl_Position = vec4(aPos, 1.0);
    ourPosition = aPos;
}

// 片段着色器:
// ================
#version 330 core;
out vec4 FragColor;
in vec3 ourPosition;

void main()
{
    //注意位置值是如何线性插值来获得所有不同的颜色的
    FragColor = vec4(ourPosition, 1.0); 
}

/*
问题的答案:你知道为什么左下角是黑色的吗?
-- --------------------------------------------------------------------
思考一下:片段颜色的输出等于(插值的)坐标三角形。
三角形左下角点的坐标是多少?这是(-0.5f， -0.5f, 0.0f)自Xy值是负的，它们被限制在0.0f的值。
这个过程一直持续到三角形，因为从那个点上的值将再次被正插值。
0.0f的值当然是黑色的这就解释了三角形的黑色部分。
*/
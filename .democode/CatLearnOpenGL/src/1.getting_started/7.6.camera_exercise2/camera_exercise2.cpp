// 试着创建你自己的LookAt函数，其中你需要手动创建一个我们在一开始讨论的观察矩阵。用你的函数实现来替换GLM的LookAt函数，看看它是否还能一样地工作
#include <glm/glm.hpp>

glm::mat4 calculate_lookAt_matrix(glm::vec3 position, glm::vec3 target, glm::vec3 worldUp)
{

    // 1. 位置=已知
    // 2. 计算cameraDirection
    glm::vec3 zaxis = glm::normalize(position - target);
    // 3. 得到正的右轴向量
    glm::vec3 xaxis = glm::normalize(glm::cross(glm::normalize(worldUp), zaxis));
    // 4. 计算相机向上矢量
    glm::vec3 yaxis = glm::cross(zaxis, xaxis);

    // 创建平移和旋转矩阵
    // 在glm中，由于列主布局，我们以mat[col][row]的方式访问元素
    glm::mat4 translation = glm::mat4(1.0f);
    translation[3][0] = -position.x; // 第三列，第一行
    translation[3][1] = -position.y;
    translation[3][2] = -position.z;

    glm::mat4 rotation = glm::mat4(1.0f);
    rotation[0][0] = xaxis.x; // 第一列，第一行
    rotation[1][0] = xaxis.y;
    rotation[2][0] = xaxis.z;
    rotation[0][1] = yaxis.x; // 第一列，第二行
    rotation[1][1] = yaxis.y;
    rotation[2][1] = yaxis.z;
    rotation[0][2] = zaxis.x; // 第一列，第三行
    rotation[1][2] = zaxis.y;
    rotation[2][2] = zaxis.z; 

    // 返回lookAt矩阵作为平移和旋转矩阵的组合
    return rotation * translation; // 记住从右向左阅读(先翻译再旋转)

}

// Don't forget to replace glm::lookAt with your own version
// view = glm::lookAt(glm::vec3(camX, 0.0f, camZ), glm::vec3(0.0f, 0.0f, 0.0f), glm::vec3(0.0f, 1.0f, 0.0f));
view = calculate_lookAt_matrix(glm::vec3(camX, 0.0f, camZ), glm::vec3(0.0f, 0.0f, 0.0f), glm::vec3(0.0f, 1.0f, 0.0f));
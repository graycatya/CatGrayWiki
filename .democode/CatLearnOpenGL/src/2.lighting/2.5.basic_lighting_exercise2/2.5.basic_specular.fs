#version 330 core
out vec4 FragColor;

in vec3 Normal;  
in vec3 FragPos;  
in vec3 LightPos; // 额外的变量，由于我们需要视图空间中的灯光位置，因此我们在顶点着色器中计算该位置

uniform vec3 objectColor;
uniform vec3 lightColor;

void main()
{
    // ambient 环境
    float ambientStrength = 0.1;
    vec3 ambient = ambientStrength * lightColor;

    // diffuse 漫反射
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(LightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;

    // specular 镜面
    float specularStrength = 0.5;
    vec3 viewDir = normalize(-FragPos); // 查看者在视图空间中始终处于（0，0，0）处，因此viewDir为（0，0，0）- Position => -Position 
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = specularStrength * spec * lightColor;

    // 最终光线计算
    vec3 result = (ambient + diffuse + specular) * objectColor;
    FragColor = vec4(result, 1.0);
}


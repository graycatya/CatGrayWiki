#version 330 core
out vec4 FragColor;

struct Material {
    sampler2D diffuse;
    sampler2D specular;
    float shininess;
};

struct Light {
    vec3 position;
    // 聚光-手电筒
    vec3 direction;
    float cutOff;
    float outerCutOff;
    

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;

    float constant;
    float linear;
    float quadratic;
};

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoords;

uniform vec3 viewPos;
uniform Material material;
uniform Light light;

void main()
{
    // ambient 环境光
    vec3 ambient = light.ambient * texture(material.diffuse, TexCoords).rgb;

    // diffuse 漫反射
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(light.position - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = light.diffuse * diff * texture(material.diffuse, TexCoords).rgb;

    // specular 镜面
    vec3 viewDir = normalize(viewPos - FragPos); // 查看者在视图空间中始终处于（0，0，0）处，因此viewDir为（0，0，0）- Position => -Position 
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    // 这里我们反转采样的镜面反射颜色。黑色变成白色
    vec3 specular = light.specular * spec * texture(material.specular, TexCoords).rgb;

    // 检查灯光是否在聚光灯锥内
    float theta = dot(lightDir, normalize(-light.direction));
    // lightDir 是从表面点到光源的方向向量。
    // light.direction 是聚光灯的朝向向量，通常指向聚光灯发光的方向。
    // normalize(-light.direction) 是将聚光灯的反方向向量进行归一化，也就是聚光灯的主轴方向。
    // dot(lightDir, normalize(-light.direction)) 计算这两个向量的点积，得到的是 lightDir 和聚光灯主轴之间的夹角的余弦值。这个值用于确定当前点是否在聚光灯的照射范围内。
    float epsilon = (light.cutOff - light.outerCutOff);
    // light.cutOff 和 light.outerCutOff 是聚光灯的光照范围参数。
    // cutOff 是聚光灯的内锥角，表示完全光照的范围。
    // outerCutOff 是聚光灯的外锥角，表示光照开始衰减的范围。
    // epsilon 是内锥角和外锥角之间的差值，用于计算光照的线性衰减。
    //float intensity = clamp((theta - light.outerCutOff) / epsilon, 0.0, 1.0);
    float intensity = smoothstep(light.outerCutOff, light.cutOff, theta);
    // theta 是前面计算的点积值，表示夹角的余弦。
    // light.outerCutOff 是外锥角的余弦值。
    // (theta - light.outerCutOff) / epsilon 计算光照强度的衰减因子。
    // clamp 函数将这个衰减因子限制在 0.0 到 1.0 之间，确保光照强度不会超过这个范围。
    diffuse *= intensity;
    specular *= intensity;

    // attenuation 光线衰减
    float distance = length(light.position - FragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));
    
    //从环境中去除衰减，否则在很远的距离内，由于其他分支的环境项，光线在聚光灯内会比在聚光灯外暗
    ambient *= attenuation;
    diffuse *= attenuation;
    specular *= attenuation;

    vec3 result = ambient + diffuse + specular;
    FragColor = vec4(result, 1.0);
    
}
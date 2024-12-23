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
    vec3 lightDir = normalize(light.position - FragPos);

    // 检查灯光是否在聚光灯锥内
    float theta = dot(lightDir, normalize(-light.direction));

    // 请记住，我们将角度视为cos而不是度数，因此使用了“>”。
    if(theta > light.cutOff)
    {
        // ambient 环境光
        vec3 ambient = light.ambient * texture(material.diffuse, TexCoords).rgb;

            // diffuse 漫反射
        vec3 norm = normalize(Normal);
        //vec3 lightDir = normalize(light.position - FragPos);
        float diff = max(dot(norm, lightDir), 0.0);
        vec3 diffuse = light.diffuse * diff * texture(material.diffuse, TexCoords).rgb;

            // specular 镜面
        vec3 viewDir = normalize(viewPos - FragPos); // 查看者在视图空间中始终处于（0，0，0）处，因此viewDir为（0，0，0）- Position => -Position 
        vec3 reflectDir = reflect(-lightDir, norm);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
        // 这里我们反转采样的镜面反射颜色。黑色变成白色
        vec3 specular = light.specular * spec * texture(material.specular, TexCoords).rgb;

        // attenuation 光线衰减
        float distance = length(light.position - FragPos);
        float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));
        
        //从环境中去除衰减，否则在很远的距离内，由于其他分支的环境项，光线在聚光灯内会比在聚光灯外暗
        //ambient *= attenuation;
        diffuse *= attenuation;
        specular *= attenuation;


        vec3 result = ambient + diffuse + specular;
        FragColor = vec4(result, 1.0);
    } else {
        // 否则，使用环境光，这样场景在聚光灯外就不会完全黑暗。
        FragColor = vec4(light.ambient * texture(material.diffuse, TexCoords).rgb, 1.0);
    }
}

// 看看你是否能够修改摄像机类，使得其能够变成一个真正的FPS摄像机（也就是说不能够随意飞行）；你只能够呆在xz平面上
//这个函数在camera类中找到。我们所做的基本上就是保持y位置值为0°f，以强制我们
//用户粘在地面。

[...]
// 处理从任何类似键盘的输入系统接收的输入。接受相机定义的ENUM形式的输入参数(从窗口系统中抽象出来)
void ProcessKeyboard(Camera_Movement direction, float deltaTime)
{
    float velocity = MovementSpeed * deltaTime;
    if (direction == FORWARD)
        Position += Front * velocity;
    if (direction == BACKWARD)
        Position -= Front * velocity;
    if (direction == LEFT)
        Position -= Right * velocity;
    if (direction == RIGHT)
        Position += Right * velocity;
    // 确保用户停留在地面水平
    Position.y = 0.0f; // <-- this one-liner keeps the user at the ground level (xz plane)
}
[...]
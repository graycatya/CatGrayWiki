# CatGray IP · v10 定版模型

v10 已定版。角色采用连续圆润的右臂弧线招手：向前抬起、立起前臂轻摆两次，再沿弧线放下。静态外形、贴图与三个基础动作随工程一起交付。

## 打开与播放

打开本目录的 [CatGray_IP.blend](CatGray_IP.blend)。时间轴已排好 **1–240 帧、24 FPS、10 秒**的预览，按空格播放。

| 时间轴 | 内容 |
| --- | --- |
| 1–72 | 待机呼吸 |
| 73–168 | 向前招手 |
| 169–240 | 两轮原地走路 |

骨骼默认不置顶，使用细线显示；辅助骨骼集合默认隐藏。需要透视编辑时，在大纲视图选择 `CATGRAY_RIG`，临时开启 **对象属性 → 视图显示 → In Front（在前面）**，再进入姿态模式。查看表面时关闭 In Front。

若 Blender 窗口里仍打开旧内容，请重新打开定版文件；自己的未保存修改先另存为其他文件。

## 文件用途

| 文件或目录 | 用途 |
| --- | --- |
| `CatGray_IP.blend` | 可编辑的骨骼、权重、材质、摄影棚、NLA 时间轴 |
| `CatGray_IP.glb` | 标准 glTF 2.0 二进制文件，含三个动作和内嵌贴图 |
| `textures/` | Fur 与 BareBody 两张 PNG，工程内也有打包副本 |
| `previews/` | 定版外形的正面、侧面、背面、局部视图和动画封面 |
| `animations/CatGray_Animation_Preview.mp4` | 10 秒完整预览 |
| `animations/Wave.mp4` | 4 秒招手，斜侧面视角 |
| `animations/Wave_Side.mp4` | 4 秒招手，侧面检查向前弧度 |
| `animations/Idle_Breathe.mp4` | 3 秒待机 |
| `animations/Walk_InPlace.mp4` | 3 秒走路，播放两个循环 |
| `source/CatGray_Base.blend` / `base_info.json` | 绑定程序需要的静态制作底模和参数 |
| `scripts/` / `manage.py` | 生成、导出、预览及验证入口 |
| `qa/` | 当前版本的检查结果及诊断截图 |

所有视频为 720 × 720、24 FPS、H.264 MP4，无音轨。GLB 可独立分发；Blender 工程中的角色贴图和三视图已打包，外部文件保留供编辑和重新生成。

## 动作与控制

28 个角色网格，84 根原生骨骼，其中 79 根启用变形。右臂有 41 个连续截面骨骼。导出时去掉 4 个脚部/膝盖 IK 控制器，GLB 保留 80 个骨骼节点；每个导出顶点最多四个骨骼影响。

| 独立 Action | 时长 | 关键帧范围 | 循环 |
| --- | --- | --- | --- |
| `Idle_Breathe` | 3 秒 | 1–73 | 是 |
| `Wave` | 4 秒 | 1–97 | 回到起始姿势 |
| `Walk_InPlace` | 1.5 秒 | 1–37 | 是 |

关键帧范围包含用于闭合动作的末端帧，因此“96 帧视频”和“1–97 动作关键帧”并不矛盾。GLB 中动作时长分别为 3、4、1.5 秒。

编辑单个 Action 时，先禁用 NLA 中的 `播放预览 • 待机 / 挥手 / 走路` 轨道，再在动作编辑器选动作。三个同名存档 NLA 轨道默认静音，避免多个动作同时叠加。

| 控制项 | 用途 |
| --- | --- |
| `CTRL_Root` | 整个角色移动、旋转 |
| `Pelvis / Spine / Chest / Head` | 身体和头部 |
| `Clavicle.L/R`、`UpperArm.L/R` | 肩部及整条手臂调整 |
| `Forearm.L / Hand.L` | 左前臂、手掌 FK |
| `ArmArc.R.00–40` | 右臂连续截面，在隐藏的辅助集合中启用后编辑 |
| `CTRL_Foot_IK.L/R` | 脚的位置及朝向 |
| `CTRL_Knee_Pole.L/R` | 膝盖方向 |
| `Ear.L/R`、`Tail.01–07` | 耳朵与尾巴 |

右臂的主要动作由 `scripts/wave_arc.py` 生成并记录成普通骨骼关键帧；`UpperArm.R` 可整体调整，旧 `Forearm.R / Hand.R` 已不驱动右臂皮肤。调整招手路径的方法见维护手册。脚部 IK 和辅助约束在导出时转换成普通骨骼关键帧；进一步编辑控制器应使用 `.blend`。

## 维护入口

环境配置与完整步骤见 [制作与维护手册](docs/WORKFLOW.md)。安装 Blender 后，在本目录运行：

```sh
python3 manage.py doctor
python3 manage.py verify
```

`verify` 检查当前成品，不重新生成模型。`rebuild` 会用静态底模重建并覆盖 `.blend` 和 `.glb`；手工编辑工程后通常只需 `export`，不要误用 `rebuild`。

坐标约定：Blender 为 Z 向上、正面朝 -Y；GLB 按标准 glTF 坐标导出。当前提供身体动作，不含眨眼、口型或手指表情绑定。

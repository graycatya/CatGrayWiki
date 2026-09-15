# CatGray IP · 模型类型

原始三视图由各模型类型共用，每种类型独立保存模型、预览和制作工具。

| 类型 | 风格与当前状态 | 入口 |
| --- | --- | --- |
| `model_3d` | 连续圆润造型，v10 定版，含骨骼和三个动画 | [模型说明](model_3d/README.md) · [预览](model_3d/previews/preview_hero.png) |
| `model_voxel` | 中等颗粒体素，v3，18 根骨骼，12 个身体 / 头部 / 表情动作 | [模型说明](model_voxel/README.md) · [动画预览](model_voxel/animations/CatGray_Voxel_Animation_Preview.mp4) |

## 体素模型 · model_voxel

- **查看、编辑模型**：[Blender 工程](model_voxel/CatGray_Voxel.blend)
- **跨软件使用**：[GLB 模型](model_voxel/CatGray_Voxel.glb)
- **播放动作**：[完整预览](model_voxel/animations/CatGray_Voxel_Animation_Preview.mp4)、[走动](model_voxel/animations/Walk_InPlace.mp4)、[跑动](model_voxel/animations/Run_InPlace.mp4)、[跳跃](model_voxel/animations/Jump.mp4)
- **头部与五官**：[点头](model_voxel/animations/Head_Nod.mp4)、[摇头](model_voxel/animations/Head_Shake.mp4)、[转头](model_voxel/animations/Head_Turn.mp4)、[眨眼](model_voxel/animations/Blink.mp4)、[嘴型](model_voxel/animations/Mouth_Talk.mp4)
- **情绪**：[四表情总览](model_voxel/previews/expressions.png)、[喜悦](model_voxel/animations/Emotion_Joy.mp4)、[悲伤](model_voxel/animations/Emotion_Sad.mp4)、[痛苦](model_voxel/animations/Emotion_Pain.mp4)、[生气](model_voxel/animations/Emotion_Angry.mp4)
- **逐块编辑**：[VOX 模型](model_voxel/CatGray_Voxel.vox)
- **参数与重建命令**：[体素模型说明](model_voxel/README.md)

## 圆润模型 · model_3d

v10 已于 2026-09-15 确认为定版。保留定版模型、制作源文件和复现工具，历史版本与过期对比素材已清理。

- **查看、编辑角色**：[Blender 工程](model_3d/CatGray_IP.blend)
- **在其他引擎使用**：[GLB 模型](model_3d/CatGray_IP.glb)，包含贴图和三个动画片段
- **播放成品**：[完整动画](model_3d/animations/CatGray_Animation_Preview.mp4)、[招手](model_3d/animations/Wave.mp4)、[侧面招手](model_3d/animations/Wave_Side.mp4)
- **文件与 Blender 操作**：[模型说明](model_3d/README.md)
- **环境配置、命令和脚本操作**：[制作与维护手册](model_3d/docs/WORKFLOW.md)

```text
ip/
├── README.md
├── references/          原始正视、侧视、背视 PNG
├── model_voxel/
│   ├── CatGray_Voxel.blend / .glb / .vox
│   ├── model_info.json / manage.py / README.md
│   ├── source/            颗粒大小与色板参数
│   ├── scripts/           体素造型、骨骼、动作、导出及验证
│   ├── previews/          静态视角、动作姿势和视频封面
│   ├── animations/        十二个动作视频与完整预览
│   └── qa/                验证报告与 GLB 重新导入截图
└── model_3d/
    ├── CatGray_IP.blend 可编辑的 v10 定版工程
    ├── CatGray_IP.glb   跨软件交付模型
    ├── model_info.json 模型、骨骼、动作及定版信息
    ├── manage.py       统一脚本入口
    ├── textures/       两张角色贴图
    ├── previews/       静态外形与动画封面
    ├── animations/     五个成品视频
    ├── source/         重建 v10 必需的静态底模及参数
    ├── scripts/        造型、绑定、导出、渲染和验证程序
    ├── qa/             验证报告和诊断截图；日志在 logs/
    └── docs/           环境与操作手册
```

`model_3d/source/CatGray_Base.blend` 是圆润模型的制作输入：保留已确认的几何、材质和摄影棚，供绑定脚本读取。它不是另一份交付版本，也不能当作带动画的成品使用。请打包整个 `ip` 目录以保留完整复现能力；只给播放端使用时可单独提供相应类型的 GLB。

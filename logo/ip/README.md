# CatGray IP · v10 定版

v10 已于 2026-09-15 确认为定版。当前目录保留定版模型、原始三视图、制作源文件和复现工具，历史版本与过期对比素材已清理。

- **查看、编辑角色**：[Blender 工程](model_3d/CatGray_IP.blend)
- **在其他引擎使用**：[GLB 模型](model_3d/CatGray_IP.glb)，包含贴图和三个动画片段
- **播放成品**：[完整动画](model_3d/animations/CatGray_Animation_Preview.mp4)、[招手](model_3d/animations/Wave.mp4)、[侧面招手](model_3d/animations/Wave_Side.mp4)
- **文件与 Blender 操作**：[模型说明](model_3d/README.md)
- **环境配置、命令和脚本操作**：[制作与维护手册](model_3d/docs/WORKFLOW.md)

```text
ip/
├── README.md
├── references/          原始正视、侧视、背视 PNG
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

`source/CatGray_Base.blend` 是制作输入：保留已确认的几何、材质和摄影棚，供绑定脚本读取。它不是另一份交付版本，也不能当作带动画的成品使用。请打包整个 `ip` 目录以保留完整复现能力；只给播放端使用时可单独提供 GLB。

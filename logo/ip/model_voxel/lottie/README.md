# CatGray 全部表情与动作 · 矢量 Lottie

## 全部表情和动作

打开 `preview.html` 可离线选择全部 12 个动作，并下载对应 JSON。
`all_actions/` 包含走动、跑动、跳跃、点头、摇头、转头、眨眼、嘴型和喜悦、悲伤、痛苦、生气。
每个动作配有独立 JSON、离线 HTML 播放页和 SVG 封面。
`CatGray_All_Actions.json` 按原工程顺序串联全部动作，35.5 秒；走、跑、跳按原预览重复。
`CatGray_All_Vector_Lottie.zip` 包含全套动画及离线预览。

全套动画直接采样原始 GLB 的骨骼、形态键及其插值，每秒 24 帧。
将共面三角形合并，按实际深度裁切遮挡，再转换为二维矢量路径；背景透明，无图片资源。
身体动作采用略偏侧的全身正交视角；头部、表情动作采用接近正面的头部近景。
采用简化的矢量明暗，不包含原摄影棚的真实光影。所有动作已烘焙为二维路径，不能改变相机或实时混合骨骼。
逐帧矢量文件较大，适合按需加载独立动作；移动端性能和其他 Lottie 播放器仍需在目标设备验证。

重建：安装 `numpy`、`shapely` 后，在模型目录运行 `python scripts/export_all_lottie.py`。
可用 `CATGRAY_LOTTIE_DEPS` 指定额外的 Python 包目录。此脚本会更新全套预览首页。

## 最初的正面表情循环

- 成品：`CatGray_Head_Blink_Joy.json`，512 × 512，24 FPS，5 秒循环。
- 内容：默认 → 眨眼 → 默认 → 开心 → 默认，首尾状态一致。
- 正面正交二维投影，透明背景，保留体素轮廓与原始色板；不包含 3D 光影、转头或骨骼。
- 全部图形由矢量路径和填色构成，JSON 无图片、字体及外部资源依赖。
- 双击 `preview.html` 可离线预览；播放器已内嵌。棋盘格仅用于显示透明区域。
- `Neutral.svg`、`Half.svg`、`Blink.svg`、`Joy.svg` 为独立表情快照，`states.png` 为检查图。
- `lottie.min.js` 为 lottie-web 5.12.2；许可证见 `LOTTIE-LICENSE.md`。

在模型目录运行 `python scripts/export_lottie.py` 可重新生成动画和预览。
生成器读取现有 VOX、model_info.json、色板和 facial_voxel.py 的表情函数，无需 Blender。

接入时将 JSON 作为播放器的 animationData 或 path，开启 loop 即可。

# v10 制作底模

- `CatGray_Base.blend`：已确认的静态几何、材质、参考图、相机和灯光，供 `manage.py rebuild` 绑定和生成动作。
- `base_info.json`：静态造型参数和尺寸，供生成成品参数及验证使用。

这两个文件是当前 v10 的构建输入，不能替代上一级带动画的 `CatGray_IP.blend`。它们不依赖历史版本目录。

需要从造型源代码重新生成时运行 `python3 manage.py build-base`（入口位于上一级）；仅修改动作时无需重建底模。完整步骤见 [维护手册](../docs/WORKFLOW.md)。

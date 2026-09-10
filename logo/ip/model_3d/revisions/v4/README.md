# CatGray IP 三视图模型 · v4 比例与柔和造型修正版

依据上级目录的 `正视.png`、`侧视.png`、`背视.png` 修改现有模型。原三视图未改动，本次修改前的完整 v3 模型、脚本和预览保存在 `revisions/v3`；更早版本保存在 `revisions/v1` 和 `revisions/v2`。

## 本次修改

当前为 **v4 身体比例、自由手臂与柔和耳朵版**。

- 保留 v3 的头部、眼睛、鼻子和嘴巴的几何形状与彼此位置；整体向上移动 0.21075，为加高的身体让出空间。
- 身体高度比 v3 增加约 15%，躯干宽度增加约 12%、深度增加约 8%，维持圆润短身、短腿的方向。白色腹纹随身体调整为宽 0.88、高 1.06、中心高度 1.05。
- 重建双臂位置与内侧轮廓，让前臂和下段上臂与躯干之间有真实可见间隙，仅在肩部连接。肩部经过局部平滑，保持身体整体为一个封闭曲面。
- 耳朵改为圆钝、加厚的封闭耳壳，取消外沿和粉色区域的黑色描边。粉色内耳与灰色耳缘位于同一连续表面，不再使用单独贴片或轮廓曲线。
- 保留去衣、白色椭圆腹纹、灰色虎斑和卷尾。尾巴随身体适当调整大小与根部位置。

三张参考图都穿着衣服，裸身与腹纹依据本次确认的造型方向。当前身体比例是在 v3 基础上按反馈放大；参考图是风格化手绘稿，三个方向并非严格一致的工程投影。

## 文件

| 文件 | 用途 |
| --- | --- |
| `CatGray_IP.blend` | 可编辑 Blender 工程，含模型、打包贴图、隐藏三视图参考、八台相机与灯光 |
| `CatGray_IP.glb` | 可导入常见 3D 软件的静态角色模型，内嵌两张贴图 |
| `preview_hero.png` | 三分之四角度预览 |
| `preview_comparison.png` | 左 v3、右 v4，在同一正交比例下比较 |
| `preview_front.png` / `preview_side.png` / `preview_back.png` | 正交三视图 |
| `preview_rear_quarter.png` | 后脑与背部斜角预览 |
| `preview_body.png` / `preview_face_side.png` / `preview_ear.png` | 身体、鼻嘴贴合及柔和耳壳近景 |
| `CatGray_Fur_BaseColor.png` | 头部虎斑贴图，2048 × 1536 |
| `CatGray_BareBody_BaseColor.png` | 灰色裸身与白色腹纹贴图，2048 × 2048 |
| `build_cat.py` | 主建模和导出脚本 |
| `bare_body.py` | 身体比例、手臂间隙和白色椭圆腹纹模块，参数位于文件顶部 |
| `soft_ears.py` | 圆润封闭耳壳与一体粉色内耳模块 |
| `model_info.json` | 对象、面数、材质、尺寸及腹纹参数 |
| `qa/unclothed_revision_verification.json` | 几何连接、服装移除、鼻嘴贴合、腹纹及头部修形检查 |
| `qa/v4_revision_verification.json` | 与 v3 比较头脸几何、身体放大、真实手臂间隙和耳壳结构 |
| `qa/export_verification.json` | 实际交付 GLB 的重新导入检查 |

## 编辑与生成

在 Blender 选择 `CATGRAY_IP • Model root` 可整体变换角色。角色位于 `CATGRAY • Character` 集合，场景灯光相机位于 `STUDIO • Cameras and lighting`，三视图参考位于 `REFERENCES • Original three views`，默认隐藏。

使用 Blender 在后台执行 `build_cat.py` 可生成工程、GLB 和八张渲染图。`--quick` 使用 800 像素预览和较低采样；`--build-only` 仅生成模型。主脚本、`bare_body.py` 和 `soft_ears.py` 必须位于同一目录。脚本使用 Blender 自带 Python 和 NumPy。`render_comparison.py` 会读取 v3 备份与当前模型，在同一相机比例下生成比较图。

Blender 为 Z 轴向上、角色正面朝 -Y；GLB 使用 glTF 的 Y 轴向上约定。尺寸采用相对比例，尚未指定厘米尺度。当前交付为静态模型，头部、身体、耳朵和五官仍为可单独编辑的对象，未做骨骼绑定或 3D 打印用全角色一体化。

`body_refinement.py` 与 `qa/verify_body_revision.py` 是 v2 服装版的历史脚本，当前 v4 不再调用。历史 v2 的验证记录请以 `revisions/v2/qa` 为准。

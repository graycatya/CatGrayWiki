# CatGray IP 三视图模型 · v5 参考耳廓与自然手臂版

依据上级目录的 `正视.png`、`侧视.png`、`背视.png` 修改现有模型。原三视图未改动，本次修改前的完整 v4 模型、脚本和预览保存在 `revisions/v4`；更早版本保存在 `revisions/v1`、`revisions/v2` 和 `revisions/v3`。

## 本次修改

当前为 **v5 参考耳廓与自然手臂版**。

- 保持已确认的 v4 头身比例、头脸几何与位置、躯干尺寸、腿脚和白色椭圆腹纹。
- 耳朵改用连贯、凸出的完整耳廓，取消 v4 上下内凹的转折；根部延伸到头部内部，外侧轮廓采用圆润的三角耳形。
- 外耳恢复三视图的深灰色 `#747474`，内耳使用 `#FFA3A3`。降低高光感，保留柔和表面，不恢复黑色描边。
- 缩小粉色内耳，并按相同正交比例测量 v3、v4、新版与正视原图的可见粉色面积。测量结果保存在 `qa/ear_projection_measurements.json`。
- 手臂参考 v3 的较短、圆润手掌与放松姿态：手掌轻微前移和内收，缩短笔直下垂感；同时保持双臂内侧连续可见的间隙。
- 躯干、肩颈、双臂和腿脚仍为一个封闭曲面；灰色虎斑、鼻嘴贴合、卷尾及内嵌腹部贴图均保留。

三张参考图是风格化手绘稿，三个方向并非严格一致的工程投影。模型以正视图确定耳朵大小与粉色比例，并协调侧、背面轮廓。材质基础色取自原图，渲染明暗仍受场景灯光影响。

## 文件

| 文件 | 用途 |
| --- | --- |
| `CatGray_IP.blend` | 可编辑 Blender 工程，含模型、打包贴图、隐藏三视图参考、八台相机与灯光 |
| `CatGray_IP.glb` | 可导入常见 3D 软件的静态角色模型，内嵌两张贴图 |
| `preview_hero.png` | 三分之四角度预览 |
| `preview_comparison.png` | 左 v4、右 v5，在同一正交比例下比较 |
| `preview_front.png` / `preview_side.png` / `preview_back.png` | 正交三视图 |
| `preview_rear_quarter.png` | 后脑与背部斜角预览 |
| `preview_body.png` / `preview_face_side.png` / `preview_ear.png` | 身体、鼻嘴贴合及柔和耳壳近景 |
| `CatGray_Fur_BaseColor.png` | 头部虎斑贴图，2048 × 1536 |
| `CatGray_BareBody_BaseColor.png` | 灰色裸身与白色腹纹贴图，2048 × 2048 |
| `build_cat.py` | 主建模和导出脚本 |
| `bare_body.py` | 身体比例、手臂间隙和白色椭圆腹纹模块，参数位于文件顶部 |
| `soft_ears.py` | 参考耳廓、深灰外耳与较小粉色内耳模块 |
| `model_info.json` | 对象、面数、材质、尺寸及腹纹参数 |
| `qa/unclothed_revision_verification.json` | 几何连接、服装移除、鼻嘴贴合、腹纹及头部修形检查 |
| `qa/v5_revision_verification.json` | v4 比例保持、连续手臂间隙、凸耳廓、参考配色和内耳面积检查 |
| `qa/ear_projection_measurements.json` | v3 / v4 / v5 与原图可见粉色面积比较 |
| `qa/export_verification.json` | 实际交付 GLB 的重新导入检查 |

## 编辑与生成

在 Blender 选择 `CATGRAY_IP • Model root` 可整体变换角色。角色位于 `CATGRAY • Character` 集合，场景灯光相机位于 `STUDIO • Cameras and lighting`，三视图参考位于 `REFERENCES • Original three views`，默认隐藏。

使用 Blender 在后台执行 `build_cat.py` 可生成工程、GLB 和八张渲染图。`--quick` 使用 800 像素预览和较低采样；`--build-only` 仅生成模型。主脚本、`bare_body.py` 和 `soft_ears.py` 必须位于同一目录。脚本使用 Blender 自带 Python 和 NumPy。`render_comparison.py` 会读取 v4 备份与当前模型，在同一相机比例下生成比较图。

Blender 为 Z 轴向上、角色正面朝 -Y；GLB 使用 glTF 的 Y 轴向上约定。尺寸采用相对比例，尚未指定厘米尺度。当前交付为静态模型，头部、身体、耳朵和五官仍为可单独编辑的对象，未做骨骼绑定或 3D 打印用全角色一体化。

`body_refinement.py` 与 `qa/verify_body_revision.py` 是 v2 服装版的历史脚本，当前 v5 不再调用。历史 v2 的验证记录请以 `revisions/v2/qa` 为准。

# CatGray IP 三视图模型 · v3 去衣与造型修正版

依据上级目录的 `正视.png`、`侧视.png`、`背视.png` 修改现有模型。原三视图未改动，修改前的完整 v2 模型、脚本和预览保存在 `revisions/v2`。

## 本次修改

- 移除帽衫、帽领、白色内衬、袖口、抽绳、拉链、口袋和所有服装结构；重新建立灰色胸腹、肩颈和手臂。
- 裸身采用圆润短身、短手短腿，躯干、肩颈、双臂、髋部和腿脚为一个连续封闭曲面。
- 保留正背面的头宽、头高和五官定位，增加后脑上部体积，使后侧轮廓更接近参考图，调整后下部收束。
- 鼻边缘嵌入脸面，保留浅浅鼻头体积；嘴线和舌头轮廓沿头部表面密采样贴合，消除原本悬浮的间隙。
- 重建宽而短的肩颈过渡，颈上端深入头部，维持原有大头短身比例。
- 身体正面为竖向白色椭圆毛色，直接绘入皮肤基础颜色贴图，无额外腹部壳片。腹纹宽 0.78、高 0.92，中心高度 0.91，白色为 `#F4F3F0`，灰色为 `#979797`。

三张参考图都穿着衣服，裸身与白色腹纹采用本次确认的造型方向。三视图是风格化手绘稿，侧面头顶和耳朵高度与正背面并非严格一致，因此以正背面宽高比例为基准协调侧面轮廓。

## 文件

| 文件 | 用途 |
| --- | --- |
| `CatGray_IP.blend` | 可编辑 Blender 工程，含模型、打包贴图、隐藏三视图参考、七台相机与灯光 |
| `CatGray_IP.glb` | 可导入常见 3D 软件的静态角色模型，内嵌两张贴图 |
| `preview_hero.png` | 三分之四角度预览 |
| `preview_front.png` / `preview_side.png` / `preview_back.png` | 正交三视图 |
| `preview_rear_quarter.png` | 后脑与背部斜角预览 |
| `preview_body.png` / `preview_face_side.png` | 身体及鼻嘴贴合近景 |
| `CatGray_Fur_BaseColor.png` | 头部虎斑贴图，2048 × 1536 |
| `CatGray_BareBody_BaseColor.png` | 灰色裸身与白色腹纹贴图，2048 × 2048 |
| `build_cat.py` | 主建模和导出脚本 |
| `bare_body.py` | 连续裸身及白色椭圆腹纹模块，参数位于文件顶部 |
| `model_info.json` | 对象、面数、材质、尺寸及腹纹参数 |
| `qa/unclothed_revision_verification.json` | 几何连接、服装移除、鼻嘴贴合、腹纹及头部修形检查 |
| `qa/export_verification.json` | 实际交付 GLB 的重新导入检查 |

## 编辑与生成

在 Blender 选择 `CATGRAY_IP • Model root` 可整体变换角色。角色位于 `CATGRAY • Character` 集合，场景灯光相机位于 `STUDIO • Cameras and lighting`，三视图参考位于 `REFERENCES • Original three views`，默认隐藏。

使用 Blender 在后台执行 `build_cat.py` 可生成工程、GLB 和七张渲染图。`--quick` 使用 800 像素预览和较低采样；`--build-only` 仅生成模型。主脚本和 `bare_body.py` 必须位于同一目录。脚本使用 Blender 自带 Python 和 NumPy。

Blender 为 Z 轴向上、角色正面朝 -Y；GLB 使用 glTF 的 Y 轴向上约定。尺寸采用相对比例，尚未指定厘米尺度。当前交付为静态模型，头部、身体、耳朵和五官仍为可单独编辑的对象，未做骨骼绑定或 3D 打印用全角色一体化。

`body_refinement.py` 与 `qa/verify_body_revision.py` 是 v2 服装版的历史脚本，当前 v3 不再调用。历史 v2 的验证记录请以 `revisions/v2/qa` 为准。

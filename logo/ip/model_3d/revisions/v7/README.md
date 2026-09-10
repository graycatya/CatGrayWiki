# CatGray IP 三视图模型 · v7 饱满耳壳版

依据上级目录的 `正视.png`、`侧视.png`、`背视.png` 修改现有模型。修改前的完整 v6 工程、导出文件、脚本和预览保存在 `revisions/v6`；更早版本保存在对应的 `revisions/v1` 至 `revisions/v5`。

## 本次修改

- 耳壳前后深度从 0.17 增至 0.36，主要向耳背增加体积，使侧面更饱满。
- 前后表面使用连续的圆弧衔接，外缘平滑，不增加单独的描边或叠层。
- 保留正面耳廓的 X/Z 轮廓、粉色内耳的区域分配以及参考灰色、粉色。前表面中心位置保持，外缘随加厚自然后移。
- 头部、五官、身体、独立双臂、圆润腿根和尾巴沿用 v6。
- 新增 `preview_ear_edge.png`，从侧后方近距离查看耳朵厚度。

三张参考图是风格化手绘稿，三个方向并非严格一致的工程投影。模型保留此前确认的形体和参考配色，渲染明暗仍受场景灯光影响。

## 文件

| 文件 | 用途 |
| --- | --- |
| `CatGray_IP.blend` | 可编辑 Blender 工程，含独立手臂、打包贴图、隐藏三视图参考、九台相机与灯光 |
| `CatGray_IP.glb` | 静态角色模型，保留独立手臂，内嵌两张贴图 |
| `preview_comparison.png` | 左 v6、右 v7，完整角色等比例比较 |
| `preview_body_comparison.png` | 历史 v6 修改对比：左 v5、右 v6，手臂和腿根近景 |
| `preview_ear_edge.png` | 新增耳壳厚度近景 |
| `preview_hero.png` | 三分之四角度预览 |
| `preview_front.png` / `preview_side.png` / `preview_back.png` | 正交三视图 |
| `preview_rear_quarter.png` | 后脑与背部斜角预览 |
| `preview_body.png` / `preview_face_side.png` / `preview_ear.png` | 身体、鼻嘴及耳朵近景 |
| `CatGray_Fur_BaseColor.png` | 头部虎斑贴图，2048 × 1536 |
| `CatGray_BareBody_BaseColor.png` | 灰色身体与白色腹纹贴图，2048 × 2048 |
| `model_info.json` | 对象、面数、材质、尺寸与各部位修订信息 |
| `qa/v7_revision_verification.json` | 耳朵厚度与体积、封闭曲面、正面耳廓、粉色可见面积及其余角色几何保持检查 |
| `qa/unclothed_revision_verification.json` | 服装移除、鼻嘴贴合、白色腹纹和头部修形检查 |
| `qa/export_verification.json` | 实际交付 GLB 的重新导入检查 |

## 后续骨骼动画

当前为静态模型，尚未创建骨骼和权重。左右手臂对象分别为 `Arm L • independent rounded limb`、`Arm R • independent rounded limb`，每条手臂有 1,312 个基础顶点，保留未应用的细分修改器。对象原点位于肩部；关节参考位置存放在对象自定义属性中。

躯干、髋部和双腿仍为一个封闭网格；手臂与躯干保持独立。肩根有隐藏的体积交叠，后续绑定时需要协调肩部权重，检查抬臂和前后摆动时的衔接。躯干目前是较密的造型网格；正式动画制作时宜结合动作要求整理关节拓扑，再进行权重和极限姿势测试。GLB 导出的是细分后的静态表面，进一步绑定优先使用 Blender 工程。

## 编辑与生成

选择 `CATGRAY_IP • Model root` 可整体变换角色。角色位于 `CATGRAY • Character` 集合，灯光相机位于 `STUDIO • Cameras and lighting`，隐藏参考位于 `REFERENCES • Original three views`。

使用 Blender 在后台执行 `build_cat.py` 可生成工程、GLB 和九张渲染图。`--quick` 使用 800 像素预览和较低采样；`--build-only` 仅生成模型。主脚本、`bare_body.py` 和 `soft_ears.py` 必须位于同一目录。脚本使用 Blender 自带 Python 和 NumPy。`render_comparison.py` 读取 v6 备份与当前模型，生成完整角色比较图。

Blender 为 Z 轴向上、角色正面朝 -Y；GLB 使用 glTF 的 Y 轴向上约定。尺寸采用相对比例，尚未指定厘米尺度。

历史版本检查脚本和报告保留在 `qa`，对应版本的完整归档在 `revisions`。当前修订验证以 v7 和 GLB 重新导入报告为准；v6 的身体与裸身基础检查也保留供参考；`body_refinement.py` 是 v2 服装版历史脚本，当前不调用。

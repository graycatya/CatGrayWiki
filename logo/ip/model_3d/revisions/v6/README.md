# CatGray IP 三视图模型 · v6 贴身圆润手臂与腿根优化

依据上级目录的 `正视.png`、`侧视.png`、`背视.png` 修改现有模型。修改前的完整 v5 工程、导出文件、脚本和预览保存在 `revisions/v5`；更早版本保存在对应的 `revisions/v1` 至 `revisions/v4`。

## 本次修改

- 双臂顺着圆润腹部的外轮廓下垂、向内收，手掌末端修圆，缩小之前过大的离身空隙。
- 左右手臂各自为独立、封闭的网格，与躯干没有焊接。露出的手臂内侧与身体保持细小间隙，肩根藏入肩部，让静态外观自然衔接。
- 手臂使用可编辑的四边面环线，原点设在肩部，记录肩、肘、腕参考位置，供后续骨骼绑定使用。
- 重新调整下腹、髋部与大腿上部的形状，并局部平滑，消除原先腿根的台阶和硬折痕。
- 保留已确认的头身比例、头部、耳朵、五官、尾巴、灰色虎斑和白色椭圆腹纹。

三张参考图是风格化手绘稿，三个方向并非严格一致的工程投影。模型保留此前确认的形体和参考配色，渲染明暗仍受场景灯光影响。

## 文件

| 文件 | 用途 |
| --- | --- |
| `CatGray_IP.blend` | 可编辑 Blender 工程，含独立手臂、打包贴图、隐藏三视图参考、八台相机与灯光 |
| `CatGray_IP.glb` | 静态角色模型，保留独立手臂，内嵌两张贴图 |
| `preview_comparison.png` | 左 v5、右 v6，完整角色等比例比较 |
| `preview_body_comparison.png` | 左 v5、右 v6，手臂和腿根近景比较 |
| `preview_hero.png` | 三分之四角度预览 |
| `preview_front.png` / `preview_side.png` / `preview_back.png` | 正交三视图 |
| `preview_rear_quarter.png` | 后脑与背部斜角预览 |
| `preview_body.png` / `preview_face_side.png` / `preview_ear.png` | 身体、鼻嘴及耳朵近景 |
| `CatGray_Fur_BaseColor.png` | 头部虎斑贴图，2048 × 1536 |
| `CatGray_BareBody_BaseColor.png` | 灰色身体与白色腹纹贴图，2048 × 2048 |
| `model_info.json` | 对象、面数、材质、尺寸与各部位修订信息 |
| `qa/v6_revision_verification.json` | 保留几何、身体比例、独立封闭手臂、间隙、肩部原点及腿根过渡检查 |
| `qa/unclothed_revision_verification.json` | 服装移除、鼻嘴贴合、白色腹纹和头部修形检查 |
| `qa/export_verification.json` | 实际交付 GLB 的重新导入检查 |

## 后续骨骼动画

当前为静态模型，尚未创建骨骼和权重。左右手臂对象分别为 `Arm L • independent rounded limb`、`Arm R • independent rounded limb`，每条手臂有 1,312 个基础顶点，保留未应用的细分修改器。对象原点位于肩部；关节参考位置存放在对象自定义属性中。

躯干、髋部和双腿仍为一个封闭网格；手臂与躯干保持独立。肩根有隐藏的体积交叠，后续绑定时需要协调肩部权重，检查抬臂和前后摆动时的衔接。躯干目前是较密的造型网格；正式动画制作时宜结合动作要求整理关节拓扑，再进行权重和极限姿势测试。GLB 导出的是细分后的静态表面，进一步绑定优先使用 Blender 工程。

## 编辑与生成

选择 `CATGRAY_IP • Model root` 可整体变换角色。角色位于 `CATGRAY • Character` 集合，灯光相机位于 `STUDIO • Cameras and lighting`，隐藏参考位于 `REFERENCES • Original three views`。

使用 Blender 在后台执行 `build_cat.py` 可生成工程、GLB 和八张渲染图。`--quick` 使用 800 像素预览和较低采样；`--build-only` 仅生成模型。主脚本、`bare_body.py` 和 `soft_ears.py` 必须位于同一目录。脚本使用 Blender 自带 Python 和 NumPy。`render_comparison.py` 读取 v5 备份与当前模型，生成完整角色与身体近景比较图。

Blender 为 Z 轴向上、角色正面朝 -Y；GLB 使用 glTF 的 Y 轴向上约定。尺寸采用相对比例，尚未指定厘米尺度。

历史版本检查脚本和报告保留在 `qa`，对应版本的完整归档在 `revisions`。当前验证以 v6、裸身基础检查及 GLB 重新导入报告为准；`body_refinement.py` 是 v2 服装版历史脚本，当前不调用。

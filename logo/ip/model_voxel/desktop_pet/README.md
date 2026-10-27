# CatGray Voxel 桌宠角色包 v1

对应桌宠 UI 组件库 PRD 0.2 的 Sprite schemaVersion 1。打开 `preview.html` 离线检查；运行时只需要 `manifest.json`、`spritesheet.png`、`LICENSE.txt`，预览图可选。

- 单元：192×208 RGBA，8 FPS；统一正交全身镜头、固定灯光，无背景与地板。
- 锚点：`[0.5, 0.92]`，作为固定地面参考点，不逐帧追踪脚底。动作自身的跳跃和姿态位移保留。
- 七个标准状态全部映射，无缺失状态回退。Idle、Success、Error 是桌宠专用程序化姿态循环。Thinking、Working、Waiting、Speaking 使用桌宠 Blender 工程中的独立烘焙 Action。
- Success：微笑、抬爪；Error：低头、轻微摇头。两者持续循环，直到宿主切换状态。庆祝跳跃通过 `jump` 临时动作单独触发。
- Working：双爪在体素键盘上交替敲击，头部向下专注，键盘带支架。Thinking：歪头、抬爪悬停在下巴下方，另一爪收在身体前侧。Waiting：放松双臂、缓慢左右张望、轻微重心移动。Speaking：交替爪子手势、点头、身体起伏及专用说话嘴型；不提供音素同步。
- walk/run 是原地循环，窗口位置由宿主控制；jump 是一次性动作，已含动画竖直位移，宿主不要再次叠加跳跃高度。
- 帧按从左到右、从上到下排列。源动作的重复闭合末帧不导出。
- `contact_sheet.png` 按 manifest 动作顺序展示各动作中间帧；`verification.json` 记录逐帧透明边界与资源预算检查。
- 素材允许随桌宠应用分发，禁止单独售卖素材；详见 LICENSE.txt。

## 重建

在 `model_voxel` 目录执行（Blender 5.2、CPU Cycles）：

```sh
blender --factory-startup -b -t 6 --python-exit-code 1 --python scripts/export_desktop_pet.py
```

只读取现有 `.blend`，另存 `CatGray_DesktopPet.blend`，不覆盖原模型、GLB、Lottie 或源动作。覆盖本角色包的图集、manifest、预览与验证报告。中间 PNG 保留在已忽略的 `frames/` 中供检查。

```sh
blender --factory-startup -b -t 4 --python-exit-code 1 --python scripts/export_desktop_pet.py -- --smoke
```

`--smoke` 只渲染第一帧到 `frames/idle_000.png`，不更新完整角色包。

## 验证范围

生成器检查每帧非空、轮廓不触碰画布边缘，输出图集不超过 4096×4096、RGBA 解码预算不超过 128 MiB。已有模型验证报告可作为源资产检查依据，不代表本包已通过目标 Qt 播放器验证。仍需在实际组件中验证动作调度、高 DPI、透明合成、窗口交互和运行时性能。

独立校验交付图集（逐格与中间 PNG 对照，检查帧序、引用、透明边界及预算）：

```sh
blender --factory-startup -b --python-exit-code 1 --python scripts/verify_desktop_pet.py
```

`browser_verification.json` 是 Chromium 离线预览交互检查记录，`browser_preview.png` 为浏览器截图。`--pack-only` 可仅重新打包已完整渲染的中间帧；仅限帧未过期且制作参数未改变时使用。

## 可编辑桌宠动作工程

`CatGray_DesktopPet.blend` 包含原有 12 个动作和新增的 `Pet_Thinking`、`Pet_Working`、`Pet_Waiting`、`Pet_Speaking` 四个独立 Action。24 FPS，骨骼变换为普通 FK 关键帧，五官为 STEP 形态键，无运行时 IK 依赖。

打开工程按空格可播放四段 NLA 预览：思考 1–72，工作 73–120，等待 121–216，说话 217–288。键盘仅在工作段显示。选择单个 Action 编辑时需同时选择骨架的 OBJECT 插槽和五官的 KEY 插槽，并停用预览 NLA；键盘位于 `DesktopPet • Keyboard` 集合。

动作制作代码：`scripts/desktop_pet_actions.py`。制作源改动应优先修改该文件；导出会重新生成桌宠专用工程，覆盖其中手工修改。

校验交付 Blender 工程：

```sh
blender --factory-startup -b --python-exit-code 1 --python scripts/verify_desktop_pet_actions.py
```

[四动作对比预览](review.html) 可同时观看四个状态；`review/` 中的 MP4 仅用于检查，浅色背景不是角色素材背景。结构校验通过不代表动作语义已获确认，最终表现仍需人工审阅。

对比视频可由完整帧序列重建：

```sh
python3 scripts/render_desktop_pet_review.py
```

需要 FFmpeg。视频以 Sprite 的 8 FPS 播放，放大到 384×416 便于检查；Blender Action 本身为 24 FPS。

## 专用说话嘴型

`Pet_Speaking` 使用新增的 `Mouth_TalkRest`、`Mouth_TalkSmall`、`Mouth_TalkMedium`、`Mouth_TalkOpen`：固定嘴角与上唇，从闭口到小开、中开、大开，配合不等长的开合和停顿。不会轮播原先的 A／E／O 或情绪嘴型；每帧仅激活一个说话嘴型，权重为 1，其他嘴型为 0，保持体素轮廓和 STEP 切换。

新嘴型仅添加到桌宠工程，不改动原始模型。制作代码位于 `scripts/desktop_pet_speech.py`。

## 手部穿模回归检查

思考与工作已按爪子、前臂的实际体积调整：肩部留出头部间隙，收手避开躯干，键盘前移，敲击轨迹为实体按键留出空间。说话与等待也复查了手臂和头部的间隙。

```sh
blender --factory-startup -b --python-exit-code 1 --python scripts/verify_desktop_pet_clearance.py
blender --factory-startup -b -t 4 --python-exit-code 1 --python scripts/preview_desktop_pet_clearance.py
```

`clearance_verification.json` 检查实际求值后的网格：上臂／头部、前臂／头部、前臂／躯干、工作状态手臂／键盘；以 24 FPS 的半帧间隔采样，容差 0.01 Blender 单位（体素边长的十分之一）。相连肩部与躯干的关节接合不作为穿模，此检查不覆盖所有身体部件组合。

`review/clearance_views.png` 上排为思考、下排为工作；每排按正面、左侧、右侧排列，便于人工检查可见轮廓和接触。

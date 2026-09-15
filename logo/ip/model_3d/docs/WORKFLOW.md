# v10 制作与维护手册

## 1. 环境配置

本次定版实际验证环境：

| 项目 | 版本 / 说明 |
| --- | --- |
| Blender | **5.2.1 LTS** |
| 操作系统 | macOS 26.6.2，Apple Silicon / arm64 |
| Blender 自带 Python | 3.13.13 |
| Blender 自带 NumPy | 2.3.4 |
| 统一入口 | 系统 Python 3.9 或以上；本次入口使用 3.9.6，仅依赖标准库 |
| 渲染 | 动画为 Eevee；静态造型脚本支持 Cycles |
| 视频 | Blender 自带 FFmpeg，输出 H.264 / MP4 |

优先使用同一 Blender 版本复现定版。Windows / Linux 的命令示例也列在下面，但未在这两种系统上做本次完整验证。其他 Blender 版本应先运行 `doctor` 和 `verify`；低于 5.2 的版本会被环境检查拒绝。

从 [Blender 官方下载页](https://www.blender.org/download/) 安装 Blender；需要同版时可查 [官方历史版本目录](https://download.blender.org/release/)。不需要安装插件，不需要另装 FFmpeg，也不需要为模型脚本执行 `pip install bpy` 或安装系统 NumPy。`bpy`、`bmesh`、`mathutils` 和 NumPy 都由 Blender 自带 Python 提供。

### macOS

Blender 安装在 `/Applications/Blender.app` 时，入口会自动识别。终端执行：

```sh
cd /Volumes/CatDisk/codes/catgray/CatGrayWiki/logo/ip/model_3d
python3 manage.py doctor
```

如果安装在其他位置，当前终端可设置：

```sh
export BLENDER_BIN="/Applications/Blender.app/Contents/MacOS/Blender"
python3 manage.py doctor
```

### Windows PowerShell

先安装 Python 3，并把路径替换为实际安装位置：

```powershell
Set-Location "D:\CatGrayWiki\logo\ip\model_3d"
$env:BLENDER_BIN = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
py -3 manage.py doctor
```

### Linux

```sh
cd /path/to/CatGrayWiki/logo/ip/model_3d
export BLENDER_BIN="/opt/blender/blender"
python3 manage.py doctor
```

也可以让 `blender` 位于 `PATH` 中。Eevee 仍需要可用的图形驱动；`--background` 表示不打开交互窗口，不代表无需图形环境。无显示服务器的 Linux 机器需要自行配置可用的离屏图形环境，本次未验证这一部署方式。

### 临时指定 Blender 与线程数

```sh
python3 manage.py --blender "/Applications/Blender.app/Contents/MacOS/Blender" --threads 6 doctor
```

可选参数放在命令名前。路径含空格时使用引号。默认使用 4 个 CPU 线程；线程数并不等于 GPU 的并行度。

`doctor` 检查实际 Blender 版本、Action slot API、GLB 导入导出、NumPy 和必要源文件，并写出 `qa/environment_verification.json`。它不会测试所有渲染功能；完整渲染与视频验证见下面步骤。

## 2. 根据工作内容选择操作

### 只查看定版

直接打开 `CatGray_IP.blend`，空格播放。无需安装系统 Python，也无需运行任何脚本。用于引擎或网页播放时，导入 `CatGray_IP.glb`，按动作名称选片段。

### 已在 Blender 中手工修改姿态、关键帧或材质

先保存 `.blend`，然后：

```sh
python3 manage.py export
python3 manage.py preview
python3 manage.py render
python3 manage.py verify
```

`export` 读取当前工程，在内存中采样约束并导出 GLB，不保存对原生控制器的改动。**不要用 `rebuild` 导出手工编辑的工程**：它会重新读取静态底模、创建骨骼和动作，替换手工改动。

导出和检查脚本按三个约定动作、84 根骨骼及现有网格组织编写。若主动修改骨骼数量、命名、动作长度或角色网格结构，需同步修改生成脚本、`model_info.json`、视频分段和验证规则，不能只改工程里的名字。

### 修改招手轨迹或绑定规则

编辑 `scripts/wave_arc.py` 或 `scripts/rig_cat.py` 后：

```sh
python3 manage.py doctor
python3 manage.py rebuild
python3 manage.py preview
python3 manage.py render
python3 manage.py verify
```

`rebuild` 从 `source/CatGray_Base.blend` 构建完整绑定，并自动导出 GLB。先用 `preview` 的几张关键姿势检查，再渲染完整视频。

### 从造型代码完整重建

这一流程会覆盖静态底模和贴图，属于造型维护，日常导出不需要运行：

```sh
python3 manage.py doctor
python3 manage.py build-base
python3 manage.py rebuild
python3 manage.py preview
python3 manage.py render
python3 manage.py verify
```

`build-base` 读取 `../references` 中的原始三视图，运行造型源代码，生成 `source/CatGray_Base.blend`、`source/base_info.json` 和两张贴图。它不会把无动画模型写到成品 `.blend`，也不会生成另一份静态 GLB。

修改造型源代码后重新生成的模型属于对定版的修改；建议在复制出的 `ip` 目录工作，确认效果后再替换成品。统一入口无需当前工作目录恰好是模型目录，使用绝对路径调用 `manage.py` 也可运行。

## 3. 命令和覆盖范围

| 命令 | 输入 | 主要输出 / 覆盖 |
| --- | --- | --- |
| `doctor` | 本机 Blender、必要资源 | 环境报告 |
| `build-base` | `scripts/geometry`、原始三视图 | 静态底模、底模参数、两张贴图 |
| `rig` | 静态底模、绑定和动作代码 | `.blend`、`model_info.json`、绑定报告；不导出 GLB |
| `rebuild` | 同上 | `.blend`、`.glb`、参数与绑定/烘焙报告 |
| `export` | 当前 `.blend`、动作参数 | `.glb`、烘焙报告 |
| `preview` | 当前 `.blend` | `qa/wave_arc_*.png` 六张关键姿势 |
| `render` | 当前 `.blend` | 五个 MP4、动画封面、视频报告 |
| `render-main` | 当前 `.blend` | 完整预览及待机/招手/走路 MP4、动画封面 |
| `render-side` | 当前 `.blend` | 侧面招手 MP4、侧面源帧和验证图 |
| `encode-main` | 已存在的 240 张主预览帧 | 主预览的四个 MP4、封面、验证图 |
| `verify` | 当前成品、底模、参数、视频及封面 | 四类校验报告与导入/解码检查图 |

所有命令会把完整输出记录到 `qa/logs/<脚本名>.log`，同名日志下次运行时覆盖。任何一步失败都会停止当前命令并返回非零退出码；入口为 Blender 设置 `--python-exit-code 1`，避免 Python 出错却被当作执行成功。

主渲染先生成 `qa/animation_frames/frame_0001.png` 至 `frame_0240.png`。编码与解码对比通过后自动删除临时序列。若渲染已完成、编码失败，可修复原因后用 `encode-main` 重试；缺帧时应重新运行 `render-main`。侧面渲染使用 `qa/wave_side_frames`，失败时重新运行 `render-side`。

本机 720 × 720 的完整预览通常需要数分钟，另加侧面视频；硬件、驱动、线程设置和后台负载会影响耗时。日志仍持续产生帧记录时，渲染正在正常工作。

## 4. 脚本职责和调整位置

| 脚本 | 职责 |
| --- | --- |
| `scripts/geometry/build_base.py` | 场景、头部五官、贴图、相机和灯光，调用身体与耳朵模块 |
| `scripts/geometry/bare_body.py` | 连续身体、独立圆润手臂、腿部、腹纹贴图 |
| `scripts/geometry/soft_ears.py` | 耳朵外壳、内耳和厚度 |
| `scripts/rig_cat.py` | 骨骼、权重、IK、三个动作、NLA 时间轴、原生工程与参数 |
| `scripts/wave_arc.py` | 右臂的截面绑定、抬手弧线、摆动和形状过渡 |
| `scripts/export_rig.py` | 约束采样、普通骨骼关键帧烘焙、GLB 导出 |
| `scripts/render_animations.py` | 主视角逐帧渲染、四段视频编码与源帧对比 |
| `scripts/render_wave_side.py` | 侧面招手渲染、编码与源帧对比 |
| `scripts/qa/preview_wave_arc.py` | 正面、侧面、斜侧面及抬手阶段截图 |
| `scripts/qa/verify_rig.py` | 静态外形、权重、闭合姿势、接地和抽样穿插 |
| `scripts/qa/verify_wave_revision.py` | 招手全部 97 帧的自相交、截面面积与相邻截面转角 |
| `scripts/qa/verify_animated_export.py` | GLB 内容、贴图、动作时长、重新导入后姿势比较 |
| `scripts/qa/verify_videos.py` | 五个视频的帧数、代表帧解码及封面对比 |
| `scripts/check_environment.py` | 运行环境与源资源检查 |
| `scripts/package_assets.py` | 目录整理后的贴图相对路径修正、打包检查与定版标记；日常操作无需调用 |

### 招手路径

在 `wave_arc.py` 的 `WaveArc.target()` 中调整 `p1 / p2 / p3`：它们控制弯肘位置、前臂走向和手掌终点，`p0` 为肩根。坐标是 **X 左右、Y 前后、Z 高度，负 Y 为角色前方**。

- 调整终点的 Y：改变手掌向前伸出的距离。
- 调整终点的 Z：改变抬手高度，同时检查大头前缘间距。
- `wiggle` 的 X 系数：改变摆手幅度；中段与终点应协调调整，避免局部反折。
- `rig_cat.py` 中 `wave_pose()` 的 `envelope`：控制抬起和放下节奏。
- `wave_time` 与正弦项：控制摆动次数及开始、结束时的幅度收拢。

截面方向使用旋转插值，避免上下姿势直接线性混合而缩短手臂；截面权重采用重叠过渡。修改后要同时看正面、侧面和抬手途中。自动检查能够发现部分塌陷、穿插和急弯，不能代替对动作自然程度的视觉判断。

### 分辨率、帧率、时长

动画分辨率和 Eevee 采样数在两个 `render_*.py` 中；修改分辨率还要同步编码、解码和 `verify_videos.py` 的设置。帧率与动作时长需要同步 `rig_cat.py`、主时间轴、视频分段、侧面片段和导出检查。仅改一个数字会造成动作时长或源帧对比失败。

## 5. 直接使用 Blender 命令

排查入口问题时可以直接调用，顺序见 [Blender 命令行参数文档](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)：

```sh
"/Applications/Blender.app/Contents/MacOS/Blender" \
  --background --factory-startup --threads 4 --python-exit-code 1 \
  --python scripts/rig_cat.py -- --no-export
```

`--` 后面是脚本自己的参数。`scripts/geometry/build_base.py` 支持 `--build-only`（不渲染静态视图）和 `--quick`（较低采样的静态预览）；直接运行不带 `--build-only` 时会更新 `previews` 中的静态图。

不要用 `python3 scripts/rig_cat.py` 运行 Blender 脚本，否则会出现 `No module named bpy`。普通 Python 只用来启动 `manage.py`。

## 6. 常见问题

| 现象 | 处理 |
| --- | --- |
| 找不到 Blender | 检查 `BLENDER_BIN` 是否指向可执行文件；macOS 不是 `.app` 目录本身 |
| Action slots、视频属性或 glTF API 报错 | 先核对 `doctor` 输出，优先用经过验证的 Blender 5.2.1 |
| `No module named bpy` | 通过 `manage.py` 或 Blender `--python` 启动 |
| 刚修改工程，视频仍是旧动作 | 先保存工程，再 `export`、`render`、`verify`；旧窗口需重新打开更新文件 |
| 手工修改在重建后消失 | `rebuild` 会从制作源重新生成；手工编辑后应使用 `export` |
| 骨骼挡住表面 | 关闭骨架 In Front；隐藏“辅助”骨骼集合；切回物体模式 |
| 右手 Forearm / Hand 不起作用 | v10 右臂使用 `ArmArc.R.*`，用 `UpperArm.R` 整体调整或修改弧线代码 |
| 多个动作叠加、姿势不对 | 编辑独立 Action 前禁用播放预览 NLA 轨道；存档轨道保持静音 |
| 粉色材质、找不到参考图 | 打开内嵌资源的成品工程；完整目录应保留 `textures` 和 `../references` |
| 渲染退出、没有视频 | 查看 `qa/logs` 末尾错误；修复图形驱动、权限或资源问题后重跑对应渲染命令 |
| 脚本提示验证失败 | 不忽略异常；看报告和日志，先修复导致失败的动作/导出变化，再生成成品 |

## 7. 定版维护边界

`source`、`scripts` 和原始三视图属于当前版本必要的制作输入；删除这些文件会失去从头复现能力。`qa/logs`、Python 缓存、失败渲染的临时帧可以清理。定版成品与元数据保留在模型目录顶层，避免同时维护多个同内容的视频别名。

发布前建议完成：环境检查 → 必要的重建或导出 → 关键姿势目视检查 → 视频渲染 → `verify`。本次目录迁移的实际验证记录见 `../qa/release_verification.json`。

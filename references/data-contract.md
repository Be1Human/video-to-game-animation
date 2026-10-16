# 工具、数据与运行契约

以下命令在技能目录执行，输入/输出路径自行指定。Python 3.11+；数学工具依赖 NumPy 2.x。Blender 导出器使用 Blender 内置 Python，已在 4.5.3 LTS 实测；其他版本需要小样检查。视频工具依赖可选的 MediaPipe/OpenCV，模型不随包发布。

## 数学工具快速验证

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s scripts -p 'test_*.py' -v
python scripts/make_demo.py --output-dir demo-output
python scripts/analyze_motion.py demo-output/smooth-sliding.json --output demo-output/report.json
```

演示是合成反例：脚底匀速滑动而 jerk 接近零，不是人类动作测试。`motion_math.py` 是可导入库，不单独生成动作。

## 姿态捕捉

```sh
python -m pip install -r requirements-capture.txt
python scripts/extract_video_pose.py --video input.mp4 --start 10 --duration 3 --fps 30 --model pose_landmarker.task --output capture
```

需显式提供兼容的本地模型，可用 `--model-source URL` 记录出处。输出目录必须空；没有下载/上传行为。JSON 保存源时戳、33 点图像/估计世界坐标、visibility/presence、缺失、哈希与版本。多人或无人物留空；无自动身份追踪、镜头拆分或人体重定向。`--visibility` 仅影响覆盖统计，不是验收门槛，退出码 0 只说明读到了帧。叠加视频是恒定帧率检查预览，VFR/漏帧分析使用 JSON 原时戳，不能用预览重建精确节奏。

## Blender 求值导出

配置示例（骨名、时长、米制比例必须与真实输入一致）：

```json
{
  "rig":"Armature", "mode":"action", "action":"Walk",
  "bones":["pelvis","hand.L","hand.R","foot.L","foot.R"],
  "meters_per_unit":1.0, "axes":"Z-up, -Y-forward", "up_axis":"Z",
  "frame_start":1, "frame_end":61, "frame_step":0.5,
  "scale_m":1.7, "root_motion":"in_place",
  "markers":{"sole.L":"SoleMarker.L"}, "contacts":[]
}
```

```sh
blender --background character.blend --disable-autoexec --python-exit-code 1 --python scripts/export_blender_motion.py -- --config export.json --output motion.json
python scripts/analyze_motion.py motion.json --output report.json
```

导出器不保存源 Blend。action 模式选一个动作，并在选中 rig 上关闭 NLA、设 REPLACE/影响 1；多槽动作须给 `action_slot` 标识。scene 模式不切动作/NLA，分析当前实际场景组合。其他对象动画保留，约束依赖需检查。禁用自动执行可能影响需要自定义 Python 的驱动，无法求值时应说明依赖，不绕过环境限制。Blender API 的 [evaluated depsgraph](https://docs.blender.org/api/current/bpy.types.Depsgraph.html) 与原 keyframe 数值并不相同。

位置是骨头 head/配置标记物的世界位置，旋转是世界 wxyz；脚骨 head 不代表鞋底。要评价接触，准备真实鞋底标记物及可靠标签。反射/剪切拒绝，变换政策需单独处理。配置轴声明仅作记录，不旋转数据。采样范围必须整除 frame_step，不悄悄拼接不等间隔终点。

## 分析 JSON

完整分析至少 9 个有限、严格递增、等间隔样本，单位必须 `m`；未标定像素/视频估计不可伪装成精确米。输入字段：

- `name, time_s, units, axes, up_axis`（X/Y/Z，缺省 Z）；`scale_m` 可选，≤0 则不算尺度归一指标。
- `positions`: 名称 → `[N,3]` 世界或声明分析空间中的轨迹；`world_quaternions`: 名称 → `[N,4]` 世界主动 wxyz。
- `loop` 可选：`duplicate_endpoint:true, period_s:T`；需重复端点且 T 等于输入时长。位移/转弯周期先消除预期周期根变换，再做接缝分析；导出器不会代做此步骤。
- `contacts`: `point, start_s, end_s, evidence, surface_stationary:true, ground_height`。时间相对本片段，点在静止地面空间；动平台应先转换。循环规范空间的点不能直接复用作脚滑。无标签返回未评估。
- `provenance`：来源类别、求值模式、过滤、重采样、root/相位处理和限制。

分析使用递归中心差分，jerk 统计去掉首尾各 3 样本；输出摘要与 `.curves.json`。接缝速度为采样差分估计，不是解析证明。没有滤波、接触分类或自动通过阈值。

## 网格诊断 NPZ

```sh
python scripts/mesh_diagnostics.py mesh_samples.npz --min-edge-m 0.001 --output mesh-report.json
```

数组：`rest[V,3]`、`posed[T,V,3]`（米，同空间/同顶点序）、`edges[E,2]` 整数、预先定义的 `region[K]` 顶点整数 ID；可选 `disabled[T,V,3]` 为同帧禁用指定链后的实际求值网格。需要自行保存采样时间、区域理由、禁用链和求值设置；该工具只算度量，不抓取 Blender 网格。没有可用区域边返回 null，不叫通过。1 mm 是可覆盖的示例过滤量，不是所有角色通用尺度。

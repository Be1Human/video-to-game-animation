# v0.1.0 发布验证

验证日期：2026-10-16（北京时间）。这是技能与工具的发布检查，不是输入角色的最终自然度验收。

| 范围 | 实际结果 |
| --- | --- |
| 技能结构 | skill-creator quick_validate 通过；入口和引用分层可达 |
| 数学与诊断 | 19 项 unittest 通过：时间/空间缩放、q/−q、小角旋转、恒角速度、Log/Exp、周期拟合、切空间切口拒绝、五次端点、平滑滑步反例、Y-up 接触、网格刚性不变性和对应错误拒绝等 |
| 可运行演示 | 合成匀速脚底轨迹：jerk 接近零，同时接触段滑移 1 m；无误报接触通过 |
| Blender 4.5.3 LTS | 本地实际 Run_Stop 工程导出 193 时刻、7 位置和 7 旋转轨迹，分析成功；源文件哈希不变 |
| 视频入口 | 本地单人片段真实执行 MediaPipe，10 个采样帧均输出唯一人物；仅证明接口/推理/文件链路，不证明 3D 真值精度 |
| 网格 CLI | 合成网格输入与反事实样本成功分析；刚性变换/缩放的不变量由测试覆盖 |
| 公开包 | 仅代码、说明、配置、许可和合成测试；不包含角色、原片、模型或本机绝对路径 |

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s scripts -p 'test_*.py' -v
python scripts/make_demo.py --output-dir demo-output
python scripts/analyze_motion.py demo-output/smooth-sliding.json --output demo-output/report.json
```

本地实测输入不随仓库分发；此处是发布记录，不承诺克隆后无需自行提供输入即可复现私人角色实验。纯数学测试与合成反例可完全复现。视频精度、所有 Blender 版本、任意骨架、最终衣物碰撞、水平足锁及游戏运行效果不在发布验收范围内。

## 两技能整合复验（2026-10-16）

整合用户提供的 animation-quality-review 完整评审、指标边界与步态融合参考；保留已验证的分析脚本实现。quick_validate 通过，19 项 unittest 重新通过，全部 Markdown 相对引用可达。补充项目内不可变视频归档、蒙皮算法对应、驱动烘焙与导出帧零点检查。来源哈希见 quality-integration.json。

## README 实际案例展示（2026-10-16）

新增 4 组实际动画 GIF/MP4、同姿势图片、4 张数学图和 8 份短窗口测量快照。原始估计以骨线重绘；动作重建与仅修改蒙皮分开比较。帧数、时长、文件哈希见 [媒体清单](../docs/showcase/media-manifest.json)，来源和版本见 [MEDIA.md](../docs/showcase/MEDIA.md)。这些是阶段性制作证据，不替代自然度验收。

`python scripts/plot_showcase.py` 从公开的 Blender 轨迹重算头部 jerk RMS 和左手角加速度 P95，并与记录值核对，再生成四张图；CI 同步执行。完整私人角色工程仍不分发，无法仅靠本仓库重渲染原角色。四张图可独立重建，其中相位图明确为合成方法示意。

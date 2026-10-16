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

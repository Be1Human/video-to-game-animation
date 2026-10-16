# 展示媒体的来源、版本与范围

**简体中文** | [English](MEDIA.en.md)

本目录服务于 README 的技术过程对照。动画均为实际关节点可视化或本项目 Blender 输出，没有使用生成图片代替实测结果。

| 文件 | 内容与来源 | 时间/版本 |
| --- | --- | --- |
| raw-capture.gif / .mp4 | MediaPipe 的实际未平滑关节点，髋中心估计坐标；重新画成骨线，没有原片像素 | 参考片 153.800–154.967 s；36 样本，播放前 35 帧 |
| walk-before-after.gif / .mp4 | 本项目 Blender 对照。左：捕捉加早期修型；右：UAL 参考辅助协调重建 | 同一骨架/蒙皮与 35/30 s 步行周期，原速 3 次 |
| back-binding-before-after.gif / .mp4 | 本项目 Blender 对照。原始蒙皮 vs 首轮背部修订；动作固定 | Run_Stop，0–1.6 s，包含终止帧 |
| shoulder-same-pose.jpg | 本项目同一姿势正/侧/背对照。上原始绑定，下后续肩袖修订 | Run_Stop 第 1 帧；实际渲染 |
| shoulder-refined-run-stop.gif / .mp4 | 后续肩袖修订的实际全动作，正/侧/背 | Run_Stop，0–1.6 s，包含终止帧 |
| motion-diagnostics.png / back-contribution.png / skinning-optimization.png | 从本目录 data/ 的实际测量和优化日志绘制 | 脚本可重建 |
| phase-method.png | 五次混合与相位抵消的合成数学示意 | 图内标注 METHOD ILLUSTRATION，不能充当角色实验 |
| running-contact-before-after.gif / .mp4；running-contact.png | 同蒙皮的冲刺接触修前修后；固定地面、相机跟随；图表来自 data/running-contact.json | 两次 2/3 秒原速循环，40 帧；设计根速度 4.4 m/s，未声称恢复原片根轨迹 |

最新跑步接触修订只改 Jog / Sprint 动作下肢接触，上半身曲线与肩袖蒙皮保持，其他 11 动作曲线保持。原地曲线加设计根速度形成可比较实验；120 Hz 固定接触窗口与低高度窗口分别报告。游戏足锁另做 60 / 30 fps 平地验证。下文“水平足锁待验收”描述此前历史媒体，不覆盖这次限定范围的修订；坡面、急转和最终全身自然度仍待验收。

## 来源和许可

- 宣传片：[项目记录的视频入口](https://www.youtube.com/watch?v=4NccLyRQQZY&t=153s)；[IGN 转载来源](https://open.video/@ign/v/varsapura-official-gameplay-video-2)。来源 URL 由原制作记录保留。本次公开的是短窗口关节点重绘及来源链接，未上传原片或叠加原片的视频；不宣称原片为 CC0/MIT。
- 协调参考：[Quaternius Universal Animation Library](https://quaternius.com/packs/universalanimationlibrary.html)，原作者标注 CC0。项目使用 Standard 中的步态参考；这不代表影片角色或用户模型也采用同一许可。
- 渲染角色：用户提供的警员模型；原始资产作者/再分发许可证未核实。本目录是用户要求公开的制作过程对比媒体，不含源角色模型、材质/贴图包或可复用角色资产。代码与说明的 MIT 许可不覆盖第三方角色权益，也不提供该角色独立复用许可。
- 数值：data/ 是用于复核本次示例的短片段估计、实际求值快照和指标记录，不是可覆盖不同人物/风格的统计基准，也不是标定动捕真值。

## 可比性与已知不足

步行修前已包含早期修型，修后采用参考辅助重建，因此不是“仅对原始捕捉滤波”的实验。相同周期防止通过放慢动作降低导数，但其他动作如站立/跑步的时长曾改动，本页未将它们混作同速对照。

背部隔离实验使用预选的 122 点；肩袖任务另有固定分区和 incident-edge 规则。两套区域的边长比不可直接互换。后续肩袖修订保持同一动作曲线和中央背部约束，但局部压缩、服装碰撞、水平足锁及最终全身自然度仍需验收。

MP4 是 30 fps 原速。GIF 同帧序，计时量化为 10 ms，因此原始周期 1.166667 s 的 GIF 为 1.16 s；跑停含终帧显示，MP4 1.633333 s、GIF 1.63 s。重复播放仅为观察，不能证明一次性动作无缝循环。具体以 media-manifest.json 为准。

"""本地视频 -> 33 个估计 3D 关节与逐帧置信度；本步骤不是最终角色动作。

运行环境：本仓库 requirements-capture.txt；显式提供本地模型。
官方说明：https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/python
输入须指定源视频与片段；不自动上传，不用现有动作库代替捕捉。
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import cv2
import mediapipe as mp
import numpy as np

EDGES = [(11,12),(11,13),(13,15),(12,14),(14,16),(11,23),(12,24),(23,24),(23,25),(25,27),(24,26),(26,28),(27,29),(29,31),(28,30),(30,32)]
CORE = [11,12,13,14,15,16,23,24,25,26,27,28]


def sha256(file):
    digest=hashlib.sha256()
    with file.open('rb') as source:
        for chunk in iter(lambda:source.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()


def extract(args):
    video=Path(args.video).expanduser().resolve()
    model=Path(args.model).expanduser().resolve()
    out=Path(args.output).expanduser().resolve()
    if not video.is_file() or not model.is_file():raise ValueError('源视频或模型文件不存在')
    if not 0<=args.visibility<=1 or args.start<0 or args.duration<=0 or not 1<=args.fps<=60:raise ValueError('起点、时长或采样帧率无效')
    if out.exists() and any(out.iterdir()):raise ValueError('输出目录不是空目录，避免覆盖已有捕捉结果')
    cap=cv2.VideoCapture(str(video))
    if not cap.isOpened():raise ValueError('OpenCV 无法解码该视频')
    source_fps=cap.get(cv2.CAP_PROP_FPS)
    total=cap.get(cv2.CAP_PROP_FRAME_COUNT)
    if source_fps<=0:raise ValueError('视频缺少可用帧率')
    duration=total/source_fps
    if args.start>=duration:raise ValueError('片段起点超过视频时长')
    out.mkdir(parents=True,exist_ok=True)
    cap.set(cv2.CAP_PROP_POS_MSEC,args.start*1000)
    options=mp.tasks.vision.PoseLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(model)),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,num_poses=2,
        min_pose_detection_confidence=.5,min_pose_presence_confidence=.5,min_tracking_confidence=.5)
    frames=[];next_sample=args.start;last_ms=-1;writer=None;fallback_count=0
    try:
        with mp.tasks.vision.PoseLandmarker.create_from_options(options) as detector:
            while True:
                ok,bgr=cap.read()
                if not ok:break
                t=cap.get(cv2.CAP_PROP_POS_MSEC)/1000
                if t<=0 and cap.get(cv2.CAP_PROP_POS_FRAMES)>1:
                    t=(cap.get(cv2.CAP_PROP_POS_FRAMES)-1)/source_fps;fallback_count+=1
                if t>=args.start+args.duration:break
                if t+1e-6<next_sample:continue
                next_sample=t+1/args.fps
                stamp=max(last_ms+1,round(t*1000));last_ms=stamp
                rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
                detected=detector.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(rgb)),stamp)
                count=len(detected.pose_landmarks)
                frame={'timestamp_ms':stamp,'time_in_clip_s':t-args.start,'detected_people':count,'image_landmarks':None,'world_landmarks':None,'core_visibility':0.0}
                if count==1:
                    frame['image_landmarks']=[[p.x,p.y,p.z,p.visibility,p.presence] for p in detected.pose_landmarks[0]]
                    frame['world_landmarks']=[[p.x,p.y,p.z,p.visibility,p.presence] for p in detected.pose_world_landmarks[0]]
                    frame['core_visibility']=float(np.mean([frame['image_landmarks'][i][3] for i in CORE]))
                    height,width=bgr.shape[:2]
                    pts=[(int(p[0]*width),int(p[1]*height)) for p in frame['image_landmarks']]
                    for a,b in EDGES:
                        if min(frame['image_landmarks'][a][3],frame['image_landmarks'][b][3])>=.5:cv2.line(bgr,pts[a],pts[b],(60,220,90),2)
                    for i in CORE:cv2.circle(bgr,pts[i],4,(40,190,255),-1)
                frames.append(frame)
                cv2.putText(bgr,f't={t:.2f}s people={count} confidence={frame["core_visibility"]:.2f}',(12,28),cv2.FONT_HERSHEY_SIMPLEX,.6,(0,220,255),2)
                if writer is None:
                    height,width=bgr.shape[:2]
                    writer=cv2.VideoWriter(str(out/'pose_overlay.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),min(source_fps,args.fps),(width,height))
                    if not writer.isOpened():raise RuntimeError('无法创建叠加视频')
                writer.write(bgr)
    finally:
        cap.release()
        if writer:writer.release()
    valid=[f['detected_people']==1 and f['core_visibility']>=args.visibility for f in frames]
    coverage=sum(valid)/max(len(frames),1)
    gap=longest=0.0
    for i,good in enumerate(valid):
        delta=(frames[i]['timestamp_ms']-frames[i-1]['timestamp_ms'])/1000 if i else 1/args.fps
        gap=0 if good else gap+delta;longest=max(longest,gap)
    report={'schema_version':1,'stage':'raw_pose_estimation_not_retargeted_animation','source_video':video.name,'source_sha256':sha256(video),'source_fps':source_fps,'source_duration_s':duration,'requested_start_s':args.start,'requested_duration_s':args.duration,'sample_fps_max':args.fps,'overlay_note':'constant-rate review preview; use stored source timestamps for analysis; VFR gaps are not retimed faithfully','timestamp_fallback_frames':fallback_count,'model_sha256':sha256(model),'model_source':args.model_source or 'user-provided local model; verify provenance separately','mediapipe_version':mp.__version__,'coordinates':'MediaPipe world coordinates in estimated meters, hip midpoint origin; absolute ground trajectory not recovered','landmark_values':['x','y','z','visibility','presence'],'quality':{'frames':len(frames),'usable_coverage':coverage,'longest_low_confidence_gap_s':longest,'visibility_threshold':args.visibility,'review_required':True},'limitations':['单目深度与遮挡关节为估计；无绝对世界位移','多人帧留空，不能推断身份对应','尚未进行时间平滑、骨长约束、脚接触处理或角色烘焙'],'frames':frames}
    (out/'pose_landmarks.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':'))+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='frames'},ensure_ascii=False,indent=2))
    return 0 if frames else 2


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video',required=True)
    parser.add_argument('--start',type=float,default=0)
    parser.add_argument('--duration',type=float,required=True)
    parser.add_argument('--fps',type=float,default=30)
    parser.add_argument('--model',required=True,help='Local compatible MediaPipe task model; never downloaded automatically')
    parser.add_argument('--visibility',type=float,default=.6,help='Exploratory coverage threshold, not acceptance')
    parser.add_argument('--output',required=True)
    parser.add_argument('--model-source',help='Provenance URL for the supplied model')
    args=parser.parse_args()
    try:sys.exit(extract(args))
    except (ValueError,RuntimeError) as error:parser.exit(1,f'{error}\n')

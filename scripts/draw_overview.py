#!/usr/bin/env python3
"""Draw the README's conceptual overview images (Pillow; no project media).

python scripts/draw_overview.py --font /path/to/CJK-font.ttf
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = 1600
INK = '#172c49'
MUTED = '#566b83'
BLUE = '#336fe4'
TEAL = '#148c87'
ORANGE = '#c77a20'
LINE = '#dbe4ee'
BG = '#f3f6fa'
FONT = None


def label(d, xy, value, size=28, color=INK):
    d.text(xy, value, font=ImageFont.truetype(FONT, size), fill=color, anchor='lt')


def box(d, xy, fill='white', outline=LINE, radius=24, width=2):
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def arrow(d, a, b, color=BLUE, width=5):
    d.line([a, b], fill=color, width=width)
    angle = math.atan2(b[1]-a[1], b[0]-a[0])
    pts = [b] + [(b[0]-16*math.cos(angle+s), b[1]-16*math.sin(angle+s)) for s in (-.5, .5)]
    d.polygon(pts, fill=color)


def person(d, x, y, scale=1, color=BLUE, pose=0, joints=False):
    # A drawn stick figure, not motion-capture output.
    s = scale
    coords = [(0, 0), (0, 25), (0, 66), (-30, 34), (30, 34),
              (-48+pose*10, 69), (48-pose*12, 69),
              (-18-pose*14, 104), (18+pose*13, 105),
              (-25-pose*20, 140), (25+pose*22, 139)]
    points = [(x+a*s, y+b*s) for a,b in coords]
    for a,b in [(1,2),(1,3),(1,4),(3,5),(4,6),(2,7),(2,8),(7,9),(8,10)]:
        d.line([points[a], points[b]], fill=color, width=max(2, int(6*s)))
    d.ellipse((x-12*s,y-13*s,x+12*s,y+11*s),fill=color)
    if joints:
        for px,py in points[1:]:
            d.ellipse((px-4*s,py-4*s,px+4*s,py+4*s),fill='white',outline=color,width=2)


def waveform(d, rect, color=BLUE, jagged=False):
    x,y,w,h=rect
    d.line((x,y+h,x+w,y+h),fill=LINE,width=2)
    pts=[]
    for i in range(161):
        t=i/160
        v=math.sin(t*math.pi*4)
        if jagged:
            v += .33*math.sin(t*math.pi*31)
        pts.append((x+t*w, y+h/2-v*h*.30))
    d.line(pts,fill=color,width=4)


def mesh(d, x, y, color=TEAL):
    # Garment-shaped grid with a highlighted shoulder region.
    rows=[]
    for j in range(5):
        row=[]
        for i in range(7):
            px=x+i*31+(3-i)*(4-j)*2
            py=y+j*22-17*math.cos((i-3)*.7)*(1-j/5)
            row.append((px,py))
        rows.append(row)
    for row in rows:
        d.line(row,fill=color,width=2)
    for i in range(7):
        d.line([row[i] for row in rows],fill=color,width=2)
    for row in rows:
        for px,py in row:
            d.ellipse((px-3,py-3,px+3,py+3),fill=color)
    d.ellipse((x+135,y-27,x+205,y+43),outline=ORANGE,width=4)


def icon(d, kind, x, y):
    if kind == 'video':
        box(d,(x,y,x+175,y+115),'#eaf1fe',BLUE,12)
        d.polygon([(x+68,y+31),(x+68,y+84),(x+114,y+57)],fill=BLUE)
        person(d,x+280,y+7,.68,TEAL,joints=True)
        label(d,(x+195,y+43),'+',32,MUTED)
    elif kind == 'capture':
        person(d,x+76,y+5,.8,BLUE,pose=.4,joints=True)
        for i,length in enumerate([140,114,63]):
            box(d,(x+170,y+15+i*34,x+310,y+29+i*34),'#e8edf5',None,6)
            box(d,(x+170,y+15+i*34,x+170+length,y+29+i*34),TEAL if i<2 else ORANGE,None,6)
    elif kind == 'clips':
        for i,(name,color) in enumerate([('Walk',BLUE),('Turn',TEAL),('Stop',ORANGE)]):
            bx=x+i*111
            box(d,(bx,y+6,bx+99,y+88),'#edf3fa',color,10)
            label(d,(bx+14,y+31),name,23,color)
        d.line((x,y+107,x+322,y+107),fill=MUTED,width=3)
        for i in range(10):
            d.line((x+i*35,y+102,x+i*35,y+112),fill=MUTED,width=2)
    elif kind == 'curves':
        waveform(d,(x,y,330,100),BLUE)
        for i in [0,2,4]:
            box(d,(x+i*66,y+113,x+i*66+38,y+125),TEAL,None,4)
        label(d,(x,y+144),'旋转 · 相位 · 足部接触',23,MUTED)
    elif kind == 'mesh':
        mesh(d,x+12,y+28)
        person(d,x+281,y+7,.74,BLUE,pose=.6,joints=True)
    elif kind == 'game':
        box(d,(x,y,x+210,y+133),'#eef5f6',TEAL,12)
        d.line((x+22,y+112,x+187,y+112),fill=LINE,width=3)
        person(d,x+105,y+19,.59,TEAL,pose=.4)
        d.line((x+105,y+133,x+105,y+148),fill=TEAL,width=4)
        d.line((x+66,y+148,x+144,y+148),fill=TEAL,width=4)
        box(d,(x+244,y+23,x+332,y+107),'#eaf1fe',BLUE,12)
        label(d,(x+259,y+49),'GLB',25,BLUE)


def header(d, kicker, title, subtitle):
    label(d,(56,34),kicker,22,BLUE)
    label(d,(56,75),title,46)
    label(d,(56,137),subtitle,25,MUTED)


def pipeline(out):
    im=Image.new('RGB',(W,1130),BG);d=ImageDraw.Draw(im)
    header(d,'VIDEO TO GAME ANIMATION / WORKFLOW','从视频参考，到游戏里的单元动作','制作与质量评审合在一条流程里；已有动画核对输入后，可从第 04 步进入。')
    steps=[
        ('01','输入审查','video',['视频、角色、现有骨架','核对许可、单位、骨轴与 rest 姿态']),
        ('02','姿态捕捉','capture',['逐帧关键点 + 时间戳 + 置信度','遮挡、换人、深度不确定性要保留']),
        ('03','拆分与重定向','clips',['走 / 跑 / 转向 / 起停 → 独立动作','同一骨架标定，再烘焙动作曲线']),
        ('04','协调动作','curves',['SO(3) 旋转拟合与启停融合','统一相位，复查接触和身体朝向']),
        ('05','Blender 全身复验','mesh',['同动作查肩、袖窿、背与四肢','固定曲线修权重，逐动作多视角看']),
        ('06','导出与游戏核验','game',['候选文件 + 指标 + 修前修后证据','复核骨架路径、形变、切换与实跑']),
    ]
    for i,(num,title,kind,lines) in enumerate(steps):
        col=i%3;row=i//3;x=56+col*512;y=202+row*432
        box(d,(x,y,x+464,y+395))
        box(d,(x+24,y+24,x+82,y+68),'#eaf1fe',None,10)
        label(d,(x+35,y+31),num,28,BLUE)
        label(d,(x+103,y+32),title,31)
        icon(d,kind,x+48,y+110)
        for j,line in enumerate(lines):
            label(d,(x+24,y+294+j*43),line,23,INK if j==0 else MUTED)
        if col<2:
            arrow(d,(x+475,y+196),(x+502,y+196))
    label(d,(56,1080),'方法概览 · 发现问题就返回对应环节 · 原件与每轮审阅证据持续保留',25,MUTED)
    im.save(out/'pipeline.png',optimize=True)


def review(out):
    im=Image.new('RGB',(W,1010),BG);d=ImageDraw.Draw(im)
    header(d,'QUALITY REVIEW / THREE LAYERS','先定位哪一层，再修；最后回到全身看','分清动作、蒙皮与引擎三个层面，避免修好后背却把肩袖或脚步弄坏。')
    titles=['动作曲线与融合','网格与蒙皮权重','导出与引擎运行']
    colors=[BLUE,TEAL,ORANGE]
    content=[
        ['骨骼怎么动？','轨迹、角速度 / 角加速度、jerk','相位、支撑脚滑移、启停连续性','同骨架、同速度、同相位对照'],
        ['骨骼怎样带动网格？','锁定动作曲线，比较真实网格','肩袖拉伸、背部牵拉、附件贴合','局部修改后，检查全身与独立试姿'],
        ['引擎里是否仍然一致？','核对单位、朝向与动画轨道','比较 Blender 与引擎求值形变','用实际角色检查动作切换与实跑'],
    ]
    for i in range(3):
        x=56+i*512;y=206;c=colors[i]
        box(d,(x,y,x+464,y+467))
        box(d,(x+24,y+24,x+440,y+80),c,None,10)
        label(d,(x+42,y+36),titles[i],30,'white')
        if i==0:
            waveform(d,(x+44,y+112,165,86),ORANGE,True)
            arrow(d,(x+228,y+159),(x+258,y+159),BLUE,3)
            waveform(d,(x+278,y+112,140,86),BLUE)
        elif i==1:
            mesh(d,x+70,y+142)
            arrow(d,(x+288,y+159),(x+335,y+159),TEAL,3)
            d.ellipse((x+347,y+123,x+401,y+178),outline=TEAL,width=5)
            label(d,(x+358,y+137),'W',23,TEAL)
        else:
            person(d,x+105,y+113,.68,BLUE,pose=.6)
            arrow(d,(x+196,y+164),(x+262,y+164),ORANGE,3)
            person(d,x+351,y+113,.68,TEAL,pose=.6)
            label(d,(x+61,y+228),'Blender',23,MUTED)
            label(d,(x+322,y+228),'游戏',23,MUTED)
        for j,line in enumerate(content[i]):
            label(d,(x+24,y+286+j*40),line,27 if j==0 else 23,c if j==0 else INK)
    label(d,(56,712),'每次修改都走一遍',30)
    loop=['定位问题层','只改对应变量','同姿势修前 / 修后','全动作 + 全身复验']
    for i,txt in enumerate(loop):
        x=56+i*384
        box(d,(x,769,x+344,849),'#eaf1fe',None,14)
        label(d,(x+22,794),txt,27,BLUE)
        if i<3:
            arrow(d,(x+352,809),(x+377,809),BLUE,4)
    box(d,(56,889,1544,966),'#e7efed',None,18)
    label(d,(81,911),'判断依据：原速多视角 + 接触与形变 + 实测曲线；保留改善，也记录退化。',28,TEAL)
    im.save(out/'quality-review.png',optimize=True)


def main():
    global FONT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font',type=Path,help='CJK TrueType/OpenType font; not bundled')
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'docs/overview')
    args=parser.parse_args()
    candidates=[args.font,Path('/System/Library/Fonts/PingFang.ttc'),
                Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'),
                Path('C:/Windows/Fonts/msyh.ttc')]
    FONT=next((str(p) for p in candidates if p and p.is_file()),None)
    if not FONT:
        parser.error('Provide --font with a Chinese-capable font.')
    args.output.mkdir(parents=True,exist_ok=True)
    pipeline(args.output);review(args.output)
    print(f'Wrote 2 conceptual diagrams to {args.output}')


if __name__=='__main__':
    main()

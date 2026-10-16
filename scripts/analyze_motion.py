"""Analyze already-evaluated trajectories. Requires numpy>=2; never emits a naturalness score."""
import argparse,json
from pathlib import Path
import numpy as np

def quat_clean(q):
 q=np.array(q,dtype=float,copy=True);n=np.linalg.norm(q,axis=1)
 if np.any(n<1e-12):raise ValueError('Zero quaternion')
 q/=n[:,None]
 for i in range(1,len(q)):
  if q[i]@q[i-1]<0:q[i]*=-1
 return q

def mul(a,b):
 return np.concatenate([(a[...,0]*b[...,0]-np.sum(a[...,1:]*b[...,1:],axis=-1))[...,None],a[...,0,None]*b[...,1:]+b[...,0,None]*a[...,1:]+np.cross(a[...,1:],b[...,1:])],axis=-1)

def inv(q):
 x=q.copy();x[...,1:]*=-1;return x

def logq(q):
 q=np.array(q,copy=True);q[q[...,0]<0]*=-1;s=np.linalg.norm(q[...,1:],axis=-1);angle=2*np.arctan2(s,np.clip(q[...,0],-1,1));return q[...,1:]*(angle/np.maximum(s,1e-12))[...,None]

def analyze(d):
 if d.get('units')!='m':raise ValueError('This executable schema requires meters; do not mislabel uncalibrated video units')
 t=np.asarray(d['time_s'],float);dt=np.diff(t);N=len(t)
 if N<9 or not np.isfinite(t).all() or np.any(dt<=0):raise ValueError('Need >=9 finite increasing timestamps per continuous segment')
 if not np.allclose(dt,dt.mean(),rtol=1e-4,atol=1e-7):raise ValueError('Explicitly resample irregular data first; gaps must be separate inputs')
 up=d.get('up_axis','Z')
 if up not in ['X','Y','Z']:raise ValueError('up_axis must be X, Y or Z')
 ui=['X','Y','Z'].index(up);tangent=[i for i in range(3) if i!=ui]
 if not d.get('positions') and not d.get('world_quaternions'):raise ValueError('Need at least one trajectory')
 h=float(dt.mean());T=float(t[-1]-t[0]);scale=float(d.get('scale_m',0));loop=d.get('loop') or {};duplicate=loop.get('duplicate_endpoint',False)
 if loop and not duplicate:raise ValueError('Loop seam evaluator requires declared duplicate endpoint; append evaluated endpoint using true period')
 if loop and abs(float(loop['period_s'])-T)>1e-5:raise ValueError('period_s must match duplicate-endpoint duration')
 out={'name':d['name'],'duration_s':T,'samples':N,'fps':1/h,'units':d['units'],'axes':d['axes'],'provenance':d.get('provenance',{}),'method':'raw samples; recursive central differences np.gradient edge_order=2; jerk statistics discard 3 samples at each end; angular interval increments in fixed world axes; no filtering','positions':{},'rotations':{},'contacts':[],'status':'待复核：无自然度评分、未设置自动验收阈值'}
 curves={'time_s':t.tolist(),'linear':{},'angular':{}}
 for name,arr in d.get('positions',{}).items():
  p=np.asarray(arr,float)
  if p.shape!=(N,3) or not np.isfinite(p).all():raise ValueError('Invalid position '+name)
  v=np.gradient(p,h,axis=0,edge_order=2);a=np.gradient(v,h,axis=0,edge_order=2);j=np.gradient(a,h,axis=0,edge_order=2);jn=np.linalg.norm(j,axis=1);valid=slice(3,-3);i=int(np.argmax(jn[valid])+3)
  r={'speed_p95':float(np.percentile(np.linalg.norm(v[valid],axis=1),95)),'jerk_rms':float(np.sqrt(np.mean(jn[valid]**2))),'peak_jerk_time_s':float(t[i]),'peak_jerk':float(jn[i]),'range_xyz':np.ptp(p,axis=0).tolist(),'J_scale_body':float(T**5/scale**2*np.trapezoid(jn[valid]**2,t[valid])) if scale>0 and np.ptp(p,axis=0).max()>1e-7 else None}
  if duplicate:r['seam_position']=float(np.linalg.norm(p[-1]-p[0]));r['seam_velocity']=float(np.linalg.norm(v[-1]-v[0]))
  out['positions'][name]=r;curves['linear'][name]={'position':p.tolist(),'speed':np.linalg.norm(v,axis=1).tolist(),'jerk':jn.tolist()}
 for name,arr in d.get('world_quaternions',{}).items():
  q=quat_clean(arr)
  if q.shape!=(N,4) or not np.isfinite(q).all():raise ValueError('Invalid rotation '+name)
  w=logq(mul(q[1:],inv(q[:-1])))/h;alpha=np.gradient(w,h,axis=0,edge_order=2);an=np.linalg.norm(alpha,axis=1);i=int(np.argmax(an[2:-2])+2)
  r={'angular_speed_p95_rad_s':float(np.percentile(np.linalg.norm(w[2:-2],axis=1),95)),'angular_accel_p95_rad_s2':float(np.percentile(an[2:-2],95)),'peak_accel_time_s':float((t[i]+t[i+1])/2),'peak_accel_rad_s2':float(an[i])}
  if duplicate:r['seam_angle_rad']=float(np.linalg.norm(logq(mul(q[-1:],inv(q[:1])))[0]));r['seam_angular_velocity_rad_s']=float(np.linalg.norm((1.5*w[-1]-.5*w[-2])-(1.5*w[0]-.5*w[1])))
  out['rotations'][name]=r;curves['angular'][name]={'time_s':((t[:-1]+t[1:])/2).tolist(),'speed_rad_s':np.linalg.norm(w,axis=1).tolist(),'accel_rad_s2':an.tolist()}
 for contact in d.get('contacts',[]):
  if contact.get('start_s',0)>contact.get('end_s',0):raise ValueError('Invalid contact interval')
  if not contact.get('surface_stationary') or not contact.get('evidence'):raise ValueError('Contact requires stationary surface and evidence')
  idx=np.flatnonzero((t>=contact['start_s']-1e-7)&(t<=contact['end_s']+1e-7));p=np.asarray(d['positions'][contact['point']],float)[idx]
  if len(p)<2:continue
  out['contacts'].append({**contact,'horizontal_path_m':float(np.linalg.norm(np.diff(p[:,tangent],axis=0),axis=1).sum()),'max_horizontal_offset_m':float(np.linalg.norm(p[:,tangent]-p[0,tangent],axis=1).max()),'max_penetration_m':float(max(0,contact.get('ground_height',contact.get('ground_z',0))-p[:,ui].min()))})
 if not out['contacts']:out['contact_status']='未评估：无地面坐标接触标签；原地足部运动不能直接视为滑步'
 return out,curves

def main():
 ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('--output',required=True);args=ap.parse_args();d=json.loads(Path(args.input).read_text());r,c=analyze(d);o=Path(args.output);o.parent.mkdir(parents=True,exist_ok=True);o.write_text(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False));o.with_suffix('.curves.json').write_text(json.dumps(c,separators=(',',':')))
if __name__=='__main__':main()

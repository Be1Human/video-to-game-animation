"""Semantic checks: invariances and counterexamples, not mirrored implementation."""
import copy,unittest,numpy as np
from analyze_motion import analyze

def data(speed=1,scale=1):
 t=np.linspace(0,1,61)/speed;p=np.column_stack([np.sin(2*np.pi*t*speed),np.zeros(len(t)),np.zeros(len(t))])*scale
 return {'name':'synthetic','time_s':t.tolist(),'units':'m','axes':'Z-up','scale_m':scale,'positions':{'hand':p.tolist()},'world_quaternions':{},'loop':{'period_s':1/speed,'duplicate_endpoint':True}}
class Semantics(unittest.TestCase):
 def test_time_scale_J(self):
  a=analyze(data())[0];b=analyze(data(2))[0];self.assertAlmostEqual(a['positions']['hand']['J_scale_body'],b['positions']['hand']['J_scale_body'],places=6);self.assertAlmostEqual(b['positions']['hand']['jerk_rms']/a['positions']['hand']['jerk_rms'],8)
 def test_space_scale_J(self):
  self.assertAlmostEqual(analyze(data())[0]['positions']['hand']['J_scale_body'],analyze(data(scale=2))[0]['positions']['hand']['J_scale_body'],places=6)
 def test_sign_flip(self):
  d=data();d['world_quaternions']['head']=[[(-1)**i,0,0,0] for i in range(61)];self.assertEqual(analyze(d)[0]['rotations']['head']['peak_accel_rad_s2'],0)
 def test_constant_rotation(self):
  d=data();d.pop('loop');t=np.asarray(d['time_s']);d['world_quaternions']['head']=np.column_stack([np.cos(t/2),np.zeros(len(t)),np.zeros(len(t)),np.sin(t/2)]).tolist();r=analyze(d)[0]['rotations']['head'];self.assertAlmostEqual(r['angular_speed_p95_rad_s'],1);self.assertLess(r['peak_accel_rad_s2'],1e-10)
 def test_tiny_rotation_does_not_round_to_zero(self):
  d=data();d.pop("loop");t=np.asarray(d["time_s"]);rate=1e-5;d["world_quaternions"]["head"]=np.column_stack([np.cos(t*rate/2),np.zeros(len(t)),np.zeros(len(t)),np.sin(t*rate/2)]).tolist();self.assertAlmostEqual(analyze(d)[0]["rotations"]["head"]["angular_speed_p95_rad_s"],rate,places=12)
 def test_smooth_sliding_is_not_contact_pass(self):
  d=data();t=np.array(d['time_s']);d.pop('loop');d['positions']['foot']=np.column_stack([t,np.zeros(len(t)),np.zeros(len(t))]).tolist();d['contacts']=[{'point':'foot','start_s':0,'end_s':1,'surface_stationary':True,'evidence':'synthetic known contact'}];r=analyze(d)[0];self.assertAlmostEqual(r['contacts'][0]['horizontal_path_m'],1);self.assertLess(r['positions']['foot']['jerk_rms'],1e-7)
 def test_gap_rejected(self):
  d=data();d['time_s'][30]+=.005
  with self.assertRaises(ValueError):analyze(d)
 def test_static_J_null(self):
  d=data();d['positions']['hand']=[[0,0,0]]*61;self.assertIsNone(analyze(d)[0]['positions']['hand']['J_scale_body'])
 def test_period_mismatch(self):
  d=data();d['loop']['period_s']=2
  with self.assertRaises(ValueError):analyze(d)
if __name__=='__main__':unittest.main()

"""Behavioral invariants and counterexamples; no character/video assets required."""
import unittest
import numpy as np
from motion_math import exp_rotation, log_rotation, multiply, inverse, slerp, quintic_weight, fit_periodic, evaluate_periodic
from mesh_diagnostics import analyze as mesh_analyze
from analyze_motion import analyze


class RotationTests(unittest.TestCase):
    def test_small_and_large_log_roundtrip(self):
        v = np.array([[1e-10, 0, 0], [.7, -.2, 1.1]])
        np.testing.assert_allclose(log_rotation(exp_rotation(v)), v, atol=1e-12)

    def test_slerp_sign_invariance(self):
        a = exp_rotation([.1, .2, -.3]); b = exp_rotation([.7, -.2, .1])
        np.testing.assert_allclose(slerp(a, b, .3), slerp(a, -b, .3), atol=1e-12)

    def test_periodic_recovers_known_motion_and_seam(self):
        phase = np.arange(60)/60
        v = np.column_stack([.3*np.sin(2*np.pi*phase), np.zeros(60), np.zeros(60)])
        q = exp_rotation(v); model = fit_periodic(phase, q, harmonics=2)
        error = log_rotation(multiply(evaluate_periodic(model, phase), inverse(q)))
        self.assertLess(np.abs(error).max(), 1e-12)
        np.testing.assert_allclose(evaluate_periodic(model, 0), evaluate_periodic(model, 1), atol=1e-12)

    def test_chart_cut_rejected(self):
        q = exp_rotation([[0,0,0], [np.pi,0,0], [0,0,0]])
        with self.assertRaises(ValueError): fit_periodic([0,.5,1], q, 1)

    def test_quintic_boundary_derivatives(self):
        h = 1e-5
        for t in [0., 1.]:
            slope = (quintic_weight(t+h)-quintic_weight(t-h))/(2*h)
            curvature = (quintic_weight(t+h)-2*quintic_weight(t)+quintic_weight(t-h))/h**2
            self.assertLess(abs(slope), 1e-8); self.assertLess(abs(curvature), .001)


class MeshTests(unittest.TestCase):
    def setUp(self):
        self.rest = np.array([[0.,0,0], [1,0,0], [0,1,0]])
        self.edges = np.array([[0,1], [0,2], [1,2]])
        self.region = np.arange(3)

    def test_rigid_transform_has_unit_strain(self):
        r = np.array([[0.,-1,0], [1,0,0], [0,0,1]])
        posed = (self.rest@r.T+[3,4,5])[None]
        result = mesh_analyze(self.rest, posed, self.edges, self.region)
        self.assertAlmostEqual(result['edge_ratio']['max_each_frame'][0], 1)

    def test_uniform_scale_and_ablation(self):
        posed = (self.rest*2)[None]; disabled = posed+[.01,0,0]
        result = mesh_analyze(self.rest, posed, self.edges, self.region, disabled)
        self.assertAlmostEqual(result['edge_ratio']['min_each_frame'][0], 2)
        self.assertAlmostEqual(result['chain_contribution_m']['max_each_frame'][0], .01)

    def test_missing_edges_is_not_pass(self):
        result = mesh_analyze(self.rest, self.rest[None], self.edges, np.array([0]))
        self.assertIsNone(result['edge_ratio'])

    def test_invalid_correspondence_rejected(self):
        with self.assertRaises(ValueError): mesh_analyze(self.rest, self.rest[None,:2], self.edges, self.region)


class AxisTests(unittest.TestCase):
    def test_y_up_contact(self):
        t = np.linspace(0,1,61)
        d = {'name':'synthetic-y-up', 'time_s':t.tolist(), 'units':'m', 'axes':'Y-up', 'up_axis':'Y',
             'positions':{'sole':np.column_stack([t, np.full(61,-.02), np.zeros(61)]).tolist()},
             'contacts':[{'point':'sole','start_s':0,'end_s':1,'surface_stationary':True,'evidence':'synthetic known contact'}]}
        r = analyze(d)[0]['contacts'][0]
        self.assertAlmostEqual(r['max_penetration_m'], .02)
        self.assertAlmostEqual(r['horizontal_path_m'], 1)


if __name__ == '__main__': unittest.main()

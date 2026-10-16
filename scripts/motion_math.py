"""Rotation helpers; active Hamilton wxyz. Log uses full rotation vectors."""
import numpy as np


def normalize(q):
    q = np.asarray(q, dtype=float)
    if q.shape[-1] != 4 or not np.isfinite(q).all():
        raise ValueError('Expected finite wxyz quaternions')
    norm = np.linalg.norm(q, axis=-1, keepdims=True)
    if np.any(norm < 1e-12):
        raise ValueError('Zero quaternion')
    return q / norm


def multiply(a, b):
    a, b = np.broadcast_arrays(np.asarray(a, float), np.asarray(b, float))
    return np.concatenate(((a[..., :1]*b[..., :1] - np.sum(a[..., 1:]*b[..., 1:], axis=-1, keepdims=True)),
                           a[..., :1]*b[..., 1:] + b[..., :1]*a[..., 1:] + np.cross(a[..., 1:], b[..., 1:])), axis=-1)


def inverse(q):
    out = normalize(q).copy()
    out[..., 1:] *= -1
    return out


def log_rotation(q):
    q = normalize(q)
    q = np.where(q[..., :1] < 0, -q, q)
    s = np.linalg.norm(q[..., 1:], axis=-1, keepdims=True)
    angle = 2*np.arctan2(s, q[..., :1])
    return q[..., 1:] * np.divide(angle, s, out=np.full_like(s, 2.), where=s > 1e-12)


def exp_rotation(v):
    v = np.asarray(v, dtype=float)
    if v.shape[-1] != 3 or not np.isfinite(v).all():
        raise ValueError('Expected finite rotation vectors')
    a = np.linalg.norm(v, axis=-1, keepdims=True)
    factor = np.divide(np.sin(a/2), a, out=np.full_like(a, .5), where=a > 1e-12)
    return normalize(np.concatenate((np.cos(a/2), v*factor), axis=-1))


def slerp(a, b, weight):
    a, b = normalize(a), normalize(b)
    relative = multiply(b, inverse(a))
    return normalize(multiply(exp_rotation(log_rotation(relative)*np.asarray(weight)[..., None]), a))


def quintic_weight(s):
    s = np.clip(np.asarray(s, float), 0, 1)
    return s*s*s*(10+s*(-15+6*s))


def design(phase, harmonics):
    p = np.asarray(phase, float)
    return np.stack([np.ones_like(p)] + [f(2*np.pi*k*p) for k in range(1, harmonics+1)
                                      for f in (np.cos, np.sin)], axis=-1)


def fit_periodic(phase, rotations, harmonics=3, confidence=None):
    """Fit one joint within a single Log chart. Does not infer phase or contacts."""
    phase = np.asarray(phase, float)
    q = normalize(rotations)
    if not isinstance(harmonics, int) or harmonics < 0:
        raise ValueError('harmonics must be a nonnegative integer')
    if phase.ndim != 1 or q.shape != (len(phase), 4) or not np.isfinite(phase).all():
        raise ValueError('phase/rotation shape mismatch')
    if len(q) < 2*harmonics+1:
        raise ValueError('Not enough samples for the harmonic order')
    anchor = q[0]
    vectors = log_rotation(multiply(q, inverse(anchor)))
    if np.linalg.norm(vectors, axis=1).max() >= np.pi-.05:
        raise ValueError('Motion approaches Log chart cut; segment it or use another representation')
    weights = np.ones(len(q)) if confidence is None else np.asarray(confidence, float)
    if weights.shape != phase.shape or not np.isfinite(weights).all() or np.any(weights < 0):
        raise ValueError('Invalid confidence weights')
    X = design(phase, harmonics)*np.sqrt(weights)[:, None]
    if np.linalg.matrix_rank(X) < X.shape[1]:
        raise ValueError('Insufficient independent phase observations')
    coef = np.linalg.lstsq(X, vectors*np.sqrt(weights)[:, None], rcond=None)[0]
    return {'anchor_wxyz': anchor.tolist(), 'coefficients': coef.tolist(), 'harmonics': harmonics,
            'method': 'single-chart periodic Log fit; not a contact or full-body solver'}


def evaluate_periodic(model, phase):
    vectors = design(phase, model['harmonics']) @ np.asarray(model['coefficients'])
    return multiply(exp_rotation(vectors), np.asarray(model['anchor_wxyz']))

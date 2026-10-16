"""Read evaluated Blend motion. Run with Blender --background FILE --python this.py -- ..."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def export(config):
    scene = bpy.context.scene
    rig = bpy.data.objects.get(config['rig'])
    if rig is None or rig.type != 'ARMATURE':
        raise ValueError('Configured rig is not an Armature')
    unit = float(config['meters_per_unit'])
    if not math.isfinite(unit) or unit <= 0:
        raise ValueError('Explicit positive meters_per_unit required')
    names = config['bones']
    if not names or len(set(names)) != len(names) or any(n not in rig.data.bones for n in names):
        raise ValueError('Bone selection must be unique, nonempty and present')
    mode = config.get('mode', 'action')
    if mode == 'action':
        action = bpy.data.actions.get(config['action'])
        if action is None:
            raise ValueError('Action does not exist')
        rig.animation_data_create()
        rig.animation_data.action = action
        slots = list(getattr(action, 'slots', []))
        if slots:
            desired = config.get('action_slot')
            matches = [s for s in slots if s.identifier == desired] if desired else slots
            if len(matches) != 1:
                raise ValueError('Specify action_slot for an action with multiple slots')
            rig.animation_data.action_slot = matches[0]
        for track in rig.animation_data.nla_tracks:
            track.mute = True
        rig.animation_data.action_blend_type = 'REPLACE'
        rig.animation_data.action_influence = 1
    elif mode != 'scene':
        raise ValueError('mode must be action or scene')
    first, last, step = map(float, (config['frame_start'], config['frame_end'], config.get('frame_step', 1)))
    if not all(math.isfinite(v) for v in [first, last, step]) or step <= 0 or last < first:
        raise ValueError('Invalid frame range')
    count = round((last-first)/step)+1
    if abs((count-1)*step-(last-first)) > 1e-6 or count > 1000000:
        raise ValueError('Use an evenly sampled range, at most one million samples')
    fps = scene.render.fps/scene.render.fps_base
    positions = {n: [] for n in names}
    rotations = {n: [] for n in names}
    markers = config.get('markers', {})
    if set(markers) & set(names):
        raise ValueError('Marker keys must not shadow bone names')
    for key, object_name in markers.items():
        if object_name not in bpy.data.objects:
            raise ValueError('Marker object missing: '+object_name)
        positions[key] = []
    for i in range(count):
        frame = first+i*step
        scene.frame_set(math.floor(frame), subframe=frame-math.floor(frame))
        bpy.context.view_layer.update()
        graph = bpy.context.evaluated_depsgraph_get()
        ev = rig.evaluated_get(graph)
        for name in names:
            matrix = ev.matrix_world @ ev.pose.bones[name].matrix
            # Rotation extraction with shear or nonuniform scale needs a separate policy.
            basis = matrix.to_3x3()
            axes = [basis.col[k].normalized() for k in range(3)]
            if basis.determinant() <= 0 or any(abs(axes[a].dot(axes[b])) > 1e-5 for a,b in [(0,1),(0,2),(1,2)]):
                raise ValueError('Reflection/shear detected; define a rotation extraction policy first')
            q = matrix.to_quaternion().normalized()
            positions[name].append([float(x)*unit for x in matrix.translation])
            rotations[name].append(list(q))
        for key, object_name in markers.items():
            obj = bpy.data.objects[object_name].evaluated_get(graph)
            positions[key].append([float(x)*unit for x in obj.matrix_world.translation])
    rest = [(b.name, b.parent.name if b.parent else None,
             [list(row) for row in b.matrix_local], b.use_deform) for b in rig.data.bones]
    source = Path(bpy.data.filepath)
    result = {'name': config.get('name', config.get('action', 'scene-evaluated')),
              'time_s': [i*step/fps for i in range(count)], 'units': 'm',
              'axes': config['axes'], 'up_axis': config.get('up_axis', 'Z'),
              'scale_m': config.get('scale_m', 0), 'positions': positions,
              'world_quaternions': rotations, 'contacts': config.get('contacts', []),
              'provenance': {'evaluation': 'Blender evaluated depsgraph, FK/constraints/drivers',
                             'mode': mode, 'nla_muted_on_selected_rig': mode == 'action',
                             'other_objects': 'scene animation retained; inspect dependencies',
                             'blender': bpy.app.version_string, 'filter': 'none',
                             'meters_per_unit': unit, 'source_file': source.name,
                             'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest() if source.is_file() else None,
                             'rest_sha256': digest(rest), 'frame_start': first, 'frame_end': last,
                             'frame_step': step, 'scene_fps': fps, 'config': config}}
    if config.get('loop'):
        if config.get('root_motion', 'unknown') != 'in_place':
            raise ValueError('Loop metrics need canonical root coordinates; export raw, then canonicalize separately')
        result['loop'] = config['loop']
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    result = export(json.loads(Path(args.config).read_text()))
    out = Path(args.output)
    if out.resolve() == Path(bpy.data.filepath).resolve():
        raise ValueError('Output cannot overwrite source Blend')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, allow_nan=False, separators=(',', ':')))
    print('EXPORTED', result['name'], len(result['time_s']), 'samples; source not saved')


if __name__ == '__main__':
    main()

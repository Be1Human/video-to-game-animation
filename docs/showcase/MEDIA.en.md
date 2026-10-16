# Demonstration media: sources, versions, and scope

[简体中文](MEDIA.md) | **English**

This directory supports the technical comparisons in the README. Its animations are visualizations of actual estimated landmarks or Blender outputs from the project. Generated illustrations are not used as substitutes for measured results.

| File | Content and source | Time / version |
| --- | --- | --- |
| raw-capture.gif / .mp4 | Actual, unsmoothed MediaPipe landmarks in estimated hip-centered coordinates; redrawn as a skeleton, with no source-video pixels | Reference video 153.800–154.967 s; 36 samples, first 35 played |
| walk-before-after.gif / .mp4 | Project Blender comparison. Left: capture plus earlier cleanup. Right: coordination reconstructed with UAL references | Same skeleton/skinning and 35/30 s walk cycle, repeated three times at original speed |
| back-binding-before-after.gif / .mp4 | Project Blender comparison: original skinning versus the first back revision, with motion fixed | Run_Stop, 0–1.6 s, including the terminal frame |
| shoulder-same-pose.jpg | Same-pose front/side/back comparison. Top: original binding. Bottom: later shoulder/sleeve revision | Run_Stop frame 1; actual renders |
| shoulder-refined-run-stop.gif / .mp4 | Actual complete clip after shoulder/sleeve refinement, in front/side/back views | Run_Stop, 0–1.6 s, including the terminal frame |
| motion-diagnostics.png / back-contribution.png / skinning-optimization.png | Plots from actual measurements and optimization logs in data/ | Rebuildable with the provided script |
| phase-method.png | Synthetic mathematical illustration of quintic blending and phase cancellation | Labeled METHOD ILLUSTRATION in the image; not a character experiment |
| running-contact-before-after.gif / .mp4; running-contact.png | Sprint contact revision with unchanged skinning; fixed floor and following camera; chart from data/running-contact.json | Two native 2/3-second cycles, 40 frames; designed 4.4 m/s root speed, not a recovered source-video trajectory |

The latest running revision changes lower-limb contact in Jog / Sprint, preserving upper-body curves, shoulder/sleeve skinning, and the other 11 actions. A designed root speed makes the in-place curves comparable. Fixed contact windows and near-floor windows are reported separately at 120 Hz. Runtime foot plants are tested separately on flat ground at 60 / 30 fps. Statements below that horizontal foot locking remains unaccepted describe the earlier media, not this limited running revision. Slopes, sharp turns, and final whole-body naturalness still require acceptance.

## Sources and licensing

- Reference footage: [video entry recorded by the project](https://www.youtube.com/watch?v=4NccLyRQQZY&t=153s) and [IGN repost](https://open.video/@ign/v/varsapura-official-gameplay-video-2). These URLs are retained from the production records. Only a short window of redrawn landmarks and source links are published here; the footage and videos overlaid on it are not uploaded. The original video is not claimed to be CC0 or MIT-licensed.
- Coordination reference: [Quaternius Universal Animation Library](https://quaternius.com/packs/universalanimationlibrary.html), labeled CC0 by its creator. This project uses gait references from the Standard pack. That license does not extend to characters in the video or the user's model.
- Rendered character: the user-supplied police-officer model. The original asset's author and redistribution license have not been verified. These are process-comparison media the user requested to publish, not a source model, material/texture package, or reusable character asset. The MIT license for the code and documentation does not cover third-party character rights or grant independent reuse rights to this character.
- Numerical data: data/ contains short-window estimates, evaluated trajectories, and metric records for checking this example. It is neither a statistical benchmark covering different characters/styles nor calibrated motion-capture ground truth.

## Comparability and known limitations

The walking baseline already includes earlier cleanup, and the revision uses reference-assisted reconstruction. It is not an experiment in merely filtering the raw capture. Matching the cycle duration avoids reducing derivatives simply by slowing the motion. Durations of other clips, such as idle and run, changed during production; this page does not mix them into a same-speed comparison.

The back-isolation experiment uses 122 preselected vertices. The later shoulder/sleeve task uses its own fixed regions and incident-edge rule. Edge-length ratios from those two region definitions are not interchangeable. The later revision preserves the animation curves and central-back constraint, but local compression, clothing collisions, horizontal foot locking, and final whole-body naturalness still need acceptance checks.

MP4 files preserve the original 30 fps. GIFs use the same frame sequence with timing quantized to 10 ms: a 1.166667 s cycle becomes 1.16 s in GIF. Run-to-stop media display the terminal frame, giving 1.633333 s in MP4 and 1.63 s in GIF. Repetition is for inspection and does not establish seamless looping for a one-shot action. See [media-manifest.json](media-manifest.json) for exact values.

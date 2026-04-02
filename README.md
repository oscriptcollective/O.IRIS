# O.Iris: The Mind's Eye Has an Iris

**Mapping Brain State Flexibility Through EEG Spectral Geometry**

O.Iris is an open-source pipeline that transforms EEG recordings into circular "pupil maps" showing how brain states—meditation, sleep, rest, focused work, stress—occupy distinct positions in a geometric space organized around a theoretically motivated focal point.

## What this does

- Takes raw EEG files (BDF, EDF, SET, CSV)
- Computes spectral slope, autocorrelation decay time, and flicker per window
- Maps each window to a position in circular pupil space (radius = distance from focal point, angle = balance between persistence and fluctuation)
- Generates static maps and animated GIFs showing brain state journeys over time

## Key findings

- Meditation clusters nearest the focal point (median spectral slope 1.82)
- Sleep disperses furthest (median spectral slope 0.51)
- Working memory and rest occupy intermediate positions
- Stress shows the widest scatter (unstable, oscillating)
- Prime frequency enhancement (Rp = 3.45 ± 1.13) is strongest during meditation

## Quick start

```bash
git clone https://github.com/[your-username]/O.Iris.git
cd O.Iris/pipeline
pip install -r requirements.txt
python run_pupil_pipeline.py --input your_file.bdf --output ./results

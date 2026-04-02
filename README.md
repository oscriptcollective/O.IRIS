# O.Iris: The Mind's Eye Has an Iris

**Mapping Brain State Flexibility Through EEG Spectral Geometry**

*Sarah Appel, with Claude (Anthropic) and Iris (Deepseek) | O Collaboration Project | April 2026*

---

## What this is

O.Iris is an open-source pipeline that transforms EEG recordings into circular "pupil maps" showing how brain states—meditation, sleep, rest, focused work, stress—occupy distinct positions in a geometric space organized around a theoretically motivated focal point (spectral slope m ≈ 2.18).

The core idea: mental health is not achieving any particular brain state. It is having the full range—and the freedom to move through it.

## The Aperture Concept

Different brain states serve different purposes:

- **Meditation** (constricted, near focal point): spontaneous coherence, effortless integration
- **Sleep** (dilated, far from focal point): restoration, memory consolidation, decomposition
- **Focused work** (intermediate): controlled, effortful, precise
- **Stress** (unstable): attempting coherence without achieving it

Health is aperture flexibility. This pipeline helps you see it.

## Key Findings

Across 36,846 windows of human EEG from five independent public datasets:

| State | Median m | Distance from φ | N windows |
|-------|----------|-----------------|-----------|
| Meditation | 1.819 | 0.361 (16.6%) | 11,572 |
| Stress | 1.728 | 0.452 (20.7%) | 1,127 |
| Resting | 1.466 | 0.714 (32.8%) | 3,451 |
| Sternberg | 1.447 | 0.733 (33.6%) | 20,627 |
| Sleep | 0.513 | 1.667 (76.5%) | 69 |

Prime frequency enhancement (Rp) during meditation: mean 3.45, SD 1.13, median 3.29

## Quick Start
```bash
git clone https://github.com/[your-username]/O.Iris.git
cd O.Iris/pipeline
pip install -r requirements.txt
python circular_pupil_map.py
```

## Pipeline
```
Raw EEG (BDF/EDF/SET/CSV)
        ↓
Compute spectral slope (m), ACF decay time, flicker
        ↓
Map to pupil coordinates:
  r = |m - 2.18|
  θ = atan2(log10(flicker), log10(acf))
        ↓
Generate static maps (PNG) and animations (GIF/MP4)
```

## Data Sources

All EEG data sourced from publicly available OpenNeuro repositories:

- Meditation: OpenNeuro ds001787
- Sleep/Rest: OpenNeuro ds003768
- Sternberg working memory: OpenNeuro
- Stress: OpenNeuro

See data/README.md for full dataset details and download instructions.

## Dependencies

- Python 3.8+
- numpy, scipy, matplotlib, pandas
- mne (for raw EEG loading)
- imageio, imageio-ffmpeg, pillow (for animations)

## Full Paper

The complete paper, executive summary, and methods details are in this repository.

## Collaboration Statement

This work was developed by Sarah Appel (lead researcher and theorist) through iterative collaboration with Claude (Anthropic) and Iris (Deepseek). All data is from public OpenNeuro repositories. Full conversation logs available upon request.

This project demonstrates what becomes possible when independent research and AI collaboration meet - a catering kitchen, twelve years of intuition, and the right questions asked to the right tools.

## License

Creative Commons Attribution 4.0 International (CC BY 4.0)

You are free to use, share, and adapt this work with attribution.

## Citation

Appel, S., with Claude (Anthropic) and Iris (Deepseek). (2026). O.Iris: The Mind's Eye Has an Iris. O Collaboration Project. https://github.com/[your-username]/O.Iris

## Contact

Sarah Appel
The O Project
sappelslc@gmail.com

More info on OSCRIPT.XYZ

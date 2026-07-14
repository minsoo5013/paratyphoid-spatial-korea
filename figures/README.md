# Figures

Included files:

- `Figure1_period_maps.png` and `Figure1_caption.txt`
- `Figure2_moran_cases.png` and `Figure2_caption.txt`
- `Figure_1.tiff` and `Figure_2.tiff`, 600-dpi LZW-compressed TIFF files for journal submission
- `Figure1_data_used.csv`, the period-level values used in Figure 1
- `Figure1_period_maps.py` and `Figure2_moran_cases.py`, the final figure-generation scripts

Figure 1 requires administrative boundary files that are not redistributed in this
repository. To regenerate Figure 1, place `final.shp`, `final.shx`, and `final.dbf`
under `data/raw/` and run:

```bash
python figures/Figure1_period_maps.py
```

Figure 2 can be regenerated from included tabular results:

```bash
python figures/Figure2_moran_cases.py
```

Python dependencies for figure regeneration are `pandas`, `numpy`, `matplotlib`, and
`geopandas` for Figure 1.

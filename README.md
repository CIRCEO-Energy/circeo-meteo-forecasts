# circeo-meteo-forecasts

Archive of North-Atlantic forecasts (box 20-75°N, 80°W-15°E) published as GitHub Release assets:
ECMWF (IFS HRES, AIFS, IFS ENS, WAM waves; CC-BY-4.0), NOAA (GEFS reforecast and operational,
GFS-Wave; NOAA open data) and Copernicus Marine ocean forecasts. Code, conventions, licences and
the procedure: [CIRCEO-Energy/circeo-meteo](https://github.com/CIRCEO-Energy/circeo-meteo).
Truth data (ERA5, GLORYS12) live in that repository's Releases.

Workflows (they check out the circeo-meteo code): `build` (historical extraction), `daily`
(prospective archive, 09:17 UTC), `verify` (full-resolution ensemble statistics vs ERA5).

"""Orthographic globe geometry for the Pole A family.

The globe is viewed from above the equator (tilt), so the north pole sits on
the visible face and meridians converge toward it: two of them form the A.
"""
import math

class Globe:
    def __init__(self, cx=100, cy=100, r=72, tilt=26, lon0=0):
        self.cx, self.cy, self.r = cx, cy, r
        self.p0 = math.radians(tilt); self.l0 = math.radians(lon0)

    def xy(self, lat, lon):
        f, l = math.radians(lat), math.radians(lon) - self.l0
        x = self.r*math.cos(f)*math.sin(l)
        y = self.r*(math.cos(self.p0)*math.sin(f) - math.sin(self.p0)*math.cos(f)*math.cos(l))
        vis = math.sin(self.p0)*math.sin(f) + math.cos(self.p0)*math.cos(f)*math.cos(l)
        return self.cx + x, self.cy - y, vis

    def line(self, pts, want="front"):
        """Polyline through (lat, lon) samples, split where it crosses the limb."""
        segs, cur = [], []
        for lat, lon in pts:
            x, y, v = self.xy(lat, lon)
            ok = v >= -1e-9 if want == "front" else v < 0
            if ok: cur.append((x, y))
            elif cur: segs.append(cur); cur = []
        if cur: segs.append(cur)
        return "".join("M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in s) for s in segs if len(s) > 1)

    def meridian(self, lon, lat_a=90, lat_b=-90, want="front", step=1):
        n = max(2, int(abs(lat_a-lat_b)/step))
        return self.line([(lat_a + (lat_b-lat_a)*i/n, lon) for i in range(n+1)], want)

    def parallel(self, lat, lon_a=-180, lon_b=180, want="front", step=1):
        n = max(2, int(abs(lon_b-lon_a)/step))
        return self.line([(lat, lon_a + (lon_b-lon_a)*i/n) for i in range(n+1)], want)

    def graticule(self, dlon=20, dlat=20, want="front"):
        d = "".join(self.meridian(l, 90 - dlat*0 - 0.0001, -90, want) for l in range(-180, 180, dlon))
        d += "".join(self.parallel(f, -180, 180, want) for f in range(-90 + dlat, 90, dlat))
        return d

    def path(self, legs, want="front"):
        """legs: list of ('m', lon, lat_a, lat_b) or ('p', lat, lon_a, lon_b), joined into one stroke."""
        pts = []
        for kind, a, b, c in legs:
            n = max(2, int(abs(c-b)))
            seg = [((b + (c-b)*i/n), a) if kind == "m" else (a, b + (c-b)*i/n) for i in range(n+1)]
            pts += seg if not pts else seg[1:]
        return self.line(pts, want)

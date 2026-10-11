"""The titan Atlas as a bold silhouette, built from rounded limb strokes and filled shapes.
All poses are drawn on the 200 grid; the globe they carry is passed in by the caller."""

def limb(d, c, w):
    return f'<path d="{d}" fill="none" style="stroke:var(--{c})" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'

def blob(d, c):
    return f'<path d="{d}" style="fill:var(--{c})"/>'

def kneeling(c="sil", s=1.0):
    """Farnese pose, facing right: the sphere (centre 96,70, radius 44) rests on the upper back,
    the head is bowed in front of it, both arms reach up to steady it, the back knee is on the ground."""
    out = ""
    # far arm up the sphere's left side
    out += limb("M74 112C64 106 58 98 55 84", c, 10*s)
    # back leg: thigh to the knee on the ground, shin back, toes
    out += limb("M80 148L64 177", c, 15*s) + limb("M64 177L38 175", c, 11*s) + blob("M40 169C32 168 28 176 34 180H44Z", c)
    # front leg: thigh forward to the knee, shin down, foot
    out += limb("M88 148L116 157", c, 15*s) + limb("M116 157L118 181", c, 11*s) + blob("M112 176H132C138 176 138 184 132 184H112Z", c)
    # torso: the upper back follows the underside of the sphere
    out += blob("M64 102C78 114 100 118 122 112C126 124 116 142 100 154C90 160 76 158 72 148C66 134 60 118 64 102Z", c)
    # neck and bowed head
    out += limb("M112 118L126 128", c, 12*s)
    out += f'<ellipse cx="130" cy="130" rx="9.5" ry="10.5" transform="rotate(-30 130 130)" style="fill:var(--{c})"/>'
    # near arm up the sphere's right side
    out += limb("M114 114C128 112 138 104 139 84", c, 11*s)
    return out

def standing(c="sil", s=1.0):
    """Front view: legs apart like an A, arms raised, the sphere on the shoulders. Centre x=100."""
    w = 10*s
    out = ""
    out += limb("M96 150L78 182M104 150L122 182", c, w*1.15)
    out += blob("M70 178H84V184H68C66 184 66 179 70 178Z", c) + blob("M130 178H116V184H132C134 184 134 179 130 178Z", c)
    out += limb("M86 166H114", c, w*.55)
    out += blob("M80 122C92 116 108 116 120 122C118 134 110 146 105 153H95C90 146 82 134 80 122Z", c)
    out += limb("M84 124C74 120 68 112 66 100C65 94 65 90 66 86M116 124C126 120 132 112 134 100C135 94 135 90 134 86", c, w*.95)
    out += f'<ellipse cx="100" cy="112" rx="7.5" ry="8.5" style="fill:var(--{c})"/>'
    return out

def shoulders(c="sil"):
    """Bust for small sizes: broad shoulders, bowed head, elbows out and hands on the sphere's sides.
    Pair with a sphere centred (100, 74), radius 56."""
    return (blob("M28 204C28 168 54 148 100 148C146 148 172 168 172 204Z", c) +
            limb("M60 156C40 150 28 134 32 114C35 100 40 92 46 86M140 156C160 150 172 134 168 114C165 100 160 92 154 86", c, 17) +
            f'<ellipse cx="100" cy="142" rx="17" ry="18" style="fill:var(--{c})"/>')

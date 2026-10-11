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

# ---------------------------------------------------------------- detailed Farnese Atlas
# Faces right. The sphere it carries is centred (92, 60) with radius 46 and rests on the upper back.
FARNESE_PARTS = {
    "far_upper": "M96 106C86 100 74 95 63 91C55 89 49 97 54 103C62 109 76 115 90 119Z",
    "far_fore":  "M53 101C49 91 47 81 47 72L57 69C59 79 62 89 64 98C62 104 56 105 53 101Z",
    "far_hand":  "M44 74C41 67 43 61 49 60C55 60 58 64 57 70Z",
    "back_thigh": "M73 146C63 158 55 172 56 184C58 192 73 192 74 184C78 175 88 165 97 158Z",
    "back_shin":  "M64 179C53 181 43 180 35 177C28 177 27 189 34 189C46 190 58 191 68 190Z",
    "back_foot":  "M36 177C29 174 21 178 20 187L35 189Z",
    "torso": "M95 104C83 110 73 124 71 140C69 150 65 158 69 166C73 173 82 175 90 171C100 167 108 160 112 150C116 140 122 132 126 124C128 116 124 108 116 104C109 101 101 101 95 104Z",
    "neck": "M106 101C117 103 126 110 132 118L124 127C118 120 111 116 102 112Z",
    "front_thigh": "M84 154C98 143 116 135 131 133C143 132 147 147 138 152C124 158 106 167 92 173Z",
    "front_shin":  "M128 145C116 153 115 168 123 184H134C133 174 137 162 143 150Z",
    "front_foot":  "M121 182H143C150 182 152 190 146 190H120Z",
    "drape": "M70 150C80 156 96 158 110 152C109 160 103 166 96 168C88 170 80 169 74 164C70 160 69 155 70 150Z",
    "head": "M126 116C129 110 138 108 145 112C148 115 149 118 149 121L153 126L149 128C150 130 149 132 148 133C148 138 145 142 140 142C135 142 131 138 129 134C126 130 124 122 126 116Z",
    "near_upper": "M102 106C108 96 119 91 128 89C134 87 138 84 141 82C148 80 152 90 147 95C141 100 134 105 126 109C120 112 114 116 108 118Z",
    "near_fore":  "M139 87C137 78 134 70 131 63L140 59C144 66 149 76 151 90C150 95 143 95 139 87Z",
    "near_hand":  "M129 65C126 58 128 52 134 51C139 50 142 54 141 60Z",
}
ORDER = ["far_upper", "far_fore", "far_hand", "back_thigh", "back_shin", "back_foot", "torso", "neck",
         "front_thigh", "front_shin", "front_foot", "drape", "head", "near_upper", "near_fore", "near_hand"]
# parts in front of others get an incised outline, as black-figure painters did where dark overlaps dark
OUTLINED = ["front_thigh", "front_shin", "head", "near_upper", "near_fore", "near_hand"]

FARNESE_LINES = [
    "M95 109C86 117 78 130 75 146",              # spine
    "M92 114C87 120 85 127 87 134",              # shoulder blade
    "M108 120C102 126 98 132 97 138",            # latissimus
    "M113 128C117 134 116 142 112 148",          # flank
    "M118 112C122 116 123 122 121 128",          # pectoral
    "M114 96C118 100 120 104 119 110",           # deltoid
    "M126 104C133 100 139 96 144 92",            # biceps
    "M142 80C139 73 136 67 134 62",              # forearm
    "M66 97C72 102 80 107 88 110",               # far triceps
    "M54 94C53 86 52 79 52 72",                  # far forearm
    "M100 158C111 152 122 146 133 141",          # quadriceps
    "M114 158C120 156 126 152 132 148",          # vastus
    "M130 152C124 162 123 172 126 182",          # calf
    "M69 160C64 168 61 176 61 182",              # back thigh
    "M40 183C48 184 56 185 64 185",              # back shin
    "M78 156C84 161 91 163 100 161M86 162C92 166 98 166 104 163",                                   # drapery folds
    "M130 115C133 112 137 111 140 112M128 120C131 117 135 116 138 117M128 125C130 122 133 121 136 122",  # hair
    "M146 133C145 136 143 139 139 140M142 132C141 135 139 137 136 138M138 130C137 133 135 135 132 135",  # beard
    "M143 119C142 120 141 120 140 120",          # eye
    "M146 117C144 116 142 116 140 117",          # brow
    "M131 55L129 51M135 53L134 49M138 54L139 50",  # fingers
    "M46 64L44 60M50 62L49 58M54 63L55 59",
]

def farnese(c="sil", line="lit", detail=True):
    out = ""
    for k in ORDER:
        out += f'<path d="{FARNESE_PARTS[k]}" style="fill:var(--{c})"/>'
        if detail and k in OUTLINED:
            out += f'<path d="{FARNESE_PARTS[k]}" fill="none" style="stroke:var(--{line})" stroke-width="1.1" stroke-linejoin="round"/>'
    if detail:
        out += "".join(f'<path d="{d}" fill="none" style="stroke:var(--{line})" stroke-width=".9" stroke-linecap="round" opacity=".85"/>' for d in FARNESE_LINES)
    return out

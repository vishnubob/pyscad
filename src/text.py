from core import *
from primitives import *
from utils import bezier_curve, midpoint
from decimal import *
import logging
logger = logging.getLogger(__name__)

try:
    import freetype
    __all__ = ["Glyph", "Text"]
except ImportError:
    msg = "Could not import freetype, font support disabled"
    logger.warn(msg)
    __all__ = []

SET_FLAG = (1 << 0)
DROPOUT_FLAG = (1 << 2)
DROPOUT_MASK = (1 << 5) | (1 << 6) | (1 << 7)

__face_cache__ = {}

def get_face(fontfile):
    face = __face_cache__.get(fontfile, None)
    if not face:
        face = freetype.Face(fontfile)
        __face_cache__[fontfile] = face
    return face

def to_fixed_point(num, width):
    frac = int((2 ** width - 1) * (num % 1))
    return (int(num) << width) | frac

def from_fixed_point(num, width):
    mask = int((2 ** width - 1))
    frac = (num & mask) / float(mask)
    return (num >> width) + frac

class Glyph(SCAD_Object):
    Defaults = {
        "width": {"type": float, "default": 0},
        "height": {"type": float, "default": 0},
        "depth": {"type": float, "default": 0},
        "hres": {"type": int, "default": 0},
        "vres": {"type": int, "default": 0},
        "fontfile": {"type": str},
        "ch": {"type": str},
    }

    @property
    def face(self):
        face = get_face(self.fontfile)
        width = max(self.width, 1)
        height = (self.height or width)
        width = to_fixed_point(width, 6)
        height = to_fixed_point(height, 6)
        face.set_char_size(width, height)
        face.load_char(self.ch)
        return face
    
    @property
    def glyph(self):
        return self.face.glyph

    @property
    def outline(self):
        return self.face.glyph.outline
    
    @property
    def bbox(self):
        return self.outline.get_bbox()

    def process_contours(self):
        contours = []
        start = 0
        for contour_idx in self.outline.contours:
            end = contour_idx + 1
            content = zip(self.outline.tags[start:end], self.outline.points[start:end])
            content.reverse()
            start = end
            contours.append(self.process_contour(content))
        return contours
        
    def process_contour(self, content):
        lastcp = None
        contour = []
        while content:
            (tag, point) = content.pop()
            point = (from_fixed_point(point[0], 6), (from_fixed_point(point[1], 6)))
            if (tag & SET_FLAG):
                if lastcp:
                    contour[-1].extend([point])
                contour.append([point])
                lastcp = None
            else:
                if lastcp:
                    mp = midpoint(lastcp, point)
                    contour[-1].extend([mp])
                    contour.append([mp])
                contour[-1].extend([point])
                lastcp = point
            if (tag & DROPOUT_FLAG):
                dropout = DROPOUT_MASK & tag
        contour[-1].append(contour[0][0])
        return contour

    def outline_font(self, steps=10):
        points = []
        paths = []
        cnt = 0
        contours = self.process_contours()
        for contour in contours:
            path = []
            for segment in contour:
                cnt = len(points)
                if len(segment) <= 2:
                    points.extend(segment)
                    path.append(cnt)
                else:
                    curve = list(bezier_curve(segment, steps))
                    path.extend(range(cnt, cnt + len(curve)))
                    points.extend(curve)
            paths.append(path)
        return {"points": points, "paths": paths}
    
    def render_scad(self, *args, **kw):
        pgkw = self.outline_font()
        pg = Polygon(**pgkw)
        if self.depth:
            pg = LinearExtrude(height=self.depth)(pg)
        return pg.render_scad(*args, **kw)
    
    def get_char(self, ch):
        ns = self.__namespace__.copy()
        ns["ch"] = ch
        return self.__class__(**ns)
    
    @property
    def glyph_index(self):
        return self.face.get_name_index(self.ch)

    def kern(self, other):
        vec = self.face.get_kerning(self.ch, other.ch)
        return {'x': from_fixed_point(vec.x, 6), 'y': from_fixed_point(vec.y, 6)}
    
    @property
    def advance(self):
        return {'x': from_fixed_point(self.glyph.advance.x, 6), 'y': from_fixed_point(self.glyph.advance.y, 6)}

class Text(Glyph):
    Defaults = {
        "text": {"type": str},
        "glyph": {"type": Glyph},
        "kernflag": {"type": bool, "default": True}
    }

    def render_scad(self, *args, **kw):
        res = []
        xoffset = 0
        last_ch = None
        for ch in self.text:
            ch = self.glyph.get_char(ch)
            if last_ch and self.kernflag:
                xoffset += last_ch.kern(ch)["x"]
            last_ch = ch
            _ch = Translate(x=xoffset)(ch)
            res.append(_ch)
            xoffset += ch.advance["x"] - 10
        ret = Union()(res)
        return ret.render_scad(*args, **kw)


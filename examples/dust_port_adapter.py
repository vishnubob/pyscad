#!/usr/bin/env python
from scad import *

class DustPortAdapter(SCAD_Object):
    thickness = 2
    dustport_dia = inch2mm(2.25)
    dustport_od = dustport_dia
    #dustport_id = dustport_dia - thickness
    dustport_id = inch2mm(2.0625)
    vacuumport_dia = inch2mm(1.25)
    vacuumport_od = inch2mm(1.4375) + .5
    vacuumport_id = inch2mm(1.25)
    #vacuumport_od = vacuumport_dia + thickness
    #vacuumport_id = vacuumport_dia
    junction_length = inch2mm(1)
    dustport_length = inch2mm(1)
    vacuumport_length = inch2mm(1)
    collar_length = 4

    def _scad(self):
        dustport = Pipe(idia=self.dustport_id, odia=self.dustport_od, h=self.dustport_length, center=True)
        vacuumport = Pipe(idia=self.vacuumport_id, odia=self.vacuumport_od, h=self.vacuumport_length, center=True)
        junction = Pipe(idia1=self.vacuumport_id, odia1=self.vacuumport_od, idia2=self.dustport_id, odia2=self.dustport_od, h=self.junction_length, center=True)
        dustport = Translate(z=(self.dustport_length + self.junction_length) / 2.0)(dustport)
        vacuumport = Translate(z=(self.vacuumport_length + self.junction_length) / -2.0)(vacuumport)
        body = Union()(dustport, vacuumport, junction)
        return body

    def scad(self):
        dustport = Pipe(idia=self.dustport_id, odia=self.dustport_od, h=self.dustport_length, center=True)
        vacuumport = Pipe(idia=self.vacuumport_id, odia=self.dustport_od, h=self.vacuumport_length, center=True)
        vacuumport = Translate(z=(self.dustport_length - self.vacuumport_length) / -2.0)(vacuumport)
        collar = Pipe(idia=self.vacuumport_id, odia=self.dustport_od + 4, h=self.collar_length, center=True)
        collar = Translate(z=(self.dustport_length - self.collar_length) / -2.0)(collar)
        body = Union()(dustport, vacuumport, collar)
        return body


dpa = DustPortAdapter()
dpa = SCAD_Globals(fn=100)(dpa)
dpa.render("dustport_adapter.scad")
if not os.path.exists("dustport_adapter.stl"):
    dpa.render("dustport_adapter.stl")

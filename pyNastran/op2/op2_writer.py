#pylint: disable=W0201,C0301,C0111
from __future__ import (nested_scopes, generators, division, absolute_import,
                        print_function, unicode_literals)
from six import iteritems
import sys
import copy
from datetime import date
from collections import defaultdict
from struct import Struct, pack
import warnings

import pyNastran
from pyNastran.op2.op2_f06_common import OP2_F06_Common

def make_stamp(Title, today=None):
    if 'Title' is None:
        Title = ''

    #lenghts = [7, 8, 5, 5, 3, 4, 4, 6, 9, 7, 8, 8]
    months = [' January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    if today is None:
        today = date.today()
        str_month = months[today.month - 1].upper()
        str_today = '%-9s %2s, %4s' % (str_month, today.day, today.year)
    else:
        (month, day, year) = today
        str_month = months[month - 1].upper()
        str_today = '%-9s %2s, %4s' % (str_month, day, year)
    str_today = str_today  #.strip()

    release_date = '02/08/12'  # pyNastran.__releaseDate__
    release_date = ''
    build = 'pyNastran v%s %s' % (pyNastran.__version__, release_date)
    if Title is None:
        Title = ''
    out = '1    %-67s   %-19s %-22s PAGE %%5i\n' % (Title.strip(), str_today, build)
    return out


class OP2Writer(OP2_F06_Common):
    def __init__(self):
        OP2_F06_Common.__init__(self)
        self.card_count = {}

    def make_f06_header(self):
        """If this class is inherited, the F06 Header may be overwritten"""
        return make_f06_header()

    def make_stamp(self, Title, today):
        """If this class is inherited, the PAGE stamp may be overwritten"""
        return make_stamp(Title, today)

    def write_op2(self, op2_outname, is_mag_phase=False,
                  delete_objects=True):
        """
        Writes an OP2 file based on the data we have stored in the object

        :param self:         the F06 object
        :param op2_outname:  the name of the F06 file to write
        :param is_mag_phase: should complex data be written using Magnitude/Phase
                         instead of Real/Imaginary (default=False; Real/Imag)
                         Real objects don't use this parameter.
        :param delete_objects: should objects be deleted after they're written
                         to reduce memory (default=True)
        """
        if isinstance(op2_outname, str):
            op2 = open(op2_outname, 'wb')
            op2ascii = open(op2_outname+'.txt', 'wb')
        else:
            assert isinstance(op2_outname, file), 'type(op2_outname)= %s' % op2_outname
            op2 = op2_outname
            op2_outname = op2.name
            print('op2_outname =', op2_outname)

        data = [4, 2, 4]
        op2.write(pack('3i', *data))

        if self.grid_point_weight.reference_point is not None:
            if has_attr(result, 'write_op2'):
                print("grid_point_weight")
                self.grid_point_weight.write_op2(op2, page_stamp, self.page_num)
            else:
                print("*op2 - grid_point_weight not written")


        #is_mag_phase = False

        # eigenvalues are written first
        for ikey, result in sorted(iteritems(self.eigenvalues)):
            header
            #print('%-18s SUBCASE=%i' % (result.__class__.__name__, isubcase))
            if has_attr(result, 'write_op2'):
                result.write_op2(op2, op2ascii)
                if delete_objects:
                    del result
            else:
                print("*op2 - %s not written" % result.__class__.__name__)
                asdf

        # then eigenvectors
        # has a special header
        for isubcase, result in sorted(iteritems(self.eigenvectors)):
            (subtitle, label) = self.iSubcaseNameMap[isubcase]

            if hasattr(result, 'write_op2'):
                print('%-18s SUBCASE=%i' % (result.__class__.__name__, isubcase))
                result.write_op2(op2, op2ascii, is_mag_phase=is_mag_phase)
                if delete_objects:
                    del result
            else:
                print("*op2 - %s not written" % result.__class__.__name__)
                asdf

        # finally, we writte all the other tables
        # nastran puts the tables in order of the Case Control deck,
        # but we're lazy so we just hardcode the order

        # param,post,-2 ???
        data = [  #4, 0, 4,
                #4, 2, 4,
                #4, 0, 4,
                ]
        op2.write(Struct(b'%ii' % len(data)).pack(*data))

        #if markers == [3,]:  # PARAM, POST, -2
            #self.read_markers([3])
            #data = self.read_block()
            #self.read_markers([7])
            #data = self.read_block()
            ##self.show(100)
            #data = self._read_record()

        res_types = [
            self.accelerations,
            self.displacements, self.displacementsPSD, self.displacementsATO, self.displacementsRMS,
            self.scaledDisplacements,  # ???

            self.forceVectors,
            self.loadVectors,
            self.temperatures,
            self.velocities, #self.eigenvectors,

            self.mpcForces,
            self.spcForces,
            self.thermalLoadVectors,


            #------------------------------------------
            # OEF - forces

            # alphabetical order...
            # bars
            self.barForces,
            self.cbar_force,

            # beam
            self.beamForces,
            self.bar100Forces,
            self.bendForces,
            self.cbeam_force,

            # alphabetical
            self.celas1_force,
            self.celas2_force,
            self.celas3_force,
            self.celas4_force,

            self.conrod_force,
            self.cquad4_force,
            self.plateForces,   # centroidal elements
            self.plateForces2,  # bilinear elements

            self.crod_force,
            self.cshear_force,
            self.ctria3_force,
            self.ctube_force,

            # rods
            self.rodForces,

            # springs
            self.springForces,

            # dampers
            self.damperForces,

            # cshear,
            self.shearForces,
            # other
            self.bushForces, self.gapForces, self.solidPressureForces,

            #------------------------------------------
            # OES - strain
            # 1.  cbar
            # 2.  cbeam
            # 3.  crod/ctube/conrod

            # springs,
            self.celasStrain,
            self.celas1_strain,
            self.celas2_strain,
            self.celas3_strain,
            self.celas4_strain,

            # bars/beams
            self.barStrain, self.beamStrain,
            self.cbar_strain,
            self.cbeam_strain,

            # plates
            self.plateStrain,
            self.shearStrain,
            self.compositePlateStrain,
            self.cquad4_composite_strain,
            self.cquad8_composite_strain,
            self.cquadr_composite_strain,
            self.ctria3_composite_strain,
            self.ctria6_composite_strain,
            self.ctriar_composite_strain,

            self.nonlinearPlateStrain,
            self.ctriaxStrain, self.hyperelasticPlateStress,


            # solids
            self.solidStrain,

            # rods
            self.rodStrain, self.nonlinearRodStrain,  # non-vectorized


            self.celas1_strain,
            self.celas2_strain,
            self.celas3_strain,
            self.celas4_strain,

            self.chexa_strain,
            self.conrod_strain,
            self.cpenta_strain,
            self.cquad4_strain,
            self.cquad8_strain,
            self.cquadr_strain,
            self.crod_strain,
            self.cshear_strain,
            self.ctetra_strain,
            self.ctria3_strain,
            self.ctria6_strain,
            self.ctriar_strain,
            self.ctube_strain,

            # bush
            self.bushStrain,
            #------------------------------------------
            # cbars/cbeams
            self.barStress,
            self.beamStress,
            self.cbar_stress,
            self.cbeam_stress,

            # bush
            self.bushStress, self.bush1dStressStrain,

            self.celasStress,
            self.shearStress,
            self.plateStress,
            self.solidStress,

            # rods
            self.rodStress, self.nonlinearRodStress,


            # shear
            # OES - stress
            self.celas1_stress,
            self.celas2_stress,
            self.celas3_stress,
            self.celas4_stress,

            self.chexa_stress,
            self.conrod_stress,
            self.cpenta_stress,
            self.cquad4_stress,
            self.cquad8_stress,
            self.cquadr_stress,
            self.crod_stress,
            self.cshear_stress,
            self.ctetra_stress,
            self.ctria3_stress,
            self.ctria6_stress,
            self.ctriar_stress,
            self.ctube_stress,

            self.compositePlateStress,
            self.cquad4_composite_stress,
            self.cquad8_composite_stress,
            self.cquadr_composite_stress,
            self.ctria3_composite_stress,
            self.ctria6_composite_stress,
            self.ctriar_composite_stress,

            self.nonlinearPlateStress,
            self.ctriaxStress, self.hyperelasticPlateStrain,

            #------------------------------------------

            self.gridPointStresses, self.gridPointVolumeStresses, self.gridPointForces,
        ]

        isubcases = sorted(self.iSubcaseNameMap.keys())
        res_keys = isubcases
        for res_key in res_keys:
            isubcase = res_key
            title = self.Title
            (subtitle, label) = self.iSubcaseNameMap[isubcase]
            subtitle = subtitle.strip()
            label = label.strip()

            (subtitle, label) = self.iSubcaseNameMap[isubcase]
            label = label.strip()
            subtitle = subtitle.strip()

            res_length = 0


            for res_type in res_types:
                if isubcase in res_type:
                    result = res_type[isubcase]
                    if hasattr(result, 'write_op2'):
                        result.write_op2(op2, op2ascii)
                        res_length = max(len(result.__class__.__name__), res_length)
                        continue
                    else:
                        print("*op2 - %s not written" % result.__class__.__name__)

            if res_length == 0:
                return

            print("OP2:")
            res_format = '  %%-%is SUBCASE=%%i%%s' % res_length

            for res_type in res_types:
                #print("res_type ", res_type)
                if isubcase in res_type:
                    result = res_type[isubcase]
                    if hasattr(result, 'write_op2'):
                        element_name = ''
                        if hasattr(result, 'element_name'):
                            element_name = ' - ' + result.element_name

                        print(res_format % (result.__class__.__name__, isubcase, element_name))
                        result.write_op2(op2, op2ascii, is_mag_phase=False)
                    else:
                        print("*op2 - %s not written" % result.__class__.__name__)

        op2.close()

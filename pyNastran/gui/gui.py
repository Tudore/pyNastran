# -*- coding: utf-8 -*-
# pylint: disable=C0111
from __future__ import division, unicode_literals, print_function
#from six import string_types, iteritems
from six.moves import range

# standard library
import sys
import os.path
#import traceback
#import webbrowser
#webbrowser.open("http://xkcd.com/353/")

from PyQt4 import QtCore, QtGui

import pyNastran
from pyNastran.gui.utils import check_for_newer_version


window = None
check_for_newer_version(window, pop_msg=True)

print("Using PyQt4")
fmode = 1
#except ImportError:
    #try:
        #from PySide import QtCore, QtGui
        #print("Using PySide")
        #fmode = 2
    #except ImportError:
        #msg = 'Failed to import PySide or PyQt4'
        #raise ImportError(msg)
assert fmode in [1, 2]

# 3rd party
import vtk

# pyNastran
#from pyNastran.utils import print_bad_path
from pyNastran.gui.formats import (NastranIO, Cart3dIO, PanairIO, LaWGS_IO,
    STL_IO, TecplotIO, TetgenIO, Usm3dIO, Plot3d_io, ShabpIO, ADB_IO, FastIO,
    #is_nastran, is_cart3d, is_panair, is_lawgs,
    #is_shabp, is_stl, is_tecplot, is_tetgen, is_usm3d, is_plot3d, is_openvsp,
    #is_fast
    )
from pyNastran.gui.arg_handling import get_inputs
from pyNastran.gui.gui_common import GuiCommon2

try:
    pkg_path = sys._MEIPASS #@UndefinedVariable
    script_path = os.path.join(pkg_path, 'scripts')
    icon_path = os.path.join(pkg_path, 'icons')
except:
    pkg_path = pyNastran.__path__[0]
    script_path = os.path.join(pkg_path, 'gui', 'scripts')
    icon_path = os.path.join(pkg_path, 'gui', 'icons')

#print('script_path = %s' % script_path)
#print('icon_path = %s' % icon_path)

# tcolorpick.png and tabout.png trefresh.png icons on LGPL license, see
# http://openiconlibrary.sourceforge.net/gallery2/?./Icons/actions/color-picker-grey.png
# http://openiconlibrary.sourceforge.net/gallery2/?./Icons/actions/help-hint.png
# http://openiconlibrary.sourceforge.net/gallery2/?./Icons/actions/view-refresh-8.png


# kills the program when you hit Cntl+C from the command line
# doesn't save the current state as presumably there's been an error
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


class MainWindow(GuiCommon2, NastranIO, Cart3dIO, ShabpIO, PanairIO, LaWGS_IO, STL_IO,
                 TetgenIO, Usm3dIO, Plot3d_io, ADB_IO, FastIO):
    """
    glyphs
    http://www.itk.org/Wiki/VTK/Examples/Python/Visualization/ElevationBandsWithGlyphs

    list of VTK6 classes
    http://www.vtk.org/doc/nightly/html/annotated.html

    background grid
    http://www.vtk.org/Wiki/VTK/Examples/Python/Visualization/CubeAxesActor

    pick visible
    http://www.vtk.org/Wiki/VTK/Examples/Cxx/Filtering/ExtractVisibleCells

    plane projection
    http://www.igstk.org/Wiki/VTK/Examples/Cxx/SimpleOperations/ProjectPointPlane

    warping
    http://engronline.ee.memphis.edu/eece4731/djr_lec16.pdf

    banded filter
    http://www.igstk.org/Wiki/VTK/Examples/Cxx/VisualizationAlgorithms/BandedPolyDataContourFilter
    """
    def __init__(self, inputs):
        html_logging = True
        GuiCommon2.__init__(self, html_logging, inputs)

        NastranIO.__init__(self)
        Cart3dIO.__init__(self)
        PanairIO.__init__(self)
        ShabpIO.__init__(self)
        LaWGS_IO.__init__(self)
        STL_IO.__init__(self)
        TetgenIO.__init__(self)
        Usm3dIO.__init__(self)
        Plot3d_io.__init__(self)
        ADB_IO.__init__(self)
        FastIO.__init__(self)

        fmt_order = [
            'nastran', 'cart3d', 'panair', 'shabp', 'usm3d', 'openvsp', # results
            'lawgs', 'tetgen', 'stl', 'fast', #'plot3d',  # no results
        ]
        self.build_fmts(fmt_order, stop_on_failure=False)

        self.label_actors = {}
        self.label_ids = {}
        self.label_scale = 1.0 # in percent

        logo = os.path.join(icon_path, 'logo.png')
        self.set_logo(logo)
        self.set_script_path(script_path)
        self.set_icon_path(icon_path)

        self.setup_gui()
        self.setup_post(inputs)

    def create_cell_picker(self):
        # cell picker
        self.cell_picker = vtk.vtkCellPicker()
        self.node_picker = vtk.vtkPointPicker()
        #self.cell_picker.SetTolerance(0.0005)

    def mousePressEvent(self, ev):
        #print('press x,y = (%s, %s)' % (ev.x(), ev.y()))
        if self.is_pick:
            #self.___saveX = ev.x()
            #self.___saveY = ev.y()
            pass
        else:
            self.iren.mousePressEvent(ev)

    #def LeftButtonPressEvent(self, ev):
        #asfd

    def mouseReleaseEvent(self, ev):
        #print('release x,y = (%s, %s)' % (ev.x(), ev.y()))
        if self.is_pick:
            pass
        else:
            self.iren.mousePressEvent(ev)

    def init_cell_picker(self):
        self.is_pick = False

        self.vtk_interactor.SetPicker(self.cell_picker)
        def annotate_cell_picker(object, event):
            #self.log_command("annotate_cell_picker()")
            picker = self.cell_picker
            if picker.GetCellId() < 0:
                #self.picker_textActor.VisibilityOff()
                pass
            else:
                world_position = picker.GetPickPosition()
                cell_id = picker.GetCellId()
                #ds = picker.GetDataSet()
                #select_point = picker.GetSelectionPoint()
                self.log_command("annotate_cell_picker()")
                self.log_info("XYZ Global = %s" % str(world_position))
                #self.log_info("cell_id = %s" % cell_id)
                #self.log_info("data_set = %s" % ds)
                #self.log_info("selPt = %s" % str(select_point))

                #method = 'get_result_by_cell_id()' # self.modelType
                #print('pick_state =', self.pick_state)

                duplicate_key = None
                if self.is_centroidal:
                    if self.pick_state == 'centroidal':
                        duplicate_key = cell_id

                        if 0:
                            # We use vtkExtractUnstructuredGrid because we are interested in
                            # looking at just a few cells. We use cell clipping via cell id to
                            # extract the portion of the grid we are interested in.
                            extractGrid = vtk.vtkExtractUnstructuredGrid()
                            extractGrid.SetInputConnection(connect2.GetOutputPort())
                            extractGrid.CellClippingOn()
                            extractGrid.SetCellMinimum(0)
                            extractGrid.SetCellMaximum(23)

                            parison = vtk.vtkGeometryFilter()
                            parison.SetInputConnection(extractGrid.GetOutputPort())

                        result_name, result_value, xyz = self.get_result_by_cell_id(cell_id, world_position)
                        assert result_name in self.label_actors, result_name
                    else:
                        cell = self.grid.GetCell(cell_id)
                        # get_nastran_centroidal_pick_state_nodal_by_xyz_cell_id()
                        method = 'get_centroidal_%s_result_pick_state_%s_by_xyz_cell_id' % (self.format, self.pick_state)
                        if hasattr(self, method):
                            methodi = getattr(self, method)
                            methodi(world_position, cell_id)
                        else:
                            msg = "pick_state is set to 'nodal', but the result is 'centroidal'\n"
                            msg += '  cannot find: self.%s(xyz, cell_id)' % method
                            self.log_error(msg)
                        return
                else:
                    if self.pick_state == 'nodal':
                        result_name, result_value, node_id, xyz = self.get_result_by_xyz_cell_id(world_position, cell_id)
                        assert result_name in self.label_actors, result_name
                        assert not isinstance(xyz, int), xyz
                        duplicate_key = node_id
                    else:
                        method = 'get_nodal_%s_result_pick_state_%s_by_xyz_cell_id' % (self.format, self.pick_state)
                        if hasattr(self, method):
                            methodi = getattr(self, method)
                            methodi(world_position, cell_id)
                        else:
                            msg = "pick_state is set to 'centroidal', but the result is 'nodal'\n"
                            msg += '  cannot find: self.%s(xyz, cell_id)' % method
                            self.log_error(msg)
                        return

                #print('key=%s exists=%s' % (duplicate_key, duplicate_key in self.label_ids[result_name]))
                if duplicate_key is not None and duplicate_key in self.label_ids[result_name]:
                    return
                self.label_ids[result_name].add(duplicate_key)
                self.log_info("%s = %s" % (result_name, result_value))


                #x, y, z = world_position
                x, y, z = xyz
                text = '(%.3g, %.3g, %.3g); %s' % (x, y, z, result_value)
                text = str(result_value)
                assert result_name in self.label_actors, result_name
                self._create_annotation(text, result_name, x, y, z)

        def annotate_point_picker(object, event):
            self.log_command("annotate_point_picker()")
            picker = self.cell_picker
            if picker.GetPointId() < 0:
                #self.picker_textActor.VisibilityOff()
                pass
            else:
                world_position = picker.GetPickPosition()
                point_id = picker.GetPointId()
                #ds = picker.GetDataSet()
                select_point = picker.GetSelectionPoint()
                self.log_command("annotate_picker()")
                self.log_info("world_position = %s" % str(world_position))
                self.log_info("point_id = %s" % point_id)
                #self.log_info("data_set = %s" % ds)
                self.log_info("select_point = %s" % str(select_point))

                #self.picker_textMapper.SetInput("(%.6f, %.6f, %.6f)"% pickPos)
                #self.picker_textActor.SetPosition(select_point[:2])
                #self.picker_textActor.VisibilityOn()

        self.cell_picker.AddObserver("EndPickEvent", annotate_cell_picker)
        self.node_picker.AddObserver("EndPickEvent", annotate_point_picker)

        #self.cell_picker.AddObserver("EndPickEvent", on_cell_picker)
        #self.node_picker.AddObserver("EndPickEvent", on_node_picker)

    def _create_annotation(self, text, result_name, x, y, z):
        assert isinstance(result_name, str), result_name
        # http://nullege.com/codes/show/src%40p%40y%40pymatgen-2.9.6%40pymatgen%40vis%40structure_vtk.py/395/vtk.vtkVectorText/python
        if 1:
            source = vtk.vtkVectorText()
            source.SetText(text)

            # mappers are weird; they seem to do nothing
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(source.GetOutputPort())

            # the follower lets us set the position/size/color
            follower = vtk.vtkFollower()
            follower.SetMapper(mapper)
            follower.SetPosition((x, y, z))

            # 1 point = 1/72"
            # SetScale works on model scale size
            #follower.SetScale(0.5)
            follower.SetScale(self.dim_max * 0.01 * self.label_scale)

            prop = follower.GetProperty()
            prop.SetColor(self.label_col)
            #prop.SetOpacity( 0.3 );

            # we need to make sure the text rotates when the camera is changed
            camera = self.rend.GetActiveCamera()
            follower.SetCamera(camera)
        else:
            # Create a text mapper and actor to display the results of picking.
            textMapper = vtk.vtkTextMapper()
            textMapper.SetInput(text)

            tprop = textMapper.GetTextProperty()
            tprop.SetFontFamilyToArial()
            tprop.SetFontSize(10)
            tprop.BoldOn()
            tprop.ShadowOn()
            tprop.SetColor(self.label_col)

            textActor = vtk.vtkActor2D()
            textActor.GetPositionCoordinate().SetCoordinateSystemToWorld()
            textActor.SetPosition(world_position[:2])
            textActor.SetMapper(textMapper)
            follower = textActor

        # finish adding the actor
        self.rend.AddActor(follower)
        self.label_actors[result_name].append(follower)

        #self.picker_textMapper.SetInput("(%.6f, %.6f, %.6f)"% pickPos)
        #camera.GetPosition()
        #camera.GetClippingRange()
        #camera.GetFocalPoint()

    def _on_cell_picker(self, a):
        self.vtk_interactor.SetPicker(self.cell_picker)
        picker = self.cell_picker
        world_position = picker.GetPickPosition()
        cell_id = picker.GetCellId()
        select_point = picker.GetSelectionPoint()  # get x,y pixel coordinate

        self.log_info("world_position = %s" % str(world_position))
        self.log_info("cell_id = %s" % cell_id)
        self.log_info("select_point = %s" % str(select_point))

    def _on_node_picker(self, a):
        self.vtk_interactor.SetPicker(self.node_picker)
        picker = self.node_picker
        world_position = picker.GetPickPosition()
        node_id = picker.GetPointId()
        select_point = picker.GetSelectionPoint()  # get x,y pixel coordinate

        self.log_info("world_position = %s" % str(world_position))
        self.log_info("node_id = %s" % node_id)
        self.log_info("select_point = %s" % str(select_point))

    #def on_cell_picker(self):
        #self.log_command("on_cell_picker()")
        #picker = self.cell_picker
        #world_position = picker.GetPickPosition()
        #cell_id = picker.GetCellId()
        ##ds = picker.GetDataSet()
        #select_point = picker.GetSelectionPoint()  # get x,y pixel coordinate

        #self.log_info("world_position = %s" % str(world_position))
        #self.log_info("cell_id = %s" % cell_id)
        #self.log_info("select_point = %s" % str(select_point))
        #self.log_info("data_set = %s" % ds)

    def about_dialog(self):
        """ Display about dialog """
        if fmode == 1:  # PyQt
            copyright = pyNastran.__pyqt_copyright__
        else:
            copyright = pyNastran.__copyright__

        about = [
            'pyNastran QT GUI',
            '',
            'pyNastran v%s' % pyNastran.__version__,
            copyright,
            pyNastran.__author__,
            '',
            '%s' % pyNastran.__website__,
            '',
            'Mouse',
            'Left Click - Rotate',
            'Middle Click - Pan/Recenter Rotation Point',
            'Shift + Left Click - Pan/Recenter Rotation Point',
            'Right Mouse / Wheel - Zoom',
            '',
            'Keyboard Controls',
            #'r   - reset camera view',
            #'X/x - snap to x axis',
            #'Y/y - snap to y axis',
            #'Z/z - snap to z axis',
            #'',
            #'h   - show/hide legend & info',
            'CTRL+I - take a screenshot (image)',
            'CTRL+L - cycle results',
            #'m/M    - scale up/scale down by 1.1 times',
            #'o/O    - rotate counter-clockwise/clockwise 5 degrees',
            'p      - pick node/element',
            's      - view model as a surface',
            'w      - view model as a wireframe',
            '',
            'Reload Model:  using the same filename reload the model',
        ]
        QtGui.QMessageBox.about(self, "About pyNastran GUI", "\n".join(about))

    def on_reload(self):
        """
        Runs the reload button.

        Reload allows you to edit the input model and "reload" the data without
        having to go to the pulldown menu.  For USM3D, we dynamically load the
        latest CFD results time step, which is really handy when you're running
        a job.
        """
        Title = self.Title
        if self.format == 'usm3d':
            self.step_results_usm3d()
        else:
            self.on_load_geometry(self.infile_name, self.format)

        if self.out_filename is None:
            msg = '%s - %s' % (self.format, self.infile_name)
        else:
            msg = '%s - %s - %s' % (self.format, self.infile_name, self.out_filename)
        self.set_window_title(msg)
        self.log_command('on_reload()')
        #self.cycleResults(Title)
        for i in range(10):  #  limit on number of cycles
            if self.Title != Title:
                self.cycleResults(Title)
            else:
                break

    def closeEvent(self, event):
        """
        Handling saving state before application when application is
        being closed.
        """
        settings = QtCore.QSettings()
        settings.setValue("main_WindowGeometry", self.saveGeometry())
        settings.setValue("mainWindowState", self.saveState())
        settings.setValue("backgroundColor", self.background_col)
        settings.setValue("textColor", self.text_col)
        settings.setValue("labelColor", self.label_col)
        QtGui.qApp.quit()


def main():
    app = QtGui.QApplication(sys.argv)

    QtGui.QApplication.setOrganizationName("pyNastran")
    QtGui.QApplication.setOrganizationDomain(pyNastran.__website__)
    QtGui.QApplication.setApplicationName("pyNastran")
    QtGui.QApplication.setApplicationVersion(pyNastran.__version__)

    inputs = get_inputs()
    window = MainWindow(inputs)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

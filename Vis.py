import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import time
from htm.bindings.sdr import SDR
from htm.bindings.engine_internal import Region
import threading

# Colors for glColor3f
BLACK   = (0.0, 0.0, 0.0)
WHITE   = (1.0, 1.0, 1.0)
RED     = (1.0, 0.0, 0.0)
GREEN   = (0.0, 1.0, 0.0)
BLUE    = (0.0, 0.0, 1.0)
YELLOW  = (1.0, 1.0, 0.0)
MAGENTA = (1.0, 0.0, 1.0)
CYAN    = (0.0, 1.0, 1.0)
GREY    = (0.1, 0.1, 0.1)

INACTIVE        = GREY
ACTIVE          = YELLOW
PREDICTED_TRUE  = CYAN
PREDICTED_FALSE = RED


class Vis:
    def __init__(self):
        # Define the size of the window and the size of the pixel map
        self.grid_line_width = .2
        self.tmRegion = None
        self.spRegion = None
        self.encRegions = []

        # Initialize OpenGL
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
        self.glthread = threading.Thread( target = glutMainLoop)


        # Create the window
        # glutInitWindowSize(self.window_size[0], self.window_size[1])
        glutCreateWindow("HTM Network Weights")

        # Set the idle function to update the weights and redraw the pixel map
        glutIdleFunc(self.update)

        # Set the display function
        glutDisplayFunc(self.display)

    def setRegionData(self, encs, sp, tm):
        self.encRegions = encs
        self.spRegion   = sp
        self.tmRegion   = tm

    # Define the OpenGL display function
    def display(self):
        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT)

        # Set the projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        gluOrtho2D(0, 1, 0, 1)

        # Set the modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        window_width = glutGet(GLUT_WINDOW_WIDTH)

        num_points_wide = self.encRegions[0].getParameterUInt32("size")
        num_points_tall = 1

        pixel_size = window_width / (num_points_wide + (num_points_wide * self.grid_line_width))
        # pixel_size = window_width / (num_points_wide )
        glPointSize(pixel_size)


        viewport_width = window_width
        viewport_height = pixel_size + (pixel_size * self.grid_line_width)
        viewport_y = 0

        # Draw the pixel maps for each encoder region
        if len(self.encRegions) != 0:
            num_viewports = len(self.encRegions)
            for i, encRegion in enumerate(self.encRegions):
                sdr = encRegion.getOutputArray("encoded").getSDR()
                viewport_y = i * viewport_height
                glViewport(0, int(viewport_y), viewport_width, int(viewport_height))
                glBegin(GL_POINTS)
                for j, bit in enumerate(sdr.dense):
                    if bit == 1:
                        glColor3f(*ACTIVE)
                    else:
                        glColor3f(*INACTIVE)
                    glVertex2f((j+.5)/num_points_wide, (.5)/num_points_tall)
                glEnd()

        if self.tmRegion != None:
            viewport_y += viewport_height
            # Draw the TMRegion output as a matrix with colors representing cell state
            active_cells_sdr = self.tmRegion.getOutputArray("activeCells").getSDR().dense
            predicted_active_cells_sdr = self.tmRegion.getOutputArray("predictedActiveCells").getSDR().dense
            predicted_cells_sdr = self.tmRegion.getOutputArray("predictiveCells").getSDR().dense
            num_points_tall = predicted_cells_sdr.shape[1]
            # print(active_cells_sdr)
            # Transpose the arrays
            active_cells_sdr = np.transpose(active_cells_sdr)
            predicted_active_cells_sdr = np.transpose(predicted_active_cells_sdr)
            glViewport(0, int(viewport_y), viewport_width, int(predicted_cells_sdr.shape[1] * pixel_size * (1 + self.grid_line_width)))
            glBegin(GL_POINTS)
            for i in range(predicted_cells_sdr.shape[0]):
                for j in range(predicted_cells_sdr.shape[1]):
                    if predicted_cells_sdr[i][j] > 0:

                        if predicted_active_cells_sdr[i][j] > 0:

                            glColor3f(*PREDICTED_TRUE)
                            print("true")

                        else:

                            glColor3f(*PREDICTED_FALSE)

                    elif active_cells_sdr[i][j] == 1:

                        glColor3f(*ACTIVE)
                    else:
                        glColor3f(*INACTIVE)

                    glVertex2f(((i+.5)/num_points_wide), (j+.5)/num_points_tall)


            glEnd()

        # Swap buffers
        glutSwapBuffers()


    # Define a function to update
    def update(self):
        glutPostRedisplay()

    def run(self):
        # Enter the main loop in the background
        print("Starting HTMVis thread")
        self.glthread.start()

    def stop(self):
        # Leave the main loop
        glutLeaveMainLoop()
        # Catch the thread
        self.glthread.join()




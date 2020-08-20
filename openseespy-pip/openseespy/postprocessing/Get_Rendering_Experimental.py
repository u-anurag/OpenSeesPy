##########################################################################################
##                                                                                  	##
##	Experimental functions that  being tested   										##
##																						##
##																						##
##																						##
##																						##
##																						##
##																						##
## Created By - Anurag Upadhyay, University of Utah. https://github.com/u-anurag		##
##            - Christian Slotboom, University of British Columbia.                     ##
##              https://github.com/cslotboom	                                        ##
## 																						##
##########################################################################################

# Check if the script is executed on Jupyter Notebook Ipython. 
# If yes, force inline, interactive backend for Matplotlib.
import sys
import os
import matplotlib

for line in range(0,len(sys.argv)):
    if "ipykernel_launcher.py" in sys.argv[line]:
        matplotlib.use('nbagg')
        break
    else:
        pass

from mpl_toolkits.mplot3d import Axes3D
from math import asin
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.animation as animation
from matplotlib.widgets import Slider


import openseespy.postprocessing.internal_database_functions as opp
import openseespy.postprocessing.internal_database_functions as idbf
import openseespy.postprocessing.internal_plotting_functions as ipltf
import openseespy.opensees as ops




   
class plot_deformedshape_Events:
    
    def __init__(self, Model="none", LoadCase="none", tstep = -1, scale = 10, overlap='no', monitorEleTags = [], monitorOutFile = "none"):
        self.Model = Model
        self.LoadCase = LoadCase
        self.tstep = tstep
        self.scale = scale
        self.overlap = overlap
        
        self.timeSteps, self.Disp_nodeArray = idbf._readNodeDispData(self.Model, self.LoadCase)
        self.nodeArray, self.elementArray = idbf._readNodesandElements(self.Model)

        self.monitorEleTags = monitorEleTags
        self.monitorOutFile = monitorOutFile
        self._plot()

    def _plot_on_click(self, event):
        
        timeSteps = self.timeSteps
        Disp_nodeArray =  self.Disp_nodeArray
        DeflectedNodeCoordArray = self.DeflectedNodeCoordArray
        
        # Find the Node ID
        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        ind = event.ind[0]
        fig, ax = plt.subplots()
        line = ax.plot(timeSteps, self.scale*Disp_nodeArray[:,ind,0])
        ax.set_xlabel('time (s)')
        ax.set_ylabel('Displacement')

    def _plot(self):
        """
        Command: plot_deformedshape(Model="modelName", LoadCase="loadCase name", <tstep = time (float)>, <scale = scaleFactor (float)>, <overlap='yes'>)
           	
        Keyword arguments are used to make the command clear.
           	
        Model   : Name of the model used in createODB() to read the displacement data from.
        LoadCase: Name of the load case used in createODB().
        tstep   : Optional value of the time stamp in the dynamic analysis. If no specific value is provided, the last step is used.
        scale   : Optional input to change the scale factor of the deformed shape. Default is 10.
        overlap : Optional input to plot the deformed shape overlapped with the wire frame of the original shape.
           	
        Future Work: Add option to plot deformed shape based on "time" and "step number" separately.
           	
        """

        if self.Model == "none" or self.LoadCase=="none":
            print("No output database specified to plot the deformed shape.")
            print("Command should be plot_deformedshape(Model='modelname',loadCase='loadcase',<tstep=time>,<scale=int>)")
            print("Not plotting deformed shape. Exiting now.")
            raise Exception('No model or output database specified.')

        print("Reading displacement data from "+str(self.Model)+"_ODB/"+self.LoadCase)
        nodeArray  = self.nodeArray
        elementArray = self.elementArray
        timeSteps = self.timeSteps
        Disp_nodeArray = self.Disp_nodeArray
        
        if self.tstep == -1:
            jj = len(timeSteps)-1
            printLine = "Final deformed shape"
        else:
            jj = (np.abs(timeSteps - self.tstep)).argmin()			# index closest to the time step requested.
            if timeSteps[-1] < self.tstep:
                print("XX Warining: Time-Step has exceeded maximum analysis time step XX")
            printLine = "Deformation at time: " + str(round(timeSteps[jj], 2))
  		
            
          
            
        DeflectedNodeCoordArray = nodeArray[:,1:]+ self.scale*Disp_nodeArray[int(jj),:,:]
        self.DeflectedNodeCoordArray = DeflectedNodeCoordArray
        nodetags = nodeArray[:,0]
  		
        show_element_tags = 'no'			# Set show tags to "no" to plot deformed shapes.
  
  		
        def nodecoords(nodetag):
            # Returns an array of node coordinates: works like nodeCoord() in opensees.
            i, = np.where(nodeArray[:,0] == float(nodetag))
            return nodeArray[int(i),1:]
  
          # TODO C: Can we just return DeflectedNodeCoordArray here instead of summing?
        def nodecoordsFinal(nodetag):
            # Returns an array of final deformed node coordinates
            i, = np.where(nodeArray[:,0] == float(nodetag))				# Original coordinates
            return nodeArray[int(i),1:] + self.scale*Disp_nodeArray[int(jj),int(i),:]
        
        fig = plt.figure()
  		# Check if the model is 2D or 3D
        if len(nodecoords(nodetags[0])) == 2:
            print('2D model')
            
            ax = fig.add_subplot(1,1,1)
            plt.plot(DeflectedNodeCoordArray[:,0], DeflectedNodeCoordArray[:,1], 'o', picker=2)
            for ele in elementArray:
                eleTag = int(ele[0])
                Nodes =ele[1:]
  				
                if len(Nodes) == 2:
                    # 3D beam-column elements
                    iNode = nodecoords(Nodes[0])
                    jNode = nodecoords(Nodes[1])
  					
                    iNode_final = nodecoordsFinal(Nodes[0])
                    jNode_final = nodecoordsFinal(Nodes[1])
  					
                    if self.overlap == "yes":
                        ipltf._plotBeam2D(iNode, jNode, ax, show_element_tags, eleTag, "wire")
  					
                    ipltf._plotBeam2D(iNode_final, jNode_final, ax, show_element_tags, eleTag, "solid")
  					
                if len(Nodes) == 3:
  					## 2D Planer three-node shell elements
                    iNode = nodecoords(Nodes[0])
                    jNode = nodecoords(Nodes[1])
                    kNode = nodecoords(Nodes[2])
  					
                    iNode_final = nodecoordsFinal(Nodes[0])
                    jNode_final = nodecoordsFinal(Nodes[1])
                    kNode_final = nodecoordsFinal(Nodes[2])
  
                    if self.overlap == "yes":
                        ipltf._plotTri2D(iNode, jNode, kNode, iNode, ax, show_element_tags, eleTag, "wire", fillSurface='no')
  					
                    ipltf._plotTri2D(iNode_final, jNode_final, kNode_final, iNode_final, ax, show_element_tags, eleTag, "solid", fillSurface='yes')
  					
                if len(Nodes) == 4:
                    ## 2D four-node Quad/shell element
                    iNode = nodecoords(Nodes[0])
                    jNode = nodecoords(Nodes[1])
                    kNode = nodecoords(Nodes[2])
                    lNode = nodecoords(Nodes[3])
  					
                    iNode_final = nodecoordsFinal(Nodes[0])
                    jNode_final = nodecoordsFinal(Nodes[1])
                    kNode_final = nodecoordsFinal(Nodes[2])
                    lNode_final = nodecoordsFinal(Nodes[3])
  					
                    if self.overlap == "yes":
                        ipltf._plotQuad2D(iNode, jNode, kNode, lNode, ax, show_element_tags, eleTag, "wire", fillSurface='no')
  						
                        ipltf._plotQuad2D(iNode_final, jNode_final, kNode_final, lNode_final, ax, show_element_tags, eleTag, "solid", fillSurface='yes')
  					            
            ax.text(0.1, 0.90, printLine, transform=ax.transAxes)
  		
        else:
            print('3D model')
            ax = fig.add_subplot(1,1,1, projection='3d')
            plt.plot(DeflectedNodeCoordArray[:,0], DeflectedNodeCoordArray[:,1], DeflectedNodeCoordArray[:,2], 'o', picker=2)
            for ele in elementArray:
                eleTag = int(ele[0])
                Nodes =ele[1:]
  				
                if len(Nodes) == 2:
                    ## 3D beam-column elements
                    iNode = nodecoords(Nodes[0])
                    jNode = nodecoords(Nodes[1])
  					
                    iNode_final = nodecoordsFinal(Nodes[0])
                    jNode_final = nodecoordsFinal(Nodes[1])
  					
                    if self.overlap == "yes":
                        ipltf._plotBeam3D(iNode, jNode, ax, show_element_tags, eleTag, "wire")
  					
                    ipltf._plotBeam3D(iNode_final, jNode_final, ax, show_element_tags, eleTag, "solid")
  					
                if len(Nodes) == 4:
  					## 3D four-node Quad/shell element
                    iNode = nodecoords(Nodes[0])
                    jNode = nodecoords(Nodes[1])
                    kNode = nodecoords(Nodes[2])
                    lNode = nodecoords(Nodes[3])
  					
                    iNode_final = nodecoordsFinal(Nodes[0])
                    jNode_final = nodecoordsFinal(Nodes[1])
                    kNode_final = nodecoordsFinal(Nodes[2])
                    lNode_final = nodecoordsFinal(Nodes[3])
  					
                    if self.overlap == "yes":
                        ipltf._plotQuad3D(iNode, jNode, kNode, lNode, ax, show_element_tags, eleTag, "wire", fillSurface='no')
  						
                    ipltf._plotQuad3D(iNode_final, jNode_final, kNode_final, lNode_final, ax, show_element_tags, eleTag, "solid", fillSurface='yes')
  
                if len(Nodes) == 8:
  					## 3D eight-node Brick element
  					## Nodes in CCW on bottom (0-3) and top (4-7) faces resp
                    iNode = nodecoords(Nodes[0])
                    jNode = nodecoords(Nodes[1])
                    kNode = nodecoords(Nodes[2])
                    lNode = nodecoords(Nodes[3])
                    iiNode = nodecoords(Nodes[4])
                    jjNode = nodecoords(Nodes[5])
                    kkNode = nodecoords(Nodes[6])
                    llNode = nodecoords(Nodes[7])
  					
                    iNode_final = nodecoordsFinal(Nodes[0])
                    jNode_final = nodecoordsFinal(Nodes[1])
                    kNode_final = nodecoordsFinal(Nodes[2])
                    lNode_final = nodecoordsFinal(Nodes[3])
                    iiNode_final = nodecoordsFinal(Nodes[4])
                    jjNode_final = nodecoordsFinal(Nodes[5])
                    kkNode_final = nodecoordsFinal(Nodes[6])
                    llNode_final = nodecoordsFinal(Nodes[7])
  					
                    if self.overlap == "yes":
                        ipltf._plotCubeVol(iNode, jNode, kNode, lNode, iiNode, jjNode, kkNode, llNode, ax, show_element_tags, eleTag, "wire", fillSurface='no') # plot undeformed shape
  
                    ipltf._plotCubeVol(iNode_final, jNode_final, kNode_final, lNode_final, iiNode_final, jjNode_final, kkNode_final, llNode_final, 
  									ax, show_element_tags, eleTag, "solid", fillSurface='yes')
  									
            ax.text2D(0.1, 0.90, printLine, transform=ax.transAxes)

        ipltf._setStandardViewport(fig, ax, DeflectedNodeCoordArray, len(nodecoords(nodetags[0])))					
        plt.axis('on')
        
        
        
        fig.canvas.mpl_connect('pick_event', self._plot_on_click)
        plt.show()
        return fig, ax


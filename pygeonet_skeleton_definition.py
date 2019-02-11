import numpy as np
from time import clock
from pygeonet_rasterio import *
from pygeonet_plot import *


# Skeleton by thresholding one grid measure e.g. flow or curvature
def compute_skeleton_by_single_threshold(inputArray, threshold):
    skeletonArray = np.zeros((inputArray.shape))
    skeletonArray[np.where(inputArray > threshold)] = 1
    return skeletonArray

# Skeleton by thresholding two grid measures e.g. flow and curvature
def compute_skeleton_by_dual_threshold(inputArray1, inputArray2, threshold1, threshold2):
    skeletonArray = np.zeros((inputArray1.shape))
    mask1 = np.where(inputArray1> threshold1,1,False)
    mask2 = np.where(inputArray2>threshold2,1,False)
    skeletonArray= mask1*mask2
    return skeletonArray

def main():
    outfilepath = Parameters.geonetResultsDir
    demName = Parameters.demFileName
    curvature_filename = demName.split('.')[0]+'_curvature.tif'
    fac_filename = demName.split('.')[0] + '_fac.tif'
    thresholdCurvatureQQxx = 1
##    outlets = [[2, 4, 9], [27, 26, 23]]
    filteredDemArray = read_geotif_filteredDEM()
    curvatureDemArray = read_geotif_generic(outfilepath, curvature_filename)
    finiteCurvatureDemList = curvatureDemArray[np.isfinite(curvatureDemArray[:])]
    curvatureDemMean = np.nanmean(finiteCurvatureDemList)
    curvatureDemStdDevn = np.nanstd(finiteCurvatureDemList)
    print 'Curvature mean: ', curvatureDemMean
    print 'Curvature standard deviation: ', curvatureDemStdDevn
    flowArray = read_geotif_generic(outfilepath, fac_filename)
    flowArray[np.isnan(filteredDemArray)]=np.nan
    flowMean = np.mean(flowArray[~np.isnan(flowArray[:])])
    print 'Mean upstream flow: ', flowMean
    # Define a skeleton based on flow alone
    skeletonFromFlowArray = \
    compute_skeleton_by_single_threshold(flowArray,\
                                         defaults.flowThresholdForSkeleton)    
    # Define a skeleton based on curvature alone
    skeletonFromCurvatureArray =\
    compute_skeleton_by_single_threshold(curvatureDemArray,\
                                         curvatureDemMean+
                                         thresholdCurvatureQQxx*curvatureDemStdDevn)
    # Writing the skeletonFromCurvatureArray array
    outfilename = demName.split('.')[0]+'_curvatureskeleton.tif'
    write_geotif_generic(skeletonFromCurvatureArray,\
                         outfilepath, outfilename)
    
    # Define a skeleton based on curvature and flow
    skeletonFromFlowAndCurvatureArray =\
    compute_skeleton_by_dual_threshold(curvatureDemArray, flowArray, \
                                       curvatureDemMean+thresholdCurvatureQQxx*curvatureDemStdDevn, \
                                       defaults.flowThresholdForSkeleton)
    # Writing the skeletonFromFlowAndCurvatureArray array
    outfilename = demName.split('.')[0]+'_skeleton.tif'
    write_geotif_generic(skeletonFromFlowAndCurvatureArray,\
                         outfilepath,outfilename)
    # plotting only for testing purposes
    try:
        if defaults.doPlot == 1:
            raster_point_plot(skeletonFromFlowAndCurvatureArray,outlets,
                              'Skeleton with outlets',cm.binary)
    except NameError:
        pass

if __name__ == '__main__':
    t0 = clock()
    main()
    t1 = clock()
    print "time taken to complete skeleton definition:", t1-t0, " seconds"


    

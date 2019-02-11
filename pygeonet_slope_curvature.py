import numpy as np
from scipy import stats
from time import clock
import statsmodels.api as sm
import matplotlib.pyplot as plt
from pygeonet_rasterio import *
from pygeonet_plot import *

def compute_dem_slope(filteredDemArray, pixelDemScale):
    slopeXArray,slopeYArray = np.gradient(filteredDemArray, pixelDemScale)
    slopeDemArray = np.sqrt(slopeXArray**2 + slopeYArray**2)
    slopeMagnitudeDemArrayQ = slopeDemArray
    slopeMagnitudeDemArrayQ = np.reshape(slopeMagnitudeDemArrayQ,
                                         np.size(slopeMagnitudeDemArrayQ))
    slopeMagnitudeDemArrayQ = slopeMagnitudeDemArrayQ[~np.isnan(slopeMagnitudeDemArrayQ)]
    # Computation of statistics of slope
    print ' slope statistics'
    print ' angle min:', np.arctan(np.percentile(slopeMagnitudeDemArrayQ,0.1))*180/np.pi
    print ' angle max:', np.arctan(np.percentile(slopeMagnitudeDemArrayQ,99.9))*180/np.pi
    print ' mean slope:', np.nanmean(slopeDemArray[:])
    print ' stdev slope:', np.nanstd(slopeDemArray[:])
    return slopeDemArray

    
def compute_dem_curvature(demArray, pixelDemScale, curvatureCalcMethod):
    gradXArray, gradYArray = np.gradient(demArray, pixelDemScale)
    slopeArrayT = np.sqrt(gradXArray**2 + gradYArray**2)
    if curvatureCalcMethod == 'geometric':
        #Geometric curvature
        print ' using geometric curvature'
        gradXArrayT = np.divide(gradXArray,slopeArrayT)
        gradYArrayT = np.divide(gradYArray,slopeArrayT)
    elif curvatureCalcMethod=='laplacian':
        # do nothing..
        print ' using laplacian curvature'
        gradXArrayT = gradXArray
        gradYArrayT = gradYArray
    
    gradGradXArray,tmpy = np.gradient(gradXArrayT,pixelDemScale)
    tmpx,gradGradYArray = np.gradient(gradYArrayT,pixelDemScale)
    curvatureDemArray = gradGradXArray + gradGradYArray
    curvatureDemArray[np.isnan(curvatureDemArray)] = 0
    del tmpy, tmpx
    # Computation of statistics of curvature
    print ' curvature statistics'
    tt = curvatureDemArray[~np.isnan(curvatureDemArray[:])]
    print ' non-nan curvature cell number:', tt.shape[0]
    finiteCurvatureDemList = curvatureDemArray[np.isfinite(curvatureDemArray[:])]
    print ' non-nan finite curvature cell number:', finiteCurvatureDemList.shape[0]
    curvatureDemMean = np.nanmean(finiteCurvatureDemList)
    curvatureDemStdDevn = np.nanstd(finiteCurvatureDemList)
    print ' mean: ', curvatureDemMean
    print ' standard deviation: ', curvatureDemStdDevn
    return curvatureDemArray, curvatureDemMean, curvatureDemStdDevn


def compute_quantile_quantile_curve(x):
    print 'getting qqplot estimate'
    if not hasattr(defaults, 'figureNumber'):
        defaults.figureNumber = 0
    defaults.figureNumber = defaults.figureNumber + 1
    plt.figure(defaults.figureNumber)
    res = stats.probplot(x, plot=plt)
    res1 = sm.ProbPlot(x, stats.t, fit=True)
    print res1
    return res


def main():
##    plt.switch_backend('agg')
    filteredDemArray = read_geotif_filteredDEM()
    # Computing slope
    print 'computing slope'
    slopeDemArray = compute_dem_slope(filteredDemArray, Parameters.demPixelScale)
    slopeDemArray[np.isnan(filteredDemArray)] = np.nan
    # Writing the curvature array
    outfilepath = Parameters.geonetResultsDir
    demName = Parameters.demFileName.split('.')[0]
    outfilename = demName +'_slope.tif'
    write_geotif_generic(slopeDemArray, outfilepath, outfilename)
    # Computing curvature
    print 'computing curvature'
##    curvatureDemArrayIn = filteredDemArray
    curvatureDemArray, curvatureDemMean, \
                       curvatureDemStdDevn = compute_dem_curvature(filteredDemArray,
                                                                   Parameters.demPixelScale,
                                                                   defaults.curvatureCalcMethod)
    curvatureDemArray[np.isnan(filteredDemArray)] = np.nan
    # Writing the curvature array
    outfilename = demName +'_curvature.tif'
    write_geotif_generic(curvatureDemArray, outfilepath, outfilename)
    # plotting the curvature image
    if defaults.doPlot == 1:
        raster_plot(curvatureDemArray, 'Curvature DEM')

    finiteCurvatureDemList = curvatureDemArray[np.isfinite(curvatureDemArray[:])]
    #*************************************************
    #Compute curvature quantile-quantile curve
    # This seems to take a long time ... is commented for now
    #print 'computing curvature quantile-quantile curve'
    #osm,osr = compute_quantile_quantile_curve(finiteCurvatureDemList)
    #print osm[0]
    #print osr[0]
    thresholdCurvatureQQxx = 1
    # have to add method to automatically compute the thresold
    # .....
    # .....
    #*************************************************


if __name__ == '__main__':
    t0 = clock()
    main()
    t1 = clock()
    print "time taken to complete slope and curvature computation:", t1-t0, " seconds"

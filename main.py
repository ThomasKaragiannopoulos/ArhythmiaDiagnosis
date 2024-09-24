import os
from Plotting import *
from DataPreparation import *
#All Available Subject IDs
subjects = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 111, 112, 113, 114, 115, 116, 117, 118, 119, 121, 122, 123, 124 
            ,200 ,201 ,202 ,203 ,205 ,207 ,208 , 209, 210, 212, 213, 214, 215, 217, 219, 220, 221, 222, 223, 228 ,230 ,231 ,232 
            ,233 ,234]

#AllDirectoriesUsed
DataFolderDirectory = os.path.join("Data")
OriginalSignalDirectory = os.path.join("Data", "OriginalECGs")
RawDataDirectory = os.path.join("Data","DataV0.h5")
FilteredDataDirectory = os.path.join("Data","FilteredData.h5")

#Execute Data Preperation
dp = PrepareData(OriginalSignalDirectory, DataFolderDirectory)
dp.execute()

#Plotting Functions Examples
PlotRawECG(RawDataDirectory, "203")
PlotRawChannelECG(RawDataDirectory, "107", 0)
PlotFilteredECG("222", 1, RawDataDirectory, FilteredDataDirectory)
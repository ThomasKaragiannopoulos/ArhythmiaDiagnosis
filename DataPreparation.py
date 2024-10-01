import h5py
import os
import wfdb
import numpy as np
from scipy.signal import butter, lfilter

class PrepareData:
    def __init__(self, RawDataDirectory, DataFolderDirectory):
        self.RawDataDirectory = RawDataDirectory
        self.DataFolderDirectory = DataFolderDirectory
    #execution
    def execute(self):    
        print("Extracting the ECG Signals From the Original File")
        self.LoadData(self.RawDataDirectory, self.DataFolderDirectory).RawDataToH5()
        print("Extracting the Labels From the Original File")
        self.LoadAnnotations(self.RawDataDirectory, self.DataFolderDirectory).ExtractAnnotations()
        print("Applying a Butterworths Bandpass Filter")
        self.FilterData(self.RawDataDirectory, self.DataFolderDirectory).ApplyFilter()
        print("Normalizing Data")
        self.StandardizeData(self.RawDataDirectory, self.DataFolderDirectory).ApplyStandardization()
        print("Segmenting Signals")
        self.SegmentData(self.RawDataDirectory, self.DataFolderDirectory).ApplySegmentation()
        
    class LoadData:  
            #Load The Referenced Data
            def __init__(self, RawDataDirectory, DataFolderDirectory):
                self.RawDataDirectory  = RawDataDirectory
                self.DataFolderDirectory = DataFolderDirectory
            #Conversion
            def RawDataToH5(self):
                # Create the output file path with a filename
                OutputFilePath = os.path.join(self.DataFolderDirectory, "DataV0.h5")
                # Extraction Loop
                with h5py.File(OutputFilePath, 'w') as hdf5_file:
                    for record_name in os.listdir(self.RawDataDirectory):
                        if record_name.endswith('.dat'): 
                            base_name = os.path.splitext(record_name)[0]
                            record = wfdb.rdrecord(os.path.join(self.RawDataDirectory, base_name))
                            hdf5Group = hdf5_file.create_group(base_name)
                            hdf5Group.create_dataset('pSignal', data=record.p_signal)
                            hdf5Group.attrs['Frequency'] = record.fs                
                            hdf5Group.attrs['Name'] = record.sig_name
    #Extracts the data labels
    class LoadAnnotations:
        # Load The Referenced Data
        def __init__(self, RawDataDirectory, DataFolderDirectory):
            self.RawDataDirectory = RawDataDirectory
            self.DataFolderDirectory = DataFolderDirectory
        # Extract the Labels
        def ExtractAnnotations(self):
            # Create the output file path with a filename
            OutputFilePath = os.path.join(self.DataFolderDirectory, "Annotations.h5")
            # Extraction Loop
            with h5py.File(OutputFilePath, 'w') as hdf5_file:
                for record_name in os.listdir(self.RawDataDirectory):
                    if record_name.endswith('.dat'):
                        base_name = os.path.splitext(record_name)[0]
                        annotation = wfdb.rdann(os.path.join(self.RawDataDirectory, base_name), 'atr')
                        hdf5_group = hdf5_file.create_group(base_name)
                        hdf5_group.create_dataset('AnnotationSample', data=annotation.sample)
                        hdf5_group.create_dataset('AnnotationSymbol', data=np.array(annotation.symbol, dtype='S1'))
    #Apply a Butterworths Band Pass filter to the data
    class FilterData:
        # Load The Referenced Data
        def __init__(self, RawDataDirectory, DataFolderDirectory):
            self.RawDataDirectory = RawDataDirectory
            self.DataFolderDirectory = DataFolderDirectory
        #Filter
        def ButterBandpass(self, MinCut, MaxCut, Frequency, Order=5):
            Nquist = Frequency / 2
            MinCutD = MinCut / Nquist
            MaxCutD = MaxCut / Nquist
            b, a = butter(Order, [MinCutD, MaxCutD], btype='band')
            return b, a
        #Pure Application
        def ApplyBandpassFilter(self,Data, MinCut, MaxCut, Frequency):
            Order = 5
            b, a = self.ButterBandpass(MinCut, MaxCut, Frequency, Order)
            FilteredData = lfilter(b, a, Data)
            return FilteredData
        #Final Application
        def ApplyFilter(self):
            MinCut=0.5
            MaxCut=40
            Subjects = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 111, 112, 113, 114, 115, 116, 117, 118, 119, 121, 122, 123, 124 
            ,200 ,201 ,202 ,203 ,205 ,207 ,208 , 209, 210, 212, 213, 214, 215, 217, 219, 220, 221, 222, 223, 228 ,230 ,231 ,232 ,233 ,234]
            InputFileDirectory = os.path.join(self.DataFolderDirectory, "DataV0.h5") 
            FileName = os.path.join(self.DataFolderDirectory, "FilteredData.h5")
            #Staa
            with h5py.File(InputFileDirectory, 'r') as input_hf, h5py.File(FileName, 'w') as output_hf:
                for Subject in Subjects:
                    RecordName = str(Subject)
                    if RecordName not in input_hf:
                        continue
                    record = input_hf[RecordName]
                    fs = record.attrs.get('Frequency', 360)  # Default to 360 Hz if not specified
                    signal = record['pSignal'][:]
                    num_channels = signal.shape[1]
                    for idx in range(num_channels):
                        filtered_data = self.ApplyBandpassFilter(signal[:, idx], MinCut, MaxCut, fs)                        
                        dataset_name = f"Subject_{RecordName}_channel_{idx}"
                        output_hf.create_dataset(dataset_name, data=filtered_data)
    #Standardizes the data
    class StandardizeData:
        #Load The Referenced Data
        def __init__(self, RawDataDirectory, DataFolderDirectory):
            self.RawDataDirectory = RawDataDirectory
            self.DataFolderDirectory = DataFolderDirectory
        #Standardization
        def Standardization(self, data):
            mean = np.mean(data, axis=0)
            std = np.std(data, axis=0)
            return (data - mean) / std
        def ApplyStandardization(self):
            StandardizedFileName = os.path.join(self.DataFolderDirectory, "StandardizedData.h5")
            FilteredDataPath = os.path.join(self.DataFolderDirectory, "FilteredData.h5")
            #Starting the Loop    
            with h5py.File(FilteredDataPath, 'r') as Filtered, h5py.File(StandardizedFileName, 'w') as Normalized:
                for DatasetName in Filtered:
                    data = Filtered[DatasetName][:]
                    # Standardize the data
                    StandardizedData = self.Standardization(data)            
                    Normalized.create_dataset(DatasetName, data=StandardizedData)
#Segments the data evenly(Lenght = 500)
    class SegmentData:
        def __init__(self, RawDataDirectory, DataFolderDirectory):
            self.RawDataDirectory  = RawDataDirectory
            self.DataFolderDirectory = DataFolderDirectory
        #segments the data
        def Segmentate(self, signal, NewLength=500):
            NumOfSegments = len(signal) // NewLength
            segments = []
            for i in range(NumOfSegments):
                segment = signal[i * NewLength:(i + 1) * NewLength]
                segments.append(segment)
            return np.array(segments)
        
        def ApplySegmentation(self):
            OutputFile = os.path.join(self.DataFolderDirectory, "SegmentedData.h5")
            InputFile = os.path.join(self.DataFolderDirectory, "StandardizedData.h5")
            SegmentLength=500
            #Start the segmetation loop
            with h5py.File(InputFile, 'r') as infile, h5py.File(OutputFile, 'w') as outfile:
                for dataset_name in infile.keys():
                    data = infile[dataset_name][:]
                    segmented_data = self.Segmentate(data, NewLength=SegmentLength)
                    outfile.create_dataset(dataset_name, data=segmented_data)
    
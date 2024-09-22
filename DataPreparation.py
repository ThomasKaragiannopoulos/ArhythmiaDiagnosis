import h5py
import os
import wfdb
import numpy as np

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



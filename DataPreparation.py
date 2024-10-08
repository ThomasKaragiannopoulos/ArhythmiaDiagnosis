import h5py
import os
import wfdb
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
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

    # Indicates the presence of a label through a binary vector
    class EncodeLabels:
        # Load The Referenced Data
        def __init__(self, RawDataDirectory, DataFolderDirectory):
            self.RawDataDirectory = RawDataDirectory
            self.DataFolderDirectory = DataFolderDirectory
    # Encoding Labels but grouping all Noises and Artifacts are grouped together
        def ApplyMLBFilter(self):
                # Define directories
                SegmentedDataDirectory = os.path.join(self.DataFolderDirectory, "SegmentedData.h5")
                AnnotationsDataDirectory = os.path.join(self.DataFolderDirectory, "Annotations.h5")

                # Define possible labels and ignore Q and S
                PossibleLabels = {
                    b'N': 'Normal',
                    b'R': 'Regular',
                    b'a': 'Atrial',
                    b'f': 'Fusion',
                    b'j': 'Junctional',
                    b'L': 'Lethargy',
                    b'A': 'Atrial',
                    b'V': 'Ventricular',
                    b'E': 'Ventricular',
                    b'J': 'Junctional',
                    b'F': 'Fusion',
                    b'/': 'Paced',
                    # Group noise and artifacts into a single label
                    b'Noise': [b'+', b'|', b'~', b'!', b'x', b'[', b']', b'"', b'^', b'e'],
                    b'S': 'Start',
                    b'Q': 'Unclassifiable'
                }

                mlb = MultiLabelBinarizer()
                mlb.fit([list(PossibleLabels.keys())])
                OutputDirectory = os.path.join(self.DataFolderDirectory, "EncodedLabels.h5")

                with h5py.File(SegmentedDataDirectory, 'r') as SegmentedFile, \
                    h5py.File(AnnotationsDataDirectory, 'r') as AnnotationsFile, \
                    h5py.File(OutputDirectory, 'a') as OutputFile:  # Use 'a' to append or create

                    # Loop for subjects
                    for subject in AnnotationsFile.keys():
                        # Create or open the group for the subject
                        if subject not in OutputFile:
                            SubjectGroup = OutputFile.create_group(subject)
                        else:
                            SubjectGroup = OutputFile[subject]  # If exists, use the existing group

                        # Process only one channel (e.g., channel 0)
                        channel = 0
                        ChannelName = f"Subject_{subject}_channel_{channel}"
                        
                        if ChannelName in SegmentedFile:
                            segments = SegmentedFile[ChannelName][:]  
                            annotations = AnnotationsFile[subject]['AnnotationSymbol'][:]  
                            annotationSamples = AnnotationsFile[subject]['AnnotationSample'][:]  
                            labels = []

                            for i in range(len(segments)):
                                SegmentStart = i * len(segments[0])
                                SegmentEnd = SegmentStart + len(segments[0])

                                # Find where the annotations are in the segment
                                indices = np.where((annotationSamples >= SegmentStart) & (annotationSamples < SegmentEnd))[0]
                                SegmentAnnotations = annotations[indices]

                                # Label Encoding
                                if SegmentAnnotations.size > 0:
                                    # Replace noise and artifacts with a single label
                                    mapped_annotations = [
                                        b'Noise' if ann in [b'+', b'|', b'~', b'!', b'x', b'[', b']', b'"', b'^', b'e'] else ann
                                        for ann in SegmentAnnotations
                                    ]
                                    EncodedLabels = mlb.transform([mapped_annotations])[0]
                                else:
                                    EncodedLabels = np.zeros(len(PossibleLabels))  # No labels present
                                labels.append(EncodedLabels)

                            # Save segments and labels
                            SubjectGroup.create_dataset('segments', data=segments)
                            SubjectGroup.create_dataset('labels', data=np.array(labels))
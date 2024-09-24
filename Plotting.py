import h5py
import matplotlib.pyplot as plt


#Plots ECG Raw
def PlotRawECG(RawDataH5Directory, Subject):
    #Retrieve from h5
    with h5py.File(RawDataH5Directory, 'r') as hdf5_file:
        record = hdf5_file[Subject]
        signal_data = record['pSignal'][:]
        signal_names = record.attrs.get('Name', [f'Signal {i}' for i in range(signal_data.shape[1])])

        # Plot
        plt.figure(figsize=(12, 6))
        for i in range(signal_data.shape[1]):
            plt.plot(signal_data[:, i], label=signal_names[i])
        plt.title('ECG Signals')
        plt.xlabel('Samples')
        plt.ylabel('Amplitude')
        plt.legend()
        plt.show()
        #e.g. PlotRawECG(RawDataDirectory, "203")

#Plots a single ECG signal raw
def PlotRawChannelECG(RawDataH5Directory, Subject, Channel):
    #Retrieve from h5
    with h5py.File(RawDataH5Directory, 'r') as hdf5_file:
        record = hdf5_file[Subject]
        signal_data = record['pSignal'][:]
        signal_names = record.attrs.get('Name', [f'Signal {i}' for i in range(signal_data.shape[1])])

        # Plot
        plt.figure(figsize=(12, 6))
        plt.plot(signal_data[:, Channel], label=signal_names[Channel])
        plt.title('ECG Signals')
        plt.xlabel('Samples')
        plt.ylabel('Amplitude')
        plt.legend()
        plt.show()
        #e.g. PlotRawECG(RawDataDirectory, "107", 0)


def PlotFilteredECG(RecordName, Channel, RawDataPath, FilteredDataPath):
    with h5py.File(RawDataPath, 'r') as raw_file, h5py.File(FilteredDataPath, 'r') as filtered_file:
        
        #fetch data
        filtered_dataset_name = f"Subject_{RecordName}_channel_{Channel}"
        record = raw_file[RecordName]
        original_signal = record['pSignal'][:, Channel]
        filtered_signal = filtered_file[filtered_dataset_name][:]
        
        # Plot
        plt.figure(figsize=(12, 8))
        
        # Plot original
        plt.subplot(2, 1, 1)
        plt.plot(original_signal, label='Original Signal')
        plt.title(f'Original ECG Signal - {RecordName} (Channel {Channel})')
        plt.xlabel('Samples')
        plt.ylabel('Amplitude')
        plt.legend()
        
        # Plot filtered
        plt.subplot(2, 1, 2)
        plt.plot(filtered_signal, label='Filtered Signal', color='orange')
        plt.title(f'Filtered ECG Signal - {RecordName} (Channel {Channel})')
        plt.xlabel('Samples')
        plt.ylabel('Amplitude')
        plt.legend()
        
        #combine
        plt.tight_layout()
        plt.show()
        #e.g. PlotFilteredECG("222", 1, RawDataDirectory, FilteredDataDirectory)

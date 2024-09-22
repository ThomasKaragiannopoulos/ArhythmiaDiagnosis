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


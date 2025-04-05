import matplotlib.pyplot as plt

# Replace this with the path to your .txt file
file_path_CH0 = "data/20250402_pulse_height_vary/1_2V_20s/CH0@DT5720B_75_EspectrumR_test_fixed1_2V_20s_20250402_150738.txt"
file_path_CH1 = "data/20250402_pulse_height_vary/1_2V_20s/CH1@DT5720B_75_EspectrumR_test_fixed1_2V_20s_20250402_150738.txt"

# Read the energy from the file
with open(file_path_CH0, 'r') as file:
    energies_CH0 = [float(line.strip()) for line in file if line.strip()]

# Read the energy from the file
with open(file_path_CH1, 'r') as file:
    energies_CH1 = [float(line.strip()) for line in file if line.strip()]

# crop data to the relevant ADC channels
energies_ADC_cropped_CH0 = energies_CH0[:-3990]
# crop data to the relevant ADC channels
energies_ADC_cropped_CH1 = energies_CH1[:-3950]

# Create x values as indices
x_CH0 = list(range(len(energies_ADC_cropped_CH0)))
x_CH1 = list(range(len(energies_ADC_cropped_CH1)))

# Plot the energies
plt.scatter(x_CH0, energies_ADC_cropped_CH0 , marker='o',color='r',s=10)
plt.xlabel("Index")
plt.ylabel("Value")
plt.title("Plot of energies from CH0")
plt.grid(True)
plt.show()

# Plot the energies
plt.scatter(x_CH1, energies_ADC_cropped_CH1 , marker='o',color='m',s=10)
plt.xlabel("Index")
plt.ylabel("Value")
plt.title("Plot of energies from CH1")
plt.grid(True)
plt.show()

# Visualization parameters

update_freq = 100
# Define the number of points to display
Time2Display = 2 # in seconds
SampleRate = 2000
definition = 1 / 1000
TimeStep = 1 / SampleRate
Pts2Display = round(Time2Display * SampleRate)

# Define the number of channels
MusclesNumber = 2
SynergiesNumber = 5

showMuscles = [True for _ in range(MusclesNumber)]
ShowSinergies = [True for _ in range(SynergiesNumber)]

current_x = 0

MusclesColors = ['red','blue','green','yellow','pink','brown','orange','violet']
SynergiesColors = ['red','blue','green','yellow','pink']
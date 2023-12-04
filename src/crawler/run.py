from Process_Data import Process_Data
from Extraction import Extraction
from Exploration import Exploration


process_data = Process_Data(filename="training_data/links.csv", recursive=False)
process_data.label_training_data(output_file='training_data/training_data_no_rec.csv')


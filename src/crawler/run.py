from Process_Data import Process_Data
from Extraction import Extraction
from Exploration import Exploration


# exp = Exploration(filename='training_data/links.csv')
# a = exp.get_all_links(initial_links=exp.initial_links, depth=3)
# print(a)
# # a = exp.get_recursive_links('https://dunlin.com.au/products/beadlight-cirrus')

process_data = Process_Data(filename="training_data/links.csv")
process_data.label_training_data(output_file='training_data/training_data.csv')


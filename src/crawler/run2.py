from Process_Data import Process_Data
from Extraction import Extraction
from Exploration import Exploration

process_data = Process_Data(filename="test_data/links.csv")
process_data.preprocess_h_data(file_name="test_data/train_h_data.txt", save_in_file=True)

# a = Exploration(filename="test_data/links.csv")
# a.get_all_links(initial_links=a.initial_links, depth=3, visited=set())

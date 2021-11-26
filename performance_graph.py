from matplotlib import pyplot

with open('C:/Users/Remi/Desktop/output.txt', 'r') as f:
    file_data = f.read()
    f_data_split = file_data.split('###')
    for l in f_data_split:
        pyplot.plot([v for v in l.split('\n')])

pyplot.show()
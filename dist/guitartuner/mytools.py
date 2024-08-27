import pickle
def dump(obj, file):
    pickle.dump(obj, open(file, 'wb'))

def load(file):
    return pickle.load(open(file, 'rb'))


import numpy as np
from datetime import datetime

def get_default_entry():
    now = datetime.now()
    return now.strftime("%a %d/%m/%Y %H:%M:%S %Z").upper()
    

class Evaluate():

    def __init__(self, save_path="./evaluation_metrics.txt", verbose=False, decimals=5):
        self.path = save_path
        self.verbose = verbose
        self.decimal = decimals

        self.data = []
        self.temp = ""
        self.make_new_entry()
        

    def make_new_entry(self, data=""):
        if self.temp != "": 
            self.data.append(self.temp)

        self.temp = f"{get_default_entry()} >> {data} >> "



    def jaccard_similarity(self, text1, text2):
        text1 = np.array(text1.lower().split(" "))
        text2 = np.array(text2.lower().split(" "))

        intersection = len(np.intersect1d(text1, text2))
        union = len(np.union1d(text1, text2))

        j_similarity = round(float(intersection/union), self.decimal)
        self.temp = self.temp + str(j_similarity)
        if self.verbose : print(self.temp)

        return j_similarity



    def cosine_similarity(self, text1, text2):
        text1 = text1.lower().split(" ")
        text2 = text2.lower().split(" ")

        unique_words = set(text1 + text2)

        vector1 = np.array([text1.count(word) for word in unique_words])
        vector2 = np.array([text2.count(word) for word in unique_words])

        dot_product = np.dot(vector1, vector2)
        magnitude1 = np.sqrt(np.sum(vector1 ** 2))
        magnitude2 = np.sqrt(np.sum(vector2 ** 2))

        cosine_sim = round(float(dot_product / (magnitude1 * magnitude2)), self.decimal)
        self.temp = self.temp + str(cosine_sim)
        if self.verbose : print(self.temp)

        return cosine_sim



    def eucledian_distance(self, text1, text2):
        text1 = text1.lower().split(" ")
        text2 = text2.lower().split(" ")

        unique_words = set(text1 + text2)

        vector1 = np.array([text1.count(word) for word in unique_words])
        vector2 = np.array([text2.count(word) for word in unique_words])

        eucledian_dist = round(float(np.sqrt(np.sum((vector1 - vector2) ** 2))), self.decimal)
        self.temp = self.temp + str(eucledian_dist)
        if self.verbose : print(self.temp)

        return eucledian_dist



    def save_data(self):
        with open(self.path, "w") as file:
            for line in self.data:
                file.write(line + '\n')

            file.close()


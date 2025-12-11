import pandas as pd
import os

def createCSV():
    columns = ["Roles"] + ["Games",
            "# Players",
            "# Minions",
            "% Evil Win",
            "STD-ERROR",
            "ConInt95",
            "Avg Days",
            "Avg Days|Evil Win",
            "Avg Days|Good Win"]
    
    df = pd.DataFrame(columns=columns)
    df.to_csv("results.csv", index=False)

if __name__ == "__main__" and not os.path.exists("results.csv"):
    createCSV()
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


def project_piechart(lst):
    loclst = []
    sum = 0
    labels = []
    for i in range(len(lst)):
        if lst[i]:
            loclst.append(lst[i])
            sum += lst[i]
            labels.append(f'Project {i + 1}')
    m = len(loclst)


    sizes = []
    for num in loclst:
        sizes.append((num / sum) * 100)

    colors = cm.rainbow(np.linspace(0, 1, m))

    explst = []
    for i in range(m):
        explst.append(0.1)
    explode = tuple(explst)

    plt.figure(figsize=(10, 7))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, explode=explode, textprops={'fontweight': 'bold'})
    plt.axis('equal')
    plt.gca().patch.set_alpha(0)

    plt.show()

def vintage_scatter(lst, df):
    year = []
    price = []
    for i in range(len(lst)):
        if lst[i]:
            year.append(df['Vintage'][i])
            price.append(df['Dollar'][i])



    plt.scatter(year, price, color='blue', marker='o')

    plt.xlabel('Years')
    plt.ylabel('Price in $')

    plt.xticks(range(int(min(year)), int(max(year))+1, 1))
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.show()

df = pd.read_excel('/Users/meliodas/Downloads/Book6.xlsx', engine='openpyxl')

project_piechart([2,3,4,5,6,7,15])
#vintage_scatter([2,4,5,6,7,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], df)






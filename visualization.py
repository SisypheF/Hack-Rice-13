import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pandas as pd
import seaborn as sns

from model import model


def project_piechart(lst):
    def custom_autopct(pct):
        if pct == max(sizes):
            return f'{pct:.1f}%'
        else:
            return f'{pct:.1f}%'

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

    colors = sns.color_palette("crest", m)

    explst = []
    for i in range(m):
        explst.append(0.05)
    explode = tuple(explst)

    plt.figure(figsize=(20, 14))
    wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, autopct=custom_autopct, startangle=140, explode=explode, textprops={'fontweight': 'bold', 'color': 'white'})
    for t in autotexts:
        if t.get_text() == f'{max(sizes):.1f}%':
            t.set_size(15)
        else:
            t.set_size(10)
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
    plt.figure(figsize=(20, 14))
    plt.scatter(year, price, color='blue', marker='o')
    plt.xlabel('Years')
    plt.ylabel('Price in $')

    plt.xticks(range(int(min(year)), int(max(year))+1, 1))
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.show()

def grade_scatter(lst, df):
    grade = []
    price = []
    for i in range(len(lst)):
        if lst[i]:
            grade.append(df['Grade'][i])
            price.append(df['Dollar'][i])
    order = ['F', 'D', 'C', 'B', 'A']
    for label in order:
        mask = [item == label for item in grade]
        plt.scatter([label] * sum(mask), [price[i] for i in range(len(price)) if mask[i]])
    plt.figure(figsize=(10, 14))
    plt.xlabel('Grades')
    plt.ylabel('Price in $')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.show()






df = pd.read_excel('/Users/meliodas/Downloads/Book6.xlsx', engine='openpyxl')

ourModel = model()
#ourModel.big_optimizer(100000, "high", 10000)
#ourDict = ourModel.returnValueDict()
#ourModel.small_optimizer(100000, "high", 10000, amtTypes=ourDict['amtTypes'], amtVintage=ourDict['amtVintage'], 
                            #amtRegistry=ourDict['amtRegistry'], amtLocations=ourDict['amtLocations'], 
                            #amtMechanisms=ourDict['amtMechanisms'], amtDevs=ourDict['amtDevs'])
ourModel.small_optimizer(10000, "low", 100)
portfolio = ourModel.returnPortfolio()
portfolio
project_piechart(portfolio)





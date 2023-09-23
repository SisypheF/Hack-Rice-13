import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

def piechart(lst):
    loclst = []
    sum = 0
    for num in lst:
        if num:
            loclst.append(num)
            sum += num
    m = len(loclst)  # for example, # blocks
    labels = [f'Block {i + 1}' for i in range(m)]


    sizes = []
    for num in loclst:
        sizes.append((num / sum) * 100)

    colors = cm.rainbow(np.linspace(0, 1, m))

    explst = []
    for i in range(m):
        explst.append(0.1)
    explode = tuple(explst)

    plt.figure(figsize=(10, 7))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, explode=explode)
    plt.axis('equal')

    plt.show()






import math
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import json

class model:
    def __init__(self, fileName='/Users/meliodas/Downloads/Book6.xlsx'):
        self.df = pd.read_excel(fileName)
        self.df = self.df.dropna()
        self.valueDict = {}
        self.shadowPriceDict = {}
        self.portfolio = []

    # helper functions
    def castRisk(self, character):
        mapping = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 6}
        if character in mapping.keys():
            return mapping[character]
    
    def distinct(self, d, var, num):
        """input:
        d: a list of binary numbers representing whether we purchase credits from some project developers
        var: a list of (homogeneous) objects representing the optimized combination
        num: length of var

        returns how many distinct values are in var
        """
        modVar = []
        for index in range(num):
            if d[index]:
                modVar.append(var[index])
        occurence = {}
        for item in modVar:
            if item not in occurence.keys():
                occurence[item] = 1
            else:
                occurence[item] = occurence[item] + 1
        return len(occurence.keys())

    def Var(self, x, num):
        """
        input:
        x: a list of integers representing the optimized combination
        num: length of x

        Returns variance of x
        """
        Xsum = 0
        for num in x:
            Xsum = Xsum + num
        mean = Xsum / num
        sq_sum = 0
        for num in x:
            sq_sum = sq_sum + (num - mean)**2
        return sq_sum / num

    def occurrence(self, d, var, num, proj):
        """
        input:
        d: a list of binary numbers representing whether we purchase credits from some project developers
        var: a list of integers representing the optimized combination
        num: length of var
        proj: a string representing the risk grade of the project ('A', 'B', 'C', 'D', 'F')
        
        returns the number of occurrences of proj in var
        """
        
        count = 0
        for index in range(num):
            if d[index]:
                if (self.df['Grade'][index] == proj):
                    count = count + var[index]
        return count

    def big_constraints(self, budget, riskTol, deficit):
        """
        :param budget: The maximum budget for the portfolio
        :param riskTol: The risk tolerance for the portfolio
        :param deficit: The deficit for the portfolio
        :return: T/F indicates if variables make sense given excel
        """
        # check if budget is big enough
        truncated = self.df.sort_values(by="Dollar", ascending=True)[["Dollar", "Quantity"]]
        amt = 0
        total_quantity = 0
        for index, row in truncated.iterrows():
            price = row["Dollar"]
            quantity = row["Quantity"]
            for i in range(int(quantity)):
                if total_quantity >= deficit:
                    break
                amt += price
                total_quantity += 1
            if total_quantity >= deficit:
                break

        if not (budget >= amt):
            return json.dumps({"budget": False})

        # check if deficit is small enough
        if not (deficit <= self.df["Quantity"].sum()):
            return json.dumps({"deficit": False})
        
        return json.dumps({"all": True})

    # optimizing with 3 parameters, 8 variables
    def big_optimizer(self, budget, riskTol, deficit, penalty=100):
        """
        :param budget: The maximum budget for the portfolio
        :param riskTol: The risk tolerance for the portfolio
        :param deficit: The deficit for the portfolio
        :param penalty: The penalty for the std deviation
        :return: A json formatted dict (string -> int) with the 
        amtDevs, amtVintage, amtRegistry, amtLocations, amtMechanisms, amtTypes
        """
        #if not self.big_constraints(budget, riskTol, deficit):
        #    return None

        # Low, Medium, High
        if riskTol == "low":
            pct = .05
        elif riskTol == "medium":
            pct = .07
        else:
            pct = .1

        # Initialize model
        model = gp.Model("MIP_Model")

        # Number of projects in the data table
        numProjDev = self.df.shape[0]

        # Add variables to the model
        x = model.addVars(numProjDev, vtype=GRB.INTEGER, name="quantity")
        d = model.addVars(numProjDev, vtype=GRB.BINARY, name="devTF")
        dbar = model.addVar(vtype=GRB.INTEGER, name="amtDevs")
        v = model.addVar(vtype=GRB.INTEGER, name="amtVintage")
        r = model.addVar(vtype=GRB.INTEGER, name="amtRegistry")
        l = model.addVar(vtype=GRB.INTEGER, name="amtLocations")
        m = model.addVar(vtype=GRB.INTEGER, name="amtMechanisms")
        t = model.addVar(vtype=GRB.INTEGER, name="amtTypes")

        # Initialize the objective function
        obj = dbar + v + r + l + m + t
        model.setObjective(obj, GRB.MAXIMIZE)

        # Constraints
        model.addConstr(gp.quicksum(self.df['Dollar'][i]*x[i] for i in range(numProjDev)) <= budget, "price")
        for i in range(numProjDev):
            model.addConstr(x[i] <= self.df["Quantity"][i], "quantity")
            model.addConstr(d[i] * x[i] - x[i] >= -1*pct, "1st binary constraint")
            model.addConstr(d[i] * x[i] - d[i] >= -1*pct, "2nd binary constraint")
            model.addConstr(x[i] / deficit <= pct, "maximum concentration of each project")
        model.addConstr(gp.quicksum(d[i] for i in range(numProjDev)) - dbar >= 0, "num of devs")
        model.addConstr(self.distinct(d, self.df['Vintage'], numProjDev) - v >= 0, "vintage")
        model.addConstr(self.distinct(d, self.df['Registry'], numProjDev) - r >= 0, "registry")
        model.addConstr(self.distinct(d, self.df['Location'], numProjDev) - l >= 0, "location")
        model.addConstr(self.distinct(d, self.df['Mechanism'], numProjDev) - m >= 0, "mechanism")
        model.addConstr(self.distinct(d, self.df['Type'], numProjDev) - t >= 0, "typeProject")
        model.addConstr(gp.quicksum(x[i] for i in range(numProjDev)) >= deficit, "deficit")

        # Optimization
        model.optimize()

        # Check for infeasibility
        if model.status == GRB.Status.INFEASIBLE:
            return json.dumps({})

        # Get the solution
        valueDict = {dbar.varName:dbar.X, v.varName:v.X, r.varName:r.X, l.varName:l.X, m.varName:m.X, t.varName:t.X}
        self.valueDict = valueDict

        # Return the solution
        jsonString = json.dumps(valueDict, indent=4, sort_keys=True)
        return jsonString
    
    def returnValueDict(self) -> dict:
        return self.valueDict

    def small_constraint(self, amtTypes, amtVintage, amtRegistry, amtLocations, amtMechanisms, amtDevs):
        if not (amtTypes >= 0 and amtTypes <= self.df["Type"].nunique()):
            return json.dumps({"amtTypes": False})
        if not (amtVintage >= 0 and amtVintage <= self.df["Vintage"].nunique()):
            return json.dumps({"amtVintage": False})
        if not (amtRegistry >= 0 and amtRegistry <= self.df["Registry"].nunique()):
            return json.dumps({"amtRegistry": False})
        if not (amtLocations >= 0 and amtLocations <= self.df["Location"].nunique()):
            return json.dumps({"amtLocations": False})
        if not (amtMechanisms >= 0 and amtMechanisms <= self.df["Mechanism"].nunique()):
            return json.dumps({"amtMechanisms": False})
        if not (amtDevs >= 0 and amtDevs <= self.df["Developer"].nunique()):
            return json.dumps({"amtDevs": False})

        return json.dumps({"all": True})

    # optimizing with 9 parameters, 2 variables
    def small_optimizer(self, budget, riskTol, deficit, 
                        amtTypes=1, amtVintage=1, amtRegistry=1, amtLocations=1, 
                        amtMechanisms=1, amtDevs=1, penalty=100):
        """
        :param budget: The maximum budget for the portfolio
        :param riskTol: The risk tolerance for the portfolio
        :param deficit: The deficit for the portfolio
        :param amtTypes: The number of unique types of projects
        :param amtVintage: The number of unique vintages
        :param amtRegistry: The number of unique registries
        :param amtLocations: The number of unique locations
        :param amtMechanisms: The number of unique mechanisms
        :param amtDevs: The number of unique developers
        :param penalty: The penalty for the std deviation
        :return: The portfolio as a list of quantities (int) for each project 
        """

        # Low, Medium, High
        if riskTol == "low":
            pct = .05
        elif riskTol == "medium":
            pct = .07
        else:
            pct = .1

        # Initialize model
        model = gp.Model("MIP_Model")

        # Number of projects in the data table
        numProjDev = self.df.shape[0]

        # Add variables to the model
        x = model.addVars(numProjDev, vtype=GRB.INTEGER, name="quantity")
        d = model.addVars(numProjDev, vtype=GRB.BINARY, name="devTF")

        # Initialize the objective function
        obj = sum(elem1 * self.castRisk(elem2) for elem1, elem2 in zip(x, self.df['Grade'])) + penalty * self.Var(x, numProjDev)
        model.setObjective(obj, GRB.MINIMIZE)

        # Constraints
        model.addConstr(gp.quicksum(self.df['Dollar'][i]*x[i] for i in range(numProjDev)) <= budget, "price")
        for i in range(numProjDev):
            model.addConstr(x[i] <= self.df["Quantity"][i], "quantity")
            model.addConstr(d[i] * x[i] - x[i] >= -1*pct, "1st binary constraint")
            model.addConstr(d[i] * x[i] - d[i] >= -1*pct, "2nd binary constraint")
            model.addConstr(x[i] / deficit <= pct, "maximum concentration of each project")
        model.addConstr(gp.quicksum(d[i] for i in range(numProjDev)) >= amtDevs, "amtDevs")
        model.addConstr(self.distinct(d, self.df['Vintage'], numProjDev) >= amtVintage, "amtVintage")
        model.addConstr(self.distinct(d, self.df['Registry'], numProjDev) >= amtRegistry, "amtRegistry")
        model.addConstr(self.distinct(d, self.df['Location'], numProjDev) >= amtLocations, "amtLocation")
        model.addConstr(self.distinct(d, self.df['Mechanism'], numProjDev) >= amtMechanisms, "amtMechanism")
        model.addConstr(self.distinct(d, self.df['Type'], numProjDev) >= amtTypes, "amtTypes")
        model.addConstr(gp.quicksum(x[i] for i in range(numProjDev)) >= deficit, "deficit")

        # Optimization
        model.optimize()

        # Check for infeasibility
        if model.status == GRB.Status.INFEASIBLE:
            return json.dumps({})

        self.shadowPriceDict = {}
        # Save the shadow prices for later use
        for constr in model.getConstrs():
            if constr.ConstrName in ["amtDevs", "amtVintage", "amtRegistry", "amtLocation", "amtMechanism", "amtTypes"]:
                self.shadowPriceDict[constr.ConstrName] = constr.RHS

        # Return the portfolio as a list of quantities (int) for each project 
        quantityValues = [x[i].X for i in range(numProjDev)]
        self.portfolio = quantityValues

        return quantityValues

    def returnShadowPriceDict(self) -> dict:
        return self.shadowPriceDict

    def rateOfChange(self, varName: str, delta) -> float:
        """
        :param varName: The name of the variable
        :param delta: The amount to change the variable by
        :return: The dip rate of change for the portfolio
        """
        return -1*(self.shadowPriceDict["amtDevs"] * delta)

    def returnPortfolio(self) -> list:
        return self.portfolio

if __name__ == "__main__":
    ourModel = model()
    ourModel.big_optimizer(10000, "medium", 100)
    ourDict = ourModel.returnValueDict()
    ourModel.small_optimizer(10000, "medium", 1000, amtTypes=ourDict['amtTypes'], amtVintage=ourDict['amtVintage'], 
                            amtRegistry=ourDict['amtRegistry'], amtLocations=ourDict['amtLocations'], 
                            amtMechanisms=ourDict['amtMechanisms'], amtDevs=ourDict['amtDevs'])
    portfolio = ourModel.returnPortfolio()
    #print(portfolio)
    print(ourModel.returnShadowPriceDict())
    print(ourModel.rateOfChange("amtDevs", 2))

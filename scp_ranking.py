#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import math
import itertools
from multiprocessing import Pool
import parameters

dfCPM = pd.read_csv("CPM.csv", index_col=0)
#Pokemon = {"HP":225, "Attack":112, "Defense":152}

def CPM(level):
    return dfCPM[level:level]["CPM"].values[0]

def effectiveHP(hp, level):
    realHp = hp * CPM(level)
    return int(realHp)

def effectiveAttack(attack, level):
    return attack * CPM(level)

def effectiveDefense(defense, level):
    return defense * CPM(level)

def effectiveHP_CPM(hp, cpm):
    realHp = hp * cpm
    return int(realHp)

def effectiveAttack_CPM(attack, cpm):
    return attack * cpm

def effectiveDefense_CPM(defense, cpm):
    return defense * cpm

def CP_CPM(effectiveHP, effectiveAttack, effectiveDefense, cpm):
    real = effectiveAttack * math.sqrt(effectiveHP) * math.sqrt(effectiveDefense) * math.pow(cpm, 2)
    return int(real / 10)


def CP(effectiveHP, effectiveAttack, effectiveDefense, level):
    real = effectiveAttack * math.sqrt(effectiveHP) * math.sqrt(effectiveDefense) * math.pow(CPM(level), 2)
    return int(real / 10)

def SCP(effectiveHP, effectiveAttack, effectiveDefense):
    real = math.pow(effectiveHP * effectiveAttack * effectiveDefense, 2 / 3)
    return real / 10


# In[5]:


def PokemonHP(hp):
    return parameters.Pokemon["HP"] + hp

def PokemonAttack(attack):
    return parameters.Pokemon["Attack"] + attack

def PokemonDefense(defense):
    return parameters.Pokemon["Defense"] + defense

#for row in 
def calcRow(row):
    aHp = PokemonHP(row[1])
    aAttack = PokemonAttack(row[2])
    aDefense = PokemonDefense(row[3])
    
    eHp = effectiveHP(aHp, row[0])
    eAttack = effectiveAttack(aAttack, row[0])
    eDefense = effectiveDefense(aDefense, row[0])
    
    cp = CP(aHp, aAttack, aDefense, row[0])
    scp = SCP(eHp, eAttack, eDefense)
    
    sr = (row[1] + row[2] + row[3]) / 45 * 100

    return [row[0], row[1], row[2], row[3], sr, eHp, eAttack, eDefense, cp, scp]

def PokemonLevel():
    return dfCPM[parameters.PokemonLevelRange[0]:parameters.PokemonLevelRange[1]]

def calRowWithLimitCP(row):
    h = row[0]
    a = row[1]
    d = row[2]

    aHp = PokemonHP(h)
    aAttack = PokemonAttack(a)
    aDefense = PokemonDefense(d)

    for index, row in PokemonLevel().iterrows():
        pl = index
        cpm = row[0]
        cp = CP_CPM(aHp, aAttack, aDefense, cpm)

        if (cp <= parameters.LimitCP):
            eHp = effectiveHP_CPM(aHp, cpm)
            eAttack = effectiveAttack_CPM(aAttack, cpm)
            eDefense = effectiveDefense_CPM(aDefense, cpm)

            scp = SCP(eHp, eAttack, eDefense)
            break
    
    sr = (h + a + d) / 45 * 100

    return (pl, h, a, d, sr, eHp, eAttack, eDefense, cp, scp)
    
def HPRange():
    start = parameters.Range["HP"][0]
    stop = parameters.Range["HP"][1] + 1
    return np.arange(start, stop)

def AttackRange():
    start = parameters.Range["Attack"][0]
    stop = parameters.Range["Attack"][1] + 1
    return np.arange(start, stop)

def DefenseRange():
    start = parameters.Range["Defense"][0]
    stop = parameters.Range["Defense"][1] + 1
    return np.arange(start, stop)

def nonLimitCP():
    itr =  itertools.product(PokemonLevel().index, HPRange(), AttackRange(), DefenseRange())
    if (parameters.Multiprocessing):
        pool = Pool()
        rows = pool.map(calcRow, itr)
    else:
        rows = [calcRow(row) for row in itr]

    return rows

def limitCP():
    itr =  itertools.product(HPRange(), AttackRange(), DefenseRange())
    #pool = Pool()
    #rows = pool.map(calRowWithLimitCP, itr)
    if (parameters.Multiprocessing):
        pool = Pool()
        rows = pool.map(calRowWithLimitCP, itr)
    else:
        rows = [calRowWithLimitCP(row) for row in itr]

    return rows

if __name__ == '__main__':
    if (parameters.LimitCP < 0):
        rows = nonLimitCP()
    
    else:
        rows = limitCP()

    table = pd.DataFrame(
        rows,
        columns=["Pokemon Level", "Indivisual HP", "Indivisual Attack", "Indivisual Defense", "Indivisual Satification(%)", "Effective HP", "Effective Attack", "Effective Defense", "CP", "SCP"])

    table["Rank"] = table["SCP"].rank(method='max', ascending=False)
    table.sort_values(parameters.SortValue, ascending=False, inplace=True)
    table.to_csv(parameters.OutputFileName, index=False)

    




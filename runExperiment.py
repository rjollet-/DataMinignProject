from math import sqrt
import pandas as pd
import numpy as np

# Change a dataframe into a dictionary
def retro_dictify(frame):
    d = {}
    for row in frame.values:
        here = d
        for elem in row[:-2]:
            if elem not in here:
                here[elem] = {}
            here = here[elem]
        here[row[-2]] = row[-1]
    return d

# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs,p1,p2):
    # Get the list of mutually rated items
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item]=1
 
    # Find the number of elements
    n= float(len(si))
 
    # If they have no ratings in common, return 0
    if n==0: return 0
 
    # Add up all the preferences
    sum1=sum([prefs[p1][it] for it in si])
    sum2=sum([prefs[p2][it] for it in si])
 
    # Sum up the squares
    sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq=sum([pow(prefs[p2][it],2) for it in si])
 
    # Sum up the products
    pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])
 
    # Calculate Pearson score
    num=pSum-(sum1*sum2/n)
    den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den==0: return 0
 
    r=num/den
    return r

# Gets recommendations for a person by using a weighted average of every other user's rankings
def getRecommendations(prefs,person,similarity=sim_pearson):
    totals={}
    simSums={}
    for other in prefs:
        # don't compare to self
        if other==person: continue
        sim=similarity(prefs,person,other)
 
        # ignore scores of zero or lower
        if sim<=0:continue
        for item in prefs[other]:
 
            # only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item]==0:
                # Similarity * score
                totals.setdefault(item,0)
                totals[item]+=prefs[other][item]*sim
                #Sum of similarities
                simSums.setdefault(item,0)
                simSums[item]+=sim
 
        # Create the normalised list
        rankings=[(total/simSums[item],item) for item,total in totals.items()]
 
        # Return the sorted list
        rankings.sort()
        rankings.reverse()
        return rankings[0:10]


utilityMatrix = retro_dictify(pd.read_csv('UtilityMatrix.csv'))
test = retro_dictify(pd.read_csv('testData.csv'))
y = retro_dictify(pd.read_csv('yData.csv'))

columns=('precision', 'recall','F1', 'RMSE', 'MAE', 'ARHR')
i = 0
evaluations = pd.DataFrame(columns=columns)

for author in test:
    utilityMatrix[author] = test[author]

    recomandations = getRecommendations(utilityMatrix,author,similarity=sim_pearson)

    if not recomandations: 
        precision = None
        recall = None
        F1 = None
        RMSE = None
        MAE = None
        ARHR = None

    else:
        precision = 0
        recall = 0
        F1 = 0
        RMSE = 0
        MAE = 0
        ARHR = 0
        err = []
        for rank in range(0,len(recomandations)):
            if recomandations[rank][1] in y[author].keys():
                err.append(recomandations[rank][0] - y[author][recomandations[rank][1]])
                ARHR += 1/(rank+1)
                
        precision = len(err) / len(recomandations)
        recall = len(err) / len(y[author])
        F1 = (2*precision*recall) / (precision+recall) if precision+recall>0 else 0
        RMSE = pow(np.mean([pow(x,2) for x in err]),.5) if err else 0 
        MAE = np.mean([abs(x) for x in err]) if err else 0 
        ARHR = ARHR/len(err) if err else 0 
    
    evaluations.loc[i] = [precision, recall,F1, RMSE, MAE, ARHR]
    i += 1
    del utilityMatrix[author]

evaluations.to_csv('evaluations.csv', encoding='utf-8', index=False)

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

def sim_jaccard(prefs, p1, p2):
    # Get the list of mutually rated items
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item]=1
 
    # Find the number of elements
    n= float(len(si))
 
    # If they have no ratings in common, return 0
    if n==0: return 0
 
    return float((len(prefs[p1])+len(prefs[p2])-n)/n)

def sim_euclidean_score(prefs, p1, p2):
 
    # Returns ratio Euclidean distance score of person1 and person2 
 
    both_viewed = {} # To get both rated items by person1 and person2
 
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item]=1
 
    # Find the number of elements
    n= float(len(si))
 
    # If they have no ratings in common, return 0
    if n==0: return 0
 
    # Finding Euclidean distance
    sum_of_eclidean_distance = sum([pow(prefs[p1][it] - prefs[p2][it],2) for it in si]) 
   
    return 1/(1+sqrt(sum_of_eclidean_distance))

def transformPrefs(prefs):
    results={}
    for person in prefs:
        for item in prefs[person]:
            results.setdefault(item,{})

            #Flip item and person
            results[item][person]=prefs[person][item]
    return results

def calculateSimilarItems(prefs, n=10):
    #Create  a dictionary of items showing which other items they are most similar to
    results = {}

    #invert the preference matrix to be item-centric
    itemPrefs = transformPrefs(prefs)
    c=0
    for item in itemPrefs:
        #status updates for large datasets
        c+=1
        if c%100==0: print(str(c) + "/" + str(len(itemPrefs)))
        #find the most similar items to this one
        scores=topMatches(itemPrefs, item, n=n, similarity=sim_pearson)
        results[item] = scores
    return results

def getRecommendedItems(prefs, itemMatch, user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}
    #Loop over items rated by this user
    for (item, rating) in userRatings.items():
        
        for (similarity, item2) in itemMatch[item]:
            #Ignore if this user has already rated this item
            if item2 is userRatings: continue

            # Weighted sum of rating times similarity
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating

            #Sum of all the similarities
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity

    #Divide each total score by total weighting to get an average 
    rankings = [(score/totalSim[item] if totalSim[item] != 0 else 0, item) for item, score in scores.items()]

    #Return the rankings from highest to lowest
    rankings.sort()
    rankings.reverse()
    return rankings

def topMatches(prefs, person, n=5, similarity=sim_pearson):
    scores = [(similarity(prefs, person, other),other) for other in prefs if other!=person]
    scores.sort()
    scores.reverse()
    return scores[0:n]

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
utilityMatrix.update(test)
y = retro_dictify(pd.read_csv('yData.csv'))

columns=('precision', 'recall','F1', 'RMSE', 'MAE', 'ARHR')
i = 0
evaluations = pd.DataFrame(columns=columns)
itemMatch = calculateSimilarItems(utilityMatrix)

for author in test:

    #recomandations = getRecommendations(utilityMatrix,author,similarity=sim_pearson)
    recomandations = getRecommendedItems(utilityMatrix, itemMatch, author)

    if not recomandations: 
        continue

    else:
        precision = None
        recall = None
        F1 = None
        RMSE = None
        MAE = None
        ARHR = None
        tempARHR = 0
        err = []
        for rank in range(0,len(recomandations)):
            if recomandations[rank][1] in y[author].keys():
                err.append(recomandations[rank][0] - y[author][recomandations[rank][1]])
                tempARHR += 1/(rank+1)
        if err:        
            precision = len(err) / len(recomandations)
            recall = len(err) / len(y[author]) 
            F1 = (2*precision*recall) / (precision+recall) 
            RMSE = pow(np.mean([pow(x,2) for x in err]),.5)
            MAE = np.mean([abs(x) for x in err]) 
            ARHR = tempARHR/len(err) 
    
    evaluations.loc[i] = [precision, recall,F1, RMSE, MAE, ARHR]
    i += 1

evaluations.to_csv('evaluations.csv', encoding='utf-8', index=False)

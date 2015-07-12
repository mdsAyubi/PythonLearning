'''
Created on 12-Jul-2015
Code while playing around with movie recommendation system
@author: ayubi
'''
#All of the imports go here'''
import recommendation
from math import sqrt
import pydelicious
from recommendation.delicious_funcs import initializeUserDict, fillItems

critics={'Lisa Rose':{'Lady in the Water':2.5,'Snakes on a Plane':3.5,'Just My Luck':3.0,'Superman Returns':3.5,'You Me and Dupree':2.5, 'The Night Listener':3.0},
         
         'Gene Seymour':{'Lady in the Water':3.0,'Snakes on a Plane':3.5,'Just My Luck':1.5,'Superman Returns':5.0,'You Me and Dupree':3.5, 'The Night Listener':3.0},
         
         'Michael Philips':{'Lady in the Water':2.5,'Snakes on a Plane':3.0,'Superman Returns':3.5,'The Night Listener':4.0},
         
         'Claudia Puig':{'Snakes on a Plane':3.5,'Just My Luck':3.0,'Superman Returns':4.0,'You Me and Dupree':2.5, 'The Night Listener':4.5},
         
         'Mick LaSalle':{'Lady in the Water':3.0,'Snakes on a Plane':4.0,'Just My Luck':2.0,'Superman Returns':3.0,'You Me and Dupree':2.0, 'The Night Listener':3.0},
         
         'Jack Mathews':{'Lady in the Water':3.0,'Snakes on a Plane':4.0,'Superman Returns':5.0,'You Me and Dupree':3.5, 'The Night Listener':3.0},
         
         'Toby':{'Snakes on a Plane':4.5,'Superman Returns':4.0,'You Me and Dupree':1.0},
         }

#Print the dictionary values
#print(critics)
#print(critics['Lisa Rose']);
#print(critics['Lisa Rose']['Lady in the Water'])
#print(critics['Toby'])


#Function to return the distance based similarity for person1 and person2. Based on Euclidean distance
def sim_distance(prefs,person1,person2):
    #Get the list of shared items
    si = {}
    
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1


    #Print the common items between the two persons
    #print(si)
    #return 0 if there are no matching items
    if len(si) == 0: return 0
    
    #Add up all the squares of all the differences
    sum_of_squares = sum( [pow( prefs[person1][item]-prefs[person2][item],2 ) for item in prefs[person1] if item in prefs[person2]] )
    #print(sum_of_squares)
    
    return 1/(1+sum_of_squares)

#Function to return Pearson correlation coefficient for two person
def sim_pearson(prefs,person1,person2):
    #List of shared items
    si={}
    
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1
            

    #Print the common items between the two persons
    #print("Printing common items between "+person1+" and "+person2)
    #print(si)
    n = len(si)
    #return 0 if there are no matching items
    if n == 0: return 0
    
    #Add up all the preferences
    sum1 = sum([prefs[person1][it] for it in si])
    sum2 = sum([prefs[person2][it] for it in si])
    
    #Sum up the powers
    sum1Squared = sum([pow(prefs[person1][it],2) for it in si])
    sum2Squared = sum([pow(prefs[person2][it],2) for it in si])
    
    #Sum the products
    pSum = sum([ prefs[person1][it] * prefs[person2][it] for it in si ])
    
    num = pSum - (sum1*sum2)/n
    den = sqrt((sum1Squared-pow(sum1, 2)/n) * (sum2Squared - pow(sum2, 2)/n))
    if den == 0: return 0
    
    r = num/den
    #print("Score between "+person1+" and "+person2+" is="+str(r));
    
    return r
    
#Function to get the top matches of critics for a person    
def topMatches(prefs,person,n=5,similarity=sim_pearson):
    
    scores = [( similarity(prefs,other,person),other ) 
              for other in prefs if other != person]
    #print(scores)
    scores.sort()
    scores.reverse()
    return scores[0:n]

#Function to get recommendation for a person using weighted average of the users ranking
def getRecommendations(prefs,person,similarity=sim_pearson):
    totals={}
    simSums={}
    for other in prefs:
        # Don't compare me to myself
        if other==person: continue
        sim=similarity(prefs,person,other)

        # ignore scores of zero or lower
        if sim<=0: continue
        for item in prefs[other]:
        
            # only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item]==0:
                # Similarity * Score
                totals.setdefault(item,0)
                totals[item]+=prefs[other][item]*sim
                # Sum of similarities
                simSums.setdefault(item,0)
                simSums[item]+=sim

    # Create the normalized list
    rankings=[(total/simSums[item],item) for item,total in totals.items()]

    # Return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings
    
def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
            #Flip item and person
            result[item][person] = prefs[person][item]
            
    return result;       

def calculateSimilarItems(prefs,n=10):
    # Create a dictionary of items showing which other items they
    # are most similar to.
    result={}
    # Invert the preference matrix to be item-centric
    itemPrefs=transformPrefs(prefs)
    c=0
    for item in itemPrefs:
        # Status updates for large datasets
        c+=1
        if c%100==0: print "%d / %d" % (c,len(itemPrefs))
        # Find the most similar items to this one
        scores=topMatches(itemPrefs,item,n=n,similarity=sim_distance)
        result[item]=scores
    return result

def getRecommendedItems(prefs,itemMatch,user):
    userRatings=prefs[user]
    scores={}
    totalSim={}
    # Loop over items rated by this user
    for (item,rating) in userRatings.items( ):

    # Loop over items similar to this one
        for (similarity,item2) in itemMatch[item]:

            # Ignore if this user has already rated this item
            if item2 in userRatings: continue
            # Weighted sum of rating times similarity
            scores.setdefault(item2,0)
            scores[item2]+=similarity*rating
            # Sum of all the similarities
            totalSim.setdefault(item2,0)
            totalSim[item2]+=similarity

    # Divide each total score by total weighting to get an average
    rankings=[(score/totalSim[item],item) for item,score in scores.items( )]

    # Return the rankings from highest to lowest
    rankings.sort( )
    rankings.reverse( )
    return rankings

def loadMovieLens(path='data'):
    # Get movie titles
    movies={}
    for line in open(path+'/u.item'):
        (id,title)=line.split('|')[0:2]
        movies[id]=title
  
    # Load data
    prefs={}
    for line in open(path+'/u.data'):
        (user,movieid,rating,ts)=line.split('\t')
        prefs.setdefault(user,{})
        prefs[user][movies[movieid]]=float(rating)
    return prefs
                    

#print(sim_distance(critics, 'Lisa Rose', 'Gene Seymour'))
#print(sim_pearson(critics, 'Michael Philips', 'Toby'))
#print(topMatches(critics, 'Toby',n=3))
#print(getRecommendations(critics, 'Toby'))
#print(transformPrefs(critics))
#print(topMatches(transformPrefs(critics), 'Superman Returns'))
#itemSim=calculateSimilarItems(critics)
#print(getRecommendedItems(critics, itemSim, 'Toby'))


#print(prefs['87'])
#print(getRecommendations(prefs, '87')[0:3])

prefs = loadMovieLens()
itemSim=calculateSimilarItems(prefs)
print(getRecommendedItems(prefs, itemSim, '87'))




#delusers=initializeUserDict('programming')
#print(delusers)
#fillItems(delusers)

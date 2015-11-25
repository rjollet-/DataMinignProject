# DataMinignProject
Final project of Data Mining Class.

Our project is to analyse a social network based on reddit comments between author.

Edges: Number of reply
Nodes: Author

## Preprocessing

The test sample is from a random sample of 100 000 comments

### Edges

From the sqlite database export a CSV file from the query:

```sql
SELECT 
    child.author as source
    , parent.author as target
    , count(*)
FROM 
    May2015 as child INNER JOIN May2015 as parent
    ON child.parent_id == parent.name
GROUP BY source
```

output example:
```csv
source,target,count()
0u81too,Fear_UnOwn,1
5bits,ScenesfromaCat,1
AttackOnHaseeb,Redeemed_King,1
Ayy_Photon,_JackDoe_,1
CAPSLOCK_USERNAME,copperstick6,1
Cannon1,systemlord,1
CaptaineAli,JustBigChillin,1
Chie_Ayamine,Colten_Davidson,1
ChilledZero,MagicianXy,1
```

###Nodes

From the sqlite database export a CSV file from the query:

```sql
SELECT 
      author
    , subreddit
    , count(*)
FROM 
    May2015
GROUP BY author, subreddit
ORDER BY author, count(*) DESC
```

output example:
```csv
author,subreddit,count()
-ANewReality-,Drugs,2
-ANewReality-,MDMA,1
-Aeryn-,KerbalSpaceProgram,1
-Aeryn-,pcmasterrace,1
-Aeryn-,wow,1
-Agonarch,KerbalSpaceProgram,2
-Agonarch,Games,1
-Alecat,splatoon,1
-Arcanity-,eurovision,1
```

###GDF Format

Once we have the two CSV of nodes and Edges we need to format them into a file following the [GDF format](http://gephi.github.io/users/supported-graph-formats/gdf-format/)

example:

```
nodedef>name VARCHAR,sub1 VARCHAR, sub2 VARCHAR, sub3 VARCHAR
-ANewReality,Drugs, MDMA
-Aeryn-,KerbalSpaceProgram, pcmasterrace, wow
-Agonarch, KerbalSpaceProgram, Games
edgedef>node1 VARCHAR,node2 VARCHAR, weight DOUBLE
0u81too,Fear_UnOwn,1
5bits,ScenesfromaCat,1
AttackOnHaseeb,Redeemed_King,1
Ayy_Photon,_JackDoe_,1

```
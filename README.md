>TODOS
> add images
> add heathrow airport 5 to csv
# Proposing a repoducible method of creating time resilience models in Python using NetworkX
This repo is used to showcase the methodology used in my thesis "Assessing time resilience of public transit networks using London Underground data". The motivation behind this study was to explore the importance of disruption time in public transport network resilience, and how to measure the changing impact over time. Here you can find a methodology to model a non-cascading time-dependent network model, estimating changing passenger loads in a public transport network. 

The thesis can be found here ## todo add

## Table of Contents
- [Data and structure](#data and structure)
- [Requirements](#requirements)
- [Preprocessing and scripts](#preprocessing and scripts)
- [Modelling](#modelling)
- [Processing results](#processing results)
- [closing words](#closing words)

## Data and structure

## Modelling

```python
def fixCapacity(bgraph, depth):
    depth += 1 #keep track of depth to prevent  
    nocap = [(a, b) for a, b, data in bgraph.edges(data=True) if data['capacity'] == 0] #create a list of edges with no capacity
    for start, end in nocap:
        sneighbors = [n for n in bgraph.neighbors(start)] 
        eneighbors = [n for n in bgraph.neighbors(end)]
        savg = sum([bgraph[s][start]['capacity'] for s in sneighbors])/len(sneighbors) #average of neighbours at start of link
        eavg = sum([bgraph[e][end]['capacity'] for e in eneighbors])/len(sneighbors) #average of neighbours at end of link
        bgraph[start][end]['capacity'] = (savg + eavg)//2
    if depth > 100: #if it doesn't converge at 100 iterations, stop
        print('no solution found')
        return
    if len(nocap) > 0: 
        fixCapacity(bgraph, depth)
    return
```
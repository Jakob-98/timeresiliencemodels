> add image
# Proposing a repoducible method of creating time resilience models in Python using NetworkX
This repo is used to showcase the methodology used in my thesis "Assessing time resilience of public transit networks using London Underground data". The motivation behind this study is to explore the importance of disruption time in public transport network resilience, and how to measure the changing impact over time. Here you can find a methodology to model a non-cascading time-dependent network model, estimating changing passenger loads in a public transport network. 

The thesis can be found here ## todo add

## Table of Contents
- [Data](#data)
- [Requirements](#requirements)
- [Preprocessing](#preprocessing)
- [Modelling](#modelling)
- [Processing results](#processing results)
- [closing words](#closing words)

## Data
For this research, we used passenger data from TFL (Transport For London) in order to estimate passenger loads on the London Underground network. However, our model methodology can be applied to other public transport networks using similar data. The passenger data used in the research can almost exclusively found on the TFL crowding open data website (Transport for London, n.d.-a). The data, published under the name project NUBMAT, contains a static view of travel patterns and usage of the TFL railway services. It contains passenger data for Monday-Thursday, and Friday, Saturday and Sunday separately. The Monday-Thursday data is aggregated, so therefore the data from Friday will be considered. The Friday dataset contains two datasets which are of importance to our research: the train frequency table is required in order to estimate the capacity of the links throughout the day, and the O-D (origin-destination) matrix is used to assign passengers to links using trip-assignment. An O-D Matrix shows the amount of passengers traveling between two stations during a certain time period, and is therefore representative for the trips passengers have taken in the network. The TFL O-D Matrix contains 8 discrete time-steps for which passenger journeys are shown, namely: 
['Morning (0500-0700)', 'AM Peak (0700-1000)', ‘Inter-Peak (1000-1600)', 'PM Peak (1600-1900)', 'Evening (1900-2200)', 'Late (2200-0030)', 'Night (0030-0300)', 'Early (0300-0500)']
Since these are the time-slots used in the source data, we will be using the same time-slots for the analysis of time dependency of network resilience. Notice that not all lengths of the time-slots are identical; the Morning timeslot is two hours, whereas the Inter-peak timeslot is 6. Lastly, an external source was used to create the London Underground network graph. This graph data was compared to TFL data in order to remove discrepancies between the data sources, such as station names that did not match. Appendix 8.1 in the attachment shows the data used for this paper and their respective sources. 

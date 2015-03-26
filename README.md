# apriori-algorithm
Implementation of an Apriori Algorithm and Rule generation with confidence pruning

## Usage
`python main.yp [dataset] [min_sup] [min_conf]`

`dataset` can be a url or a local .csv file.

`min_sup` is the minimum support value, default to 0.3

`min_conf` is the minimum confidence value to create rules, default to 0.6

##Dependencies
* Python 2.7
* This example knows how to transform data from: https://archive.ics.uci.edu/ml/machine-learning-databases/voting-records/house-votes-84.data

##Data Source
*    (a) Source:  
                Congressional Quarterly Almanac, 98th Congress, 
                 2nd session 1984, Volume XL: Congressional Quarterly Inc. 
                 Washington, D.C., 1985.

*    (b) Donor: Jeff Schlimmer (Jeffrey.Schlimmer@a.gp.cs.cmu.edu)
*    (c) Date: 27 April 1987 

##TODO
* Detailed documentation for education purposes
* Improve rule generation functions
* Tests

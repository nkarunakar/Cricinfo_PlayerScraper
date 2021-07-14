# Cricinfo_PlayerScraper
Python script to collect ball by ball data of a player's ODI career

# Python web scraping script to collect player ODI career data and analysis of the ODI career.

 ##### PlayerScraper.py script connects to cricinfo website & collects specified player's ODI career data ball by ball on per over basis.
 ##### The python script needs input based on Player's ID assigned to player's profile on Cricinfo
 ##### This data is stored in a form of csv file with relevant headers which can be used with Python Pandas library to perform analysis
 
 ---
 
 ## Requirements:
 
 Python==3.8.5
 
 requests==2.24.0
 
 json==2.0.9
 
 bs4==4.9.3
 
 
 ---
 
 
 ## Description:
 
 PlayerScraper.py connects to cricinfo webpage & collects publicly available data by walking through individual ODI matches in player's career.
 Player is identified by unique ID assigned to each player by Cricinfo website. **(More details in Usage section)
 Python script identifies individual Series & matches in the said series, opposition, innings #, etc & walks through commentary lines available for selected matches & converts this data into .csv format making it easier for analysis.
 
 **Data is available for all the matches that player has played where in cricinfo commentary feature is available.**
 
 **This usually translaters to any ODI cricket game player during & after 1996 ODI Cricket world cup.**
 

 
 ---
 
 

 ## Usage:

 Execute PlayerScraper.py using below command:

 ```C:\Cricket>python PlayerScraper.py <PLAYER_ID>```
 
 
 ```
C:\Cricket>python PlayerScraper.py -h
usage: PlayerScraper [-h] PlayerID

Get all ODI details of a player

optional arguments:
  -h, --help  show this help message and exit

  PlayerID    Specify the player ID
```

 <PLAYER_ID> is an integer value that corresponds to an existing Cricket player in Cricinfo

 Player ID can be obtained as shown below:
 For South African player Greame Smith, his player ID in Cricinfo is mapped to 47270
 
 
![PlayerID](https://user-images.githubusercontent.com/72927429/125595555-8935c10e-828d-40ea-92d4-3c69c85f9110.png)
 
 To collect ODI career data for Greame Smith, below command needs to be executed:
 
 ```C:\Cricket>python PlayerScraper.py 47270```
 
 Sample output:
![Output](https://user-images.githubusercontent.com/72927429/125599854-fc1d53b2-ae5d-4565-88cc-95e509489057.png)
 

 A Sample csv file with headers & data captured for Greame Smith is shown below:
 
 Header details:
 
	```SID = Series ID
	    
           MID = Match ID
	   
           CHASE (1-> true, 0-> False)
	   
           WON (1-> true, 0-> False)
	   
           OVER = Over number
	   
           TOTRUNS = Team Total runs at that over
	   
           TOTWKTS = Team Total wickets at that over
	   
           CSR = Current striker rate of player
	   
           RUNS = Runs scored by player
	   
           BALLS = Balls faced by player
	   
           ORUNS = Other player runs (other player is batsman at other end)
	   
           OBALLS = Balls faced by other player
	   
           OBCSR = Other batsman current strike rate
	   
           TGT = Target score, valid only if CHASE is true
	   
           RRR = Required run rate, valid only if CHASE is true
	   
           OUT (1 -> Player dismissed in game, 0 -> Player is not dismissed)
	   
           DELTASR = Striker difference for Player between previous & current over
	   
           CRR = Current run rate
	   
           SERIES_NAME = Name of series
	   
           FINISHED (1-> Final entry for match)
	   
           START (1-> Innings started)```

![SampleSuccess](https://user-images.githubusercontent.com/72927429/125600108-bc672d72-f146-4ae4-a6f5-1209bae77a10.png)

 Additional .csv files for different players are available in Examples folder.
 
 A Sample Analysis done for Indian ODI cricket captain MS Dhoni can be found in use_case folder.
 
 ---


## Future improvements:

* Support for Test innings

* Add checks to verify scorecard, to determine start & end over numbers, prior to data collection to optimize collection of data.

* Support to convert individual match into .csv files.

* Add logging to track operations.


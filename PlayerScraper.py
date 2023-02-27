import re, argparse, json, time
import requests
from bs4 import BeautifulSoup 


class cricketer:
    def __init__(self,PlayerID):
        self.__error=0
        self.__id=PlayerID
        self.__odiids=[]
        self.__URL=None
        self.__teamid=None
        self.__pname=None
        self.__country=None
        self.getNameAndCountry()
        if self.__error==0:
            self.getODIIDs()
            self.getTeamRef()


    def getODIIDs(self):
        if self.returnStatus:
            print("No data available")
            return
        #odiidsre=re.compile("[\s]*ODI[\s]+#[\s]+([0-9]+)")
        odiidsre=re.compile("/ci/engine/match/[0-9]+")
        URL="https://stats.espncricinfo.com/ci/engine/player/{}.html?class=2;template=results;type=batting;view=innings".format(self.__id)
        raw_form = requests.get(URL) 
        contentsoup = BeautifulSoup(raw_form.content, 'html.parser')
        mytable=contentsoup.find(string="Innings by innings list").find_parent("table")
        for row in mytable.find_all("tr")[1:]:
            tabledata=str(row.find_all("td"))
            if odiidsre.search(tabledata):
                self.__odiids.append(odiidsre.search(tabledata)[0])

            '''Converting content of soup to string so that I can search & find data - Alternate solution
            contentstr=str(contentsoup) #Convert bytes string to string type
            odiids.append(odiidsre.findall(contentstr))
            #       odiids.append(match)'''
            #print ("%s" %odiids)
        print("Found %d matches" %(len(self.__odiids)))

    def getNameAndCountry(self):
        if self.returnStatus:
            print("No data available for %d" %self.__id)
            return
        try:
            URL=r"https://www.espncricinfo.com/ci/content/player/{}.html".format(self.__id)
            raw_form = requests.get(URL) 
            if raw_form.status_code == 404:
                print("No data available for %d" %self.__id)
                self.__error=1
                return
        except Exception as e:
            repr(e)
            print("ERROR connecting to cricinfo website!!!\nPlease check internet connectivity or try again later")
            raise SystemExit

        contentsoup = BeautifulSoup(raw_form.content, 'html.parser')
        #self.__pname=contentsoup.find("div",{"class":"ciPlayernametxt"}).find("h1").text.strip() - OLD CRICINFO PAGE
        #self.__pname=contentsoup.find("div",{"class":"player-card__details"}).find("h2").text.strip()

        #For latest changes in Cricinfo layout below code is added
        #st=str(contentsoup.find("h1").parent())
        st=str(contentsoup.find("h1").parent())
        pattern1=r"([A-za-z ]+)$"
        #self.__country=re.search(pattern1,st.split("</h1")[1].split(">")[0]).group(0)
        self.__country=st.split("</span")[0].split(">")[-1]
        #self.__pname=re.search(pattern1,st.split("</h2")[0].split("</span")[0]).group(0)
        self.__pname=st.split("</h1")[0].split(">")[1]
        # Code block ends for latest changes in cricinfo layaout as of Sept 1st 2022

        #self.__country=contentsoup.find("div",{"class":"ciPlayernametxt"}).find("h3").find("b").text.strip()  - OLD CRICINFO PAGE
        #self.__country=contentsoup.find("div",{"class":"player-info"},{"class":"player-card__country-name"}).text.split("|")[0]
        self.__URL=r"https://www.espncricinfo.com/ci/content/player/{}.html".format(self.__id)
        print("Player's name -> %s\nPlayer's team -> %s" %(self.__pname,self.__country))


    def getTeamRef(self):
        if self.returnStatus:
            print("No data available")
            return
        hrefrestring="\"/team/{}-([0-9])+\"".format(self.__country.lower().replace(" ","-"))
        hrefre=re.compile(hrefrestring)
        URL=r"https://www.espncricinfo.com/team"
        raw_form = requests.get(URL) 
        contentsoup = BeautifulSoup(raw_form.content, 'html.parser')

        # Below code block is commented as its no longer applicable for latest Cricinfo layout - Sept 1st 2022

        #for row in contentsoup.find("div",{"class":"teams-section"}).find_all("a"):
        #    c=row.find("h5").text
        #    if c == self.__country:
        #        self.__teamref=hrefre.search(str(row)).group().split("=")[1].replace("\"","")
        #        break

        # For cricinfo layout as of Sept 2022
        for entry in contentsoup.find("div",{"class":"ds-grid"}).findAll("a"):
            if entry.text.strip()==self.__country:
                self.__teamid=int(hrefre.search(str(entry)).group(1))
        if self.__teamid:
            print("Team ID is %d" %self.__teamid)
        else:
            print("Team ID not found \n Exiting with error\n")
            raise SystemExit


    def getMatchDetails(self,URL):
        if self.returnStatus:
            print("No data available")
            return
        mlines=[]
        chase=0
        leg_URL=None
        retcode=1000
        tgtscore="NA"
        reqrate="NA"
        plid=None
        sname=""
        present=0
        overnum=0
        out=0
        played=0
        startph=0

        URLre=re.compile("/([\S]+?)/SCORECARDS", re.IGNORECASE)  # Observed SCORECARDS and SCORECARDs so ignoring case
        getcharsre=re.compile("([A-Za-z ]+)")
        matchidre=re.compile("([0-9]+).json")
        runsre=re.compile("([0-9]+)[\s]\(")
        ballsre=re.compile("([0-9]+)b")
        overre=re.compile("[0-9]*[0-9]+\.[0-9]")
        scardre=re.compile("SCORECARDS",re.IGNORECASE)  #For series with multiple nations
        string="href=\""+self.__URL+"\""
        playerre=re.compile(string)

        matchid=matchidre.search(URL).group(1)
        raw_form = requests.get(URL)
        mjson = json.loads(raw_form.content)

        htmlurl=URL.replace(".json",".html")   # Use pandas in future to read entire scorecard into a dataframe.
        raw_form = requests.get(htmlurl)
        msoup = BeautifulSoup(raw_form.content, 'html.parser')

        print("For match: %r with MATCHID %r" %(URL,matchid))
        if not mjson["comms"]:
            return mlines

        # For latest matches legacy_url is discontinued, so for such cases we rely in match_path for Series info
        if mjson["match"]["legacy_url"]:
            series_url=mjson["match"]["legacy_url"]
        elif mjson["match"]["match_path"]:
            series_url=mjson["match"]["match_path"]
        
        if URLre.search(series_url):
            leg_URL=URLre.search(series_url).group(1).split("/")[-1]
        else:
            leg_URL=series_url.split("/")[4]
        leg_URL=re.sub("[0-9]","",leg_URL)   # Remove numerical data such as year details.

        sid=0
        for i in range(len(mjson["series"])):
            if mjson["series"][i]["series_filename"] and mjson["series"][i]["series_filename"].find(leg_URL) >= 0:
                sname=mjson["series"][i]["series_name"]
                sid=mjson["series"][i]["object_id"]
                break
        else:   ##For series with multiple nations
            for i in range(len(mjson["series"])):
                if mjson["series"][i]["series_filename"]:
                    temp=re.sub("[0-9]","",mjson["series"][i]["series_filename"])
                    if scardre.search(temp):
                        sname=mjson["series"][i]["series_name"]
                        sid=mjson["series"][i]["object_id"]
                        break
        
        if sid==0:
            for entry in series_url.split("/"):
                if not sid==0:
                    break
                entry=re.sub("[0-9]","",entry)
                for i in range(len(mjson["series"])):
                    if mjson["series"][i]["series_filename"]:
                        temp=re.sub("[0-9]","",mjson["series"][i]["series_filename"])
                        if len(entry) > 2 and entry.find(temp) >= 0:
                            sname=mjson["series"][i]["series_name"]
                            sid=mjson["series"][i]["object_id"]
                            break
        if sname:
            print("Series name is %s" %sname)
        else:
            sname="NOT AVAILABLE"
            print("Series name is %s" %sname)

        if int(mjson["match"]["team1_id"])==self.__teamid:
            oppteam=mjson["match"]["team2_name"]
        else:
            oppteam=mjson["match"]["team1_name"]

        if int(mjson["match"]["batting_first_team_id"])==self.__teamid:
           innings=1
           print("Batting first")
        else:
            innings=3
            chase=1
            print("Batting second")
        if mjson["match"]["result_name"].find("result") >= 0:
            print("NO RESULT - SKIP")
            WON=2
            return mlines
        elif int(mjson["match"]["winner_team_id"]) == self.__teamid:
            print("%s WON" %self.__country)
            WON=1
        else:
            print("%s LOST" %self.__country)
            WON=0
        print("%d" %innings)
        scorecard=msoup.find_all("table")[innings-1]

        '''for row in scorecard.find_all("tr"):
            data=str(row.find_all("td")[0])
            if data.find(text) >= 0:
                if playerre.search(data):
                    if "not out" in row.find_all("td")[1]:
                        out=0
                    else:
                        out=1
                runs=int(row.find_all("td")[2])
                balls=int(row.find_all("td")[3])
                csr=float(row.find_all("td")[-1])
        
        #overnum? totruns? totwkts?  oruns? oballs? obscr? tgtscore? reqrate? deltasr?  
        mlines.append("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}"\
                            .format(sid,matchid,chase,WON,overnum,totruns,totwkts,csr,runs,balls,oruns,oballs,obcsr,tgtscore,reqrate,out,deltasr,sname))'''

        start=2
        oruns=0
        oballs=0
        sleep_time=30
        finished=0
        # Here we start, to further optimize maybe we can check scorecard to determine end over for each match for a player, so avoid reading till 50 overs
        # if batsman is dismissed in say first 5 overs. -> Maybe will do in future as code already exists to read scorecard for OUT & FOW details :)
        while [ True ]:
            try:
                URL2=r"https://hs-consumer-api.espncricinfo.com/v1/pages/match/comments?seriesId={}&matchId={}&inningNumber={}&commentType=ALL&fromInningOver={}"\
                .format(sid,matchid,innings,start)
                #print("Redone URL is %r" %URL2)
                raw_form1=requests.get(URL2)
                retcode=raw_form1.status_code
            except Exception as e:
                repr(e)
                print("CONNECTION - ERROR")
                retcode=1000
            #print("Request Status - %d" %retcode)
            #print("%r" %int(raw_form1.status_code) > 299 or int(raw_form1.status_code <= 199))
            if  (retcode > 299) or (retcode <= 199):
                print("Redone URL is %r" %URL2)
                print ("Status code recieved (1000->CONN ERROR) -> %d" %retcode)
                print ("Check connection, sleeping for %d seconds before next request...\n(Control+C to exit now)" %sleep_time)
                time.sleep(sleep_time)
                sleep_time=sleep_time+30
                if sleep_time > 900:
                    print ("EXITING - PLEASE CHECK CONNECTIVITY & TRY AGAIN")
                    raise SystemExit
                continue
            sleep_time=30
            commjson=json.loads(raw_form1.content)

            commcount=len(commjson["comments"])

            if commcount == 0:
                if start > 50 and overnum==50 and len(mlines) > 0:  #If start is over 50, i.e.,52 and overnum is 50 then all comments are read.
                    overnum=50
                    return mlines                    
                for row in scorecard.find_all("tr")[1:]:
                    data=str(row.find_all("td")[0])
                    if data.find("TOTAL") >= 0:
                        #fulline=row.find_all("td")[1].text
                        overnum=re.sub(r'[()]', '',row.find_all("td")[1].text.split()[0])
                        # Adjust below condition for 40.2 or 41.5 and ensure 40 & 50 are covered as well.
                        if len(overnum.split(".")) > 1 and int(overnum.split(".")[1]) > 0:
                            overnum=int(float(overnum) + 1)
                        else:
                            overnum=int(overnum)
                        (totruns,*totwkts)=map(int,row.find_all("td")[2].text.split("/"))
                        if not totwkts:
                            totwkts=10
                        else:
                            totwkts=totwkts[0]
                    if data.find("batsman-cell") >= 0:
                        data1=str(row.find_all("td"))
                        if playerre.search(data1):
                            played=1
                            if not mlines:
                                plname=getcharsre.search(row.find_all("td")[0].text).group()  
                            if row.find_all("td")[1].text.find("not out") >= 0:
                                out=0
                            else:
                                out=1
                            runs=int(row.find_all("td")[2].text)
                            balls=int(row.find_all("td")[3].text)
                            csr=float(row.find_all("td")[-1].text)
                            if len(mlines) > 0:
                                prevruns=mlines[-1].split(",")[8]
                                prevballs=mlines[-1].split(",")[9]
                                deltaruns=abs(int(runs)-int(prevruns))
                                deltaballs=abs(int(balls)-int(prevballs))
                                deltasr=mlines[-1].split(",")[16]
                                oruns=mlines[-1].split(",")[10]
                                oballs=mlines[-1].split(",")[11]
                                obcsr=mlines[-1].split(",")[12]
                                if deltaballs > 0:
                                    deltasr=(deltaruns/deltaballs)*100
                            else:
                                deltasr=0
                                oruns=0
                                oballs=0
                                obcsr=0
                                if out==1:
                                    fowlist="".join(scorecard.find_all("tr")[-1].text.split(":")[1:]).split(")")
                                    for entry in fowlist:
                                        if entry.find(plname) >= 0 or entry.find(self.__pname)>=0:
                                            (totwkts,totruns)=map(int,entry.split("(")[0].replace(",","").strip().split("-"))
                                            overnum=float(overre.search(entry).group())
                                            overnum=int(float(overnum)+1)
                                            reqrate=0
                                            if innings==2 and overmax != overnum:
                                                reqrate=(tgtscore-totruns)/(overmax-overnum)
                                            finished=1
                                            if overnum > 0:
                                                crr=totruns/overnum
                                            else:
                                                crr=0
                                            mlines.append("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}"\
                                                 .format(sid,matchid,chase,WON,overnum,totruns,totwkts,csr,runs,balls,oruns,oballs,obcsr,tgtscore,reqrate,out,deltasr,crr,sname,oppteam,finished,startph))
                                            return mlines
                reqrate=0
                if innings==2 and overmax != overnum:
                    reqrate=(tgtscore-totruns)/(overmax-overnum)
                # Ensure player batted in the innings, to eliminate "Did not bat" scenario
                if played==1:
                    finished=1
                    if overnum > 0:
                        crr=totruns/overnum
                    else:
                        crr=0
                    mlines.append("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}"\
                        .format(sid,matchid,chase,WON,overnum,totruns,totwkts,csr,runs,balls,oruns,oballs,obcsr,tgtscore,reqrate,out,deltasr,crr,sname,oppteam,finished,startph))
                return mlines
            for i in range(commcount-1,-1,-1):
                if present==1 and commjson["comments"][i]["isWicket"]:
                    #print("%r" %commjson["comments"][i]["dismissalText"])
                    if commjson["comments"][i]["dismissalText"]["commentary"].find(plname) >= 0 or commjson["comments"][i]["dismissalText"]["commentary"].find(self.__pname)>=0:
                        #We know batsman is dismissed, find his dismissal entry.
                        out=1
                        runs=runsre.search(commjson["comments"][i]["dismissalText"]["commentary"]).group(1)
                        balls=ballsre.search(commjson["comments"][i]["dismissalText"]["commentary"]).group(1)
                        csr=commjson["comments"][i]["dismissalText"]["commentary"].split(" ")[-1]
                        if len(mlines) > 0:
                            prevruns=mlines[-1].split(",")[8]
                            prevballs=mlines[-1].split(",")[9]
                            deltaruns=abs(int(runs)-int(prevruns))
                            deltaballs=abs(int(balls)-int(prevballs))
                            deltasr=mlines[-1].split(",")[16]
                            # back filling the data as we no longer find other batsman conclusively
                            oruns=mlines[-1].split(",")[10]
                            oballs=mlines[-1].split(",")[11]
                            obcsr=mlines[-1].split(",")[12]
                            if deltaballs > 0:
                                deltasr=(deltaruns/deltaballs)*100
                        else:
                            deltasr=0
                            oruns=0
                            oballs=0
                            obcsr=0
                        overnum=int(overnum)+1
                        totwkts=int(totwkts)+1
                        finished=1
                        if overnum > 0:
                            crr=totruns/overnum
                        else:
                            crr=0
                        mlines.append("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}"\
                            .format(sid,matchid,chase,WON,overnum,totruns,totwkts,csr,runs,balls,oruns,oballs,obcsr,tgtscore,reqrate,out,deltasr,crr,sname,oppteam,finished,startph))
                            #print("12-1: %r" %mlines)
                        return mlines
                if commjson["comments"][i]["over"]:
                    if tgtscore=="NA" and innings==2:   
                        chase=1
                        tgtscore=int(commjson["comments"][i]["over"]["target"])
                        overmax=int(commjson["comments"][i]["over"]["overLimit"])
                    #To accomodate for batsmen out on last ball of an over.
                    for j in range(len(commjson["comments"][i]["over"]["overEndBatsmen"])):
                        if int(commjson["comments"][i]["over"]["overEndBatsmen"][j]["player"]["objectId"])==self.__id:
                            #print("Processing over number %r" %commjson["comments"][i]["overNumber"])
                            present=1
                            plid=int(commjson["comments"][i]["over"]["overEndBatsmen"][j]["player"]["id"])
                            plname=commjson["comments"][i]["over"]["overEndBatsmen"][j]["player"]["name"]
                            #print("12 - Player name -> %r" %plname)
                            runs=int(commjson["comments"][i]["over"]["overEndBatsmen"][j]["runs"])
                            balls=int(commjson["comments"][i]["over"]["overEndBatsmen"][j]["balls"])
                            totruns=int(commjson["comments"][i]["over"]["totalRuns"])
                            totwkts=int(commjson["comments"][i]["over"]["totalWickets"])
                            overnum=int(commjson["comments"][i]["overNumber"])
                            if balls > 0:
                                csr=(runs/balls)*100
                            else:
                                csr="NA"
                            if len(mlines) > 0:
                                prevruns=mlines[-1].split(",")[8]
                                prevballs=mlines[-1].split(",")[9]
                                deltaruns=abs(int(runs)-int(prevruns))
                                deltaballs=abs(int(balls)-int(prevballs))
                                deltasr=mlines[-1].split(",")[14]
                                if deltaballs > 0:
                                    deltasr=(deltaruns/deltaballs)*100
                            else:
                                deltasr="0"  #First entry cant calculate deltra
                            if j==1 and int(commjson["comments"][i]["over"]["overEndBatsmen"][0]["balls"]) > 0:
                                oruns=commjson["comments"][i]["over"]["overEndBatsmen"][0]["runs"]
                                oballs=commjson["comments"][i]["over"]["overEndBatsmen"][0]["balls"]
                                obcsr=(oruns/oballs)*100
                            elif len(commjson["comments"][i]["over"]["overEndBatsmen"]) > 1 and int(commjson["comments"][i]["over"]["overEndBatsmen"][1]["balls"]) > 0:
                                oruns=commjson["comments"][i]["over"]["overEndBatsmen"][1]["runs"]
                                oballs=commjson["comments"][i]["over"]["overEndBatsmen"][1]["balls"]
                                obcsr=(oruns/oballs)*100
                            else:
                                obcsr="NA"
                            crr=totruns/overnum
                            if innings==2 and overmax != overnum:
                                reqrate=(tgtscore-totruns)/(overmax-overnum)
                            out=0
                            if overnum > 0:
                                crr=totruns/overnum
                            else:
                                crr=0
                            mlines.append("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}"\
                                .format(sid,matchid,chase,WON,overnum,totruns,totwkts,csr,runs,balls,oruns,oballs,obcsr,tgtscore,reqrate,out,deltasr,crr,sname,oppteam,finished,startph))
                            #print("12: %r" %mlines)
                elif present==1 and plid is not None:
                    #Check for player's dismissal
                    if  commjson["comments"][i]["isWicket"] and commjson["comments"][i]["dismissalText"]["commentary"].find(plname) >= 0 or commjson["comments"][i]["isWicket"] and commjson["comments"][i]["dismissalText"]["commentary"].find(self.__pname) >= 0:
                        #print("Is wicket is %r- Text is - %r" %(commjson["comments"][i]["isWicket"],commjson["comments"][i]["dismissalText"]["commentary"]))
                        out=1
                        runs=runsre.search(commjson["comments"][i]["dismissalText"]["commentary"]).group(1)
                        balls=ballsre.search(commjson["comments"][i]["dismissalText"]["commentary"]).group(1)
                        csr=commjson["comments"][i]["dismissalText"]["commentary"].split(" ")[-1]
                        if len(mlines) > 0:
                            prevruns=mlines[-1].split(",")[8]
                            prevballs=mlines[-1].split(",")[9]
                            deltaruns=abs(int(runs)-int(prevruns))
                            deltaballs=abs(int(balls)-int(prevballs))
                            deltasr=mlines[-1].split(",")[16]
                            #Use back fill to fill values.
                            # back filling the data as we no longer find other batsman conclusively
                            oruns=mlines[-1].split(",")[10]
                            oballs=mlines[-1].split(",")[11]
                            obcsr=mlines[-1].split(",")[12]
                            if deltaballs > 0:
                                deltasr=(deltaruns/deltaballs)*100
                        else:
                            deltasr=0
                            oruns=0
                            oballs=0
                            obcsr=0
                        overnum=int(overnum)+1
                        totwkts=int(totwkts)+1
                        finished=1
                        if overnum > 0:
                            crr=totruns/overnum
                        else:
                            crr=0
                        mlines.append("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}"\
                            .format(sid,matchid,chase,WON,overnum,totruns,totwkts,csr,runs,balls,oruns,oballs,obcsr,tgtscore,reqrate,out,deltasr,crr,sname,oppteam,finished,startph))
                        #print("12-1: %r" %mlines)
                        return mlines
            start=start+2

    def getAllODIDetails(self):
        if self.returnStatus:
            print("No data available")
            return
        rooturl=r"https://www.espncricinfo.com/"
        f=open(self.__pname.replace(" ","_")+".csv","a+",encoding="utf-8")
        '''SID = Series ID
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
           START (1-> Innings started)'''
        
        #Anything additional that needs to be added (for ex: Other player name, ground name, location...etc) needs to be addeded after DELTASR entry to 
        # avoid existing code from being affected, As we split based on index to calculate CRR, OBCSR, CSR etc for each row.
        hline="SID,MID,CHASE,WON,OVER,TOTRUNS,TOTWKTS,CSR,RUNS,BALLS,ORUNS,OBALLS,OBCSR,TGT,RRR,OUT,DELTASR,CRR,SERIES_NAME,OPPOSITION,FINISHED,START"
        f.write(hline+"\n")
        for entry in self.__odiids: #['ci/engine/match/597929']: #self.__odiids:
            finalurl=rooturl+entry+".json"
            mylines=self.getMatchDetails(finalurl)
            if len(mylines) > 0:
                mylines[0]=re.sub(',0$',',1',mylines[0])
                #print("%r",mylines)
                for line in mylines:
                    f.write(line+"\n")

    @property   
    def returnStatus(self):
        if self.__error==1:
            return True
        return False
            

if __name__=="__main__":
    my_parser = argparse.ArgumentParser(prog='PlayerScraper',description='Get all ODI details of a player')
    my_parser._positionals.title = "Mandatory arguments (Required)"
    group=my_parser.add_argument_group()
    group.add_argument('PlayerID',action='store',type=int,help="Specify the player ID")

    args = my_parser.parse_args()
    c1=cricketer(args.PlayerID)
    if not c1.returnStatus:
        c1.getAllODIDetails()
    else:
        print("Sorry!! %d does not match to any existing cricket player!!" %args.PlayerID)

import urllib
import xmltodict
from xmlutils.xml2csv import xml2csv
from difflib import SequenceMatcher
import csv

URL = 'https://hpi.de/fileadmin/user_upload/fachgebiete/naumann/projekte/repeatability/CORA/cora-all-id.xml'

def GetWebData(WebURL):
    file = urllib.request.urlopen(WebURL)
    data = file.read()
    file.close()

    data = xmltodict.parse(data)
    return data

def GetInstanceAuthor(Pub, Param, Key, Idkey):
    OutputList = []
    TempList = []
    tempstr = str()
    KeyList = []
    if Param in Pub.keys():
        if(isinstance(Pub[Param],list) == False):
            OutputList = Pub[Param][Key]
            KeyList = Pub[Param][Idkey]
        else:
            for Aut in Pub[Param]:
                if(isinstance(Aut,str) == False):
                    OutputList = Aut[Key]
                    KeyList = Aut[Idkey]
    else:
        OutputList = 'NAN'
        KeyList = 'NAN'

    return OutputList,KeyList

def GetInstanceTitle(Pub, Param):
    OutputList = []
    if Param in Pub.keys():
        for Title in Pub[Param]:
            OutputList.append(Title)
    else:
        OutputList.append('NAN')
        
    return OutputList

def GetInstanceVenue(Pub,Param,Key):
    OutputList = []
    if Param in Pub.keys():
        if Key in Pub[Param][Param].keys():
            OutputList.append(Pub[Param][Param][Key])
    else:
        OutputList.append('NAN')
    return OutputList

def ProcessNameDate(VenNameList):
    TempName = []
    TempDate = []
    TempStr = 'NAN'
    TempStrDate = 'NAN'
    for Name in VenNameList:
        if(len(Name) == 0):
            TempName.append('NAN')
        else:
            for NameEntry in Name:
                if isinstance(NameEntry,str) == True:
                    TempName.append(NameEntry)
                else:
                    TempStr = str()
                    for Index in NameEntry:
                        TempStr = TempStr + Index + " "
                    TempName.append(TempStr)
    return TempName

def MergeVenueName(VenIdList,VenNameList,VenDateList):
    TempId = []
    TempName = []
    TempDate = []
    

    
    for Id in VenIdList:
        for Entry in Id:
            TempId.append(int(Entry))

    VenNameList = ProcessNameDate(VenNameList)
    VenDateList = ProcessNameDate(VenDateList)
                    
    return TempId,VenNameList,VenDateList

def ParseData(InputData):
    TempAuthorList = []
    TempTitleList = []
    AuthorList = []
    TitleList = []
    PubIdList = []
    VenNameList = []
    VenDateList = []
    VenIdList = []
    Venue = ()
    TempPubId = []
    AutID = []
    
    for Pub in InputData['coraRADD']['publication']:
        tempAut, tempID = GetInstanceAuthor(Pub,'author','#text','@id')
        AuthorList.append(tempAut)
        AutID.append(tempID)
        PubIdList.append(Pub['@id'])
        TempTitleList.append(GetInstanceTitle(Pub,'title'))
        VenNameList.append(GetInstanceVenue(Pub,'venue','name'))
        VenIdList.append(GetInstanceVenue(Pub,'venue','@id'))
        VenDateList.append(GetInstanceVenue(Pub,'venue','date'))

            
    VenIdList,VenNameList,VenDateList = MergeVenueName(VenIdList,VenNameList,VenDateList)
      
    """for Authors in TempAuthorList:
        if Authors != ['NAN']:
            tempstr = str()
            for Entry in Authors:
                tempstr = tempstr + Entry + " "
            AuthorList.append(tempstr)
        else:
            AuthorList.append('NAN')"""

    for Title in TempTitleList:
        if Title != ['NAN']:
            tempstr = str()
            for Entry in Title:
                tempstr = tempstr + Entry + " "
            TitleList.append(tempstr)
        else:
            TitleList.append('NAN')


    
    return TitleList,PubIdList,AuthorList,AutID,VenIdList,VenNameList,VenDateList
        

def MergeVenueData(VenNameList,VenDateList):
    for i in range(0,len(VenNameList)):
        if VenNameList[i] == 'NAN':
            VenNameList[i] = VenDateList[i]
    return VenNameList

def showData(AuthorList,VenIdList,VenNameList,VenDateList):
    for i,j in zip(VenNameList,VenIdList):
        print(j," ",i)
    for i,j,k,l in zip(AuthorList,VenIdList,VenNameList,VenDateList):
        print(i,"!",j,"!",k,"!",l)

def LD(s, t):
    if s == "":
        return len(t)
    if t == "":
        return len(s)
    if s[-1] == t[-1]:
        cost = 0
    else:
        cost = 1
       
    res = min([LD(s[:-1], t)+1,
               LD(s, t[:-1])+1, 
               LD(s[:-1], t[:-1]) + cost])
    return res

def SimilarityMeasure(InputStr,ID,AvgLen):
    MatchList = []
    for i in range(0,len(InputStr)):
        for j in range(i+1,len(InputStr)):
            if InputStr[i] != 'NAN' and InputStr[j] != 'NAN':
                Sim = SequenceMatcher(None, InputStr[i], InputStr[j]).ratio()
                AverageLen = (len(InputStr[i]) + len(InputStr[j])) / 2
                if AverageLen < AvgLen:
                    if Sim > 0.9: # Similarity threshold is set as 0.9 for smaller strings
                        MatchList.append([ID[i],ID[j]])
                else:
                    if Sim > 0.7: # Similarity threshold is set as 0.7 for Larger strings
                        MatchList.append([ID[i],ID[j]])
            elif InputStr[i] == 'NAN' and InputStr[j] == 'NAN':
                MatchList.append([ID[i],ID[j]])
            else:
                # Do nothing
                None  
    return MatchList


def writeCSV(FileName,Matcheddata):
    with open(FileName,'w', newline='') as fp:
        writer = csv.writer(fp, delimiter=';')
        for i in Matcheddata:
            writer.writerow(i)

print("Program Started !!!!")    
print("Fetching Data from URL...")
InputData = GetWebData(URL)
print("Done")

print("Parsing Data from XML...")
TitleList,PubIdList,AuthorList,AutID,VenIdList,VenNameList,VenDateList = ParseData(InputData)
print("Done")


VenNameList = MergeVenueData(VenNameList,VenDateList)

#showData(AuthorList,VenIdList,VenNameList,VenDateList)


print("Calculating Similarity...")
MatchedAutName = SimilarityMeasure(AuthorList[:50],AutID[:50],4)
MatchedVenueName = SimilarityMeasure(VenNameList[:50],VenIdList[:50],8)
MatchedPublications = SimilarityMeasure(TitleList[:50],PubIdList[:50],8)
print("Done")

print("Updating CSV files...")
writeCSV("duplicates_authors1.csv",MatchedAutName)
writeCSV("duplicates_venues1.csv",MatchedVenueName)
writeCSV("duplicates_publications1.csv",MatchedPublications)


print("Done")

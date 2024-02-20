"""
Code to create and query televisionDB sqlite3 database.
Downloads the following files from IMDB:
title.basics.tsv.gz
title.ratings.tsv.gz
title.episode.tsv.gz
Creates the following tables:
TelevisionDB
EpisodeDB
RatingsDB

"""

import gzip
import unicodecsv
import sqlite3
import requests
import threading
import time
import os



def dbExists():
    """
    function that checks to see if the television.db file exists in the current working directory
    :return:
    """
    path=os.getcwd()
    if "television.db" in os.listdir():
        return True
    return False


def loadDB():
    """
    main function that calls other functions to download the data from the internet, create the database and load data
    into the database. Uses threads for downloading data concurrently, then events letting the functions know the data
    is available
    :return:
    """

    if (dbExists()):
        proceed=""
        while proceed.upper().strip() not in ('Y','N'):
            proceed=input("The television series database is already available in your directory.  Do you want to update it? (Y/N)")
        if (proceed.upper().strip() == 'N'):
            return


    start=time.time()
    e1=threading.Event()
    e2=threading.Event()
    e3=threading.Event()

    t1=threading.Thread(target=downloadFile, args=("https://datasets.imdbws.com/title.episode.tsv.gz", "title.episode.tsv.gz",e1))
    t2=threading.Thread(target=downloadFile, args=("https://datasets.imdbws.com/title.ratings.tsv.gz", "title.ratings.tsv.gz",e2))
    t3=threading.Thread(target=downloadFile, args=("https://datasets.imdbws.com/title.basics.tsv.gz", "title.basics.tsv.gz",e3))

    t1.start()
    t2.start()
    t3.start()

    loadTVEpisodes(e1)
    loadTVRatings(e2)
    loadTVBasics(e3)
    t1.join()
    t2.join()
    t3.join()
    cleanEpisodeDB()


    print(time.time() - start)
    return


def downloadFile(fileURL,fileName,eventName):
    """
    function to download a file and write the file to disk
    :param fileURL: IMDB URL
    :param fileName: name file will be called on hard disk
    :param eventName: which event to trigger when done
    :return:
    """
    try:
        reqFile=requests.get(fileURL)
        with open(fileName,"wb") as fh:
            fh.write(reqFile.content)
        eventName.set()
    except FileNotFoundError:
        print ("{:s} not found".format(fileURL))
        return 404


def loadTVEpisodes(eventName):
    """
    function to load the TVepisode data from file to DB
    :param eventName: event saying that the file is ready to be read
    :return:
    """
    eventName.wait()
    try:
        conn=sqlite3.connect('television.db')
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS EpisodeDB; ")
        cur.execute("CREATE TABLE EpisodeDB(TitleID TEXT not null,ParentID TEXT not null, SeasonNum INTEGER not null, EpisodeNum INTEGER not null)")
        with gzip.open('title.episode.tsv.gz', 'rb') as infile:
            reader=unicodecsv.reader(infile,delimiter="\t")
            for line in reader:
                if line[2].isdigit():
                    cur.execute("INSERT INTO EpisodeDB VALUES (?,?,?,?);",(line[0],line[1],line[2],line[3]))
        conn.commit()
        conn.close()
    except IOError:
            print("Error opening: title.episodes.tsv.gz")
            return -1
    return 0

def loadTVRatings(eventName):
    """
    function to load the TV ratings data from file to DB
    :param eventName: event saying that the file is ready to be read
    :return:
    """
    eventName.wait()
    try:
        conn=sqlite3.connect('television.db')
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS RatingsDB; ")
        cur.execute("CREATE TABLE RatingsDB(TitleID TEXT unique not null, Rating REAL)")
        with gzip.open('title.ratings.tsv.gz', 'rb') as infile:
            reader=unicodecsv.reader(infile,delimiter="\t")
            for line in reader:
                try:
                    rating=float(line[1])
                    cur.execute("INSERT INTO RatingsDB(TitleID,Rating) VALUES(?,?);",(line[0],rating))
                except:
                    pass
        conn.commit()
        conn.close()
    except IOError:
            print("Error opening: title.ratings.tsv.gz")
            return -1
    return 0

def loadTVBasics(eventName):
    """
    function to load the TV series data from file to DB
    :param eventName: event saying that the file is ready to be read
    :return:
    """
    eventName.wait()
    try:
        conn=sqlite3.connect('television.db')
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS TelevisionDB; ")
        commandStr="CREATE TABLE TelevisionDB(TitleID TEXT unique not null, TitleName TEXT not null,"
        commandStr=commandStr + " TitleType TEXT not null, StartYear TEXT, EndYear TEXT)"
        cur.execute(commandStr)
        with gzip.open('title.basics.tsv.gz', 'rb') as infile:
            reader=unicodecsv.reader(infile,delimiter="\t")
            for line in reader:
                if (line [1] in ('tvSeries')):
                    cur.execute("INSERT INTO TelevisionDB(TitleID,TitleName,TitleType,StartYear,EndYear) VALUES (?,?,?,?,?);",(line[0],line[2],line[1],line[5],line[6]))
        conn.commit()
        conn.close()
    except IOError:
            print("Error opening: title.basics.tsv.gz")
            return -1
    return 0

def cleanEpisodeDB():
    """
    function to delete all records in the episode DB which do not have associated ratings data
    :return:
    """
    command="delete from EpisodeDB where titleID not in (select distinct titleID from RatingsDB)"
    SQLConn("television.db",command)




def searchTVSeries(searchValue):
    """
    Function to search titleName in televisionDB table for searchv alue
    :param searchValue: string to match to titleName
    :return: list of TVseries  tuple data matching the search criteria sorted by titleName.
    Tuples consist of titleID, titleName, startYear, endYear
    """
    sv=searchValue.strip()

    command="Select titleID, titleName,startYear,endYear " \
            "from TelevisionDB t " \
            " where titleName like '%{:s}%'".format(sv)
    command =command + "and titleID in (select distinct parentID from EpisodeDB)"
    command=command + " order by titleName"
    return SQLConn("television.db",command)


def getSeriesData(titleID):
    """
    Function to find all the Series data for a particular series
    :param titleID: titleID of the series
    :return: return all record data from one record in televisionDB
    """
    command="select * from televisionDB where titleID='{:s}'".format(titleID)
    return SQLConn("television.db",command)

def getEpisodeData(seriesID):
    """
    Function to return all episode and ratings data for a TV series.
    :param seriesID: titleID of the TV Series
    :return: list of tuples of episode data sorted by seasonNum, episodeNum. Tuple consists of (TVSeriesID, EpisodeID,
    seasonNum,episodeNum,rating)
    """
    command="select parentID,e.titleID,seasonNum,episodeNum,rating from EpisodeDB e join RatingsDB r on e.titleID=r.titleID "
    command=command + "where e.parentID='{:s}'".format(seriesID) + " order by e.seasonNum, e.episodeNum"
    return SQLConn("television.db",command)

def getSingleEpisodeData(episodeID):
    """
    Function to return all episode data for a single episode
    :param episodeID: titleID of the episode
    :return: Tuple of episode data consisting of (TVSeriesID, EpisodeID,
    seasonNum,episodeNum,rating)
    """
    command="select parentID,e.titleID,seasonNum,episodeNum,rating from EpisodeDB e join RatingsDB r on e.titleID=r.titleID "
    command=command + "where e.titleID='{:s}'".format(episodeID) + " order by e.seasonNum, e.episodeNum"
    return SQLConn("television.db",command)

def SQLConn(database, command):
    """
    Function to make SQl connection to database and perform passed command.  Opens connection, executes command,
    commits and closes connection.
    :param database: database file to connect to
    :param command: sql command to execute
    :return: result of SQL command
    """
    conn=sqlite3.connect(database)
    cur=conn.cursor()
    cur.execute(command)
    result=cur.fetchall()
    #print(result)
    conn.commit()
    conn.close()
    return result

#TV Gui.py
import matplotlib
matplotlib.use('TkAgg')               
import tkinter as tk                      
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  
import matplotlib.pyplot as plt
import tkinter.messagebox as tkmb
import sqlite3 as sq
import numpy as np



from loadTVDatabase import loadDB, getEpisodeData, getSeriesData, dbExists, searchTVSeries


#Plotting window: lets user select type of chart, and then plot onto canvas. User can plot up to one of each chart onto canvas and can clear the canvas at any time
class plotWin(tk.Toplevel):
    #
    def __init__(self, master):
        
        super().__init__(master)
        
        #Variables to keep track of canvas positioning and limiting each type of chart to only be plot once
        self.i= 0
        self.trendbool = False
        self.barbool = False
        self.plotbool = False
        #-----------------------------------------------------------
        tk.Label(self, text = "Select Chart Type").grid()
        #Setting up the radio buttons for chart type choice
        self.graph = tk.StringVar()
        self.graph.set('trend')
        
        tk.Radiobutton(self, text = "Trend line", variable = self.graph, value = "trend").grid(sticky = 'w')
        tk.Radiobutton(self, text = "Bar Graph", variable = self.graph, value = "bar").grid(sticky = 'w')
        tk.Radiobutton(self, text = "Plot line", variable = self.graph, value = "plot").grid(sticky = 'w')
        #------------------------------------------------------------------------------------------------------
        tk.Button(self, text = 'plot', command = lambda : self.plot(master)).grid(row = 3, column = 1)
        tk.Button(self, text = 'clear', command = self.clear).grid(row = 3, column = 2)
        #Created frame to house the plotting canvas as well as a scrollbar for said canvas
        self.frame = tk.Frame(self)
        self.frame.grid(columnspan = 3)
       #Setting up the scroll bar to scroll the canvas
        self.canv = tk.Canvas(self.frame, width = 800, height = 500, scrollregion =(0, 0, 800, 1520))
        self.winScroll = tk.Scrollbar(self.frame, orient = 'vertical')
        self.winScroll.config(command = self.canv.yview)
        self.canv.config(yscrollcommand = self.winScroll.set)
        self.winScroll.pack(side = 'right', fill = 'y')        
        self.canv.pack(side= 'left', expand=True, fill= 'both')
        
        self.focus_set()
        self.grab_set()
        #-------------------------------------------------------------------------------------------------------
    #Clear callback to clear canvas, resetting sentinel variables and scrollbar to topmost position    
    def clear(self):
        self.canv.delete('all')
        self.i= 0
        self.trendbool = False
        self.barbool = False
        self.plotbool = False
        self.canv.yview_moveto(0)
    #Function to handle error windows    
    def displayError(self, errorTag):
        state=tkmb.showerror("Error", errorTag, parent=self)  
    #Function that handles all the labeling and tick adjustments for plotting    
    def labels(self, master):
        
        if master.choice.get() == 'epAvg': #if user selected plot by each episode of a season
            
            plt.title('Episode ratings for season '+master.seasonChoice)
            plt.ylabel('Rating out of 10')
            plt.xlabel('Episode Number')            
            plt.yticks(np.arange(1,11), np.arange(1,11))
            plt.xticks(np.arange(1,max(master.xdata)+1), np.arange(1,max(master.xdata)+1))
            
        elif master.choice.get() == 'SeasAvg': #if user selected plot by season averages
            
            plt.title('Average rating for each season of '+master.titleSelect)
            plt.ylabel('Rating out of 10')
            plt.xlabel('Season Number')
            plt.yticks(np.arange(1,11), np.arange(1,11))
            plt.xticks(np.arange(1,max(master.xdata)+1), np.arange(1,max(master.xdata)+1))
    
    #Function that finalizes and draws each plot when initiated, and positions it on the master canvas        
    def finalize(self, master):
        #adjusting canvas view when new plot is created
        if self.i == 505:
            self.canv.yview_moveto(.333)
        elif self.i == 1010:
            self.canv.yview_moveto(.667)
        
        self.labels(master)
        canvas = FigureCanvasTkAgg(self.fig, master= self.canv)
        self.canv.create_window(5,5+self.i, anchor = 'nw', window = canvas.get_tk_widget())            
        canvas.draw()
        self.i+=505        
        
    #Function that handles each type of plot's creation        
    def plot(self, master):     
        self.fig = plt.figure(figsize=(8, 5))
        
        if self.graph.get() == 'trend': # selected trendline 
            if self.trendbool == False:
                plt.scatter(master.xdata, master.ydata)
                z = np.polyfit(master.xdata, master.ydata, 1)
                p = np.poly1d(z)
                plt.plot(master.xdata,p(master.xdata),"r-")
                self.trendbool = True
                self.finalize(master)
            else:
                self.displayError("Chart already exists") # makes sure a max of only one of each plot is drawn at a time
            
        elif self.graph.get() == 'bar': # selected bar graph
            if self.barbool == False:
                plt.bar(master.xdata, master.ydata)
                self.barbool = True
                self.finalize(master)
            else:
                self.displayError("Chart already exists")            
            
        elif self.graph.get() == 'plot': # selected line plot
            if self.plotbool == False:
                plt.plot(master.xdata, master.ydata)
                self.plotbool == True
                self.finalize(master)
            else:
                self.displayError("Chart already exists")            
        
#Dialog window that prompts user to select a season. Only pops up if plot by episode of a season is selected in main win.        
class seasonWin(tk.Toplevel):
    
    def __init__(self, master):
        
        super().__init__(master)
        
        tk.Label(self, text = "Please Select a Season from "+master.titleSelect).grid()
        #Creating the list and selection variable
        self.seasons = master.seasons
        self.seasonNum = tk.StringVar()
        self.seasonNum.set("none")
        #Listbox & scrollbar
        self.S2 = tk.Scrollbar(self)
        self.LB2 = tk.Listbox(self, height= 15, width = 20)      
        self.LB2.grid(row=2, columnspan = 2)
        self.LB2.bind('<<ListboxSelect>>', self.selectS)
        self.S2.config(command = self.LB2.yview)
        self.S2.grid(row=2,column=2, sticky = 'ns')
        #---------------------------------------------------------
        
        #Button to lock in season selection and exit back to main win.
        tk.Button(self, text = "OK", command = lambda : self.lock(self)).grid()
        
        #Populating list box
        for item in self.seasons:
            if item != '\\N':
                self.LB2.insert(tk.END, item)
        
        self.focus_set()
        self.grab_set()
        self.transient(master)
               
        #Overrides exit to also set self.seasonNum to 'exit'
        self.protocol("WM_DELETE_WINDOW", self.exit)
    
    #Button callback to lock self.seasonNum and return to main win. Does nothing if no season is selected  
    def lock(self, *arg):
        if self.seasonNum.get() != "none":
            self.destroy()
        else:
            pass
    #callback to set self.seasonNum to user selected season    
    def selectS(self, arg):
        self.seasonNum.set(self.seasons[self.LB2.curselection()[0]])
    #returns selected season    
    def getSeason(self):
        return self.seasonNum.get()
    #if user exited via 'x'
    def exit(self, *arg):
        self.seasonNum.set("exit")
        self.destroy() 

#The main window
class mainWin(tk.Tk):
    #
    def __init__(self):
        super().__init__()
        
        #Variables to store user selections/sentinel for missing data
        self.epCheck = False
        self.titleSelect = None
        self.titleID = None
        self.seasonChoice = None
        
        tk.Label(self, text = "TV Shows").grid(columnspan = 2)
        #radio buttons & plot button
        self.choice = tk.StringVar()
        self.choice.set('epAvg')
        self.choiceLabel = tk.Label(self, text = "Plot Ratings by:")
        self.radio1 = tk.Radiobutton(self, text = "Seasonal Averages", variable = self.choice, value = "SeasAvg")
        self.radio2 = tk.Radiobutton(self, text = "Episode For One Season", variable = self.choice, value = "epAvg")
        self.choiceButton = tk.Button(self, text = "Plot", command = lambda : self.plotter(self))        
        
        self.choiceLabel.grid(sticky = 'w')
        self.radio1.grid(row = 1, column = 1, sticky = 'w')
        self.radio2.grid(sticky = 'w', column = 1)
        #Label and entry box for TV series search        
        tk.Label(self, text = "Search by TV Series Title (Min. 3 characters):").grid(sticky = 'w')
        self.entry = tk.StringVar()
        self.E = tk.Entry(self, textvariable = self.entry)
        self.E.grid(row = 3, column = 1)
        self.E.bind("<Return>", self.enter)        
        #Listbox & scrollbar
        self.S = tk.Scrollbar(self)
        self.LB = tk.Listbox(self, height= 15, width = 100)      
        self.LB.grid(row=5, columnspan = 2)
        self.LB.bind('<ButtonRelease-1>', self.select)
        self.S.config(command = self.LB.yview)
        self.S.grid(row=5,column=2, sticky = 'ns')
        
        self.choiceButton.grid()
        
        self.focus_set()
        self.grab_set()              
        
    #Callback for entry bind. Populates List box
    def enter(self, arg):
        self.LB.delete(0, tk.END) 
        self.userIn = self.entry.get()
        if len(self.userIn.strip()) >2:
            self.results = searchTVSeries(self.userIn) #List of tuples: [(TV series ID, Series Title, start year, end year)]
            
            if len(self.results) == 0: #checking if no matches
                self.displayError("There are no TV series titles that match with "+self.userIn)
            else:
                for record in self.results: 
                    if record[3] =='\\N':
                        temp = record[1]+' ('+record[2]+')'
                    elif record[2] == '\\N':
                        temp = record[1]+' <No data on years>'
                    else:
                        temp = record[1]+' '+record[2]+' - '+record[3]
                    self.LB.insert(tk.END, temp)
        else:
            self.displayError("Minimum 3 characters") #if entry under min. length
    #Callback for listbox selection. Prepares data to be plotted based on user selections           
    def select(self, arg):
        
        index = self.LB.curselection()[0]
        self.titleSelect = self.results[index][1]
        self.titleID = self.results[index][0]
        self.seasons = []
    
        self.episodeData = getEpisodeData(self.titleID) # list of tuples [(TV series ID, Ep ID, seasonNumber, Ep.Number, rating)...]
        for item in self.episodeData:
            if item[2] not in self.seasons:
                self.seasons.append(item[2])
        
        if self.choice.get() == 'SeasAvg': # selected season averages
            
            self.calcSeasData()        
            
        elif self.choice.get() == 'epAvg': # selected episodes for a season
            
            self.seasPop()
            
        else:
            self.displayError("Please select an option")
        
    #pops up dialog window for user to select season, checks for missing data, and prepares plot data     
    def seasPop(self):
        
        self.epCheck = False
        dialog = seasonWin(self)
        dialog.title('Select Season')
        self.wait_window(dialog)
        self.seasonChoice = dialog.getSeason()
    
        self.xdata = []
        self.ydata = []
        for item in self.episodeData:
            if str(item[2]) == self.seasonChoice:
                self.xdata.append(item[3])
                self.ydata.append(item[4])
        
        if self.seasonChoice != 'exit':
            if len(self.xdata) < max(self.xdata):
                self.epCheck = True # if missing records detected
        self.xdata = np.array(self.xdata)
        self.ydata = np.array(self.ydata)
        self.xdata = self.xdata.astype('int') 
    # prepares data to plot seasonal averages, checks for missing data
    def calcSeasData(self):
        
        self.epCheck = False
        datalist = [[] for s in self.seasons]
        for s in self.seasons:
            for item in self.episodeData:
                if item[2] == s:
                    datalist[self.seasons.index(s)].append(item[4])
                    
        if any(len(season) < max(season) for season in datalist):
            self.epCheck = True  # if missing records detected
    
        self.xdata = np.array(self.seasons)
        self.ydata = np.zeros(len(datalist))
        for i in range(len(datalist)):
            self.ydata[i] = round(sum(datalist[i])/len(datalist[i]), 2)        
    
    #Called by plotter function: sets up the plot window after checking to see if data is present and appropriate    
    def plotsetup(self):
        
        if self.choice.get() == 'epAvg':
            if self.seasonChoice != None and self.seasonChoice != 'exit':
                plot = plotWin(self)
                plot.title('Ratings')
                plot.maxsize = (815, 475)
            else:
                self.seasPop()
                
        elif self.choice.get() == 'SeasAvg':
            if self.seasonChoice == None:
                plot = plotWin(self)
                plot.title('Ratings')
                plot.maxsize = (815, 475)
            else:
                self.seasonChoice = None
                self.calcSeasData()
                plot = plotWin(self)
                plot.title('Ratings')
                plot.maxsize = (815, 475)
    #Function checks for title selection and missing data sentinel            
    def plotter(self, arg):
        if self.titleSelect != None:
            
            if self.epCheck == True:
                
                state = tkmb.askokcancel("Alert", "Some episode data is missing. Continue Plotting?", parent = self) #Asks for confirmation
                if state == True:
                    self.plotsetup()
            else:
                self.plotsetup()
                                        
        else:
            self.displayError("No Selection")
   
    #Function to handle error windows    
    def displayError(self, errorTag):
        state=tkmb.showerror("Error", errorTag, parent=self)
                

if __name__ == '__main__':        
    
    #console checks for DB file (creates if file does not exist) prompts user to update DB
    loadDB()
    app = mainWin()
    app.title('TV Series Lookup')
    app.mainloop()
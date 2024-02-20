TV Database Readme.txt
Nguyen Chau
Christina Shafer

Overall functionality:
This project allows a user to search for a TV Series and view plots of it's ratings.  Users can either view plots of ratings for one season at a time or choose to view each seasons average ratings.  

Files explained:

television.db:
A sqlite3 database file which contains the following 3 tables:
TelevisionDB - series name, ID, start and end years
EpisodeDB - series ID, episode ID
RatingsDB - episode ID, seasonNum, EpisodeNum, rating

loadTVDatabase.py:
All back-end functions for downloading data from IMDB (gzip files in tab seperated format), creating and populating the television.db file, and select functions for gathering data to display in the GUI
IMDB website: https://datasets.imdbws.com/

TV Gui.py
This file creates the front-end -- the GUI for the users to interact with the data stored in the database created in loadTVDatabase.py.

The Gui has three windows:

Main window -- The user can:
Choose to plot by:
plot by individual episode ratings for a user selected season
plot by seasonal average rating.
Search for TV series in the Entry box:
Minimum entry is 3 characters
Matches any title that contains input string
Select any matches to the search in the list box:
If user selected plot by episode, selecting a title, or pressing the plot button with no season selection, will pop up a dialog window for the user to choose a season from a listbox
Press the ‘plot’ button to bring up the plot window
If any missing data is detected (e.g. missing ratings for any episodes) pertaining to the user selection(s), a confirmation window will pop up asking for the user to confirm whether or not they wish to continue plotting.

Dialog window:
Allows user to select a season from the  selected TV series
If user clicks the ‘X’ the window closes without making any selection

Plot window:
Allows user to select type of chart/plot
The user can plot each type of chart once on the canvas below
The canvas has a scrollbar for the user to scroll through each chart they plotted if they wish to view more than one chart at a time
The user can press the ‘clear’ button to clear everything on the canvas (resetting the scrollbar to the top)





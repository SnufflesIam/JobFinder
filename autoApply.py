from bs4 import BeautifulSoup
from datetime import date
from autoApplyMods import *
import requests, re, webbrowser, os

# import the appJar library
try:
    from appJar import gui
except ModuleNotFoundError as e:
    import pip
    print(f"{e}. Importing appJar.")
    pip.main(['install', "appJar"])
    from appJar import gui
    
    
#The next step is to filter to only jobs that contain key words
def AutoApply(seek, indeed, gradconnection, searchTerms, country):
    
    #Object with links and instructions for each website
    websites = [{
        "website": "Seek",
        "dynamic": True,
        "baseURL": "https://www.seek.com.au",
        "link": f"{seek}",
        "jobREGEX": "/job/[\d]*"
    },
        {
        "website": "GradConnection",
        "dynamic": False,
        "baseURL": "https://au.gradconnection.com",
        "link": f"{gradconnection}",
        "jobREGEX": "/employers/[\w]*/jobs/[\w-]*/"
        },
        {
        "website": "Indeed",
        "dynamic": True,
        "baseURL": "https://au.indeed.com",
        "link": f"{indeed}",
        "jobREGEX": "https/pagead/clk?mo=r&ad=[.]*"
        }
                
]
    print("Getting the listings from each site...\n")
    jobLinks = []
    for item in websites:
        if len(item['link']) > 3:
            for job in GrabJobListings(item):
                jobLinks.append(job)
            
    print(f"Conducting search for '{searchTerms}' accross {country}...\n")
    broadSearch = []
    if len(searchTerms) > 0:
        try:
            broad_search = searchByTerms(searchTerms, country)
            broadSearch = broad_search
        except Exception as e:
            print(f"Error in broadSearch: {e}\nbroadSearch results contains {broadSearch}")


    print("Filtering each listing and getting details...\n")
    #Ask for user preferences, then action their choices
    applyJobs = []
    ignoredJobs = []
    #For each URL provided, scrape the job sites and add to approciate list
    apply_jobs, ignored_jobs = FilterJobListings(jobLinks)
    applyJobs = apply_jobs
    
    #For each result returned by the API, add to appropriate list
    for item in broadSearch:
        if item['ignored'] == False:
            applyJobs.append(item)
        else:
            ignoredJobs.append(item)
            
    print("Saving to database...\n")
    try:
        [SaveToDBS('A', job) for job in applyJobs]
        [SaveToDBS('I', job) for job in ignoredJobs]
    except KeyError as e:
        print(f"KeyError: {e}\n Check that the database has the appropriate tables.")
    except Exception as e:
        print(f"Error: {e}")

    print("----Jobs that can be applied to----")
    [print(f"{listing['jobListing']}\n") for listing in applyJobs]
    print("---The ignored job listings---")
    [print(f"Website: {item['website']}\nLink: {item['jobListing']}\nReason:{item['ignoreReason']}\n") for item in ignoredJobs]
    print("\n")
        
    loadPage = input("Enter the websites you'd like to open?\n'a' for all sites\n's' for seek,\n'g' for gradconection\n 'i' for indeed\n 'o' for broad search\n or nothing for nothing: ")
    if len(loadPage) > 0:
        print("Openning listings...\n")
        OpenJob(loadPage, applyJobs)
        
    editCL = input("Would you like a cover letter for each job? (y/n)")
    if editCL == "y":
        print("\nWriting cover letters...\n")
        [EditCoverletter("coverLetter.docx", listing) for listing in applyJobs]
        print(f'\nCover letters saved to {os.getcwd()}/CoverLetters/{date.today().strftime("%Y%m%d")}\n')

    print("Finished")
    
#Front-end code
#colour values
background = "black"
defaultText = "green"

#estbablish gui
app = gui()
app.setBg(f"{background}")
app.setFg(colour=f"{defaultText}")


#Configure the title and entry boxes

app.addLabel("title","JobFinder")
app.getLabelWidget("title").config(font="Times 20 bold")

#Section for URL scraping on SEEK, indeed and GradConnection
labelText = "Times 16"
app.addLabelEntry("Seek")
app.setEntry("Seek", "..")
app.getLabelWidget("Seek").config(font=f"{labelText}")

app.addLabelEntry("Indeed")
app.setEntry("Indeed", "..")
app.getLabelWidget("Indeed").config(font=f"{labelText}")

app.addLabelEntry("GradConnection")
app.setEntry("GradConnection", "..")
app.getLabelWidget("GradConnection").config(font=f"{labelText}")


#Broad search using apiJobss
app.addLabel("Broad Search Terms")
app.getLabelWidget("Broad Search Terms").config(font="Times 20 bold")

app.addLabelEntry("Search Terms")
app.setEntry("Search Terms","..")
app.getLabelWidget("Search Terms").config(font=f"{labelText}")

app.addLabelEntry("Country")
app.setEntry("Country","..")
app.getLabelWidget("Country").config(font=f"{labelText}")

try:
    def press(button):
        if button == "Cancel":
            app.stop()
        else:
            seek = app.getEntry("Seek")
            indeed = app.getEntry("Indeed")
            gradconnection = app.getEntry("GradConnection")
            searchTerms = app.getEntry("Search Terms")
            country = app.getEntry("Country")
            AutoApply(seek, indeed, gradconnection, searchTerms, country)
            
    app.addButtons(["Submit", "Cancel"], press)
    app.setButtonFg("Submit",f"{defaultText}")
    app.setButtonFg("Cancel","red")
    app.go()


except KeyboardInterrupt:
    print("Exiting gracefully :)")
except AttributeError as e:
    print(f"AttributeError: {e}")
except IndexError as e:
    print(f"IndexError: {e}")
except NameError as e:
    print(f"NameError {e}")
except ConnectionError as e:
    print(f"ConnectionError: {e}")
except RuntimeError as e:
    print(f"RuntimeError: {e}")
except TypeError as e:
    print(f"TypeError: {e}")
except re.error as e:
    print(f"REGEX error: {e}")
except Exception as e:
    print(f"Unknown error: {e}")

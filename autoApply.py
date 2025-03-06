from bs4 import BeautifulSoup
from datetime import date
from autoApplyMods import *
#from useful_functions import *
import requests, re, webbrowser, os

# import the appJar library
try:
    from appJar import gui
except ModuleNotFoundError as e:
    import pip
    print(f"{e}. Importing appJar.")
    pip.main(['install', "appJar"])
    


    
#The next step is to filter to only jobs that contain key words
def AutoApply(seek, indeed, gradconnection):
    
    #Object with links and instructions for each website
    websites = [{
        "website": "Seek",
        "dynamic": False,
        "baseURL": "",
        "link": f"{seek}",
        "jobREGEX": "/job/[\d]*"
    },
        {
        "website": "GradConnection",
        "dynamic": False,
        "baseURL": "",
        "link": f"{gradconnection}",
        "jobREGEX": "/employers/[\w]*/jobs/[\w-]*/"
        },
        {
        "website": "Indeed",
        "dynamic": True,
        "baseURL": "",
        "link": f"{indeed}",
        "jobREGEX": "https/pagead/clk?mo=r&ad=[.]*"
        }
                
]
    print("Getting the listings from each site...\n")
    jobLinks = []
    for item in websites:
        if len(item['link']) > 3:
            jobLinks.append(GrabJobListings(item))

    print("Filtering each listing and getting details...\n")
    #Ask for user preferences, then action their choices
    applyJobs = []
    ignoredJobs = []
    for item in jobLinks:
        apply_jobs, ignored_jobs = FilterJobListings(item)
        applyJobs.append(apply_jobs)
        ignoredJobs.append(ignored_jobs)
    print("Saving to database...\n")
    try:
        [SaveToDBS('A', job) for job in applyJobs]
        [SaveToDBS('I', job) for job in ignoredJobs]
    except KeyError as e:
        print("KeyError: {e}")
    except Exception as e:
        print(f"Error: {e}")
    for site in applyJobs:
        [print(f"{listing['jobListing']}\n") for listing in site]
    print("---The ignored job listings---")
    for site in ignoredJobs:
        if len(site) > 0:
            for website in site:
                [print(f"{key}: {value}") for key, value in website.items()]
                print("\n")
        
    loadPage = input("Enter the websites you'd like to open?\n's' for seek,\n'g' for gradconection\n 'i' for indeed\n or nothing for nothing: ")
    if len(loadPage) > 0:
        print("Openning listings...\n")
        for sites in applyJobs:
            OpenJob(loadPage, sites)
        
    editCL = input("Would you like a cover letter for each job? (y/n)")
    if editCL == "y":
        print("\nWriting cover letters...\n")
        for site in applyJobs:
            [EditCoverletter("coverLetter.docx", listing) for listing in site]
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


try:
    def press(button):
        if button == "Cancel":
            app.stop()
        else:
            seek = app.getEntry("Seek")
            indeed = app.getEntry("Indeed")
            gradconnection = app.getEntry("GradConnection")
            AutoApply(seek, indeed, gradconnection)
            
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



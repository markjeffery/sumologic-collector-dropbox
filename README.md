# SumoLogic-sumologic-collector-dropbox
SumoLogic collector and content for Dropbox Business
## Installation instructions
1. Choose a server that is running a SumoLogic collector. This server will need to access the dropbox API over the internet.
2. Install Python 2.7
3. Download and install the Python SDK for DropBox from: https://www.dropbox.com/developers/core
4. Create a DropBox for Business App. Go to https://www.dropbox.com/developers/apps/create/business
  1. Choose Team Auditing for permissions
  2. Provide an App Name (it needs to be unique)
  3. Note the App Key and App Secret. These details will be put into a config file.
5. Create the script, calling it dropbox_collector_for_sumologic.py (see Appendix A)
6. Create a config file, calling it dropbox_collector_for_sumologic.ini (see Appendix B)
  1. Put the App Key and App Secret inside the ini file in the [app_key] section
7. chmod +x dropbox_collector_for_sumologic.py
8. Execute the logger to create an access token:
  ./dropbox_collector_for_sumologic.py login
9. Test the logger to display up to 10 log lines. If this fails, retry the steps.
  ./dropbox_collector_for_sumologic.py test
10. Add source to collector as a script
  1. Frequency can be chosen as required (Every 5 minutes should be  OK)
  2. Command: /usr/bin/python
  3. Enter full path to collector script, e.g.: /usr/local/dropbox_collector_for_sumologic.py
    Working directory, e.g.: /usr/local
11. Import Library content (queries and dashboards)
  1. Open up "Library Export.json" in a text editor, substituting "_sourceCategory=DropBox" with the appropriate search string.
  2. Import json file using normal import method

Full Installation instructions (including screenshots) in pdf document in this repository

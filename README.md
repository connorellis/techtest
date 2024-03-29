# Interact with APIs - Connor Ellis
## Initial Setup


You will need to have python3.x installed, and the following modules:
* [venv](https://docs.python.org/3/library/venv.html) is used to create virtual environments
* [pybuilder](https://pybuilder.github.io/) is a build tool for Python

To activate the virtual environment and install the dependencies, run the following commands 
```bash
cd path/to/project

# setup new virtual environment 
python3 -m venv venv

# activate the virtual environment
# Note this was written on Ubuntu - you will need to run venv\Scripts\activate.bat if on Windows
source venv/bin/activate

# install dependencies
pip3 install -r requirements.txt
```

## Execution
This project is a CLI based and you can run the following commands to test the project
```bash
# Show help page
python3 src/main/python/tech_test.py -h

# test against the artist "Billie Eilish"
# I've chosen this artist as they only have small number of albums so it doesn't take too long
python3 src/main/python/tech_test.py -a "Billie Eilish"

# Run a few sample unit tests
pyb -v run_unit_tests
```

## Notes

There is still a lot of improvements that can be made on this project but I've cut a few corners in order to time-box (learning the various APIs took some time).


* Look at performance of the API - need to balance request rate vs 429 errors
    * Additionally improve the error handling around the API requests
* Add Paging for the musicbrainz API as it currently limited to 100 results in some cases 
* Add additional handling for non-studio albums as we are currently getting the lyrics for the same track across many albums
* Look at examples where lyrics can't be found due to slight mismatch in song name between the 2 APIs
    * This is difficult as the Lyrics API doesn't support browsing 
* Extend the unit test suite
* Extend the pandas data analysis




# Setup
1. Install python
2. Install required libraries
```
pip install -r requirements.txt
```
# Usage
```console
python scraper.py site mode --arguments
```
Where site can be:  
- sprites-resource 1
- model-resource 2
- texture-resource 3
- sound-resource 4  

Mode: 
- game: scrapes every game from urls file
- console: scrapes every game from given console

Example command for scraping every sprite from given console: 
```console
python scraper.py 1 console --console=mobile
```
Example command for scraping every sprite from games in urls file: 
```console
python scraper.py 1 game --urls=urls.txt
```
## urls file structure:
1. console
2. list of urls (1 per line)
### Example
```
mobile/
finalfantasybraveexvius/
```

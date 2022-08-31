Work in progress.
So far tested only on sprite resources

# Usage
Example command for scraping every sprite from given console: 
```console
python scraper.py site=1 mode=console --console=mobile
```
Example command for scraping every sprite from games in urls file: 
```console
python scraper.py site=1 mode=game urls=urls.txt
```
urls file structure:
1. console
2. list of urls (1 per line)
### Example
urls must end with '/' for now or it will crash
```
mobile/
finalfantasybraveexvius/
```

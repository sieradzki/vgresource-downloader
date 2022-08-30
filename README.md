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
1. main url
2. console
3. list of urls (1 per line)
### Example
urls must end with '/' for now or it will crash
```
https://www.spriters-resource.com/
mobile/
finalfantasybraveexvius/
```
# TODO
* [x] If single sprite - save in single/
* [x] Whole console scraping
* [ ] Provide option to scrape single game with game=game_name
* [ ] Check for link validity !!! 
* [ ] Error reporting (and handling)
* [x] Continue from last position after crash
* [ ] Ignore categories
* [x] Arguments
* [ ] Extract archives
* [ ] If filename exist (in case of same names) - increment number
* [ ] Code cleanup
* [ ] Nice(r) Readme

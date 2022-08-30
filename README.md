So far tested only on sprite resources

# Usage
urls file structure:
1. main url
2. console
3. list of urls (1 per line)
### Example
console url must end with '/' for now or it will crash
```
https://www.spriters-resource.com/
mobile/
finalfantasybraveexvius/
```
# TODO
* [x] If single sprite - save in single/
* [x] Whole console scraping
* [ ] Check for link validity !!! 
* [ ] Error reporting (and handling)
* [ ] Continue from last position after crash
* [ ] Ignore categories
* [ ] Arguments
* [ ] Extract archives
* [ ] If filename exist (in case of same names) - increment number
* [ ] Code cleanup
* [ ] Nice(r) Readme

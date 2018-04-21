This is an experiment of porting todoist-full-offline-backup to the web (purely client-side), through cpython-emscripten, a port of CPython to the browser.

## Requirements (possibly incomplete)

* Emscripten
* Wget
* Cython

## Instructions
* Run the makefile
* Run 'python3 -m http.server'
* Open http://localhost:8000 in the browser

## Things that need solving

* (Easy) Reduce the size of the JS files (don't embeed the entire cpython-emscripten).
* (Medium/hard) How to download the backups and attachments because of CORS.
  --> We could generate the backups through the API, which accepts CORS,
      but the attachments seem impossible without an extension to bypass CORS
* (Easy/medium) Create a decent UI
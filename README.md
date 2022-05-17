### Selenium Webscraping MyCareersFuture

## Purpose and Scope
- To develop a script to extract job posting data from mycareersfuture website
- To deploy it to aws and automate using lambda, storing data to s3

## Developing
# chromedriver and binary
- Chromium binary at https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-57/stable-headless-chromium-amazonlinux-2.zip
- chromedriver:
    - m1 > https://chromedriver.storage.googleapis.com/99.0.4844.51/chromedriver_mac64_m1.zip
    - linux > https://chromedriver.storage.googleapis.com/99.0.4844.51/chromedriver_linux64.zip
- Put chromedriver in PATH and change permission to executable (chmod 0755) for local testing
- Later docker to create PATH and copy files there



## Resources
- https://levelup.gitconnected.com/chromium-and-selenium-in-aws-lambda-6e7476a03d80
- https://github.com/adieuadieu/serverless-chrome/releases
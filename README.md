# Brute Force Quizzes (on Huskyct)

I wrote this in five hours don't judge me

## Description
* Logs in to huskyct
* Gets urls for all available quizzes
* Takes each quiz 20 times
  * We do this to ensure we get all feedback for all questions
  * Not robust but I wrote this for speed. There are at max five questions per test
  * Odds that we do not get all five questions (2 per try) after 20 times is very low.
* Each time it takes the quiz, it records feedback for every answer to a file called /tmp/quizzes.json
* The last time it takes the quiz, it makes sure to pick the correct answers

## Installation

> NOTE: (Probably) must be on a linux machine
> If you change the class attribute for quiz path you could (prob?) run it on windows
> But this is untested

```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get google-chrome-stable
```
NOTE: if you do not have google chrome installed, google: How to install google chrome linux
Then follow the cmd line args for installing chrome.

```bash
git clone git@github.com:jfuruness/brute_force_quizzes.git
cd brute_force_quizzes
sudo python3 setup.py develop
```
NOTE: if you are getting chromedriver errors, that means the chromedriver automatic install script has failed. Please contact jfuruness@gmail.com
## Usage
```
lib_brute_force_quizzes --brute_force --username myusernamehere --password mypasswordhere
```

## Developer notes:
* Christina wanted this to get feedback for every answer to study. It should be ***VERY*** easy to modify this program to only take each quiz enough times to get it correct.
* Also, you can prob skip all quizzes you have already taken in the for loop very easily
* I'm not going to make these changes because of time constraints on my end. Enjoy!

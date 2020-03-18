# The MoneyTracker Project
## Intro

MoneyTracker allows you to track your expenses and figure out what part of your money goes where. It does that by allowing you to create multiple virtual accounts which can be used to group related transactions, tag transactions and create charts to visualize your income and expenditures.


## Overview
The application is a typical django application so shouldn't be too surprising if you've used django before. In the past few years, I started adding some richer interaction in the form of javascript widgets. The approach is still the same preferring core django functionality that is enhanced using JS components instead of going all in and building an SPA.
 
The JS components are written using the [Vue](https://vuejs.org/) framework. Vue is great at adding piece-meal functionality to existing web applications. 
 
I started this project in 2006 and it has undergone many iterations. What started as a text file morphed into a spreadsheet that morphed into a desktop app that eventually became this web application. The web application itself also underwent many iterations jumping between frontend UI frameworks to eventually settle on [Bulma](https://bulma.io/) as a CSS framework and Vue for the JS framework.
 
The public release was in 2020 and reflects my needs for money tracking(get it? that's how the name came about...). A public and free instance for anybody to use is accessible at [moneytracker.codedemigod.com](https://moneytracker.codedemigod.com).  

### The backend
To run it, follow these basic steps:
* Copy *local_settings.py.sample* to *local_settings.py* to define your own local settings. The most important part of this file are the secret values.
* Create a virtual environment for the project by using pipenv and the enclosed Pipfile to create it.
* Install the requirements needed using pipenv `pipenv install`
* Run django's migrations via `./manage.py migrate`
* Run django's server via `./manage.py runserver`

### The frontend
The frontend mostly lives within the *assets/js* directory. And it consists of the Vue components that get bundled up and served via the django templates.
  
I use and recommend [yarn](https://yarnpkg.com/) for package management and the bundler used is [webpack](https://webpack.js.org/). [Babel](https://babeljs.io/) is the transpiler but the thing to note is although this is my preferred stack, anything that can run Vue can be used here. The Javascript world has been moving very quickly the past few years so blink and this stack might just be the "wrong" stack by the time you read this.
   
* To generate the frontend, run the `yarn` command in the main project directory to install the frontend requirements.
* `yarn watch` will run webpack in watch mode while you develop.
* A `yarn build` is also defined for production releases. 

# Skill Template
This is a template repo which acts as a framework for developers to create their own skill service endpoints on cloud functions in a much faster and efficient way


# Setup
## 1. Clone the repo
```
$ git clone git@github.com:keito-fukuda/mercari-ai-shain-skills.git
```

## 2. Create Skill Service repo from Template repo 
### 2.1. Create remote repo
Create a remote repo with the naming convention `mercari-ai-shain-skills-{skill_name}`

### 2.2. Change remote URL
Using below git command change the URL for your remote git repo
```
$ git remote set-url origin {git URL}
```
reference: https://docs.github.com/en/github/using-git/changing-a-remotes-url

### 2.3. Verify remote URL
Verify that the remote URL has changed to new `git URL` using below git command
```
$ git remote -v
```
### 2.4. Push remote repo
```
git push origin master
```

## 3. Creating Virtual Environment
This webhook will be run only in `Python 3.6` version. Inorder to manage the version of Python used, we have to create a virtual environment supports `Python 3.6`
```
$ python -m virtualenv -p /usr/bin/python3.6 venv
```
If you are already running Python 3.6, then use below command to create `venv`
```
$ python -m virtualenv venv 
```

## 4. Installing Packages
```
$ source venv/bin/activate  // actiavte virtual environment
$ pip install -r requirements.txt  // Install all dependencies
```


# Template Project Structure
## 1. Dependencies - requirements.txt
Manage required packages with requirements.txt. 
If you want to install the dependencies in a virtual environment, create and activate that environment first, then use the Install from requirements.txt command.
```
$ source venv/bin/activate  // actiavte virtual environment
$ pip install -r requirements.txt  // Install all dependencies
```
## 2. Logic - main.py
Logics to handle your skill must be included in `main.py`

## 3. Environment Variables - .env.template.yaml
Lists all environment variables required for your skill in `.env.template.yaml` file
```
$ cp .env.template.yaml .env.yaml
```
And add the corresponding environment variable values in `.env.yaml`

## 4. Locales - locales
Multi-lingual support for your service has been performed by including required locale files under `locales` directory
For eg.
Add `ja.yaml` file which includes messages in Japanese
Add `en.yaml` file which includes messages in English


# Deployment
```
$ gcloud config set project ${GCP_PROJECT_NAME}
$ gcloud functions deploy --trigger-http --env-vars-file .env.yaml --runtime=python37 --entry-point main [FUNCTION_NAME]
```

# Allow unauthenticated access to allUsers
```
$ gcloud alpha functions add-iam-policy-binding [FUNCTION_NAME] --member=allUsers --role=roles/cloudfunctions.invoker
```

# Share Endpoint URL
After successful deployment of the new `skill service` on `cloud function`, you need to share the `Target URL` for your endpoint on cloud function with the `respected team` so that they can configure the `webhook-proxy` to forward the requests to your endpoint.


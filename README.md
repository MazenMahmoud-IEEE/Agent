# Agent 

- this represents the final project of the Cellula Techonologies internship 
- we wil be completing task a week in seperate branches and the latest stable version will be merged into the main branch
- in the first week the target is to build a simple agent with context presence judge and web search as tools included so we will begin setting up the project structure and building those tools and testing them individually before integrating them into the agent
- we are using python 3.10 for this project 
- to install the required packages use the command: 
  ```
  pip install -r requirements.txt
  ```
- you have to install the ollama app in addition to the package in the requirements.txt to run it locally and download the model you want to use
after installing ollama run the command below to download the model
  ```
  ollama pull <model_name>
  ```
   for example to download the llama3.2:1b model run 
   ```
   ollama pull llama3.2:1b
   ```
- you can have the postman collection for testing the apis in the assets folder
- in the tools folder there are two tools context presence judge and web search for week 1
- in the prompts folder there is the prompts we are using for the tools
- in the tests folder there are unit tests for the tools
- in the api folder there are we transform the tools into apis using fastapi

# Take-Home Interview Challenge: Hidden Markov Model Map Matcher

The goal of this challenge is to demonstrate your ability to integrate a C++ library into a Python workflow, process streaming data, perform map matching, and deploy your solution in a containerized and orchestrated environment. Below are the steps and requirements.

---



## 1. Implement a Basic Hidden Markov Model (HMM) Map Matcher in C++

**Objective**: Write a C++ program that takes a sequence of GPS coordinates and outputs the most likely road segments (edges) that each trace visited.


**Guidelines**:
  - Given a road network (edges), the HMM should determine which edges were likely traveled based on the GPS trace.
  - A **basic** HMM map matcher is sufficient; it does not need to be cutting-edge. This is primarily to evaluate your application development skills.




## 2. Package the C++ Implementation into a Python Library

**Objective**: Compile your C++ code into a Python module.


**Guidelines**:
  - You can use whatever technology you want for this (e.g., using [pybind11](https://github.com/pybind/pybind11), [Cython](https://cython.org/), etc.)
  - Ensure the package can be installed into a Python environment (e.g., `pip install .`).




## 3. Build a Python Script that Uses the Package

**Objective**: Provide a Python script (e.g., `map_matcher.py`) which:
  1. Imports your C++/Python package.
  2. Instantiates the HMM-based map matcher.
  3. Exposes a function/method to process a list of GPS coordinates and returns the matched edges.




## 4. Integrate a Pulsar Queue and Save Results to PostgreSQL

**Objective**: Enhance your Python script or add additional scripts to:
  1. Push GPS traces to an [Apache Pulsar](https://pulsar.apache.org/) queue/topic.
  2. Read GPS traces from this topic and map match them with the HMM-based map matcher.
  3. Insert matched results into a PostgreSQL database table.




## 5. Create a Dockerfile

**Objective**: Package this entire solution (C++ code, Python code, Pulsar client, Postgresql server, Airflow server and UI, and dependencies) into one or more Docker containers.


**Guidelines**:
  - You can package everything as a single Dockerfile for ease of building, running, and sharing.
  - You can also choose to package everything using separate Dockerfiles. Just make sure the final output can be easily orchestrated and tested on Kubernetes, with clear directions on how to build and deploy everything.




## 6. Write a Kubernetes Job YAML

**Objective**: Provide one or more `.yaml` files that define the necessary Kubernetes resources to run your pipeline. At a minimum, include:
  - A Kubernetes **Job** resource that uses your Docker image(s).
  - Any additional manifests you need for other services (e.g., if Pulsar and PostgreSQL are also containerized and managed by Kubernetes).


**Guidelines**:
  - The Job should run your Python script to produce messages to Pulsar (if applicable) and process them once.
  - The Job should be able to run to completion after processing the data for the day.




## 7. Build an Airflow DAG

**Objective**: Create an Airflow DAG that kicks off this Kubernetes job every day at noon UTC.


**Guidelines**:
  - Use `python-airflow` or a typical Airflow DAG script (e.g., `dag_map_matcher.py`).
  - In the DAG:
    1. Create a task that triggers a Kubernetes job.
    2. Schedule it to run daily at 12:00 UTC.




## 8. Documentation on How to Run

**Objective**: Provide instructions for deploying and running the pipeline.


**Guidelines**:
  - Document any environment variables (e.g., `PULSAR_CONNECTION`, `POSTGRES_CONN`) and please make sure any secrets you provide can be safely shared publicly.
  - Provide any seed data or sample scripts to demonstrate local testing.

---



## Notes

- This bundle includes sample edge and event data that you can use to seed your pipeline.
- Each task in this take-home interview could, in a real-world setting, require months of development to perfect. Because this is only a take-home assignment, we recommend prioritizing task completion and clarity of approach over perfection.
- If there are additional considerations you would like to explore in any task, feel free to include notes discussing them.

---



## Bonus Considerations

- We want this problem to be open-ended, so if you feel the objective can be solved in a different, better way, please feel free to explore that.
- We will be paying attention to any additional work you put in above and beyond the requirements, but we want to be mindful of your time, so don't feel that it is in any way necessary.

---



## Deliverables

1. **C++ Source Code** for the hidden Markov model map matcher.
2. **Python Package** build files that wrap the C++ implementation.
3. **Python Script(s)** (map matcher) that integrates with Pulsar and PostgreSQL.
4. **Dockerfile(s)** that can build and run the entire application.
5. **Kubernetes Job YAML** (and any other Kubernetes YAML needed) to run your containerized solution.
6. **Airflow DAG** (Python-based) for daily scheduling at noon UTC.
7. **Documentation** (e.g., a `README.md` or similar) with build/run instructions.

---



## Submission Instructions

Provide a public Git repository (GitHub, GitLab, or equivalent) containing:
1. Source code for the HMM solution (C++ and Python).
2. Dockerfile, Kubernetes YAML, and Airflow DAG code.
3. A clear `README.md` covering how to build, run, and test locally, as well as how to deploy in Kubernetes and configure Airflow.
4. Any seed data and environment variables required to run the pipeline.

---



**Thank you for taking on this challenge!** We look forward to seeing your solution, code quality, and documentation. Good luck!

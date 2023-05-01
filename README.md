# TTM4115-group-14

Source code for TTM4115 project

**Teacher site**: https://ttm4115.diderikk.dev/teacher/  
**Student site**: https://ttm4115.diderikk.dev/student/


**CREDENTIALS:**  
Student:
```
email: student1@test.com
password: test123
```
Teacher:
```
email: teacher@test.com
password: test123
```

## Prerequisites

Poetry is a Python package manager and dependency manager that simplifies the process of managing Python projects and their dependencies. To install Poetry, you can use the following link to download the dependency:

[Poetry Link](https://python-poetry.org/docs/)

## Installing and run

To install and run the application, the user should first navigate to the project directory in their terminal and run the following commands:

```python
poetry install
hermes runserver
```

The application should now be available at http://127.0.0.1:8000/teacher/ and http://127.0.0.1:8000/student/.

## Docker
Otherwise, here are the steps to run the Django application using the provided Dockerfile:

Make sure that Docker is installed on your machine.

Navigate to the root directory of your project where the Dockerfile is located.

Open a terminal in the root directory.

Build the Docker image using the following command:

```bash
docker build -t \<image-name> .
```

Replace \<image-name> with the name you want to give to the Docker image. The . at the end specifies that the build context is the current directory.

Run the Docker container using the following command:

```
docker run -p 8000:8000 <image-name>
```

Open a web browser and go to http://127.0.0.1:8000/teacher/ or http://127.0.0.1:8000/student/ to access the application.

That's it! You should now be able to access and use the Django application.

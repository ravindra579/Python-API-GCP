## Python Rest Api & GCP bigquery
Gets the data realted to id which need to send as a request to the API and return the data related to the id in the big query 

## API Reference

#### Login

```http
  POST http://127.0.0.1:5000/login
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `email`   | `string` | **Required**.              |
| `password`| `string` | **Required**.              |

#### Get item

```http
  POST http://127.0.0.1:5000/bigquery
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `int`    | **Required**. Id of item to fetch |

#### Swagger Documentation urls

```http
   http://127.0.0.1:5000/swagger-ui
   http://127.0.0.1:5000/swagger
```

## Run Locally

Clone the project

```bash
  git clone https://github.com/ravindra579/Python-API-GCP.git
```

Go to the project directory

```bash
  cd Python-API-GCP
```

Install dependencies

```bash
  pip ...
```

Start the server

## Tech Stack

Python, Rest API's, GCP bigquery, SQL

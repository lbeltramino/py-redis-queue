# Redis Queue API

This project is a message queue system built with Flask and Redis. It exposes an API with three endpoints: pop, push, and count.

## API Endpoints

### Health
- Endpoint: /api/health
- Method: GET
- Response:
    - Status code: `200` if Redis is online, `500` if Redis is offline
    - Body:

    ```json
    {
        "status": "ok",
        "redis": "online"
    }
    ```
    or

    ```json
    {
        "status": "error",
        "redis": "offline"
    }
    ```

- Testing with curl:

    You can use the following curl command to check the health status:

    ```bash
    curl -X GET -H "x-api-key: your-api-key" http://localhost:5050/api/health
    ```

    Replace `your-api-key` with your actual API key.


### Pop
- Endpoint: /api/queue/pop
- Method: POST
- Body

    ```json
    {
        "n": <number_of_messages_to_pop>
    }
    ```

    If n is not provided in the request, it defaults to 1.

- Response:
    - Status code: 200
    - Body:
        
        ```json
        {
            "status": "ok",
            "messages": [<msg1>, <msg2>, ...]
        }
        ```

- Testing with curl:

    To pop a message from the queue, use the following command:

    ```bash
    curl -X POST -H "Content-Type: application/json" -H "x-api-key: your-api-key" -d '{"n":1}' http://localhost:5050/api/queue/pop

    ```

    Replace `1` with the number of messages you want to pop and `your-api-key` with your actual API key.

### Push
- Endpoint: /api/queue/push
- Method: POST
    - Body:

        ```json
        {
            "messages": [<msg1>, <msg2>, ...]
        }
        ```

    - Response:
        - Status code: 200
        - Body:

            ```json
            {
                "status": "ok"
            }
            ```
- Testing with curl:

    To push one or more messages to the queue, use the following command:

    ```bash
    curl -X POST -H "Content-Type: application/json" -H "x-api-key: your-api-key" -d '{"messages":["message1", "message2"]}' http://localhost:5050/api/queue/push

    ```

    Replace `"message1"`, `"message2"` with your actual messages and `your-api-key` with your actual API key.

### Count
- Endpoint: /api/queue/count
- Method: GET
- Response:
    - Status code: 200
    - Body:

        ```json
        {
            "status": "ok",
            "count": <count>
        }
        ```

- Testing with curl:

    To get the number of messages in the queue, use the following command:

    ```bash
    curl -X GET -H "x-api-key: your-api-key" http://localhost:5050/api/queue/count

    ```

    Replace `your-api-key` with your actual API key.

## Docker

The application is containerized using Docker. You can start the application using Docker Compose with the following command:

```shell
docker-compose up
```

This will start the Flask application, Redis, Prometheus, and Grafana.

## API Key
The API key is loaded from a configuration file named config.ini, which is mounted in the container with the Flask application. This file should have the following format:

```toml
[API]
Key = your-api-key
```

Replace your-api-key with your actual API key.

## Enhancements

### The API includes several enhancements:

- API authentication: Requests to the API must include a valid API key in the x-api-key header.
- Logging: The application logs information about each request to a file named app.log.
- Batch operations: The pop and push endpoints support batch operations.
- Metrics: The application exports metrics in the Prometheus format.
- Health check: The /api/health endpoint returns the health status of Redis.

### Automated provisioning of Prometheus and Grafana

This solution also includes the automated provisioning of Prometheus and Grafana services, which are essential for monitoring and visualizing the metrics of the application:

- Prometheus is a powerful monitoring and alerting toolkit that collects metrics from monitored targets by scraping metrics HTTP endpoints. In this project, Prometheus is configured to scrape the Flask application’s /metrics endpoint, where metrics about the API requests are exposed.

- Grafana is a multi-platform open-source analytics and interactive visualization web application. It provides charts, graphs, and alerts for the web when connected to supported data sources, in this case, Prometheus.

The docker-compose.yml file includes the configuration for both Prometheus and Grafana services: 

- The Prometheus service is configured with a volume that mounts the `prometheus.yml` file from the host to the `/etc/prometheus/prometheus.yml` file in the container. This file contains the configuration for Prometheus, including the targets to scrape.

    - Related URLs: 
        
        - Targets: 

        ```bash
            http://localhost:9090/targets
        ```

        - Metrics:

        ```bash
            http://localhost:5050/metrics
        ```



- The Grafana service is also configured with a volume that mounts the `./grafana-provisioning` directory from the host to the `/etc/grafana/provisioning` directory in the container. This directory contains Grafana configuration files that specify a data source and a dashboard that will be provisioned when Grafana starts up.

- Related URLs:

    - Grafana: 

        ```bash
        http://localhost:3000
        ```

        The default username and password are both `admin`. You may be prompted to change the password on your first login.




### Web Application for Testing
This solution includes a web application that you can use to test the API. The web application is built with HTML, CSS, and JavaScript, and it provides a user interface for interacting with the API.

The web application is also containerized using Docker and is part of the services defined in the docker-compose.yml file. When you start the application using Docker Compose, the web application will be available at http://localhost:8080.

#### Here’s how you can use the web application to test the API:

- API Key: Enter the API key in the API key input field. This should be the same API key that you’ve set in the config.ini file.

- Push: Enter one or more messages in the Push textarea, each on a new line. Click the Push button to send the messages to the queue. The response from the API will be displayed below the button.

- Pop: Enter the number of messages to pop in the Pop input field. Click the Pop button to remove the specified number of messages from the queue. The removed messages will be displayed below the button.

- Count: Click the Count button to get the number of messages currently in the queue. The count will be displayed below the button.


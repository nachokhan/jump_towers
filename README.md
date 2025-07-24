# Tower Jumps

This project is a web application that displays information about tower jumps.

## Running the project

To run this project, you will need to have Docker and Docker Compose installed.

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/nachokhan/tower_jumps.git
    cd tower_jumps
    ```

2.  **Create the environment files:**

    Create a `.env` file in the `api-gateway` directory with the following content:

    ```bash
    PROCESSOR_URL=http://processor:8001
    ```

    Create an empty `.env` file in the `processor` directory.

3.  **Build and run the services:**

    ```bash
    docker-compose up --build
    ```

4.  **Access the application:**

    Once the services are running, you can access the frontend at `http://localhost:3000`.

## Future Work

- Implement websockets to show the progress of the analysis.
- Enhance the analysis method to make it faster, if possible.
- Add time-window, threshold and method to the UI options.
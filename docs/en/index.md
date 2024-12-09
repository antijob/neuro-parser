# Welcome to the Project Documentation

Welcome to the documentation of our project. Here you will find all the information necessary to work with the project.

## About the Project

Neural Parser is a tool for parsing and analyzing news and content to detect incidents related to specific topics.  
The main goals of the project include:

- Processing and analyzing data from various sources.
- Tracking incidents and automatically filtering information.
- Sending notifications about significant events via Telegram and other platforms.

The project is built using modern technologies, including Python, Django, Docker, and Telegram Bot API, and is intended for use by both developers and administrators.

---

## Key Features

- **News and Data Parsing.** Utilization of external models for text processing.
- **Notifications.** Integration with Telegram for receiving updates on new incidents.
- **REST API.** A comprehensive interface with automatic documentation.
- **Infrastructure.** Ability to deploy the project on your own server.
- **Administrative Features.** Management of channels, incident category settings, and proxy usage for sources.

---

## Getting Started

### Local Deployment

1. Install dependencies using PDM:

    ```bash
    pdm install
    ```

2. Configure the `.env` file based on `.env.template`.
3. Start the containers:

    ```bash
    docker-compose up -d
    ```

4. Configure local domains in the `/etc/hosts` file:

    ```bash
    127.0.0.1 report.local
    ```

### Production Deployment

1. Configure the `.env` file and create the database.
2. Use the production configuration:

    ```bash
    docker-compose -f docker-compose.prod.yaml up -d
    ```

Detailed instructions are available in the file [developers.md](developers.md).

---

## Developer Guide

The following resources are available for development:

- **Dependency Management:** PDM.
- **Local Run and Debugging.**
- **API Documentation:** Swagger at `/swagger-ui`.

Read the complete guide [here](developers.md).

---

## Administration

The project provides robust administration tools:

- **Message broadcasting via Telegram.**
- **Category and source settings.**
- **Management of proxy servers for parsing.**

Administration instructions are available [here](administration.md).

---

## Contributing

We welcome community contributions. If you want to contribute to this project:

1. Review [CONTRIBUTING.md](https://github.com/antijob/neuro-parser/blob/main/CONTRIBUTING.md).
2. Open a PR with a description of the changes.

---

## Additional Resources

- [Project Repository](https://github.com/antijob/neuro-parser).
- [Contact Us](mailto:info@antijob.net).

---

If you have any questions, please contact us at <info@antijob.net>.

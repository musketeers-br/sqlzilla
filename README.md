[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat&logo=AdGuard)](LICENSE)

# SQLzilla

SQLzilla leverages the power of Python and AI to simplify data access through natural language SQL query generation, bridging the gap between complex data queries and users with minimal programming experience.

![SQLZilla made by AI](./assets/logo.png)

## Description

SQLzilla is an innovative project that transforms the way users interact with databases. By integrating with InterSystems IRIS, we've crafted a tool that allows even those unfamiliar with SQL to effortlessly extract and analyze data across various tables.

Our solution is designed to democratize data access, enabling users from diverse backgrounds—whether they be business analysts, managers, or educational professionals—to harness the full potential of data without the need to master technical query languages. Additionally, SQLzilla offers experienced users the ability to accelerate their workflow, enhancing productivity through its intuitive interface and powerful AI-driven capabilities.

We believe SQLzilla is not just a tool, but a movement towards more inclusive and empowered data interaction. Our project is rooted in the philosophy that access to data should be straightforward and barrier-free, opening up opportunities for more informed decision-making and innovative insights in organizations of all sizes.

We hope that SQLzilla serves as a catalyst for change, making data more accessible than ever and inspiring a new wave of users to engage with technology in meaningful ways.

Join us in redefining data interaction and expanding the possibilities of what we can achieve with information at our fingertips.

## Prerequisites

Ensure you have [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Docker Desktop](https://www.docker.com/products/docker-desktop) installed.

## Installation 

### Setting an LLM API Key

To utilize the Large Language Model (LLM) service, you'll need an API key. Currently, the project supports OpenAI's LLM service.

[Obtain your OpenAI API key by creating an account on their platform](https://openai.com/).

#### Configuring Environment Variables

Environment variables are used to store sensitive information like API keys and tokens. These variables need to be set before building the Docker image.

There are two ways to configure these variables:

When launching the Docker container, you can set the `OPENAI_KEY` environment variable using the `-e` flag:

```bash
# OpenAI API key
export OPENAI_KEY=$OPENAI_KEY
```

### Docker

Clone the repository into any local directory:

```bash
$ git clone https://github.com/musketeers-br/sqlzilla.git
```

Open the terminal in this directory and run:

```bash
$ docker-compose build --no-cache --progress=plain
$ docker-compose up -d
```

### Without Docker

1. Clone this repository.
2. Install dependencies: `pip install -r python/sqlzilla/requirements.txt`
3. Run the app: `streamlit run python/sqlzilla/app.py`

## How to Use It

### Jupyter Notebook Version
1. Add a `.env` file with the API key.
2. Go to [http://localhost:29999/](http://localhost:29999/).

### Web Version
1. Go to [http://localhost:8501/](http://localhost:8501/).
2. Enter your OpenAI API key for the AI assistant you also can add a `.env` file with the API key.
3. Configure the database connection details (default configuration for docker user).
4. Write SQL queries in the editor or chat window.
5. Click "Execute" to run queries and see results.

## Dream Team

Our team is a group of passionate individuals dedicated to tackling complex challenges and slaying metaphorical giants (think Godzilla, not spreadsheets)

![Musketeers tokusatsu style](./assets/tokusatsu_team.png)

* [Henry Pereira](https://community.intersystems.com/user/henry-pereira)
* [José Roberto Pereira](https://community.intersystems.com/user/jos%C3%A9-roberto-pereira-0)
* [Henrique Dias](https://community.intersystems.com/user/henrique-dias-2)
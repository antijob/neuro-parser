# Neural Parser

A neural parser is a tool for parsing and analyzing news and content to search for incidents related to a specific topic.

## Development

### Managing Python Packages

For managing Python packages, we use [PDM](https://pdm-project.org/):

```
# install all locked packages from lock file
pdm install

# resolve all dependencies and lock packages to lock file
pdm lock

# update all packages 
pdm update

# add new package to pyproject.toml
pdm add <package_name>
```

git should contain both pyproject.toml and pdm.lock files 


## Running local

Firstly create `.env` from `.env.template` and create database.

Run `docker-compose up -d` inside root directory for start local container.

Add for you `/etc/hosts` file record which resolve domain for local traefik

```
127.0.0.1 report.local
```

Open admin panel in `http://report.local/s/ecret/admin`

Or use api `http://report.local/api`


## Running production


Firstly modify `config/.env`, create database.

Run `docker-compose -f docker-compose.prod.yaml up -d` inside root directory for start local container.


## Contributing

We welcome contributions from the community. If you would like to contribute to this project, please follow the guidelines in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## Contact

If you have questions or need further assistance, please contact us at info@antijob.net.

# Telegram bot
You can use telegram bot to receive notifications about new incidents.

## Setup
To install it you need to register new bot with BotFather
Then add settings to .env file
```
TELEGRAM_BOT_TOKEN=
```
* TELEGRAM_BOT_TOKEN - Token from BotFather

Then you need to create new telegram chat and add bot there. That's all bot remember that group 
and will send notifications there. If you want receive notifications only for some of existing categories
use command ```/categ``` for bot settings. 
Also you can go to Django admin and check Bot section to explore channels that are saved. 

## Message Broadcasting Functionality

This project includes a feature that allows administrators to broadcast messages to multiple channels via the Django admin panel. 

## How to Use

### 1. Selecting Channels

1. Navigate to the Django admin panel of your project.
2. Open the list of channels (`Channel`).
3. Select the channels to which you want to send a message.

### 2. Using the Broadcast Function

1. After selecting the channels, choose the action "Send message to selected channels" from the actions dropdown menu.
2. Click the "Apply" button.
3. On the new page, enter the message text and confirm the selected channels.
4. Click the button to send the message.

### 3. Message Handling

- If no channels are selected, you will receive a warning "Channels not selected."
- Upon successful sending, you will receive a message indicating the number of channels the message was sent to.
- If an error occurs during sending, you will be notified in the admin panel.

Thank you for your contributions to the Neural Parser project!



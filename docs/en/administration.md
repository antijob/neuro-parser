# Administration of the project

Here are some features that may not be obvious but are important for using the project in case of independent installation.

## Sending messages to the bot

The project has a feature for administrators to send messages to multiple channels through the Django admin panel.

### How to use

Instructions for developers and setting up the project for local and production environments can be found in the file [developers guide](https://neuro-parser.readthedocs.io/ru/latest/ru/developers.html).

#### 1. Selecting channels

1. Go to the Django admin panel of your project.
2. Open the list of channels (`Channel`).
3. Select the channels you want to send a message to.

#### 2. Using the mass messaging feature

1. After selecting channels, select the action "Send message to selected channels" from the dropdown list of actions.
2. Click the "Apply" button.
3. On the new page, enter the text of the message and confirm the selected channels.
4. Click the button to send the message.

#### 3. Processing messages

- If no channels are selected, you will receive a warning "Channels are not selected".
- After a successful send, you will receive a message with the number of channels to which the message was sent.
- If an error occurs while sending, you will receive a notification in the admin panel.


## Disabling individual models for specific chats

There is a possibility to hide each individual category for each channel. This may be related to the need to separate models or security requirements.

### How to use

To do this, go to the admin panel in `Channel incident types`, find the record with the desired type of incident and channel ID, and open it. In the settings, a new field **show** has appeared. If it is enabled, the category is displayed in the channel settings in Telegram. If disabled, the category is not displayed.

### Features

- When the **show** field is disabled, the **status** field is also disabled. This means that if we hide a category for a channel, incidents from this category are no longer sent to this channel.


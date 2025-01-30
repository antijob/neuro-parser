# Project Administration

This document describes some functions that may not be obvious but are important for project usage in case of self-installation.

## Sending Messages to Bot

This project implements a feature for administrators to send messages to multiple channels through the Django admin panel.

### How to Use

Instructions for developers and project configuration for local and production environments can be found in the [DEVELOPERS.md](developers.md) file.

#### 1. Channel Selection

1. Go to the Django admin panel of your project.
2. Open the list of channels (`Channel`).
3. Select the channels where you want to send a message.

#### 2. Using the Broadcast Feature

1. After selecting channels, choose the action "Send message to selected channels" from the dropdown action list.
2. Click the "Apply" button.
3. On the new page, enter the message text and confirm the selected channels.
4. Click the button to send the message.

#### 3. Message Processing

- If no channels are selected, you'll receive a warning "No channels selected".
- After successful sending, you'll get a message indicating the number of channels the message was sent to.
- In case of an error during sending, you'll receive a notification in the admin panel.

## Disabling Specific Categories for Individual Chats

There is an option to hide each individual category for each channel. This may be related to the need to separate models or security requirements.

### How to Use

To do this, go to the admin panel in `Channel incident types`, find the entry with the desired incident type and channel ID, and open it. A **show** field now appears in the settings. If it is enabled, the category is displayed in the channel settings in Telegram. If disabled, the category is not shown.

### Features

- When the **show** field is turned off, the **status** field is also disabled. This means that if we hide a category for a channel, incidents from this category will no longer come to this channel.

## Hidden Telegram channels

Telethon client is used for parsing, its configuration is described in the [developer guide](developers.md).
To activate the client, check the box `"Hidden Telegram channel"` in the source settings

## Proxies for Sources

If necessary, you can make requests to sites through a proxy server. To do this, in the source settings, you need to indicate that a proxy is required, and directly in the Proxy section, add one or more proxy servers. At the moment, only HTTPS proxy is supported.

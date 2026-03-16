# Simon Says

> 🎮 🤖 Play Simon Says with TJBot!

This recipe uses the IBM [watsonx Assistant](https://www.ibm.com/products/watsonx-assistant) service to help TJBot play the game of Simon Says!

## Requirements

[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-3B+-cc342d)](https://www.raspberrypi.org/)
![LED](https://img.shields.io/badge/Hardware-LED-orange)
![Microphone](https://img.shields.io/badge/Hardware-Microphone-orange)
![Speaker](https://img.shields.io/badge/Hardware-Speaker-orange)
[![Node.js](https://img.shields.io/badge/Node.js-20%2B-yellow)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org/)

> [!CAUTION]
> We recommend a Raspberry Pi 4+ for local Text-to-Speech (TTS) synthesis. The recipe will work on other Raspberry Pi hardware using one of the cloud-based TTS backends.

## How it Works

IBM's [watsonx Assistant](https://www.ibm.com/products/watsonx-assistant) service is used to understand the commands you tell TJBot. TJBot listens to your voice using its microphone and uses a speech-to-text service to convert your speech into text. Next, that text is passed to watsonx Assistant which determines what you are trying to tell it to do, such as "wave your arm," "shine your light," or "repeat after me."

## Configure

> [!CAUTION]
> Make sure you have configured your Raspberry Pi for TJBot by following the [bootstrap instructions](https://github.com/ibmtjbot/tjbot/tree/master/bootstrap).

As this recipe demonstrates how to use IBM's [watsonx Assistant](https://www.ibm.com/products/watsonx-assistant) service, you will need to register for an IBM Cloud account.

### Register for an IBM Cloud account

If you do not already have an IBM Cloud account, [register for one](https://cloud.ibm.com/).

### Configure watsonx Assistant

> [!WARNING]
> TBD: These instructions need to be updated

Set up Watson Assistant using the following steps:

1. Launch the Watson Assistant tool and create a new assistant.
2. Click "Add dialog skill" and then "Import Skill."
3. Upload the `tjbot-action-sample.json` file.
4. Go back to the Assistants screen and click the menu (with the three dots), and click "Settings."
5. Click "API Details" in the left sidebar.
6. Copy the "Assistant ID".

In your `recipe.toml` file, fill in the `assistantId` and `environmentId` parameters with the Assistant ID you just retrieved.

## Run

You can run this recipe using the `tjbot` command or you can run it manually using `mise`.

### Run using `tjbot run`

Open a Terminal and run the following command from anywhere on your system:

```sh
tjbot run simon_says
```

> [!NOTE]
> `tjbot` invokes `mise` under the hood, which will automatically install any required software dependencies before running the recipe.

You should see the following output:

```sh
$ tjbot run simon_says

> simon_says@3.0.0 start
> tsx index.ts

TODO: ADD SAMPLE CONSOLE OUTPUT HERE
```

> [!IMPORTANT]
> The first time you run this script, your TJBot may download a Text to Speech and Speech to Text models. These downloads may take a little time, please be patient!

### Run manually using `mise`

Open a Terminal, navigate to this recipe's directory, and run using `mise`.

```sh
cd ~/.tjbot/recipes/simon_says
mise run start
```

## Customize

### Customization 1: Try a different LLM

Want to try a different large language model? Check out the [full list of large language models](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-api-model-ids.html?context=wx&audience=wdp) supported by watsonx.ai. and then change the `modelId` parameter in your `recipe.toml` file.

```toml
modelId = 'meta-llama/llama-3-70b-instruct'
```

### Customization 2: Change the LLM parameters

You can also try changing different [model parameters](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-model-parameters.html?context=wx&audience=wdp), such as the `modelDecodingMethod` and the `modelTemperature` to change how TJBot responds to you.

## Troubleshoot

If you are having difficulties in making your TJBot work, please see the [troubleshooting guide](https://github.com/tjbot-ce/tjbot/wiki/Troubleshooting-TJBot).

## Contribute

If you would like to contribute to TJBot, please see the [contributor's guide](https://github.com/tjbot-ce/tjbot/wiki/Contributing-to-TJBot).

## License

This project is licensed under Apache 2.0. Full license text is available in [LICENSE](../../LICENSE).

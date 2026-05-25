# Chat with TJ

> 🤖 🎤 Converse with TJBot using IBM watsonx.ai!

This recipe uses IBM's [watsonx.ai](https://www.ibm.com/products/watsonx-ai) service to turn TJBot into a conversational partner.

## Requirements

[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-3B+-cc342d)](https://www.raspberrypi.org/)
![Microphone](https://img.shields.io/badge/Hardware-Microphone-orange)
![Speaker](https://img.shields.io/badge/Hardware-Speaker-orange)
![LED](https://img.shields.io/badge/Hardware-LED%20(Optional)-orange)
[![Node.js](https://img.shields.io/badge/Node.js-20%2B-yellow)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org/)
[![watsonx.ai](https://img.shields.io/badge/IBM-watsonx.ai-0F62FE?logo=ibm&logoColor=white)](https://www.ibm.com/products/watsonx-ai)

> [!CAUTION]
> We recommend a Raspberry Pi 4+ for local Text-to-Speech (TTS) synthesis. The recipe will work on other Raspberry Pi hardware using one of the cloud-based TTS backends.

## How it Works

IBM's [watsonx.ai](https://www.ibm.com/products/watsonx-ai) service is an inference platform for large language models (LLMs). This recipe demonstrates how to use this service to create a conversational partner. TJBot listens to your voice using its microphone and uses a speech-to-text service to convert your speech into text. Next, that text is passed to an LLM to produce TJBot's chat response to you. Finally, that chat response is converted to audio using a text-to-speech service.

Here is a picture of how this works.

```mermaid
graph LR
    A["🎤 You speak"] --> B["Speech to Text (local or cloud)"]
    B --> C["Text input + conversational history"]
    C --> D["watsonx.ai (cloud-hosted LLM)"]
    D --> E["Chat response"]
    E --> F["Text to speech (local or cloud)"]
    F --> G["🔊 TJBot speaks"]

    style A fill:#e1f5ff
    style G fill:#e1f5ff
    style D fill:#fff3e0
```

## Configure

> [!CAUTION]
> Make sure you have configured your Raspberry Pi for TJBot by following the [bootstrap instructions](https://github.com/ibmtjbot/tjbot/tree/master/bootstrap).

As this recipe demonstrates how to use IBM's [watsonx.ai](https://www.ibm.com/products/watsonx-ai) service, you will need to register for an IBM Cloud account, obtain an IBM Cloud API key, and create a watsonx.ai project.

### Prepare your recipe's configuration

Create a `recipe.toml` file by copying the sample `recipe.sample.toml` file:

```sh
cp recipe.sample.toml recipe.toml
```

### Register for an IBM Cloud account

If you do not already have an IBM Cloud account, [register for one](https://cloud.ibm.com/).

### Obtain an IBM Cloud API key

Create an IBM Cloud IAM API key by following these steps:

1. Visit the [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys) page.
2. Click the blue "Create" button.
3. Type in a name for your API key and click "Create" (we recommend "TJBot"!)
4. Copy the API key. **Important**: Once you close the dialog, you will not be able to retrieve this API key in the future; instead, you will need to revoke the key and generate a new one.

Once you have your API key, add it to your `recipe.toml` file:

```toml
apiKey = '' # FILL IN WITH YOUR WATSONX.AI API KEY
```

### Create a watsonx.ai project

Create a watsonx.ai project by following these steps:

1. Launch [watsonx.ai](https://dataplatform.cloud.ibm.com/wx/home?context=wx) and sign in.
2. Click the "+" button in the "Projects" section and follow the steps to create a new project.
3. After the project has been created, click the "IBM watsonx" button at the top to navigate to the home screen.
4. In the "Developer access" box, select your project.
5. Copy the "Project ID" and paste it into your `recipe.toml` file under `projectId`.
6. Copy the "watsonx.ai URL" and paste it into your `recipe.toml` file under `serviceUrl`.

> [!TIP]
> In the United States, the watsonx.ai `serviceUrl` is `https://us-south.ml.cloud.ibm.com`.

## Run

You can run this recipe using the `tjbot` command or you can run it manually using `mise`.

> [!IMPORTANT]
> If you have configured your TJBot to use the local Text-to-Speech (TTS) backend, your TJBot may download a TTS model the first time you run this script. This download may take a little time, please be patient!

### Run using `tjbot run`

Open a Terminal and run the following command from anywhere on your system:

```sh
tjbot run chat_with_tj
```

> [!NOTE]
> `tjbot` invokes `mise` under the hood, which will automatically install any required software dependencies before running the recipe.

You should see the following output:

```sh
$ tjbot run chat_with_tj

> chat_with_tj@3.0.0 start
> tsx index.ts

...
```

### Run manually using `mise`

Open a Terminal, navigate to this recipe's directory, and run using `mise`.

```sh
cd ~/.tjbot/recipes/chat_with_tj
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

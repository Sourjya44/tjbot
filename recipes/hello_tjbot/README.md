# Hello, TJBot! <!-- markdownlint-disable-line MD026 -->

> :robot: :speaker: Say hello, TJBot!

This recipe provides a simple example for how to make TJBot say hello using Text to Speech (TTS).

## Requirements

[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-3B+-cc342d)](https://www.raspberrypi.org/)
![Speaker](https://img.shields.io/badge/Hardware-Speaker-orange)
[![Node.js](https://img.shields.io/badge/Node.js-20%2B-yellow)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org/)

> [!CAUTION]
> We recommend a Raspberry Pi 4+ for local Text-to-Speech (TTS) synthesis. The recipe will work on other Raspberry Pi hardware using one of the cloud-based TTS backends.

## How It Works

This recipe demonstrates TJBot's speech capabilities by having it say hello using text-to-speech synthesis. You can configure your TJBot to use one of the following text-to-speech backends:

- [Sherpa-ONNX](https://github.com/k2-fsa/sherpa-onnx) is a lightweight on-device speech recognition engine that requires no internet connection or cloud API keys.
- [IBM Watson Text to Speech](https://www.ibm.com/products/text-to-speech) is a cloud-based text-to-speech service offered by IBM.
- [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech) is a cloud-based text-to-speech service offered by Google.
- [Microsoft Azure Speech](https://azure.microsoft.com/en-us/products/cognitive-services/speech-services) is a cloud-based text-to-speech service offered by Microsoft.

## Configure

> [!CAUTION]
> Make sure you have configured your Raspberry Pi for TJBot by following the [bootstrap instructions](https://github.com/tjbot-ce/tjbot/wiki/Bring-TJBot-to-Life).

## Run

You can run this recipe using the `tjbot` command or you can run it manually using `mise`.

### Run using `tjbot run`

Open a Terminal and run the following command from anywhere on your system:

```sh
tjbot run hello_tjbot
```

> [!NOTE]
> `tjbot` invokes `mise` under the hood, which will automatically install any required software dependencies before running the recipe.

You should see the following output:

```sh
$ tjbot run hello_tjbot

> hello_tjbot@3.0.0 start
> tsx index.ts

...
```

> [!IMPORTANT]
> The first time you run this script, your TJBot may download a Speech to Text model. This download may take a little time, please be patient!

### Run manually using `mise`

Open a Terminal, navigate to this recipe's directory, and run using `mise`.

```sh
cd ~/.tjbot/recipes/hello_tjbot
mise run start
```

## Customize

### Customization 1: Change the greeting

You can change how TJBot greets you by editing `index.js` and modifying the text on this line:

```js
/* Customization 1: Change the greeting message */
await tj.speak('Hello! My name is TJBot and it is very nice to meet you!');
```

### Customization 2: Change the voice

Have TJBot speak in a different voice by editing your TJBot configuration. You can do this using the `tjbot config` configuration wizard.

You can also edit the `~/.tjbot/tjbot.toml` configuration file directly. Search for the `[speak.backend.local]` section and change this line:

```toml
model = 'vits-piper-en_US-ryan-medium'
```

to this:

```toml
model = 'vits-piper-en_US-kathleen-low'
```

You can find a full list of supported voice models in the [configuration guide](https://github.com/tjbot-ce/tjbot/wiki/Configuring-TJBot).

## Troubleshoot

If you are having difficulties in making this recipe work, please see the [troubleshooting guide](https://github.com/tjbot-ce/tjbot/wiki/Troubleshooting-TJBot).

## Contribute

If you would like to contribute to TJBot, please see the [contributor's guide](https://github.com/tjbot-ce/tjbot/wiki/Contributing-to-TJBot).

## License

This project is licensed under Apache 2.0. Full license text is available in [LICENSE](../../LICENSE).

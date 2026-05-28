# Parrot

> 🤖 🦜 Turn TJBot into a parrot!

This recipe turns TJBot into a parrot that listens for speech on the microphone and echoes what it hears.

## Requirements

[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-3B+-cc342d)](https://www.raspberrypi.org/)
![Microphone](https://img.shields.io/badge/Hardware-Microphone-orange)
![Speaker](https://img.shields.io/badge/Hardware-Speaker-orange)
[![Node.js](https://img.shields.io/badge/Node.js-20%2B-yellow)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org/)

> [!CAUTION]
> We recommend a Raspberry Pi 4+ for local Speech-to-Text (STT) recognition and Text-to-Speech (TTS) synthesis. The recipe will work on other Raspberry Pi hardware using cloud-based STT & TTS backends.

## How It Works

This recipe demonstrates TJBot's ability to listen to your speech using speech recognition and synthesize speech using text-to-speech synthesis. You can configure your TJBot to use one of the following speech-to-text and text-to-speech backends:

- [Sherpa-ONNX](https://github.com/k2-fsa/sherpa-onnx) is a lightweight on-device speech recognition engine that requires no internet connection or cloud API keys.
- [IBM Watson Speech to Text](https://www.ibm.com/products/speech-to-text) and [IBM Watson Text to Speech](https://www.ibm.com/products/text-to-speech) are cloud-based speech services offered by IBM.
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text) and [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech) are cloud-based services offered by Google.
- [Microsoft Azure Speech](https://azure.microsoft.com/en-us/products/cognitive-services/speech-services) is a cloud-based speech service offered by Microsoft.

## Configure

> [!CAUTION]
> Make sure you have configured your Raspberry Pi for TJBot by following the [setup instructions](https://github.com/tjbot-ce/tjbot/wiki/Bring-TJBot-to-Life).

## Run

You can run this recipe using the `tjbot` command or you can run it manually using `mise`.

> [!IMPORTANT]
> If you have configured your TJBot to use the local Text-to-Speech (TTS) and/or Speech-to-Text (STT) backends, your TJBot may download TTS/STT models the first time you run this script. These downloads may take a little time, please be patient!

### Run using `tjbot run`

Open a Terminal and run the following command from anywhere on your system:

```sh
tjbot run parrot
```

> [!NOTE]
> `tjbot` invokes `mise` under the hood, which will automatically install any required software dependencies before running the recipe.

You should see the following output:

```sh
$ tjbot run parrot

> parrot@3.0.0 start
> tsx index.ts

...
```

### Run manually using `mise`

Open a Terminal, navigate to this recipe's directory, and run using `mise`.

```sh
cd ~/.tjbot/recipes/parrot
mise run start
```

## Customize

### Customization 1: Change the Text-to-Speech and Speech-to-Text backend

Instead of performing Text-to-Speech and Speech-to-Text locally, try one of the cloud-based backends for these services. You can find instructions on how to set up these services in the [configuration guide](https://github.com/tjbot-ce/tjbot/wiki/Configuring-TJBot).

## Troubleshoot

If you are having difficulties in making this recipe work, please see the [troubleshooting guide](https://github.com/tjbot-ce/tjbot/wiki/Troubleshooting-TJBot).

## Contribute

If you would like to contribute to TJBot, please see the [contributor's guide](https://github.com/tjbot-ce/tjbot/wiki/Contributing-to-TJBot).

## License

This project is licensed under Apache 2.0. Full license text is available in [LICENSE](../../LICENSE).

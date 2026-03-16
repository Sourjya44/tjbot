# TJ Says

> 🎮 🤖 Play a game of TJ Says!

This recipe turns TJBot into a "Simon Says" game. TJBot will tell you to do things like touch your head, touch your ears, jump up and down, and your job is to follow its instructions! But be careful to only do what TJBot says when it says "TJ Says," otherwise you'll be out of the game!

## Requirements

[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-3B+-cc342d)](https://www.raspberrypi.org/)
![LED](https://img.shields.io/badge/Hardware-LED-orange)
![Microphone](https://img.shields.io/badge/Hardware-Microphone-orange)
![Servo](https://img.shields.io/badge/Hardware-Servo-orange)
![Speaker](https://img.shields.io/badge/Hardware-Speaker-orange)
[![Node.js](https://img.shields.io/badge/Node.js-20%2B-yellow)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org/)

> [!CAUTION]
> We recommend a Raspberry Pi 4+ for local Text-to-Speech (TTS) synthesis. The recipe will work on other Raspberry Pi hardware using one of the cloud-based TTS backends.

## How It Works

TJBot will choose an action at random and ask you to perform that action. It uses text-to-speech synthesis to speak the action out loud. It also shines its LED and waves its arm. You can configure your TJBot to use one of the following text-to-speech backends:

- [Sherpa-ONNX](https://github.com/k2-fsa/sherpa-onnx) is a lightweight on-device speech recognition engine that requires no internet connection or cloud API keys.
- [IBM Watson Speech to Text](https://www.ibm.com/products/speech-to-text) and [IBM Watson Text to Speech](https://www.ibm.com/products/text-to-speech) are cloud-based speech services offered by IBM.
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text) and [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech) are cloud-based services offered by Google.
- [Microsoft Azure Speech](https://azure.microsoft.com/en-us/products/cognitive-services/speech-services) is a cloud-based speech service offered by Microsoft.

> [!TIP]
> TJBot doesn't actually know whether you performed the action or not so this game is played on the honor system.

## Configure

> [!CAUTION]
> Make sure you have configured your Raspberry Pi for TJBot by following the [bootstrap instructions](https://github.com/tjbot-ce/tjbot/wiki/Bring-TJBot-to-Life).

## Run

You can run this recipe using the `tjbot` command or you can run it manually using `mise`.

### Run using `tjbot run`

Open a Terminal and run the following command from anywhere on your system:

```sh
tjbot run tj_says
```

> [!NOTE]
> `tjbot` invokes `mise` under the hood, which will automatically install any required software dependencies before running the recipe.

You should see the following output:

```sh
$ tjbot run tj_says

> tj_says@3.0.0 start
> tsx index.ts

TODO: ADD SAMPLE CONSOLE OUTPUT HERE
```

> [!IMPORTANT]
> The first time you run this script, your TJBot may download a Text to Speech model. This download may take a little time, please be patient!

### Run manually using `mise`

Open a Terminal, navigate to this recipe's directory, and run using `mise`.

```sh
cd ~/.tjbot/recipes/tj_says
mise run start
```

## Customize

### Customization 1: Add a new action

What other kinds of actions should TJBot ask you to do while playing the game? All of the actions are defined in the `recipe.toml` file. Edit this file and add some new actions. Be creative!

### Customization 2: Change the likelihood that TJBot doesn't say "TJ Says"

TJBot decides at random whether to say or not to say "TJ Says" when choosing the next action for you to perform. The likelihood that TJBot says "TJ Says" is defined in `recipe.toml` as `tjDidntSayLikelihood`. The default is `0.33`, which means that roughly one third of the time, TJBot will not say "TJ Says" before it asks you to do something. Try changing this value and see how it impacts your game!

## Troubleshoot

If you are having difficulties in making this recipe work, please see the [troubleshooting guide](https://github.com/tjbot-ce/tjbot/wiki/Troubleshooting-TJBot).

## Contribute

If you would like to contribute to TJBot, please see the [contributor's guide](https://github.com/tjbot-ce/tjbot/wiki/Contributing-to-TJBot).

## License

This project is licensed under Apache 2.0. Full license text is available in [LICENSE](../../LICENSE).

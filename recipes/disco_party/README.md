# Disco Party

> 🪩 Control TJBot's LED with your voice!

This recipe uses speech-to-text to let you control the color of TJBot's LED with your voice. For example, if you say "turn the light green," TJBot will change the color of the LED to green.

## Requirements

[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-3B+-cc342d)](https://www.raspberrypi.org/)
![LED](https://img.shields.io/badge/Hardware-LED-orange)
![Microphone](https://img.shields.io/badge/Hardware-Microphone-orange)
[![Node.js](https://img.shields.io/badge/Node.js-20%2B-yellow)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org/)

> [!CAUTION]
> We recommend a Raspberry Pi 4+ for local Speech-to-Text (STT) synthesis. The recipe will work on other Raspberry Pi hardware using one of the cloud-based STT backends.

## How It Works

This recipe demonstrates TJBot's capabilities to recognize speech by having it listen to your voice through the microphone. You can configure your TJBot to use one of the following speech-to-text backends:

- [Sherpa-ONNX](https://github.com/k2-fsa/sherpa-onnx) is a lightweight on-device speech recognition engine that requires no internet connection or cloud API keys.
- [IBM Watson Speech to Text](https://www.ibm.com/products/speech-to-text) is a cloud-based speech-to-text service offered by IBM.
- [Google Cloud Speech-To-Text](https://cloud.google.com/speech-to-text) is a cloud-based text-to-speech service offered by Google.
- [Microsoft Azure Speech](https://azure.microsoft.com/en-us/products/cognitive-services/speech-services) is a cloud-based speech-to-text service offered by Microsoft.

## Configure

> [!CAUTION]
> Make sure you have configured your Raspberry Pi for TJBot by following the [bootstrap instructions](https://github.com/tjbot-ce/tjbot/wiki/Bring-TJBot-to-Life).

## Run

You can run this recipe using the `tjbot` command or you can run it manually using `mise`.

### Run using `tjbot run`

Open a Terminal and run the following command from anywhere on your system:

```sh
tjbot run disco_party
```

> [!NOTE]
> `tjbot` invokes `mise` under the hood, which will automatically install any required software dependencies before running the recipe.

You should see the following output:

```sh
$ tjbot run disco_party

> disco_party@3.0.0 start
> tsx index.ts

TODO: ADD SAMPLE CONSOLE OUTPUT HERE
```

> [!IMPORTANT]
> The first time you run this script, your TJBot may download a Text to Speech model. This download may take a little time, please be patient!

### Run manually using `mise`

Open a Terminal, navigate to this recipe's directory, and run using `mise`.

```sh
cd ~/.tjbot/recipes/disco_party
mise run start
```

## Customize

### Customization 1: Change the duration and speed of the disco party

Try changing the duration and speed of the disco party. The `discoDuration` and `discoSpeed` variables are defined in the `discoParty` method:

```typescript
const discoDuration = 5 * 1000; // 5 seconds
const discoSpeed = 250; // change colors every 250ms
```

The `discoDuration` specifies for how many seconds the disco party will last (default: 5 seconds, computed as 5 * 1000ms). The `discoSpeed` specifies for how long TJBot will wait before changing the color of its led (default: 250 milliseconds).

> [!TIP]
> For an added challenge, change the code so that instead of picking colors at random, TJBot cycles through colors in a fixed pallete that you define!

### Customization 2: Use a cloud-based Speech to Text backend

Try out one of the cloud-based STT backends. You can do this using the `tjbot config` configuration wizard.

You can also edit the `~/.tjbot/tjbot.toml` configuration file directly. Search for the `[listen.backend]` section and change this line:

```toml
type = 'local'
```

to one of these:

- `type = 'ibm-watson-stt'` for IBM's [Speech to Text](https://www.ibm.com/products/speech-to-text) service
- `type = 'google-cloud-stt'` for Google's [Speech to Text](https://cloud.google.com/speech-to-text) service
- `type = 'azure-stt'` for Microsoft's [Speech to Text](https://azure.microsoft.com/en-us/products/cognitive-services/speech-services) service

> [!TIP]
> When using a cloud-based STT provider, you will need to create an instance of the STT service and download your authentication credentials. Check out [the configuration guide](https://github.com/tjbot-ce/tjbot/wiki/Configuring-TJBot) for instructions.

## Troubleshoot

If you are having difficulties in making this recipe work, please see the [troubleshooting guide](https://github.com/tjbot-ce/tjbot/wiki/Troubleshooting-TJBot).

## Contribute

If you would like to contribute to TJBot, please see the [contributor's guide](https://github.com/tjbot-ce/tjbot/wiki/Contributing-to-TJBot).

## License

This project is licensed under Apache 2.0. Full license text is available in [LICENSE](../../LICENSE).

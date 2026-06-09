# What Do You See?

> 🤖 👀 TJ, TJ, what do you see?

This recipe uses TJBot's camera and computer vision AI models to identify objects.

## Requirements

[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-3B+-cc342d)](https://www.raspberrypi.org/)
![Microphone](https://img.shields.io/badge/Hardware-Microphone-orange)
![Camera](https://img.shields.io/badge/Hardware-Camera-orange)
![LED](https://img.shields.io/badge/Hardware-LED-orange)
![Speaker](https://img.shields.io/badge/Hardware-Speaker-orange)
[![Node.js](https://img.shields.io/badge/Node.js-20%2B-yellow)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org/)

> [!CAUTION]
> We recommend a Raspberry Pi 4+ for local Speech-to-Text (STT) recognition and Text-to-Speech (TTS) synthesis. The recipe will work on other Raspberry Pi hardware using cloud-based STT & TTS backends.

## How It Works

This recipe demonstrates TJBot's ability to detect objects using its camera. It can use either a local computer vision model or cloud-based computer vision service to perform object detection. This process identifies a set of objects that may be present in an image along with a confidence for how likely it is that the object is actually in the image. TJBot will filter out low-confidence objects, pick one to focus on, and report its findings.

You can configure your TJBot to use one of the following computer vision backends:

- **ONNX vision (offline)** uses on-device object detection and image classification models, so it can run without internet access or cloud API keys.
- [Google Cloud Vision](https://cloud.google.com/vision) is a cloud-based computer vision service offered by Google.
- [Microsoft Azure AI Vision](https://azure.microsoft.com/en-us/products/ai-services/ai-vision) is a cloud-based computer vision service offered by Microsoft.

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
tjbot run what_do_you_see
```

> [!NOTE]
> `tjbot` invokes `mise` under the hood, which will automatically install any required software dependencies before running the recipe.

You should see the following output:

```sh
$ tjbot run what_do_you_see

> what_do_you_see@3.0.0 start
> tsx index.ts

...
```

### Run manually using `mise`

Open a Terminal, navigate to this recipe's directory, and run using `mise`.

```sh
cd ~/.tjbot/recipes/what_do_you_see
mise run start
```

## Customize

### Customization 1: Try a different computer vision backend

Edit your TJBot's configuration file to choose a different computer vision backend. You can do this using the `tjbot config` tool or by editing `~/.tjbot/tjbot.toml` yourself. Change the backend in `[see.backend]`:

```toml
[see.backend]
# 'type' chooses the CV provider:
#   'none'                -> disable computer vision
#   'local'               -> on-device ONNX (OFFLINE)
#   'google-cloud-vision' -> Google Cloud Vision (CLOUD)
#   'azure-vision'        -> Microsoft Azure Vision (CLOUD)
type = "local"
```

> [!TIP]
> Compare how the different backends perform. Do they recognize the same objects? Do they confuse one object for another? Do they have trouble recognizing some objects? 🤔

### Customization 2: Change the object detection confidence

Having trouble getting TJBot to recognize different objects? You can change the confidence level TJBot uses to determine which objects it actually sees by editing the `objectDetectionConfidence` parameter in your `~/.tjbot/tjbot.toml` file. The default is `0.8` which means that TJBot needs to be 80% confident that the object was detected for it to report it back to you. Try adjusting that threshold and seeing what happens!

## Troubleshoot

If you are having difficulties in making this recipe work, please see the [troubleshooting guide](https://github.com/tjbot-ce/tjbot/wiki/Troubleshooting-TJBot).

## Contribute

If you would like to contribute to TJBot, please see the [contributor's guide](https://github.com/tjbot-ce/tjbot/wiki/Contributing-to-TJBot).

## License

This project is licensed under Apache 2.0. Full license text is available in [LICENSE](../../LICENSE).

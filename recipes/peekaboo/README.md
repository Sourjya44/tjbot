# peekaboo

> 🙈 🙉 Play peekaboo with TJBot!

This recipe uses TJBot's camera and a facial detection model to play peekaboo!

## Requirements

[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-3B+-cc342d)](https://www.raspberrypi.org/)
![Camera](https://img.shields.io/badge/Hardware-Camera-orange)
![LED](https://img.shields.io/badge/Hardware-LED-orange)
![Speaker](https://img.shields.io/badge/Hardware-Speaker-orange)
![Servo](https://img.shields.io/badge/Hardware-Servo-orange)
[![Node.js](https://img.shields.io/badge/Node.js-20%2B-yellow)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org/)

## How It Works

This recipe implements an interactive peekaboo game using TJBot's camera, LED, servo arm, and speaker. The game starts when TJBot detects a face in its camera view. While waiting, it pulses its LED yellow. Once your face is detected, the game begins!

TJBot asks you to hide, then it keeps searching for you until it finds you. Once you reveal your face, TJBot celebrates by shining its light green, pointing its arm at you, and exclaiming "Peekaboo, I found you!"

After each round, TJBot shines its light orange and invites you to play again.

## Configure

> [!CAUTION]
> Make sure you have configured your Raspberry Pi for TJBot by following the [bootstrap instructions](https://github.com/ibmtjbot/tjbot/tree/master/bootstrap).

## Run

You can run this recipe using the `tjbot` command or you can run it manually using `mise`.

### Run using `tjbot run`

Open a Terminal and run the following command from anywhere on your system:

```sh
tjbot run peekaboo
```

> [!NOTE]
> `tjbot` invokes `mise` under the hood, which will automatically install any required software dependencies before running the recipe.

You should see the following output:

```sh
$ tjbot run peekaboo

> peekaboo@3.0.0 start
> tsx index.ts

TODO: ADD SAMPLE CONSOLE OUTPUT HERE
```

### Run manually using `mise`

Open a Terminal, navigate to this recipe's directory, and run using `mise`.

```sh
cd ~/.tjbot/recipes/peekaboo
mise run start
```

## Customize

### Customization 1: Adjust the face detection threshold

You can adjust the face detection threshold by editing your `~/.tjbot/tjbot.toml` configuration file and changing this line:

```toml
faceDetectionConfidence = 0.5
```

> [!NOTE]
> Higher values may make it harder for TJBot to recognize your face. Lower values may trigger false positives: TJBot thinks it found a face when it actually didn't.

## Troubleshoot

If you are having difficulties in making this recipe work, please see the [troubleshooting guide](https://github.com/tjbot-ce/tjbot/wiki/Troubleshooting-TJBot).

## Contribute

If you would like to contribute to TJBot, please see the [contributor's guide](https://github.com/tjbot-ce/tjbot/wiki/Contributing-to-TJBot).

## License

This project is licensed under Apache 2.0. Full license text is available in [LICENSE](../../LICENSE).

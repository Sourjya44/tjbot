# TJBot Hardware Tests

These tests are provided to help you ensure your TJBot's hardware is functioning correctly.

## Running Hardware Tests

Hardware tests are run via the `tjbot` launcher, which delegates to node-tjbotlib's live hardware test suite.

### List available tests

```sh
tjbot test
```

### Run a specific hardware test

```sh
tjbot test camera
tjbot test led
tjbot test microphone
tjbot test servo
tjbot test stt
tjbot test speaker
tjbot test tts
```

## How It Works

- Tests are sourced from `node-tjbotlib/tests/live/`
- Dependencies are automatically installed on first run
- Each test is interactive and will prompt you to verify that TJBot performed the expected action
- Tests require `sudo` for GPIO hardware access (automatically handled)

## Running Tests Without `tjbot`

You can run the hardware tests from this directory directly using `mise`:

```sh
mise run test-camera
mise run test-led
mise run test-microphone
mise run test-servo
mise run test-speaker
mise run test-stt
mise run test-tts
```

> 💡 `mise` will automatically install the latest version of `node-tjbotlib`, which is where the hardware tests are kept.

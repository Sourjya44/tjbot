# TJBot Hardware & Software Tests

These tests are provided to help you ensure your TJBot's hardware & software are functioning correctly.

## Running Tests

TJBot's tests are run via the `tjbot` launcher, which delegates to node-tjbotlib's live test suite.

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
tjbot test vision
```

## How It Works

- Tests are TypeScript-based and sourced from `node-tjbotlib/tests/live/`
- Dependencies are automatically installed on first run
- Each test is interactive and will prompt you to verify that TJBot performed the expected action

## Running Tests Without `tjbot`

You can run the hardware tests from this directory directly using `mise`:

```sh
mise run <test-name>
```

> 💡 `mise` will automatically install the latest version of `node-tjbotlib`, which is where the hardware tests are kept.

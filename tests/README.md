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
tjbot test speaker
```

## How It Works

- Tests are sourced from `node-tjbotlib/tests/live/`
- Dependencies are automatically installed on first run
- Each test is interactive and will prompt you to verify that TJBot performed the expected action
- Tests require `sudo` for GPIO hardware access (automatically handled)

## Environment Setup

If you're running tests from this directory directly, you can also use `mise`:

```sh
mise install      # Install node-tjbotlib dependency
```
